import os
from fastapi.testclient import TestClient

# Env for stub
os.environ['SUPABASE_FORCE_STUB'] = '1'
os.environ['SUPABASE_INDEXER_SERVICE_KEY'] = 'stub_key'
os.environ['SUPABASE_INDEXER_URL'] = 'https://stub.supabase.co'
os.environ['RAG_RETRIEVAL_MODE'] = 'supabase'
os.environ['DATABASE_URL'] = 'postgresql://stub:stub@localhost:5432/stub'

# Provide lightweight embedding stub before importing app
def _stub_embed_texts(texts):
    # Return fixed-length numeric vectors without torch
    return [[float(len(t)) % 1.0 for _ in range(8)] for t in texts]

import app.main as main_mod  # type: ignore
main_mod._embed_texts = _stub_embed_texts  # type: ignore

def _stub_pg_connect():  # avoid actual DB
    class _Conn:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def cursor(self): return self
        def execute(self, *a, **k): self._rows = []
        def fetchall(self): return getattr(self, '_rows', [])
    return _Conn()

main_mod._pg_connect = _stub_pg_connect  # type: ignore

from app.main import app  # type: ignore  # noqa: E402
client = TestClient(app)

def test_rag_query_supabase_stub():
    resp = client.post('/rag/query', json={'query': 'test question', 'top_k': 1})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert 'hits' in data
    # In stub mode we expect either the stubbed RPC result or empty fallback if alert fired
    if data['hits']:
        assert data['hits'][0]['text'] in ('stub_chunk',)
