import os, sys
sys.path.append(os.path.abspath('.'))
from fastapi.testclient import TestClient
from app.main import app  # noqa: E402

client = TestClient(app)

def test_supabase_key_status_env(monkeypatch):
    monkeypatch.setenv('SUPABASE_INDEXER_SERVICE_KEY', 'sb_secret_demo_1234567890')
    monkeypatch.setenv('SUPABASE_URL', 'https://example.supabase.co')
    # Force internal stub
    monkeypatch.setenv('SUPABASE_FORCE_STUB', '1')
    r = client.get('/supabase/key-status')
    assert r.status_code == 200
    body = r.json()
    assert body['present'] is True
    assert body['source'] == 'env'
    assert body['client_initialized'] is True
    assert body['masked'].startswith('sb_sec')
