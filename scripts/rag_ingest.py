#!/usr/bin/env python
"""Batch ingest for RAG doc embeddings.

Usage:
    python scripts/rag_ingest.py --source docs --file path/to/file.txt
    python scripts/rag_ingest.py --source guide --glob 'docs/**/*.md'

Features:
    * Overlapping fixed-size character chunking (configurable)
    * Embedding via local HTTP endpoint (expects {"embeddings": [[...], ...]})
    * Inserts into Postgres doc_embeddings (pgvector) with optional metadata JSONB
    * Adds per-chunk SHA256 content hash to metadata for future dedupe
    * Dry-run mode to preview rows without inserting
    * Basic duplicate suppression within a single batch (hash set)

Optional (flags / env):
    * Generate MessagePack batch artifact (list of chunk records) for Supabase wrapper
    * Publish Redis Pub/Sub summary (small msgpack payload) announcing new batch
      - Channel defaults to RAG_INDEX_UPDATES (override via REDIS_CHANNEL)
      - Redis URL via REDIS_URL (ex: redis://localhost:6379/0)
      - Embeddings excluded from MessagePack unless --include-embeddings set
    * Offline mode (--offline) skips embedding HTTP + DB insert; still chunks and writes msgpack for later replay

Env Vars:
    REDIS_URL, REDIS_CHANNEL, RAG_MSGPACK_DIR (fallback for --msgpack-out)

Redis Publication Format (summary message):
    {
       "event": "rag_index_batch",
       "batch_tag": str,
       "source": str,
       "row_count": int,
       "embedding_dim": int,
       "file": path to msgpack artifact (if written),
       "timestamp": iso8601
    }

Future (not yet implemented here): streaming embeddings, async batching, multi-model routing.
"""
from __future__ import annotations
import os, argparse, glob, json, hashlib, time
from datetime import datetime, UTC
from typing import Optional
import requests
from typing import List, Sequence, Tuple
import re

def simple_clarifying_questions(text: str, n: int) -> List[str]:
    """Heuristic placeholder: extract candidate noun phrases / capitalized terms and form questions.
    This should be replaced by a model-based generator (LLM) later.
    """
    # crude candidate terms
    tokens = re.findall(r"[A-Z][a-zA-Z]{3,}\b", text)[:10]
    dedup = []
    for t in tokens:
        if t.lower() not in {d.lower() for d in dedup}:
            dedup.append(t)
    questions = []
    for t in dedup[:n]:
        questions.append(f"What is the significance of {t} in this context?")
    # fallback generic if insufficient
    while len(questions) < n:
        questions.append("What additional context would clarify this section?")
    return questions[:n]

def generate_and_persist_clarifying(rows: List[Tuple[str, str, List[float], dict, str]], n: int, model_name: str, dry_run: bool=False):
    if not DSN and not dry_run:
        print('[clarify] DATABASE_URL not set; skipping persist')
        return
    out_records = []
    total_q = 0
    for (src, chunk, emb, meta, batch_tag) in rows:
        qs = simple_clarifying_questions(chunk, n)
        for q in qs:
            out_records.append({
                'content_hash': meta.get('content_hash'),
                'question': q,
                'priority': 5,
                'model_name': model_name,
                'metadata': {'source': src, 'batch_tag': batch_tag}
            })
            total_q += 1
    if dry_run:
        print(f"[clarify][dry-run] Would insert {len(out_records)} questions")
        return
    import psycopg2, psycopg2.extras
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO chunk_clarifying_questions(content_hash, question, priority, model_name, metadata)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                [ (r['content_hash'], r['question'], r['priority'], r['model_name'], json.dumps(r['metadata'])) for r in out_records ]
            )
    print(f"[clarify] inserted {len(out_records)} clarifying questions")
    # Prometheus exposition (plain text metrics line) optional: simply log
    print(f"metric clarify_questions_generated_total {len(out_records)}")

EMBED_ENDPOINT = os.getenv("EMBED_ENDPOINT", "http://127.0.0.1:8000/model/embed")
# Allow SUPABASE style fallback var
DSN = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")

DEFAULT_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", 800))
DEFAULT_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", 80))
DEFAULT_MSGPACK_DIR = os.getenv("RAG_MSGPACK_DIR", "data/msgpack")

def now_iso() -> str:
    return datetime.now(UTC).isoformat()

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def read_text(path: str) -> str:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def chunk_text(txt: str, chunk_size: int, overlap: int) -> List[Tuple[str, int, int]]:
    """Return list of (segment, char_start, char_end)."""
    txt = txt.replace('\r','')
    segments=[]; start=0; n=len(txt)
    while start < n:
        end = min(start+chunk_size, n)
        seg_raw = txt[start:end]
        seg = seg_raw.strip()
        if seg:
            # compute trimmed offsets relative to original start
            left_trim = len(seg_raw) - len(seg_raw.lstrip())
            right_trim = len(seg_raw) - len(seg_raw.rstrip())
            seg_start = start + left_trim
            seg_end = end - right_trim
            segments.append((seg, seg_start, seg_end))
        next_start = end - overlap
        if next_start <= start:  # prevent infinite loop
            next_start = end
        start = next_start
        if start >= n:
            break
    return segments

def embed(chunks: Sequence[str]) -> List[List[float]]:
    if not chunks:
        return []
    r = requests.post(EMBED_ENDPOINT, json={"texts": list(chunks)}, timeout=180)
    r.raise_for_status()
    data = r.json()
    embs = data["embeddings"]
    if len(embs) != len(chunks):
        raise RuntimeError(f"Embedding count mismatch: got {len(embs)} for {len(chunks)} inputs")
    return embs

def insert(rows: List[Tuple[str, str, List[float], dict, str]], dry_run: bool=False, return_ids: bool=False):
    if dry_run:
        print(f"[dry-run] Would insert {len(rows)} rows")
        return
    if not DSN:
        raise SystemExit("DATABASE_URL / SUPABASE_DB_URL not set")
    from psycopg2.extras import execute_values, Json
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            sql = """
                INSERT INTO doc_embeddings (source, chunk, embedding, metadata, batch_tag)
                VALUES %s RETURNING id
            """ if return_ids else """
                INSERT INTO doc_embeddings (source, chunk, embedding, metadata, batch_tag)
                VALUES %s
            """
            execute_values(
                cur,
                sql,
                [ (src, chunk, emb, Json(meta), batch) for (src, chunk, emb, meta, batch) in rows ]
            )
            if return_ids:
                return [r[0] for r in cur.fetchall()]
    return []

def write_msgpack(rows: List[Tuple[str, str, List[float], dict, str]], out_dir: str, include_embeddings: bool, source: str, batch_tag: str) -> Optional[str]:
    """Write a MessagePack artifact of the batch rows.

    Returns path to file or None if skipped.
    """
    if not rows:
        return None
    try:
        import msgpack  # type: ignore
    except Exception:
        print("[msgpack] python-msgpack not installed; skipping artifact")
        return None
    os.makedirs(out_dir, exist_ok=True)
    # Determine embedding dim if consistent
    emb_dim = len(rows[0][2]) if rows and rows[0][2] else 0
    records = []
    for (src, chunk, emb, meta, batch) in rows:
        rec = {
            "source": src,
            "text": chunk,
            "metadata": meta,
            "batch_tag": batch,
        }
        if include_embeddings:
            rec["embedding"] = emb
        records.append(rec)
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    filename = f"rag_batch_{source}_{batch_tag}_{ts}.msgpack"
    path = os.path.join(out_dir, filename)
    with open(path, 'wb') as f:
        f.write(msgpack.packb({
            "version": 1,
            "created_at": now_iso(),
            "source": source,
            "batch_tag": batch_tag,
            "embedding_dim": emb_dim,
            "count": len(records),
            "records": records,
        }, use_bin_type=True))
    print(f"[msgpack] wrote {len(records)} records -> {path}")
    return path

def publish_redis_summary(redis_url: str, channel: str, source: str, batch_tag: str, row_count: int, emb_dim: int, artifact_path: Optional[str]):
    try:
        import redis  # type: ignore
    except Exception:
        print("[redis] redis-py not installed; skipping publish")
        return
    try:
        import msgpack  # type: ignore
    except Exception:
        print("[redis] msgpack not installed; skipping publish")
        return
    try:
        r = redis.from_url(redis_url)
        summary = {
            "event": "rag_index_batch",
            "source": source,
            "batch_tag": batch_tag,
            "row_count": row_count,
            "embedding_dim": emb_dim,
            "file": artifact_path,
            "timestamp": now_iso(),
        }
        payload = msgpack.packb(summary, use_bin_type=True)
        r.publish(channel, payload)
        print(f"[redis] published summary to {channel} ({row_count} rows)")
    except Exception as e:
        print(f"[redis] publish failed: {e}")

def process(paths: List[str], source: str, batch_tag: str, chunk_size: int, overlap: int, dry_run: bool=False, limit_files: int|None=None,
            msgpack_out: Optional[str]=None, publish_redis: bool=False, include_embeddings: bool=False,
            redis_url: Optional[str]=None, redis_channel: str="RAG_INDEX_UPDATES", offline: bool=False,
            register_artifact: bool=False, timescale_flag: bool=True,
            gen_clarifying: int = 0, clarifying_model: str | None = None):
    all_rows: List[Tuple[str, str, List[float], dict, str]] = []
    seen_hashes = set()
    file_count = 0
    for p in paths:
        if limit_files is not None and file_count >= limit_files:
            break
        file_count += 1
        try:
            txt = read_text(p)
        except Exception as e:
            print(f"[warn] Failed to read {p}: {e}")
            continue
        segments = chunk_text(txt, chunk_size, overlap)
        if not segments:
            continue
        seg_texts = [s for s,_,_ in segments]
        if offline:
            embs = [[] for _ in seg_texts]  # placeholder empty embeddings
        else:
            embs = embed(seg_texts)
        dim = len(embs[0]) if embs and embs[0] else 0
    for (seg, start, end), emb in zip(segments, embs):
            h = sha256_text(seg)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            meta = {
                "path": p,
                "char_start": start,
                "char_end": end,
                "content_hash": h,
                "chunk_size": chunk_size,
                "overlap": overlap,
                "embedding_dim": dim,
            }
            all_rows.append((source, seg, emb, meta, batch_tag))
    artifact_path = None
    inserted_ids = []
    if all_rows:
        if not offline:
            inserted_ids = insert(all_rows, dry_run=dry_run, return_ids=register_artifact)
        else:
            print(f"[offline] Skipping DB insert; prepared {len(all_rows)} rows")
        if msgpack_out:
            artifact_path = write_msgpack(all_rows, msgpack_out, include_embeddings, source, batch_tag)
        if publish_redis and not dry_run and not offline:
            emb_dim = len(all_rows[0][2]) if all_rows and all_rows[0][2] else 0
            publish_redis_summary(
                redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                os.getenv("REDIS_CHANNEL", redis_channel),
                source,
                batch_tag,
                len(all_rows),
                emb_dim,
                artifact_path,
            )
        # Register artifact + mapping if requested
        if register_artifact and not dry_run and not offline and (artifact_path or inserted_ids):
            try:
                import psycopg2
                import psycopg2.extras
                sha256_val = None
                if artifact_path and os.path.exists(artifact_path):
                    h = hashlib.sha256()
                    with open(artifact_path,'rb') as fh:
                        for chunk in iter(lambda: fh.read(65536), b''):
                            h.update(chunk)
                    sha256_val = h.hexdigest()
                with psycopg2.connect(DSN) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO artifact_registry(artifact_type, path, sha256, bytes, metadata)
                            VALUES (%s,%s,%s,%s,%s) RETURNING id
                            """,
                            (
                                'rag_msgpack_batch',
                                artifact_path or 'inline_rows',
                                sha256_val,
                                os.path.getsize(artifact_path) if artifact_path and os.path.exists(artifact_path) else None,
                                json.dumps({'source': source, 'batch_tag': batch_tag, 'row_count': len(all_rows)})
                            )
                        )
                        art_id = cur.fetchone()[0]
                        if inserted_ids:
                            psycopg2.extras.execute_values(
                                cur,
                                "INSERT INTO doc_embedding_artifact_map(artifact_id, embedding_id) VALUES %s",
                                [(art_id, eid) for eid in inserted_ids]
                            )
                print(f"[artifact] registered artifact id={art_id} rows={len(inserted_ids)}")
            except Exception as e:
                print(f"[artifact] registration failed: {e}")
    # Clarifying question generation (post collection, before returning)
    if gen_clarifying > 0 and all_rows:
        try:
            generate_and_persist_clarifying(all_rows, gen_clarifying, clarifying_model or 'clarify-default', dry_run=dry_run or offline)
        except Exception as e:
            print(f"[clarify] generation failed: {e}")
    return len(all_rows)

def main():
    ap = argparse.ArgumentParser(description="Ingest documents into pgvector doc_embeddings with metadata and hashing.")
    ap.add_argument('--source', required=True)
    ap.add_argument('--file')
    ap.add_argument('--glob')
    ap.add_argument('--batch-tag', default='manual_ingest')
    ap.add_argument('--chunk-size', type=int, default=DEFAULT_CHUNK_SIZE)
    ap.add_argument('--overlap', type=int, default=DEFAULT_OVERLAP)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--max-files', type=int)
    ap.add_argument('--msgpack-out', help='Directory to write MessagePack batch (enables msgpack output)', default=None)
    ap.add_argument('--publish-redis', action='store_true', help='Publish Redis summary event (requires redis lib)')
    ap.add_argument('--include-embeddings', action='store_true', help='Include embeddings inside msgpack records (larger)')
    ap.add_argument('--offline', action='store_true', help='Skip embedding + DB insert; still produce msgpack & (optionally) redis publish disabled')
    ap.add_argument('--register-artifact', action='store_true', help='Register batch artifact + map embedding ids')
    ap.add_argument('--gen-clarifying', type=int, default=0, help='Generate N clarifying questions per chunk (simple heuristic)')
    ap.add_argument('--clarify-model', type=str, help='Model name/id used for clarifying generation logging')
    args = ap.parse_args()
    paths=[]
    if args.file:
        paths.append(args.file)
    if args.glob:
        paths.extend(glob.glob(args.glob, recursive=True))
    if not paths:
        raise SystemExit('Provide --file or --glob')
    msgpack_dir = args.msgpack_out or (DEFAULT_MSGPACK_DIR if args.msgpack_out is not None else None)
    total = process(paths, args.source, args.batch_tag, args.chunk_size, args.overlap, dry_run=args.dry_run, limit_files=args.max_files,
                    msgpack_out=msgpack_dir, publish_redis=args.publish_redis, include_embeddings=args.include_embeddings,
                    offline=args.offline, register_artifact=args.register_artifact,
                    gen_clarifying=args.gen_clarifying, clarifying_model=args.clarify_model)
    print(f"Rows processed: {total} (dry-run={args.dry_run})")

if __name__ == '__main__':
    main()
