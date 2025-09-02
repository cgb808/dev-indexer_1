"""Queue Embedding Worker

Purpose:
  Poll the staging ingestion queue (code_chunk_ingest_queue) created by the
  Supabase Edge function `curate-code`, generate embeddings for pending rows,
  and upsert them into the retrieval table (doc_embeddings). Marks rows done or
  error and is safe to run continuously.

Design Goals:
  * Light: single-process loop; no external scheduler required.
  * Safe: uses SELECT ... FOR UPDATE SKIP LOCKED to avoid double work when scaled.
  * Idempotent: skips rows already processed (status != pending) or already
    embedded (matching checksum/batch_tag).
  * Extensible: easy hooks for future enrichment (static analysis, token count).

Environment Variables:
  DATABASE_URL / SUPABASE_DB_URL : Postgres DSN (required)
  QUEUE_TABLE                   : Default code_chunk_ingest_queue
  EMBED_ENDPOINT                : HTTP endpoint for embedding (default http://127.0.0.1:8000/model/embed)
  WORKER_BATCH_SIZE             : Max rows per embedding call (default 16)
  WORKER_POLL_INTERVAL          : Sleep seconds when no work (default 5)
  WORKER_MAX_CONTENT_CHARS      : Guard; skip overly large content (default 100_000)
  WORKER_LOG_EVERY_N            : Emit progress every N cycles (default 20)
  MODEL_TIMEOUT_SEC             : Embedding request timeout (default 120)

Schema Expectations:
  Queue table columns (subset): id, file_path, content, checksum, status,
    error_message, repository, commit_sha, git_ref, confidence_score, created_at.
  Retrieval table: doc_embeddings(source TEXT, chunk TEXT, embedding VECTOR, batch_tag TEXT).

Processing Steps:
  1. Begin transaction
  2. Lock up to WORKER_BATCH_SIZE pending rows FOR UPDATE SKIP LOCKED
  3. Mark them status='processing'
  4. Commit (release early so other workers can proceed) OR keep tx open while embedding
  5. Embed contents in batch (order preserved)
  6. Insert into doc_embeddings with batch_tag = checksum (ON CONFLICT DO NOTHING)
  7. Update queue rows -> status='done' (store latency) OR status='error'

Exit: Ctrl+C (SIGINT) triggers graceful shutdown after current batch.

Future Extensions (not implemented here):
  * Token counting + cost attribution
  * Static language detection / complexity metrics
  * NOTIFY channel when batch completes
  * Retry policy for transient network errors vs permanent failures
  * Structured metrics export (Prometheus / statsd)
"""
from __future__ import annotations

import os
import time
import json
import signal
import logging
import math
from typing import List, Sequence, Optional

import requests  # type: ignore

try:
    import psycopg2  # type: ignore
    import psycopg2.extras  # type: ignore
except ImportError as e:  # pragma: no cover
    raise SystemExit("psycopg2 is required for queue_embedding_worker.py") from e

# Configuration ----------------------------------------------------------------
DSN = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
if not DSN:
    raise SystemExit("DATABASE_URL or SUPABASE_DB_URL must be set")

QUEUE_TABLE = os.getenv("QUEUE_TABLE", "code_chunk_ingest_queue")
EMBED_ENDPOINT = os.getenv("EMBED_ENDPOINT", "http://127.0.0.1:8000/model/embed")
WORKER_BATCH_SIZE = int(os.getenv("WORKER_BATCH_SIZE", "16"))
POLL_INTERVAL = float(os.getenv("WORKER_POLL_INTERVAL", "5"))
MAX_CONTENT_CHARS = int(os.getenv("WORKER_MAX_CONTENT_CHARS", "100000"))
LOG_EVERY_N = int(os.getenv("WORKER_LOG_EVERY_N", "20"))
MODEL_TIMEOUT_SEC = int(os.getenv("MODEL_TIMEOUT_SEC", "120"))
USE_LISTEN = os.getenv("WORKER_LISTEN", "0") == "1"
LISTEN_CHANNEL = os.getenv("WORKER_LISTEN_CHANNEL", "code_chunk_ingest")
EMIT_METRICS = os.getenv("METRICS_EMIT", "1") == "1"  # on by default
ESTIMATE_TOKENS = os.getenv("WORKER_ESTIMATE_TOKENS", "1") == "1"

logging.basicConfig(level=logging.INFO, format="[worker] %(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("queue_embedding_worker")

_shutdown = False

def _handle_sigint(signum, frame):  # pragma: no cover
    global _shutdown
    logger.info("Received signal %s - will shut down after current cycle", signum)
    _shutdown = True

signal.signal(signal.SIGINT, _handle_sigint)
signal.signal(signal.SIGTERM, _handle_sigint)

# Embedding --------------------------------------------------------------------

def embed_texts(texts: Sequence[str]) -> List[List[float]]:
    if not texts:
        return []
    r = requests.post(EMBED_ENDPOINT, json={"texts": list(texts)}, timeout=MODEL_TIMEOUT_SEC)
    if r.status_code != 200:
        raise RuntimeError(f"embed endpoint {EMBED_ENDPOINT} status={r.status_code} body={r.text[:200]}")
    data = r.json()
    if "embeddings" not in data:
        raise RuntimeError("embed endpoint missing 'embeddings' field")
    embs = data["embeddings"]
    if len(embs) != len(texts):
        raise RuntimeError("embedding count mismatch")
    return embs

# Database helpers --------------------------------------------------------------

LOCK_SQL = f"""
SELECT id, file_path, content, checksum, repository, commit_sha, git_ref
FROM {QUEUE_TABLE}
WHERE status='pending'
ORDER BY created_at
LIMIT %s
FOR UPDATE SKIP LOCKED
"""

MARK_PROCESSING_SQL = f"UPDATE {QUEUE_TABLE} SET status='processing', updated_at=NOW() WHERE id = ANY(%s)"
MARK_DONE_SQL = f"UPDATE {QUEUE_TABLE} SET status='done', updated_at=NOW() WHERE id = ANY(%s)"
MARK_ERROR_SQL = f"UPDATE {QUEUE_TABLE} SET status='error', error_message=%s, updated_at=NOW() WHERE id = ANY(%s)"

# Optional unique index for idempotency: (source, batch_tag)
ENSURE_UNIQUE_SQL = "CREATE UNIQUE INDEX IF NOT EXISTS doc_embeddings_source_batch_tag_idx ON doc_embeddings (source, batch_tag)"
INSERT_EMB_SQL = "INSERT INTO doc_embeddings (source, chunk, embedding, batch_tag) VALUES %s ON CONFLICT DO NOTHING"

CYCLE = 0


def _listen_connection() -> Optional["psycopg2.extensions.connection"]:
    """Establish a LISTEN connection if enabled; return None if disabled or fails."""
    if not USE_LISTEN:
        return None
    try:  # pragma: no cover - network dependent
        conn = psycopg2.connect(DSN)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        cur.execute(f"LISTEN {LISTEN_CHANNEL};")
        logger.info("LISTEN mode active on channel '%s'", LISTEN_CHANNEL)
        return conn
    except Exception as e:  # pragma: no cover
        logger.warning("Failed to enter LISTEN mode (%s); falling back to polling", e)
        return None


def main():  # pragma: no cover - runtime script
    global CYCLE
    logger.info("Queue embedding worker starting (batch_size=%s poll=%.1fs)", WORKER_BATCH_SIZE, POLL_INTERVAL)
    with psycopg2.connect(DSN) as conn:
        conn.autocommit = False
        with conn.cursor() as cur:
            # Ensure unique index for idempotent inserts
            try:
                cur.execute(ENSURE_UNIQUE_SQL)
                conn.commit()
            except Exception as e:  # pragma: no cover
                conn.rollback()
                logger.warning("Could not ensure unique index: %s", e)

    listen_conn = _listen_connection()
    while not _shutdown:
        CYCLE += 1
        start_cycle = time.time()
        batch_rows = []
        try:
            with psycopg2.connect(DSN) as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(LOCK_SQL, (WORKER_BATCH_SIZE,))
                    rows = cur.fetchall()
                    if not rows:
                        conn.commit()
                        if listen_conn is not None:
                            # Block waiting for notification (with timeout) to reduce idle CPU
                            try:
                                # Wait up to poll interval for notify
                                listen_conn.poll()
                                notified = False
                                start_wait = time.time()
                                while time.time() - start_wait < POLL_INTERVAL:
                                    if listen_conn.notifies:
                                        listen_conn.notifies.clear()
                                        notified = True
                                        break
                                    time.sleep(0.25)
                                    listen_conn.poll()
                                if not notified and CYCLE % LOG_EVERY_N == 0:
                                    logger.info("Idle (LISTEN) cycle=%s", CYCLE)
                            except Exception as e:  # pragma: no cover
                                logger.warning("LISTEN wait failed (%s); fallback to sleep", e)
                                time.sleep(POLL_INTERVAL)
                        else:
                            if CYCLE % LOG_EVERY_N == 0:
                                logger.info("No work (cycle=%s)", CYCLE)
                            time.sleep(POLL_INTERVAL)
                        continue
                    ids = [r["id"] for r in rows]
                    cur.execute(MARK_PROCESSING_SQL, (ids,))
                    conn.commit()  # release locks early
                    batch_rows = rows
        except Exception as e:
            logger.error("Error locking rows: %s", e)
            time.sleep(min(POLL_INTERVAL * 2, 30))
            continue

        texts = []
        sources = []
        checksums = []
        id_map = []
        for r in batch_rows:
            content = r["content"] or ""
            if len(content) > MAX_CONTENT_CHARS:
                logger.warning("Row id=%s content too large (%s chars) skipping", r["id"], len(content))
                continue
            texts.append(content)
            repo = r.get("repository")
            source_label = f"{repo}:{r['file_path']}" if repo else r["file_path"]
            sources.append(source_label)
            checksums.append(r["checksum"])  # use as batch_tag
            id_map.append(r["id"])

        if not texts:
            # Mark skipped rows done to avoid retry loops
            try:
                with psycopg2.connect(DSN) as conn:
                    with conn.cursor() as cur:
                        if id_map:
                            cur.execute(MARK_DONE_SQL, (id_map,))
                            conn.commit()
            except Exception:
                pass
            continue

        embed_start = time.time()
        try:
            embeddings = embed_texts(texts)
        except Exception as e:
            logger.error("Embedding failure on batch size %s: %s", len(texts), e)
            # Mark rows error
            try:
                with psycopg2.connect(DSN) as conn:
                    with conn.cursor() as cur:
                        cur.execute(MARK_ERROR_SQL, (str(e)[:500], id_map))
                        conn.commit()
            except Exception as e2:  # pragma: no cover
                logger.error("Secondary failure marking errors: %s", e2)
            time.sleep(min(POLL_INTERVAL * 2, 60))
            continue

        # Insert embeddings
        records = [(s, t, json.dumps(v), c) for s, t, v, c in zip(sources, texts, embeddings, checksums)]
        total_tokens = 0
        if ESTIMATE_TOKENS:
            # Fast heuristic: assume ~4 chars per token average for code+text mix
            total_chars = sum(len(t) for t in texts)
            total_tokens = max(1, math.ceil(total_chars / 4))
        try:
            with psycopg2.connect(DSN) as conn:
                with conn.cursor() as cur:
                    psycopg2.extras.execute_values(cur, INSERT_EMB_SQL, records)
                    cur.execute(MARK_DONE_SQL, (id_map,))
                    if EMIT_METRICS:
                        # Emit latency metric (ms per item + total) into runtime_metrics if table exists
                        try:
                            total_ms = (time.time() - embed_start) * 1000.0
                            per_item = total_ms / max(1,len(records))
                            # Insert a no-op placeholder removed (legacy)
                        except Exception:
                            pass
                        try:
                            # Bulk insert via execute_values
                            metric_rows = [
                                ("worker:embedding","embed_batch_latency_ms", total_ms, json.dumps({"batch_size": len(records), "tokens": total_tokens })),
                                ("worker:embedding","embed_item_latency_ms", per_item, json.dumps({"batch_size": len(records) })),
                            ]
                            if ESTIMATE_TOKENS and total_tokens:
                                metric_rows.append(("worker:embedding","embed_tokens_per_sec", (total_tokens / (total_ms/1000.0)), json.dumps({"batch_size": len(records)})))
                                metric_rows.append(("worker:embedding","embed_tokens", float(total_tokens), json.dumps({"batch_size": len(records)})))
                            psycopg2.extras.execute_values(cur,
                                "INSERT INTO runtime_metrics (source, metric, value, labels) VALUES %s",
                                metric_rows
                            )
                        except Exception:
                            pass
                    conn.commit()
        except Exception as e:
            logger.error("DB upsert failure: %s", e)
            # Partial error handling: mark error for rows not inserted? For simplicity mark all error.
            try:
                with psycopg2.connect(DSN) as conn:
                    with conn.cursor() as cur:
                        cur.execute(MARK_ERROR_SQL, (str(e)[:500], id_map))
                        conn.commit()
            except Exception:
                pass
            time.sleep(min(POLL_INTERVAL * 2, 60))
            continue

        dur = time.time() - start_cycle
        logger.info("Processed %s rows in %.2fs (cycle=%s)", len(records), dur, CYCLE)

    logger.info("Worker exiting after %s cycles", CYCLE)


if __name__ == "__main__":  # pragma: no cover
    main()
