"""Secrets retrieval utilities.

Primary goal: obtain the scoped Supabase indexer service key WITHOUT
hardcoding it in .env when running in secured environments.

Strategy (priority order):
1. Environment variable SUPABASE_INDEXER_SERVICE_KEY (fast path)
2. Fallback: Postgres Vault extension (vault.get_secret) if available
   Requires: select vault.create_secret('SUPABASE_INDEXER_SERVICE_KEY', '<value>');

If found, we also mirror the value into SUPABASE_KEY (used by llm_client)
unless SUPABASE_KEY already set. Value cached for process lifetime.
"""

from __future__ import annotations

import os
import threading
from typing import Optional, Tuple

SECRET_NAME = "SUPABASE_INDEXER_SERVICE_KEY"
TARGET_RUNTIME_VAR = "SUPABASE_KEY"

_cache_lock = threading.Lock()
_cached_indexer_key: Optional[str] = None
_cached_source: Optional[str] = None  # 'env' | 'vault' | None


def get_supabase_indexer_service_key(refresh: bool = False) -> Optional[str]:
    val, _ = get_supabase_indexer_service_key_with_source(refresh=refresh)
    return val


def get_supabase_indexer_service_key_with_source(
    refresh: bool = False,
) -> Tuple[Optional[str], Optional[str]]:
    global _cached_indexer_key, _cached_source
    if not refresh and _cached_indexer_key is not None:
        return _cached_indexer_key, _cached_source

    # 1. Environment
    env_val = os.getenv(SECRET_NAME)
    if env_val and not env_val.startswith("replace_with_"):
        with _cache_lock:
            _cached_indexer_key = env_val
            _cached_source = "env"
        return env_val, "env"

    # 2. Vault via DATABASE_URL
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        return None, None
    try:  # pragma: no cover
        import psycopg2  # type: ignore
    except Exception:  # pragma: no cover
        return None, None
    try:  # pragma: no cover
        with psycopg2.connect(dsn) as conn:  # type: ignore[arg-type]
            with conn.cursor() as cur:  # type: ignore
                cur.execute("SELECT vault.get_secret(%s);", (SECRET_NAME,))
                row = cur.fetchone()
                if row and row[0]:
                    secret_val = row[0]
                    with _cache_lock:
                        _cached_indexer_key = secret_val
                        _cached_source = "vault"
                    return secret_val, "vault"
    except Exception:
        return None, None
    return None, None


def bootstrap_supabase_key(refresh: bool = False) -> None:
    """Fetch key and ensure SUPABASE_KEY env var populated if possible."""
    current = os.getenv(TARGET_RUNTIME_VAR)
    if current and not refresh:
        return
    key = get_supabase_indexer_service_key(refresh=refresh)
    if key and not current:
        # set for downstream modules (llm_client)
        os.environ[TARGET_RUNTIME_VAR] = key


__all__ = [
    "get_supabase_indexer_service_key",
    "get_supabase_indexer_service_key_with_source",
    "bootstrap_supabase_key",
]
