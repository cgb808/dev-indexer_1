#!/usr/bin/env python3
"""Ensure ann_runtime_config table exists and seed baseline parameter sets.

Usage:
  python ensure_ann_runtime_config.py                   # create table + upsert defaults
  ANN_PARAM_SET=balanced python ensure_ann_runtime_config.py --show balanced

Env:
  DATABASE_URL  Postgres DSN (required)

Table definition (simplified):
  name PRIMARY KEY
  metric TEXT (cosine|l2|ip) default l2
  lists INT (for IVF)
  probes INT (ivfflat.probes)
  ef_search INT (hnsw.ef_search)
  min_candidate INT
  max_candidate INT

Seed rows:
  default  : generic conservative probes
  fast     : fewer probes, lower recall
  balanced : medium probes / ef_search
  quality  : higher probes / ef_search, more candidates
"""
from __future__ import annotations
import os, sys, argparse
import psycopg2  # type: ignore

DDL = """
CREATE TABLE IF NOT EXISTS ann_runtime_config (
  name TEXT PRIMARY KEY,
  metric TEXT DEFAULT 'l2',
  lists INT,
  probes INT,
  ef_search INT,
  min_candidate INT DEFAULT 50,
  max_candidate INT DEFAULT 150,
  updated_at TIMESTAMPTZ DEFAULT now()
);
"""

SEED_ROWS = [
    ("default",  None,  None,  None,  50, 150),  # rely on planner defaults
    ("fast",     None,  5,     32,    40, 120),
    ("balanced", None,  10,    64,    50, 150),
    ("quality",  None,  20,    128,   60, 200),
]

UPSERT_SQL = """
INSERT INTO ann_runtime_config(name, metric, probes, ef_search, min_candidate, max_candidate)
VALUES (%s, COALESCE(%s,'l2'), %s, %s, %s, %s)
ON CONFLICT (name) DO UPDATE SET
  metric = EXCLUDED.metric,
  probes = EXCLUDED.probes,
  ef_search = EXCLUDED.ef_search,
  min_candidate = EXCLUDED.min_candidate,
  max_candidate = EXCLUDED.max_candidate,
  updated_at = now();
"""

def ensure(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)
        for row in SEED_ROWS:
            cur.execute(UPSERT_SQL, row)
    conn.commit()

def show(conn, name: str):
    with conn.cursor() as cur:
        cur.execute("SELECT name, metric, probes, ef_search, min_candidate, max_candidate FROM ann_runtime_config WHERE name=%s", (name,))
        r = cur.fetchone()
        if not r:
            print(f"(not found) {name}")
        else:
            print({
                "name": r[0],
                "metric": r[1],
                "probes": r[2],
                "ef_search": r[3],
                "min_candidate": r[4],
                "max_candidate": r[5],
            })

def list_all(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT name, probes, ef_search, min_candidate, max_candidate FROM ann_runtime_config ORDER BY name")
        for r in cur.fetchall():
            print(f"{r[0]:9s} probes={r[1]} ef_search={r[2]} cand=[{r[3]},{r[4]}]")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--show', help='Show a specific parameter set after seeding')
    ap.add_argument('--list', action='store_true', help='List all parameter sets after seeding')
    args = ap.parse_args()

    dsn = os.getenv('DATABASE_URL')
    if not dsn:
        print('DATABASE_URL not set', file=sys.stderr)
        sys.exit(1)
    with psycopg2.connect(dsn) as conn:
        ensure(conn)
        if args.show:
            show(conn, args.show)
        if args.list:
            list_all(conn)
        if not (args.show or args.list):
            print('Seeded ann_runtime_config (use --list to display)')

if __name__ == '__main__':  # pragma: no cover
    main()
