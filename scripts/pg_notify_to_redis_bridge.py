"""Postgres -> Redis notification bridge.

Listens to Postgres NOTIFY channel(s) and republishes messages onto Redis Pub/Sub.

Env Vars:
  DATABASE_URL (required)
  PG_LISTEN_CHANNELS (comma list; default engagement_updates)
  REDIS_HOST / REDIS_PORT / REDIS_DB / REDIS_PASSWORD / REDIS_SSL
  REDIS_BRIDGE_CHANNEL (default engagement_updates)
  LOG_LEVEL (default INFO)

Message JSON envelope:
  {
    "type": "engagement_update",
    "channel": <pg_channel>,
    "chunk_id": <int|null>,
    "raw_payload": <string>,
    "ts": <ISO8601 UTC>
  }

Reliability: at-most-once. For stronger guarantees add an outbox table or Redis Streams.
"""
from __future__ import annotations

import os
import json
import time
import logging
import select
from datetime import datetime, timezone
from typing import List

import psycopg2  # type: ignore
import psycopg2.extensions  # type: ignore
import redis

def _bool(v: str|None) -> bool:
    return (v or '').lower() in {'1','true','yes','on'}

def _connect_pg(dsn: str) -> psycopg2.extensions.connection:
    conn = psycopg2.connect(dsn)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    return conn

def _redis_client() -> redis.Redis:
    return redis.Redis(
        host=os.getenv('REDIS_HOST','localhost'),
        port=int(os.getenv('REDIS_PORT','6379')),
        db=int(os.getenv('REDIS_DB','0')),
        password=os.getenv('REDIS_PASSWORD'),
        ssl=_bool(os.getenv('REDIS_SSL')),
        socket_timeout=5,
    )

def main():  # pragma: no cover
    log_level = os.getenv('LOG_LEVEL','INFO').upper()
    logging.basicConfig(level=log_level, format='[%(asctime)s] %(levelname)s %(message)s')
    logger = logging.getLogger('pg_notify_bridge')

    dsn = os.getenv('DATABASE_URL')
    if not dsn:
        raise SystemExit('DATABASE_URL required')

    channels_env = os.getenv('PG_LISTEN_CHANNELS','engagement_updates')
    channels: List[str] = [c.strip() for c in channels_env.split(',') if c.strip()]
    redis_channel = os.getenv('REDIS_BRIDGE_CHANNEL','engagement_updates')

    backoff = 1.0
    r = _redis_client()
    while True:
        try:
            logger.info(f'Connecting to Postgres; listening on {channels}')
            conn = _connect_pg(dsn)
            cur = conn.cursor()
            for ch in channels:
                cur.execute(f'LISTEN {ch};')
            logger.info('Bridge active.')
            backoff = 1.0
            while True:
                if select.select([conn], [], [], 5) == ([], [], []):
                    continue
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    payload = notify.payload or ''
                    chunk_id = None
                    if payload.isdigit():
                        try:
                            chunk_id = int(payload)
                        except ValueError:  # pragma: no cover
                            pass
                    msg = {
                        'type':'engagement_update',
                        'channel': notify.channel,
                        'chunk_id': chunk_id,
                        'raw_payload': payload,
                        'ts': datetime.now(timezone.utc).isoformat(),
                    }
                    try:
                        r.publish(redis_channel, json.dumps(msg))
                        logger.debug(f'Published {msg}')
                    except Exception as e:  # pragma: no cover
                        logger.error(f'Redis publish failed: {e}')
        except Exception as e:
            logger.error(f'Bridge error: {e}')
            logger.info(f'Reconnecting in {backoff:.1f}s')
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)
            continue

if __name__ == '__main__':  # pragma: no cover
    main()
