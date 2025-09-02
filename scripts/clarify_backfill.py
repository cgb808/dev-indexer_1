#!/usr/bin/env python
"""Backfill clarifying questions for existing doc_embeddings rows lacking them.

Strategy:
- Select chunks with clarifying_question_count IS NULL or < target_min (default 1)
- Generate up to N questions per chunk (--per-chunk)
- Insert into chunk_clarifying_questions (id / content_hash linking)
- Update counts via DB trigger (if present); fallback manual update if desired.
- Emits basic Prometheus-style metrics lines if --emit-metrics specified.

This uses the same simple heuristic as rag_ingest for now; can be swapped for model API.
"""
from __future__ import annotations
import argparse, os, sys, re, json, time
from typing import List, Tuple

DSN = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')

import psycopg2, psycopg2.extras

def simple_clarifying_questions(text: str, n: int) -> List[str]:
    tokens = re.findall(r"[A-Z][a-zA-Z]{3,}\b", text)[:10]
    dedup = []
    for t in tokens:
        if t.lower() not in {d.lower() for d in dedup}:
            dedup.append(t)
    qs = [f"What is the significance of {t} here?" for t in dedup[:n]]
    while len(qs) < n:
        qs.append("What further context would make this clearer?")
    return qs[:n]

def fetch_target_chunks(limit: int, min_existing: int, conn) -> List[Tuple[int,str,str]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, chunk, metadata->>'content_hash' FROM doc_embeddings
            WHERE COALESCE(clarifying_question_count,0) < %s
            ORDER BY id ASC
            LIMIT %s
            """, (min_existing, limit)
        )
        return cur.fetchall()

def insert_questions(records, conn, model_name: str):
    with conn.cursor() as cur:
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO chunk_clarifying_questions(embedding_chunk_id, content_hash, question, priority, model_name, metadata)
            VALUES %s ON CONFLICT DO NOTHING
            """,
            records
        )

def backfill(batch_size: int, per_chunk: int, loop: bool, sleep_s: float, target_min: int, model_name: str, emit_metrics: bool):
    if not DSN:
        raise SystemExit('DATABASE_URL not set')
    total_inserted = 0
    start = time.time()
    while True:
        with psycopg2.connect(DSN) as conn:
            chunks = fetch_target_chunks(batch_size, target_min, conn)
            if not chunks:
                if emit_metrics:
                    print(f"metric clarifying_backfill_empty_batches_total 1")
                if not loop:
                    break
                time.sleep(sleep_s)
                continue
            recs = []
            for (cid, chunk_text, content_hash) in chunks:
                qs = simple_clarifying_questions(chunk_text, per_chunk)
                for q in qs:
                    recs.append((cid, content_hash, q, 5, model_name, json.dumps({'source':'backfill'})))
            insert_questions(recs, conn, model_name)
            inserted = len(recs)
            total_inserted += inserted
            if emit_metrics:
                print(f"metric clarifying_backfill_inserted_total {inserted}")
            print(f"[backfill] inserted {inserted} questions (chunks={len(chunks)}) total={total_inserted}")
        if not loop:
            break
        time.sleep(sleep_s)
    dur = time.time() - start
    if emit_metrics:
        print(f"metric clarifying_backfill_runtime_seconds {dur:.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch-size', type=int, default=200)
    ap.add_argument('--per-chunk', type=int, default=1)
    ap.add_argument('--loop', action='store_true')
    ap.add_argument('--sleep', type=float, default=30.0)
    ap.add_argument('--target-min', type=int, default=1, help='Ensure at least this many questions per chunk')
    ap.add_argument('--model-name', default='clarify-default')
    ap.add_argument('--emit-metrics', action='store_true')
    args = ap.parse_args()
    backfill(args.batch_size, args.per_chunk, args.loop, args.sleep, args.target_min, args.model_name, args.emit_metrics)

if __name__ == '__main__':
    main()
