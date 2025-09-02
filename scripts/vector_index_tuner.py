#!/usr/bin/env python3
"""Suggest IVF lists parameter for pgvector index based on row count.

Formula: recommended_lists ≈ clamp( sqrt(N), 16, 2000 )
Where N = total rows in doc_embeddings with non-null embedding.

Outputs a reindex SQL snippet if current lists differs.

Requires DATABASE_URL / SUPABASE_DB_URL or psql via docker-compose service.
"""
from __future__ import annotations

import os, math, json, sys, re
import argparse
import subprocess

def query_row_count(psql_cmd: list[str]) -> int:
    q = "SELECT count(*) FROM doc_embeddings WHERE embedding IS NOT NULL;"
    cmd = psql_cmd + ['-t', '-c', q]
    out = subprocess.check_output(cmd, text=True)
    return int(out.strip()) if out.strip() else 0

def query_index_def(psql_cmd: list[str]) -> str:
    q = "SELECT pg_get_indexdef(indexrelid) FROM pg_stat_user_indexes WHERE indexrelname='doc_embeddings_embedding_ivf'";
    cmd = psql_cmd + ['-t', '-c', q]
    out = subprocess.check_output(cmd, text=True)
    return out.strip()

def parse_lists(defn: str) -> int | None:
    m = re.search(r"lists='?(\\d+)'?", defn)
    if m:
        return int(m.group(1))
    return None

def main():
    ap = argparse.ArgumentParser(description='Suggest pgvector IVF lists param')
    ap.add_argument('--psql', help='Explicit psql command prefix, e.g. "psql -U zenglow -d zenglow -h localhost -p 54322"')
    ap.add_argument('--service', default='timescaledb-local', help='Compose service (if using docker-compose exec)')
    ap.add_argument('--compose-file', default='docker-compose.dev-core.yml')
    args = ap.parse_args()

    if args.psql:
        psql_cmd = args.psql.split()
    else:
        psql_cmd = ['docker-compose','-f', args.compose_file,'exec','-T', args.service,'psql','-U','zenglow','-d','zenglow']

    try:
        rows = query_row_count(psql_cmd)
    except Exception as e:
        print(f"Failed to query rows: {e}", file=sys.stderr)
        return 2
    rec_lists = max(16, min(2000, round(math.sqrt(rows) or 16)))
    try:
        defn = query_index_def(psql_cmd)
        current = parse_lists(defn) if defn else None
    except Exception:
        current = None
        defn = ''
    suggestion = {
        'rows': rows,
        'recommended_lists': rec_lists,
        'current_index_def': defn or None,
        'current_lists': current,
        'needs_change': current is not None and current != rec_lists,
        'reindex_sql': f"DROP INDEX IF EXISTS doc_embeddings_embedding_ivf; CREATE INDEX doc_embeddings_embedding_ivf ON doc_embeddings USING ivfflat (embedding vector_l2_ops) WITH (lists={rec_lists});"
    }
    print(json.dumps(suggestion, indent=2))
    return 0

if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
