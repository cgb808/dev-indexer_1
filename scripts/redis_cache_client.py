"""RedisCache Client (Class-Based Wrapper)

Purpose:
  Provides an object-oriented wrapper around the existing functional
  caching utilities in `redis_cache.py`, while preserving key pattern
  compatibility and hashing strategy.

Key Design Points:
  - Maintains prior RAG key pattern: rag:q:<sha1(query)>:<top_k>
  - Adds namespaced generic JSON / MsgPack setters with MD5 hashing
    (internal) without altering legacy functions.
  - Provides build update publishing aligned with existing
    `publish_build_update.py` envelope schema.
  - Graceful degradation if msgpack unavailable (falls back to JSON).

Usage:
  from redis_cache_client import RedisCache, RedisCacheError, create_cache
  cache = create_cache()
  cache.set_json_namespace('example', 'user_profile:42', {'x':1})
  result = cache.get_json_namespace('example', 'user_profile:42')

Backward Compatibility:
  Existing code using functions in `redis_cache.py` continues to work.
  This client internally reuses a newly created redis.Redis connection
  (does not import functional module to avoid circular dependencies).

Environment Variables:
  REDIS_HOST / REDIS_PORT / REDIS_DB / REDIS_PASSWORD / REDIS_SSL
  DEFAULT_TTL_SECONDS (optional default TTL; fallback 300)
  REDIS_BUILD_CHANNEL (default build_updates)

"""
from __future__ import annotations

import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Optional, Dict

try:
    import redis  # type: ignore
except ImportError:  # pragma: no cover
    redis = None  # type: ignore

try:
    import msgpack  # type: ignore
except ImportError:  # pragma: no cover
    msgpack = None  # type: ignore

logger = logging.getLogger(__name__)

class RedisCacheError(Exception):
    """Custom exception for Redis cache operations."""


def _bool(v: Optional[str]) -> bool:
    return (v or '').lower() in {'1', 'true', 'yes', 'on'}


def _sha1(data: str) -> str:
    # Security: hashing for anonymity, not cryptographic security requirement here.
    return hashlib.sha1(data.encode('utf-8')).hexdigest()  # nosec


def _md5(data: str) -> str:
    return hashlib.md5(data.encode('utf-8')).hexdigest()  # nosec


class RedisCache:
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        password: Optional[str] = None,
        ssl: Optional[bool] = None,
        default_ttl: Optional[int] = None,
        socket_timeout: int = 5,
    ) -> None:
        if redis is None:  # pragma: no cover
            raise RedisCacheError("redis library not installed. Run: pip install redis")
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = port or int(os.getenv('REDIS_PORT', '6379'))
        self.db = db or int(os.getenv('REDIS_DB', '0'))
        self.password = password or os.getenv('REDIS_PASSWORD')
        self.ssl = bool(ssl) if ssl is not None else _bool(os.getenv('REDIS_SSL'))
        self.default_ttl = default_ttl or int(os.getenv('DEFAULT_TTL_SECONDS', '300'))
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                ssl=self.ssl,
                socket_timeout=socket_timeout,
            )
            self.client.ping()
        except Exception as e:  # pragma: no cover
            raise RedisCacheError(f"Could not connect to Redis: {e}")

    # ---- Generic Namespaced Helpers (MD5 internal hashing) ----
    def _ns_key(self, namespace: str, key: str) -> str:
        return f"{namespace}:{_md5(key)}"

    def set_json_namespace(self, namespace: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            full_key = self._ns_key(namespace, key)
            data = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
            return bool(self.client.set(full_key, data, ex=ttl or self.default_ttl))
        except Exception as e:  # pragma: no cover
            logger.warning(f"set_json_namespace failed: {e}")
            return False

    def get_json_namespace(self, namespace: str, key: str) -> Any:
        full_key = self._ns_key(namespace, key)
        raw = self.client.get(full_key)
        if not raw:
            return None
        try:
            return json.loads(raw)
        except Exception:  # pragma: no cover
            return None

    def set_msgpack_namespace(self, namespace: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if msgpack is None:
            return self.set_json_namespace(namespace, key, value, ttl)
        try:
            full_key = self._ns_key(namespace, key)
            packed = msgpack.packb(value, use_bin_type=True)
            return bool(self.client.set(full_key, packed, ex=ttl or self.default_ttl))
        except Exception as e:  # pragma: no cover
            logger.warning(f"set_msgpack_namespace failed: {e}")
            return False

    def get_msgpack_namespace(self, namespace: str, key: str) -> Any:
        full_key = self._ns_key(namespace, key)
        raw = self.client.get(full_key)
        if not raw:
            return None
        if msgpack is None:
            return self.get_json_namespace(namespace, key)
        try:
            return msgpack.unpackb(raw, raw=False)
        except Exception:  # pragma: no cover
            return None

    # ---- RAG Query Caching (Preserves Legacy Pattern) ----
    def rag_query_key(self, query: str, top_k: int) -> str:
        return f"rag:q:{_sha1(query)}:{top_k}"

    def cache_rag_query_result(self, query: str, results: Any, top_k: int = 5, ttl: Optional[int] = None) -> bool:
        key = self.rag_query_key(query, top_k)
        payload = {
            'q_hash': _sha1(query),
            'top_k': top_k,
            'results': results,
            'cached_at': datetime.now(timezone.utc).isoformat(),
        }
        return self._set_msgpack_or_json(key, payload, ttl)

    def get_cached_rag_query(self, query: str, top_k: int = 5) -> Any:
        key = self.rag_query_key(query, top_k)
        return self._get_msgpack_or_json(key)

    # ---- Low-level convenience (single key) ----
    def _set_msgpack_or_json(self, key: str, value: Any, ttl: Optional[int]) -> bool:
        if msgpack is None:
            try:
                data = json.dumps(value, separators=(',', ':'))
                return bool(self.client.set(key, data, ex=ttl or self.default_ttl))
            except Exception as e:  # pragma: no cover
                logger.warning(f"_set_json failed: {e}")
                return False
        try:
            packed = msgpack.packb(value, use_bin_type=True)
            return bool(self.client.set(key, packed, ex=ttl or self.default_ttl))
        except Exception as e:  # pragma: no cover
            logger.warning(f"_set_msgpack failed: {e}")
            return False

    def _get_msgpack_or_json(self, key: str) -> Any:
        raw = self.client.get(key)
        if not raw:
            return None
        if msgpack is None:
            try:
                return json.loads(raw)
            except Exception:  # pragma: no cover
                return None
        try:
            return msgpack.unpackb(raw, raw=False)
        except Exception:  # pragma: no cover
            return None

    # ---- Build Update Publication ----
    def publish_build_update(self, content: Dict[str, Any], channel: Optional[str] = None, **extra) -> bool:
        channel = channel or os.getenv('REDIS_BUILD_CHANNEL', 'build_updates')
        envelope = {
            'type': 'build_update',
            'content': content,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
        envelope.update({k: v for k, v in extra.items() if v is not None})
        try:
            if msgpack:
                data = msgpack.packb(envelope, use_bin_type=True)
            else:
                data = json.dumps(envelope, separators=(',', ':'))
            self.client.publish(channel, data)
            return True
        except Exception as e:  # pragma: no cover
            logger.warning(f"publish_build_update failed: {e}")
            return False

    # ---- Utility ----
    def exists(self, key: str) -> bool:
        try:
            return bool(self.client.exists(key))
        except Exception:  # pragma: no cover
            return False

    def delete(self, *keys: str) -> int:
        try:
            return int(self.client.delete(*keys))
        except Exception:  # pragma: no cover
            return 0

    def flush_namespace(self, namespace: str) -> int:
        pattern = f"{namespace}:*"
        deleted = 0
        try:
            for k in self.client.scan_iter(match=pattern, count=500):  # type: ignore
                deleted += self.client.delete(k)
        except Exception as e:  # pragma: no cover
            logger.warning(f"flush_namespace failed: {e}")
        return deleted


def create_cache() -> RedisCache:
    return RedisCache()

__all__ = [
    'RedisCache', 'RedisCacheError', 'create_cache'
]

if __name__ == '__main__':  # pragma: no cover
    logging.basicConfig(level=logging.INFO)
    c = create_cache()
    ok = c.set_json_namespace('example', 'ping', {'msg': 'hello'})
    logger.info(f'set_json_namespace -> {ok}')
    logger.info(f'get_json_namespace -> {c.get_json_namespace("example", "ping")}')
    c.cache_rag_query_result('What is ZenGlow?', [{'id':1,'score':0.9}])
    logger.info(f'get_cached_rag_query -> {c.get_cached_rag_query("What is ZenGlow?")}')
    c.publish_build_update({'status': 'demo', 'progress': 0.25})
