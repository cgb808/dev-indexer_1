# DevOps TODO (Indexer / Embeddings)

## 1. Runtime & Infra

- [ ] Provision dedicated embedding service container (GPU optional) with health
      endpoint
- [ ] Add readiness & liveness probes for indexer + embedding API
- [ ] Parameterize EMBED_ENDPOINT via env in docker-compose
- [ ] CPU offload strategy doc (Ryzen 9 local) vs remote CUDA: classify tasks -> CPU (compression, zstd dict training, msgpack pack/unpack, hashing, audit stats) / GPU (embedding, heavy model inference)
- [ ] Edge worker trigger via pub/sub for deferred embeddings (Redis channel -> queue)

## 2. Database

- [ ] Migration script for `doc_embeddings` (vector vs jsonb) + schema version
      table
- [ ] Nightly VACUUM / analyze schedule
- [ ] Partition or batch_tag index strategy for large growth

## 3. Observability

- [ ] Structured JSON logs (uvicorn + ingestion script) with batch_tag
- [ ] Prometheus metrics: ingest_processed_total, ingest_rejected_total,
      fallback_fraction_gauge
- [ ] Grafana dashboard: acceptance rate, by_source distribution, latency p95
 - [ ] (TEMP) Profile change polling watcher (remove after Leonardo model provides event-driven pipeline)

## 4. Quality & Governance

- [ ] Persist ingestion summary JSON per batch (S3 or local `ingest_reports/`)
- [ ] Add automated drift check vs previous batch (source mix deltas >
      threshold)
- [ ] PII scan hook before DB insert

## 5. Backups & Retention

- [ ] Daily pg_dump of doc_embeddings (delta or full)
- [ ] Embedding model artifact version tagging
- [ ] Retention policy: drop batches older than N days unless whitelisted
- [ ] Cron: pack recent plain-text docs -> msgpack+zstd artifact (filename with timestamp + doccount + sha prefix) -> push to remote (Drive / S3) -> register artifact row
- [ ] ZFS snapshot schedule: hourly (24 keep), daily (14 keep), weekly (8 keep) for corpus + artifacts datasets

## 6. Security

- [ ] API key / token auth for ingest endpoint
- [ ] Network ACL restrict embedding + Postgres to private subnet
- [ ] Secret rotation plan (DATABASE_URL)

## 7. Scaling Plan

- [ ] Async batch embed pipeline (queue + workers)
- [ ] Move large batch ingestion to background job (Celery / RQ) with status API
- [ ] Shard or swap to external vector DB (pgvector tuning / dedicated service)
- [ ] Multi-stream ingestion design: length-prefixed msgpack frames -> segment rotation (64MB or 10min) -> seal -> enqueue for embedding -> artifact registration
- [ ] zstd dictionary training job (daily) using latest segments for improved compression ratio
- [ ] Resource cap guard: max concurrent active sessions (env MAX_ACTIVE_SESSIONS) -> new sessions queue or reject with retry

## 8. Testing

- [ ] Add unit tests for chunking, quality filters, adaptive relaxation
- [ ] Integration test: mock embed endpoint returns deterministic vectors
- [ ] Load test: 10k chunks ingestion latency + memory profile
- [ ] Streaming segment stress test: simulate 3 concurrent users appending events at 5 msg/s each -> measure end-to-end embed latency
- [ ] Validation test: verify conversation separation (no cross-user leakage) by inserting overlapping names

## 9. Automation

- [ ] Makefile targets: `curate`, `ingest-dry-run`, `ingest-live`, `report`
- [ ] GitHub Action: On curated dataset commit -> dry run ingest simulation log
      artifact
- [ ] Cron spec (doc):
      * Every 6h: corpus pack + remote sync
      * Nightly: audit script (jeeves_data_audit) -> store JSON diff vs previous
      * Nightly: zstd dict retrain (if > X new segments) -> save dict.bin
      * Hourly: orphan artifact check (registry entries with 0 mapped embeddings)

## 10. Documentation

- [ ] Diagram: data flow (curation -> quality gate -> embedding -> storage ->
      retrieval)
- [ ] Update README with embedding dimensionality & model provenance
- [ ] Add troubleshooting section (common errors: 000 curl, DSN missing)
- [ ] Add section: Multi-tier embeddings (event, summary, doc, profile, artifact) + retrieval union algorithm
- [ ] Add guide: CPU vs GPU workload split (embedding latency vs packing throughput)
- [ ] Explain session isolation & validation strategy (user_id scoping, queries enforce)

---

**Priority Order (Suggested)**: 1 (health) -> 2 (schema) -> 3 (observability) ->
4 (governance) -> 6 (security) -> 5 (backups) -> 7 (scaling) -> 8 (tests) -> 9
(automation) -> 10 (docs)
