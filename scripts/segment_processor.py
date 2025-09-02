#!/usr/bin/env python3
"""Segment Processor

Consumes sealed append log segments (.log) containing length-prefixed msgpack
frames and inserts rows into conversation_events. Optionally queues embeddings
or performs immediate embedding via EMBED_ENDPOINT.
"""
from __future__ import annotations
import argparse, os, struct, sys, json, hashlib
from datetime import datetime, UTC
from pathlib import Path
from typing import List
import requests

try:
    import msgpack  # type: ignore
except Exception as e:  # noqa: BLE001
    print("msgpack required", e, file=sys.stderr); raise

DSN = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
EMBED_ENDPOINT = os.getenv('EMBED_ENDPOINT','http://127.0.0.1:8000/model/embed')

def read_frames(path: Path):
    with path.open('rb') as fh:
        while True:
            hdr = fh.read(4)
            if not hdr:
                break
            if len(hdr)!=4:
                print(f"[warn] truncated frame in {path}")
                break
            (length,) = struct.unpack('>I', hdr)
            payload = fh.read(length)
            if len(payload)!=length:
                print(f"[warn] incomplete frame in {path}")
                break
            try:
                obj = msgpack.unpackb(payload, raw=False)
                yield obj
            except Exception as e:  # noqa: BLE001
                print(f"[warn] frame decode failed: {e}")

def embed_texts(chunks: List[str]):
    if not chunks:
        return []
    r = requests.post(EMBED_ENDPOINT, json={'texts': chunks}, timeout=180)
    r.raise_for_status()
    embs = r.json().get('embeddings', [])
    return embs

def process(path: Path, immediate_embed: bool, dry_run: bool=False):
    frames = list(read_frames(path))
    if not frames:
        return 0
    contents = [f.get('content','') for f in frames]
    embeddings = []
    if immediate_embed:
        embeddings = embed_texts(contents)
    if not DSN and not dry_run:
        raise SystemExit('No DATABASE_URL/SUPABASE_DB_URL for insert')
    if dry_run:
        print(f"[dry] would insert {len(frames)} events")
        return len(frames)
    import psycopg2, psycopg2.extras
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            rows=[]
            for i,f in enumerate(frames):
                emb = embeddings[i] if immediate_embed and i < len(embeddings) else None
                rows.append((
                    f.get('time'), f.get('session_id'), f.get('user_id'), f.get('role','user'),
                    f.get('seq'), f.get('content'), emb, bool(emb),
                    hashlib.sha256(f.get('content','').encode()).hexdigest(),
                    None, 'candidate', json.dumps(f.get('metadata') or {})
                ))
            psycopg2.extras.execute_values(cur, """
                INSERT INTO conversation_events (time, session_id, user_id, role, seq, content, embedding, embedded, content_hash, importance, retention_policy, metadata)
                VALUES %s
            """, rows)
    print(f"[segment] inserted {len(frames)} events from {path}")
    return len(frames)

def main():
    ap = argparse.ArgumentParser(description='Process sealed append log segments into conversation_events')
    ap.add_argument('--segment', required=True)
    ap.add_argument('--immediate-embed', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    process(Path(args.segment), args.immediate_embed, args.dry_run)

if __name__=='__main__':
    main()
