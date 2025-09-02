#!/usr/bin/env python
"""Memory ↔ RAG Bridge

Watches an MCP memory server file (JSONL) and ingests new memories into the
`doc_embeddings` table for semantic retrieval.

Env Vars:
  MEMORY_FILE_PATH (required) - path used by @modelcontextprotocol/server-memory
  DATABASE_URL (required)     - Postgres DSN with pgvector
  EMBED_ENDPOINT (optional)   - HTTP endpoint that accepts {"texts": [...]} and returns {"embeddings": [...]}
                                default: http://127.0.0.1:8000/model/embed
  BATCH_SIZE (optional)       - Number of memory lines to batch per embedding call (default 16)
  LOOP_INTERVAL (optional)    - Seconds to sleep between polling cycles (default 2)

CLI Usage:
  python memory_rag_bridge.py --once      # Run single sync pass then exit
  python memory_rag_bridge.py --search "query text" --top-k 5
  python memory_rag_bridge.py             # Continuous tail + ingest

Assumptions:
  * Memory file is append-only JSON Lines where each line is a JSON object containing at least:
      id (string/number), content (string), created_at (ISO) or timestamp.
    If fields differ, map them in `_extract_text`.
  * Duplicate prevention via storing a hash of content in doc_embeddings.batch_tag or using a dedicated table.
"""
from __future__ import annotations
import os, time, json, hashlib, argparse, sys, signal, math
from dataclasses import dataclass
from typing import List, Optional
import psycopg2
from psycopg2.extras import execute_values
import requests

EMBED_ENDPOINT = os.getenv("EMBED_ENDPOINT", "http://127.0.0.1:8000/model/embed")
DSN = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
MEM_PATH = os.getenv("MEMORY_FILE_PATH")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "16"))
LOOP_INTERVAL = float(os.getenv("LOOP_INTERVAL", "2"))
OFFSET_FILE = os.getenv("MEMORY_OFFSET_FILE", ".memory_rag_offset")
EMBED_RETRIES = int(os.getenv("EMBED_RETRIES", "3"))
EMBED_BACKOFF_BASE = float(os.getenv("EMBED_BACKOFF_BASE", "0.75"))
SIMILARITY_METRIC = os.getenv("VECTOR_METRIC", "l2").lower()  # l2 | cosine

if not DSN:
    print("[bridge] DATABASE_URL not set", file=sys.stderr)
if not MEM_PATH:
    print("[bridge] MEMORY_FILE_PATH not set", file=sys.stderr)

@dataclass
class MemoryLine:
    raw: dict
    text: str
    content_hash: str
    memory_id: str | None = None
    created_at: str | None = None

def _extract_text(obj: dict) -> str:
    # Adaptable mapping logic.
    if 'content' in obj:
        c = obj['content']
        if isinstance(c, dict) and 'text' in c:
            return str(c['text'])
        return str(c)
    # Fallback join of string values
    parts = []
    for k,v in obj.items():
        if isinstance(v, str):
            parts.append(v)
    return " | ".join(parts)

def load_ingested_hashes(conn) -> set:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memory_ingest_dedup (
              content_hash TEXT PRIMARY KEY,
              inserted_at TIMESTAMPTZ DEFAULT now()
            );
        """)
        cur.execute("SELECT content_hash FROM memory_ingest_dedup")
        return {r[0] for r in cur.fetchall()}

def mark_hashes(conn, hashes: List[str]):
    with conn.cursor() as cur:
        execute_values(cur,
            "INSERT INTO memory_ingest_dedup(content_hash) VALUES %s ON CONFLICT DO NOTHING",
            [(h,) for h in hashes])

def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    attempt = 0
    while True:
        try:
            r = requests.post(EMBED_ENDPOINT, json={"texts": texts}, timeout=120)
            r.raise_for_status()
            data = r.json()
            embs = data['embeddings']
            if len(embs) != len(texts):
                raise RuntimeError(f"Embedding count mismatch {len(embs)} vs {len(texts)}")
            # If cosine metric expected, optionally normalize client-side to unit length
            if SIMILARITY_METRIC == 'cosine':
                normed=[]
                for v in embs:
                    norm=math.sqrt(sum(x*x for x in v)) or 1.0
                    normed.append([x / norm for x in v])
                return normed
            return embs
        except Exception as e:
            attempt += 1
            if attempt > EMBED_RETRIES:
                print(f"[bridge] embedding failed after {EMBED_RETRIES} retries: {e}", file=sys.stderr)
                raise
            backoff = EMBED_BACKOFF_BASE * (2 ** (attempt-1))
            print(f"[bridge] embed error: {e}; retry {attempt}/{EMBED_RETRIES} in {backoff:.2f}s", file=sys.stderr)
            time.sleep(backoff)

def _has_column(conn, table: str, column: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name=%s AND column_name=%s
        """, (table, column))
        return cur.fetchone() is not None

_COLUMN_CACHE = {}
def has_col(conn, table: str, column: str) -> bool:
    key=(table,column)
    if key not in _COLUMN_CACHE:
        _COLUMN_CACHE[key]=_has_column(conn, table, column)
    return _COLUMN_CACHE[key]

def insert_embeddings(conn, mems: List[MemoryLine], vectors: List[List[float]]):
    if not mems:
        return
    rows_meta = []
    include_metadata = has_col(conn, 'doc_embeddings', 'metadata')
    include_content_hash_col = has_col(conn, 'doc_embeddings', 'content_hash')
    # Build per-row meta
    for m, vec in zip(mems, vectors):
        meta = {
            "memory_id": m.memory_id,
            "created_at": m.created_at,
        }
        rows_meta.append((m, vec, meta))
    with conn.cursor() as cur:
        if include_metadata and include_content_hash_col:
            execute_values(cur, """
                INSERT INTO doc_embeddings (source, chunk, embedding, content_hash, metadata, batch_tag)
                VALUES %s ON CONFLICT DO NOTHING
            """, [ ("memory", m.text, vec, m.content_hash, json.dumps(meta), m.content_hash) for m, vec, meta in rows_meta ])
        elif include_metadata:
            execute_values(cur, """
                INSERT INTO doc_embeddings (source, chunk, embedding, metadata, batch_tag)
                VALUES %s ON CONFLICT DO NOTHING
            """, [ ("memory", m.text, vec, json.dumps(meta), m.content_hash) for m, vec, meta in rows_meta ])
        else:
            execute_values(cur, """
                INSERT INTO doc_embeddings (source, chunk, embedding, batch_tag)
                VALUES %s ON CONFLICT DO NOTHING
            """, [ ("memory", m.text, vec, m.content_hash) for m, vec, _ in rows_meta ])

def _load_offset() -> int:
    try:
        with open(OFFSET_FILE, 'r') as f:
            return int(f.read().strip() or 0)
    except Exception:
        return 0

def _store_offset(offset: int):
    try:
        with open(OFFSET_FILE, 'w') as f:
            f.write(str(offset))
    except Exception as e:
        print(f"[bridge] failed to store offset: {e}", file=sys.stderr)

def tail_once(state):
    new_lines = []
    with open(MEM_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(state['offset'])
        while True:
            line = f.readline()
            if not line:
                break
            state['offset'] = f.tell()
            line=line.strip()
            if not line:
                continue
            try:
                obj=json.loads(line)
            except Exception:
                continue
            txt=_extract_text(obj)
            if not txt:
                continue
            h=hashlib.sha256(txt.encode('utf-8')).hexdigest()
            m_id = str(obj.get('id')) if 'id' in obj else None
            created = obj.get('created_at') or obj.get('timestamp') or None
            new_lines.append(MemoryLine(obj, txt, h, m_id, created))
    return new_lines

_SHUTDOWN=False
def _handle_sig(signum, frame):
    global _SHUTDOWN
    _SHUTDOWN=True
    print(f"[bridge] signal {signum} received; shutting down after current batch")

signal.signal(signal.SIGINT, _handle_sig)
signal.signal(signal.SIGTERM, _handle_sig)

def process_new():
    if not (DSN and MEM_PATH):
        print("[bridge] missing DSN or MEM_PATH; exiting")
        return
    state={'offset': _load_offset()}
    with psycopg2.connect(DSN) as conn:
        dedup = load_ingested_hashes(conn)
        print(f"[bridge] start offset={state['offset']} dedup={len(dedup)} metric={SIMILARITY_METRIC}")
        while True:
            mems = [m for m in tail_once(state) if m.content_hash not in dedup]
            if mems:
                total=len(mems)
                for i in range(0, total, BATCH_SIZE):
                    if _SHUTDOWN: break
                    batch=mems[i:i+BATCH_SIZE]
                    vecs=embed_texts([m.text for m in batch])
                    insert_embeddings(conn, batch, vecs)
                    mark_hashes(conn, [m.content_hash for m in batch])
                    dedup.update(m.content_hash for m in batch)
                print(f"[bridge] Ingested {total} new memory lines (offset={state['offset']})")
                _store_offset(state['offset'])
            if _SHUTDOWN or ARGS.once:
                break
            time.sleep(LOOP_INTERVAL)
    _store_offset(state['offset'])

def similarity_search(query: str, top_k: int):
    if not DSN:
        print("DATABASE_URL not set", file=sys.stderr); return
    vec = embed_texts([query])[0]
    op = '<->'
    score_expr = '1 - (embedding <-> %s::vector)' if SIMILARITY_METRIC=='cosine' else '1 - (embedding <-> %s::vector)'
    # For cosine when storing normalized vectors, L2 over unit vectors is monotonic; can switch to <=> if opclass installed.
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT chunk, {score_expr} AS score
                FROM doc_embeddings
                WHERE source='memory'
                ORDER BY embedding {op} %s::vector
                LIMIT %s
            """, (vec, vec, top_k))
            for chunk, score in cur.fetchall():
                print(f"[score={score:.4f}] {chunk[:160]}")

parser = argparse.ArgumentParser(description="Continuously sync memory JSONL into pgvector and allow similarity search.")
parser.add_argument('--once', action='store_true', help='Single pass ingest then exit')
parser.add_argument('--search', type=str, help='Run a semantic search instead of ingest loop')
parser.add_argument('--top-k', type=int, default=int(os.getenv('RAG_TOP_K_DEFAULT', '5')))
parser.add_argument('--metric', choices=['l2','cosine'], help='Override similarity metric for this run')
ARGS = parser.parse_args()

if ARGS.metric:
    SIMILARITY_METRIC = ARGS.metric

def main():
    if ARGS.search:
        similarity_search(ARGS.search, ARGS.top_k)
    else:
        process_new()

if __name__ == '__main__':
    main()
