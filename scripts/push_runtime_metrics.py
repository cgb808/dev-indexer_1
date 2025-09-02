"""push_runtime_metrics.py
Collect local Docker container stats + Supabase queue/doc counts (optional) and
push to the runtime_metrics table for UI consumption.

Requires:
  DATABASE_URL (or SUPABASE_DB_URL) for direct INSERT (service role or metrics role)
Optional:
  DOCKER_SOCK (/var/run/docker.sock) accessible for container stats
  METRICS_SOURCE_TAG (string prefix)
  INCLUDE_QUEUE=1 to also summarize queue directly (faster than edge call)

This can run via cron/systemd timer every N seconds.
"""
from __future__ import annotations
import os, time, json, socket
from datetime import datetime, timezone
from typing import List, Dict

try:
    import psycopg2  # type: ignore
    import psycopg2.extras  # type: ignore
except ImportError as e:
    raise SystemExit("psycopg2 required") from e

DSN = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
if not DSN:
    raise SystemExit('DATABASE_URL or SUPABASE_DB_URL required')

DOCKER_SOCK = os.getenv('DOCKER_SOCK', '/var/run/docker.sock')
SOURCE_TAG = os.getenv('METRICS_SOURCE_TAG', 'host')
QUEUE_TABLE = os.getenv('QUEUE_TABLE', 'code_chunk_ingest_queue')
INCLUDE_QUEUE = os.getenv('INCLUDE_QUEUE', '0') == '1'

# Lightweight docker stats (no docker SDK) using Engine API (GET /containers/json, /containers/{id}/stats?stream=false)

def _docker_get(path: str) -> dict | list | None:
    if not os.path.exists(DOCKER_SOCK):
        return None
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.settimeout(2)
        s.connect(DOCKER_SOCK)
        req = f"GET {path} HTTP/1.1\r\nHost: localhost\r\nAccept: application/json\r\nConnection: close\r\n\r\n"
        s.sendall(req.encode())
        data = b''
        while True:
            chunk = s.recv(8192)
            if not chunk:
                break
            data += chunk
    finally:
        s.close()
    # Split headers/body
    try:
        header, body = data.split(b"\r\n\r\n",1)
        body = body.strip()
        return json.loads(body) if body else None
    except Exception:
        return None

def collect_docker_metrics() -> List[Dict]:
    base = _docker_get('/containers/json')
    metrics: List[Dict] = []
    if not isinstance(base, list):
        return metrics
    for c in base[:15]:  # cap to first 15 containers
        cid = c.get('Id')
        name = (c.get('Names') or [''])[0].lstrip('/')
        stat = _docker_get(f'/containers/{cid}/stats?stream=false')
        if not isinstance(stat, dict):
            continue
        cpu_pct = None
        try:
            cpu_delta = stat['cpu_stats']['cpu_usage']['total_usage'] - stat['precpu_stats']['cpu_usage']['total_usage']
            sys_delta = stat['cpu_stats']['system_cpu_usage'] - stat['precpu_stats']['system_cpu_usage']
            if sys_delta > 0 and cpu_delta >= 0:
                cpu_pct = (cpu_delta / sys_delta) * len(stat['cpu_stats'].get('cpu_usage', {}).get('percpu_usage', []) or [1]) * 100.0
        except Exception:
            pass
        mem_usage = stat.get('memory_stats', {}).get('usage')
        metrics.append({'source': f'docker:{SOURCE_TAG}', 'metric':'container_cpu_percent','value':cpu_pct,'labels':{'container':name}})
        if mem_usage is not None:
            metrics.append({'source': f'docker:{SOURCE_TAG}', 'metric':'container_mem_bytes','value':float(mem_usage),'labels':{'container':name}})
    return metrics

def collect_queue_metrics(cur) -> List[Dict]:
    if not INCLUDE_QUEUE:
        return []
    cur.execute(f"SELECT status, count(*) FROM {QUEUE_TABLE} GROUP BY status")
    rows = cur.fetchall()
    out = []
    for status, count in rows:
        out.append({'source':'supabase:queue','metric':'queue_count','value':float(count),'labels':{'status':status}})
    return out

def push_metrics(rows: List[Dict]):
    if not rows:
        return
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(cur,
                "INSERT INTO runtime_metrics (source, metric, value, labels) VALUES %s",
                [(r['source'], r['metric'], r['value'], json.dumps(r.get('labels') or {})) for r in rows]
            )
            conn.commit()

if __name__ == '__main__':  # pragma: no cover
    rows: List[Dict] = []
    rows.extend(collect_docker_metrics())
    try:
        if INCLUDE_QUEUE:
            with psycopg2.connect(DSN) as conn:
                with conn.cursor() as cur:
                    rows.extend(collect_queue_metrics(cur))
    except Exception as e:
        pass
    push_metrics(rows)
    print(f"pushed {len(rows)} metrics entries")
