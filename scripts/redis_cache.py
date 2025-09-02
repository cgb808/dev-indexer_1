"""Redis Cache Utilities for RAG & Build Pipelines.

Features:
  - Centralized Redis client from env vars
  - Namespaced key patterns: <namespace>:<type>:<hash>
  - JSON & MessagePack serialization helpers
  - RAG query result cache (short TTL, anonymity via hash(query))
  - Generic get/set with TTL override

Env Vars:
  REDIS_HOST (default: localhost)
  REDIS_PORT (default: 6379)
  REDIS_DB   (default: 0)
  REDIS_PASSWORD (optional)
  REDIS_SSL (if '1' or 'true')
  DEFAULT_TTL_SECONDS (default: 300)

Key Patterns:
  rag:q:<sha1(query)>:<top_k>
  build:artifact:<artifact_id>
  generic:<custom>

"""
from __future__ import annotations

import os
import json
import time
import hashlib
import logging
from typing import Any, Optional, Sequence

try:
    import msgpack  # type: ignore
except ImportError:  # graceful degradation
    msgpack = None  # type: ignore

import redis

logger = logging.getLogger(__name__)

def _bool(v: Optional[str]) -> bool:
    return (v or '').lower() in {'1', 'true', 'yes', 'on'}

def _redis_client() -> redis.Redis:
    ssl = _bool(os.getenv('REDIS_SSL'))
    return redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        db=int(os.getenv('REDIS_DB', '0')),
        password=os.getenv('REDIS_PASSWORD'),
        ssl=ssl,
        socket_timeout=5,
    )

R = _redis_client()
DEFAULT_TTL = int(os.getenv('DEFAULT_TTL_SECONDS', '300'))

def _sha1(text: str) -> str:
    return hashlib.sha1(text.encode('utf-8')).hexdigest()  # nosec - cache hash

def cache_key_rag_query(query: str, top_k: int) -> str:
    return f"rag:q:{_sha1(query)}:{top_k}"

def cache_set_json(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    try:
        data = json.dumps(value, separators=(',', ':'))
        return bool(R.set(key, data, ex=ttl or DEFAULT_TTL))
    except Exception as e:  # pragma: no cover - defensive
        logger.warning(f"cache_set_json failed: {e}")
        return False

def cache_get_json(key: str) -> Any:
    raw = R.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:  # pragma: no cover
        return None

def cache_set_msgpack(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    if msgpack is None:
        return cache_set_json(key, value, ttl)
    try:
        return bool(R.set(key, msgpack.packb(value, use_bin_type=True), ex=ttl or DEFAULT_TTL))
    except Exception as e:  # pragma: no cover
        logger.warning(f"cache_set_msgpack failed: {e}")
        return False

def cache_get_msgpack(key: str) -> Any:
    raw = R.get(key)
    if not raw:
        return None
    if msgpack is None:
        return cache_get_json(key)
    try:
        return msgpack.unpackb(raw, raw=False)
    except Exception:  # pragma: no cover
        return None

def cache_rag_query_result(query: str, top_k: int, results: Sequence[dict], ttl: Optional[int] = None) -> bool:
    key = cache_key_rag_query(query, top_k)
    payload = {
        'q_hash': _sha1(query),
        'top_k': top_k,
        'results': results,
        'cached_at': int(time.time())
    }
    return cache_set_msgpack(key, payload, ttl)

def get_cached_rag_query(query: str, top_k: int) -> Optional[dict]:
    key = cache_key_rag_query(query, top_k)
    return cache_get_msgpack(key)

__all__ = [
    'cache_set_json','cache_get_json','cache_set_msgpack','cache_get_msgpack',
    'cache_rag_query_result','get_cached_rag_query','cache_key_rag_query'
]
