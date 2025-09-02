#!/usr/bin/env python3
"""Tiny FastAPI health & metrics view for embedding worker.

Exposes:
  GET /health -> {status: ok, last_batch_ts, stale_seconds}
  GET /metrics -> text/plain Prometheus style minimal metrics
  GET /info -> static service info

Run (example):
  uvicorn worker_health_api:app --host 0.0.0.0 --port 9108

The embedding worker should be launched with --health-file pointing to same path
this API reads (env WORKER_HEALTH_FILE).
"""
from __future__ import annotations
import os, time, json
from fastapi import FastAPI, Response
from pathlib import Path

HEALTH_FILE = os.getenv('WORKER_HEALTH_FILE', '/tmp/async_embed_worker.health')
SERVICE_NAME = os.getenv('SERVICE_NAME','async-embed-worker')
APP_ENV = os.getenv('APP_ENV','dev')
START_TS = int(time.time())

app = FastAPI(title='Async Embedding Worker Health')

@app.get('/health')
async def health():
    now = int(time.time())
    last = None
    stale = None
    status = 'starting'
    p = Path(HEALTH_FILE)
    if p.exists():
        try:
            last = int(p.read_text().strip())
            stale = now - last
            status = 'ok' if stale < 300 else 'stale'
        except Exception:
            status = 'error'
    return {'status': status, 'last_batch_ts': last, 'stale_seconds': stale, 'service': SERVICE_NAME, 'env': APP_ENV}

@app.get('/info')
async def info():
    return {'service': SERVICE_NAME, 'env': APP_ENV, 'start_ts': START_TS}

@app.get('/metrics')
async def metrics():
    # Minimal placeholder; real metrics aggregated by log scraper.
    now = int(time.time())
    lines = [
        f"service_start_timestamp {START_TS}",
        f"service_uptime_seconds {now-START_TS}",
    ]
    return Response('\n'.join(lines)+'\n', media_type='text/plain')
