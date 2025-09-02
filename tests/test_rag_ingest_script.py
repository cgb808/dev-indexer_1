"""Tests for `scripts/rag_ingest.py` (batch RAG ingestion) using mocks.

We avoid real HTTP and DB connections by monkeypatching:
 - requests.post -> returns fake embeddings sized to chunk count
 - psycopg2.connect -> captures execute_values arguments
"""
from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import List, Any

import importlib


class _FakeCursor:
    def __init__(self, store: dict):
        self.store = store

    def __enter__(self):  # context manager support
        return self

    def __exit__(self, exc_type, exc, tb):  # noqa: D401
        return False

    def execute(self, *args, **kwargs):  # not used in current script
        self.store.setdefault("exec", []).append((args, kwargs))

    def mogrify(self, *args, **kwargs):  # safety stub for psycopg2 interface completeness
        return b""

    def close(self):
        pass


class _FakeConn:
    def __init__(self, store: dict):
        self.store = store
        self.closed = False

    def cursor(self):  # context manager via _FakeCursor
        return _FakeCursor(self.store)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def commit(self):
        pass

    def close(self):
        self.closed = True


def _mock_requests_post(chunks_holder: dict):  # returns callable matching requests.post
    class _Resp:
        def __init__(self, embeddings: List[List[float]]):
            self._embeddings = embeddings

        def raise_for_status(self):
            return None

        def json(self):
            return {"embeddings": self._embeddings}

    def _post(url: str, json: Any, timeout: int):  # noqa: D401
        texts = json["texts"]
        chunks_holder["last_texts"] = texts
        # Return simple 3-dim vector for each chunk
        return _Resp([[0.1, 0.2, 0.3] for _ in texts])

    return _post


def test_rag_ingest_process_inserts(monkeypatch, tmp_path):
    # Prepare sample text > CHUNK_SIZE to force multiple chunks (CHUNK_SIZE=800, overlap=80)
    sample_text = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 30)  # ~1700 chars
    f = tmp_path / "sample.txt"
    f.write_text(sample_text)

    # Monkeypatch env to trigger DSN branch
    os.environ["DATABASE_URL"] = "postgresql://user:pass@host:5432/db"  # arbitrary

    calls_store: dict = {}
    chunks_holder: dict = {}

    # Patch psycopg2.connect
    import psycopg2  # type: ignore

    def _fake_connect(dsn):  # noqa: D401
        return _FakeConn(calls_store)

    monkeypatch.setattr(psycopg2, "connect", _fake_connect)

    # Patch requests.post
    import requests  # type: ignore
    monkeypatch.setattr(requests, "post", _mock_requests_post(chunks_holder))

    # Import script module fresh (so constants defined) and call process
    ingest_mod = importlib.import_module("scripts.rag_ingest")
    # Force reload to ensure clean state if prior tests imported
    ingest_mod = importlib.reload(ingest_mod)

    inserted = ingest_mod.process([str(f)], source="test_src", batch_tag="test_batch")

    # If EMBED_DUMMY fast path active, requests.post not called; fallback assertion.
    if os.getenv("EMBED_DUMMY") == "1":
        assert inserted > 1
    else:
        # Validate chunking produced multiple entries and we inserted same count
        assert inserted == len(chunks_holder.get("last_texts", []))
        assert inserted > 1  # ensures multi-chunk scenario covered


def test_rag_ingest_empty_file(monkeypatch, tmp_path):
    empty = tmp_path / "empty.txt"
    empty.write_text("")
    os.environ["DATABASE_URL"] = "postgresql://user:pass@host:5432/db"

    import psycopg2  # type: ignore

    monkeypatch.setattr(psycopg2, "connect", lambda dsn: _FakeConn({}))

    import requests  # type: ignore
    # If no chunks, embed() never called; guard by raising if it does
    def _fail_post(*args, **kwargs):  # noqa: D401
        raise AssertionError("embed called for empty file")

    monkeypatch.setattr(requests, "post", _fail_post)

    ingest_mod = importlib.import_module("scripts.rag_ingest")
    ingest_mod = importlib.reload(ingest_mod)
    inserted = ingest_mod.process([str(empty)], source="empty", batch_tag="none")
    assert inserted == 0
