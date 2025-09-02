#!/usr/bin/env python3
"""Unified Retrieval Helper

Performs layered retrieval:
  - Recent conversation events (decay + similarity)
  - Conversation summaries
  - Document embeddings (knowledge)

Outputs JSON with ranked context blocks.
"""
from __future__ import annotations
import argparse, os, json, math, sys
from typing import List, Dict, Any
import requests

DSN = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
EMBED_ENDPOINT = os.getenv('EMBED_ENDPOINT','http://127.0.0.1:8000/model/embed')

def embed_query(q: str):
    r = requests.post(EMBED_ENDPOINT, json={'texts':[q]}, timeout=60)
    r.raise_for_status()
    return r.json()['embeddings'][0]

def pg_vector_param(dim: int) -> str:
    # Format as Postgres vector literal
    return '(' + ','.join('0' for _ in range(dim)) + ')'  # placeholder if not using server-side embedding

def retrieve(user_id: str, query: str, k_events: int, k_summ: int, k_docs: int) -> Dict[str, Any]:
    import psycopg2, psycopg2.extras
    qvec = embed_query(query)
    dim = len(qvec)
    import numpy as np
    pq = '(' + ','.join(str(x) for x in qvec) + ')'
    sql = f"""
    WITH recent AS (
      SELECT id, time, content, embedding, 1 - (embedding <=> {pq}::vector) AS sim
      FROM conversation_events
      WHERE user_id=%s AND embedded
        AND time > now() - interval '7 days'
        AND embedding IS NOT NULL
      ORDER BY time DESC
      LIMIT 400
    ), recent_rank AS (
      SELECT *, sim * exp(-EXTRACT(EPOCH FROM (now()-time))/86400.0 * 0.15) AS score
      FROM recent
      ORDER BY score DESC
      LIMIT %s
    ), summ AS (
      SELECT id, time, summary AS content, embedding, 1 - (embedding <=> {pq}::vector) AS score, scope
      FROM conversation_summaries
      WHERE user_id=%s AND embedding IS NOT NULL
      ORDER BY score DESC
      LIMIT %s
    ), docs AS (
      SELECT id, created_at AS time, chunk AS content, embedding, 1 - (embedding <=> {pq}::vector) AS score
      FROM doc_embeddings
      WHERE embedding IS NOT NULL
      ORDER BY embedding <=> {pq}::vector ASC
      LIMIT %s
    )
    SELECT 'event' AS kind, id, time, content, score FROM recent_rank
    UNION ALL
    SELECT 'summary', id, time, content, score FROM summ
    UNION ALL
    SELECT 'doc', id, time, content, score FROM docs
    ORDER BY score DESC
    LIMIT (%s+%s+%s);
    """
    with psycopg2.connect(DSN) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, (user_id, k_events, user_id, k_summ, k_docs, k_events, k_summ, k_docs))
            rows = cur.fetchall()
    return {
        'query': query,
        'user_id': user_id,
        'results': [dict(r) for r in rows]
    }

def main():
    ap = argparse.ArgumentParser(description='Unified retrieval over events/summaries/docs')
    ap.add_argument('--user-id', required=True)
    ap.add_argument('--query', required=True)
    ap.add_argument('--k-events', type=int, default=8)
    ap.add_argument('--k-summaries', type=int, default=4)
    ap.add_argument('--k-docs', type=int, default=8)
    ap.add_argument('--out')
    args = ap.parse_args()
    data = retrieve(args.user_id, args.query, args.k_events, args.k_summaries, args.k_docs)
    out = json.dumps(data, indent=2)
    if args.out:
        with open(args.out,'w',encoding='utf-8') as f: f.write(out)
    print(out)

if __name__=='__main__':
    main()
