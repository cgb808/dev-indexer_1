"""Publish build / ingestion update messages to Redis.

Envelope Schema:
  {
    "type": "build_update",
    "content": <string|dict>,
    "timestamp": <ISO8601>,
    ...extra
  }

Env Vars:
  REDIS_HOST / REDIS_PORT / REDIS_DB / REDIS_PASSWORD / REDIS_SSL
  REDIS_BUILD_CHANNEL (default: build_updates)

Usage:
  python publish_build_update.py --content "Rebuilt code embeddings" --artifact-id xyz
"""
from __future__ import annotations

import os
import json
import argparse
from datetime import datetime, timezone
import logging

try:
    import msgpack  # type: ignore
except ImportError:  # pragma: no cover
    msgpack = None  # type: ignore

import redis

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s')
logger = logging.getLogger('publish_build_update')

def _bool(v: str|None) -> bool:
    return (v or '').lower() in {'1','true','yes','on'}

def redis_client() -> redis.Redis:
    return redis.Redis(
        host=os.getenv('REDIS_HOST','localhost'),
        port=int(os.getenv('REDIS_PORT','6379')),
        db=int(os.getenv('REDIS_DB','0')),
        password=os.getenv('REDIS_PASSWORD'),
        ssl=_bool(os.getenv('REDIS_SSL')),
        socket_timeout=5,
    )

def publish(content: str|dict, channel: str, **extra):
    payload = {
        'type':'build_update',
        'content': content,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
    payload.update({k:v for k,v in extra.items() if v is not None})
    r = redis_client()
    if msgpack:
        data = msgpack.packb(payload, use_bin_type=True)
    else:
        data = json.dumps(payload, separators=(',',':'))
    r.publish(channel, data)
    logger.info(f'Published build_update to {channel}: {payload}')

def main():  # pragma: no cover
    ap = argparse.ArgumentParser()
    ap.add_argument('--content', required=True, help='Message or summary of build event')
    ap.add_argument('--artifact-id')
    ap.add_argument('--doc-count', type=int)
    ap.add_argument('--duration-ms', type=int)
    ap.add_argument('--channel', default=os.getenv('REDIS_BUILD_CHANNEL','build_updates'))
    args = ap.parse_args()
    publish(args.content, args.channel, artifact_id=args.artifact_id, doc_count=args.doc_count, duration_ms=args.duration_ms)

if __name__ == '__main__':  # pragma: no cover
    main()
