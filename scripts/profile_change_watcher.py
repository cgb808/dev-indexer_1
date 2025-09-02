#!/usr/bin/env python3
"""Poll family/member/profile tables for changes to a target member (default Charles Bowen).

Temporary utility until Leonardo model is trained (then event-driven approach will replace).

Features:
  * Periodic checksum of member + profile row JSON
  * Emits log line on change with diff keys
  * Optional Redis publish (--redis-url) channel PROFILE_CHANGE (msgpack summary)
  * Optional webhook POST (--webhook) with JSON payload

Usage:
  python dev-indexer_1/scripts/profile_change_watcher.py --dsn $DATABASE_URL --interval 15
"""
from __future__ import annotations
import os, time, json, argparse, hashlib, psycopg2
from psycopg2.extras import RealDictCursor

def fetch_profile(conn, full_name: str):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT m.id as member_id, m.full_name, m.role, f.family_key, f.display_name,
                   p.preferences, p.traits, p.updated_at
            FROM family_members m
            JOIN families f ON f.id = m.family_id
            LEFT JOIN member_profiles p ON p.member_id = m.id
            WHERE m.full_name=%s
            LIMIT 1
            """, (full_name,))
        row = cur.fetchone()
    return row

def stable_hash(obj) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(",",":"))
    return hashlib.sha256(data.encode()).hexdigest()

def publish_redis(redis_url: str, payload: dict):
    try:
        import redis, msgpack  # type: ignore
        r = redis.from_url(redis_url)
        r.publish('PROFILE_CHANGE', msgpack.packb(payload, use_bin_type=True))
    except Exception as e:  # noqa: BLE001
        print(f"[redis] publish failed: {e}")

def post_webhook(url: str, payload: dict):
    try:
        import requests  # type: ignore
        requests.post(url, json=payload, timeout=5)
    except Exception as e:  # noqa: BLE001
        print(f"[webhook] post failed: {e}")

def main():
    ap = argparse.ArgumentParser(description='Poll for profile changes')
    ap.add_argument('--dsn', default=os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL'), help='Postgres DSN')
    ap.add_argument('--full-name', default='Charles Bowen')
    ap.add_argument('--interval', type=int, default=20)
    ap.add_argument('--redis-url')
    ap.add_argument('--webhook')
    ap.add_argument('--once', action='store_true')
    args = ap.parse_args()
    if not args.dsn:
        raise SystemExit('Provide --dsn or set DATABASE_URL')
    prev_hash = None
    while True:
        try:
            with psycopg2.connect(args.dsn) as conn:
                row = fetch_profile(conn, args.full_name)
            if not row:
                print(f"[watch] member not found: {args.full_name}")
            else:
                h = stable_hash(row)
                if prev_hash and h != prev_hash:
                    payload = {'event':'profile_change','full_name': args.full_name,'timestamp': time.time(),'row': row}
                    print(f"[change] detected new profile state hash={h[:12]}")
                    if args.redis_url: publish_redis(args.redis_url, payload)
                    if args.webhook: post_webhook(args.webhook, payload)
                prev_hash = h
        except Exception as e:  # noqa: BLE001
            print(f"[error] {e}")
        if args.once:
            break
        time.sleep(args.interval)
    return 0

if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
