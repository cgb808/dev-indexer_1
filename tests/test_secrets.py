"""Tests for secrets retrieval (environment & vault fallback)."""

import sys

from app.core.secrets import SECRET_NAME  # type: ignore[attr-defined]
from app.core.secrets import (get_supabase_indexer_service_key,
                              get_supabase_indexer_service_key_with_source)


class DummyCursor:
    def __init__(self, value):
        self._value = value

    def execute(self, *_args, **_kwargs):  # pragma: no cover - no logic
        pass

    def fetchone(self):  # pragma: no cover - deterministic
        return (self._value,)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):  # pragma: no cover
        return False


class DummyConn:
    def __init__(self, value):
        self._value = value

    def cursor(self):  # pragma: no cover
        return DummyCursor(self._value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):  # pragma: no cover
        return False


class DummyPsycopg:
    def __init__(self, value):
        self._value = value

    def connect(self, dsn):  # pragma: no cover - trivial
        return DummyConn(self._value)


def test_secret_env_fast_path(monkeypatch):
    monkeypatch.setenv(SECRET_NAME, "sb_secret_env_value")
    val = get_supabase_indexer_service_key(refresh=True)
    assert val == "sb_secret_env_value"
    v2, source = get_supabase_indexer_service_key_with_source()
    assert v2 == "sb_secret_env_value" and source == "env"


def test_secret_vault_fallback(monkeypatch):
    monkeypatch.delenv(SECRET_NAME, raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@host/db")
    dummy = DummyPsycopg("sb_secret_from_vault")
    sys.modules["psycopg2"] = dummy  # type: ignore
    val = get_supabase_indexer_service_key(refresh=True)
    assert val == "sb_secret_from_vault"
    v2, source = get_supabase_indexer_service_key_with_source(refresh=False)
    assert v2 == "sb_secret_from_vault" and source == "vault"


def test_secret_absent(monkeypatch):
    monkeypatch.delenv(SECRET_NAME, raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    # Remove dummy psycopg if previously set
    if "psycopg2" in sys.modules:
        del sys.modules["psycopg2"]
    val = get_supabase_indexer_service_key(refresh=True)
    assert val is None
