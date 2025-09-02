<!-- Relocated from repository root on 2025-08-30 -->
<!-- Relocated from repository root on 2025-08-30; canonical now under docs/devops/ -->
[Back to Docs Index](../DOCS_INDEX.md)

ZenGlow DevOps & Operational Practices (Living Document)
Last Updated: 2025-08-27

Tracks non-code operational concerns: CI, deployment, observability, security, reliability.

Companion backlog now tracked via issue tracker; historical placeholder file removed during root hygiene pass.

## 1. Build & CI
Planned:
- [ ] GitHub Actions workflow (.github/workflows/ci.yml): checkout -> cache deps -> make check -> upload coverage.
- [ ] Cache pip deps keyed by hash(requirements*.txt).
- [ ] Coverage badge publication.

Local:
- Use `make venv && make dev-setup` to prepare environment.
- `make check` runs lint + tests (pytest) with quiet output.

## 2. Environments
| Env | Purpose | Notes |
|-----|---------|-------|
| local | Developer machine | GPU optional; Postgres/Redis via docker-compose |
| staging | Pre-prod validation | Enable tracing & extended metrics |
| prod | Production | API auth, rate limiting, structured logging |

Env Config Enhancements Implemented:
- Backcompat shim: FUSION_* -> RAG_FUSION_*, RAG_TOP_K -> RAG_TOP_K_DEFAULT.
- Required env validation (fail-fast): DATABASE_URL, REDIS_HOST, REDIS_PORT.
- Sanitized environment endpoint: `/config/env` (excludes secret markers).

## 3. Observability
Implemented:
- `/metrics` (Prometheus) basic query counters + latency histogram.
- `/metrics/json` with system metrics (CPU, memory, GPU), query stats, model registry.
- System metrics via psutil / pynvml fallback.
- `/metrics/basic` lightweight in-process counters + stage latency snapshots (embed, retrieval, feature, ltr, fusion, pipeline) captured via `app.core.metrics` (Prometheus export for these stages still pending).

Planned / Open:
- [ ] Prometheus export of per-stage timings (currently only in-process snapshot via `/metrics/basic`).
- [ ] Tracing (OpenTelemetry) across pipeline spans.
- [ ] Structured JSON logging w/ request & correlation IDs.
- [ ] Persistent performance store (TimescaleDB hypertable `query_performance`).
- [ ] Alert thresholds: p95 latency, cache hit rate, error rate.

## 4. Model Ops
Implemented:
- Static model registry seeded; endpoint `/health/models`.
- Fusion weights management endpoints `/rag/fusion/weights` (GET/PUT) with normalized + versioned override support.

Planned:
- [ ] Dynamic registry refresh & loading state.
- [ ] Per-model throughput & latency rolling stats.
- [ ] Hot weight adjustment persistence layer (current override is in-process only; lost on restart).

## 5. Security & Compliance
Current:
- Secret bootstrap from Vault (Supabase Indexer key) populates SUPABASE_KEY.

Planned:
- [ ] API key middleware toggle (`ENABLE_API_KEYS`).
- [ ] Rate limiting (Redis token bucket) for `/rag/*`.
- [ ] PII scrubbing in logs.
- [ ] Basic auth / mTLS (stretch).

## 6. Data & Retrieval
Current:
- pgvector similarity search (`doc_embeddings`).
- Feature-level cache & full response cache in Redis.

Planned:
- [ ] Retrieval mode abstraction (env `RAG_RETRIEVAL_MODE`: pgvector | supabase_rpc).
- [ ] ANN strategy toggle (future HNSW / IVF) config table.
- [ ] TimescaleDB integration for longitudinal stats.

## 7. Deployment
- Multi-stage Docker build (planned refinement: slim runtime + optional GPU base).
- Blue/green / canary strategy for scoring changes via weight env or Redis.
- Rollback path: deploy previous image + revert weight config.

## 8. Operational Backlog (Condensed)
- [ ] CI workflow & coverage
- [ ] Prometheus stage timing histogram export (in-process observation done)
- [ ] Retrieval mode branching
- [ ] Structured logging & tracing
- [ ] Rate limiting & API keys
- [ ] Persistent metrics (TimescaleDB)
- [ ] Model throughput sampler
- [ ] Extended query stats (stage latencies)
- [ ] Config validation endpoint enrichment
- [ ] Automate Memory MCP snapshot after successful index diff commit
- [ ] Persist project index + model registry snapshot into Memory MCP after each significant refactor
- [ ] Fine-tuning pipeline automation (base model + specialization training)
- [ ] Model artifact management and versioning
- [ ] Interruption handling model deployment
- [ ] Training data quality validation automation

## 9. Runbook: High Latency `/rag/query2`
1. Check cache hit distribution (`/metrics/json` query_stats.cache_hits).
2. Validate Postgres health & slow queries (vector index usage).
3. Confirm fusion weights sane (sum > 0) via env or planned weights endpoint.
4. Inspect system metrics for CPU/GPU saturation.
5. Increase feature cache TTL or reduce `top_k` if constant feature recompute.

## 10. Glossary
Fusion Score: Weighted normalized blend of LTR and conceptual similarity.
Feature Cache: Redis object storing candidate feature vectors & LTR scores.
Backcompat Shim: Environment variable mapper ensuring old names still respected.

---
Evolves alongside platform maturity.

### Recent Maintenance
2025-08-27:
	- Cleaned redundant experimental UI & model folders -> moved to `archive/` (dashboard copies, gemma_phi_ui, extracted_zip, model_finetune_quant copies).
	- Introduced `scripts/index_codebase.py` for lightweight module inventory + optional model registry seeding (excludes `archive/`).
	- Added `/metrics/basic` endpoint + in-process stage timing observation (embed/retrieval/feature/ltr/fusion/pipeline) feeding dashboard health pill.
	- Implemented fusion weights management endpoints `/rag/fusion/weights` (GET/PUT) + versioning.
	- Dual-agent chat UI (Gemma/Phi/Ollama/Llama selectable) with health indicator polling `/metrics/basic` and per-stage timing display.
	- Memory MCP should store: active models (gemma:2b, bge-small), implemented stage timing (in-process), pending Prometheus export, and archive boundary to reduce irrelevant context resurfacing.

2025-08-28:
	- Leonardo Voice Integration: Connected TTS (Piper) and Whisper to Leonardo (Mistral 7B).
	- Model Upgrade: Replaced Leonardo's model from smaller variants to Mistral 7B (4.4GB) in Docker environment.
	- Voice Architecture: Created app/leonardo/audio_router.py with speak, listen, think, analyze endpoints.
	- Setup Automation: Built scripts/setup_leonardo_voice.sh with comprehensive voice capability installation.
	- Environment Resolution: Resolved Docker vs host confusion - Leonardo now operational in containerized environment.
	- Voice Framework: British analytical TTS voice, Whisper speech recognition, complete testing suite ready for deployment.
