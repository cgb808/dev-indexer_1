# ZenGlow RAG / Retrieval Task Checklist

Last Updated: 2025-08-27
Source Context: Development progress, hybrid architecture draft, Artifact B scaffold, ranking router integration.

---
## 1. Completed
- FastAPI app bootstrap (`app/main.py`).
- Health router + DB/LLM checks.
- Legacy `/rag/query` endpoint (baseline retrieval + edge LLM call).
- RAG core modules (`pipeline.py`, `db_client.py`, `embedder.py`, `llm_client.py`).
- Dynamic conceptual scoring layer (distance + recency + metadata tags) in `RAGPipeline`.
- Redis cache utilities with JSON / msgpack + namespaced query caching.
- Real embedding HTTP integration + fallback logic.
- LLM client (Supabase Edge → Ollama fallback).
- Dependency Injection factory for `RAGPipeline`.
- Pydantic schemas for RAG query request/response.
- Runtime & dev dependency manifests (`requirements.txt`, `requirements-dev.txt`).
- Lint/format tooling (Ruff, Black, isort, Flake8, pre-commit).
- Redis build update publisher + secure options.
- Development progress & remote DB access docs.
- LTR linear model scaffold (`ltr.py`).
- Feature assembler scaffold (schema v1: similarity_primary, log_length, bias).
- Ranking router (`/rag/query2`) with LTR scoring + feature metadata + Redis caching.
- Unit test for RAG pipeline (`tests/test_rag_pipeline.py`).
- Expanded API tests for `/rag/pipeline`.
- Whisper.cpp setup script & local model fetch (`scripts/setup_whisper_cpp.sh`).
- Audio transcription router `/audio/transcribe` + static voice recorder UI.
- Character persona card (`docs/CHARACTER_CARD_EN.json`).
- Initial dashboard frontend scaffold inspection.
- Fusion scoring (conceptual + LTR) surfaced in `/rag/query2` (fused_score + weights).
- Deprecated legacy embedding & retrieval modules removed (merged into ranking path).
- Added model registry & /health/models endpoint + dashboard ModelPanel.
- Dashboard enhancements: sortable results, fusion weight badges, metrics JSON subset, voice iframe, query history stub.

---
## 2. In Progress / Drafted
- Hybrid retrieval architecture doc (summary placeholder; full spec external).
- (Moved to Completed) Legacy `/rag/query` now delegates to ranking + fusion path.

---
## 3. Next (Short-Term Targets)
| Priority | Task | Notes |
|----------|------|-------|
| P0 | (Done) Refactor `/rag/query` to reuse ranking pipeline | Completed – remove duplicate logic |
| P0 | Add tests for fusion scoring + ranking router & feature assembler | Ensure stability before expansions |
| P1 | Add DI-based embedder usage in ranking router (remove local instantiation) | Unify embedding path |
| P1 | Add advanced score fusion strategy (additional components: recency, metadata tags) | Extend conceptual component beyond distance |
| P1 | Add robust error / timeout handling + custom exception handlers | Observability integration |
| P2 | Streaming provisional→refined diff output (SSE/WebSocket) | Align with Architecture Section 8 |
| P2 | Introduce ANN parameter runtime config integration | Table `ann_runtime_config` (Artifact A) |
| P2 | Cache feature vectors & LTR + fused scores (short TTL) | Faster re-queries |
| P2 | Persist query performance to TimescaleDB hypertable | Long-term trend analysis |
| P2 | Implement dynamic scoring strategy interface | Pluggable strategies |
| P3 | Logging & tracing spans (OpenTelemetry) | Stages embed/ann/feature/ltr/refine |
| P3 | Metrics export (Prometheus) | Latency, recall canary placeholders |
| P3 | Security: API key / token guard on advanced endpoints | Env-driven toggle |
| P4 | Feature enrichment pipeline (NER, topic, authority scoring) | Populate `chunk_features` |
| P4 | LTR model load from external artifact (LightGBM / Torch / ONNX) | Replace linear placeholder |
| P4 | Dual index routing module (IVFFLAT vs HNSW) | Artifact C |
| P5 | Contextual LM re-ranking augmentation (top M) | Artifact B extension / Architecture 7 |
| P5 | Diversity / novelty / policy filters | MMR + allowlist / blocklist hooks |
| P6 | Bandit exploration layer (LinUCB/Thompson) | After stable metrics |
| P6 | Experiment framework: A/B + interleaving | Link to metrics store |

---
## 4. Artifact Mapping
| Artifact | Scope | Status |
|----------|-------|--------|
| A | SQL DDL: schema, indexes, materialized views | Initial schema_v2 committed (`sql/artifacts/schema_v2.sql`) |
| B | Feature assembly + LTR scaffold | Partial (scaffold done) |
| C | Dual-index routing (IVF/HNSW) | Pending |
| D | Streaming diff API | Pending |
| E | Bundle (A–D) | Pending |

---
## 5. Planned Tables (Artifact A Preview)
- `documents`, `chunks`, `chunk_features`, `interaction_events`, `chunk_engagement_stats` (MV)
- `scoring_experiments`, `query_performance`, `ann_runtime_config`
- `model_registry`, `scoring_weights`, `feature_snapshots`

---
## 6. Configuration Keys (Current + Upcoming)
Current: EMBED_ENDPOINT, SUPABASE_URL, SUPABASE_KEY, OLLAMA_URL, OLLAMA_MODEL, PG_* vars, DATABASE_URL, REDIS_* vars, RAG_WEIGHT_DISTANCE, RAG_WEIGHT_RECENCY, RAG_WEIGHT_METADATA.
Upcoming: RAG_FUSION_LTR_WEIGHT, RAG_FUSION_CONCEPTUAL_WEIGHT, RAG_STREAMING_ENABLED, ANN_PARAM_SET, ENABLE_HNSW, MAX_RERANK_CANDIDATES.

---
## 7. Technical Debt / Cleanup
- Type annotations for metadata fields in conceptual scoring (TypedDict).
- Consolidate legacy retrieval & new pipeline modules.
- Provide consistent embedding dimension validation.
- Add graceful shutdown for background streaming tasks (future).

---
## 8. Test Coverage Gaps
- Fusion scoring math & weight normalization (new).
- Ranking router / feature assembler unit tests.
- Error paths (timeouts, empty results).
- Redis caching correctness (hit/miss logic).
- Conceptual scoring edge cases (missing timestamp / tags once metadata integrated).

---
## 9. Observability TODO
- Structured JSON logging (uvicorn access + app loggers).
- Trace IDs propagation.
- Latency histograms per stage.
- Recall canary sampling harness.

---
## 10. Security TODO
- API key verification middleware.
- Rate limiting (basic token bucket) for advanced endpoints.
- PII scrubbing filter for LM prompts.

---
## 11. Completion Definition (Milestone: Baseline RAG v1)
Must have: Unified `/rag/query2` + legacy `/rag/query` consolidation, fused scoring (done), metrics, caching, basic auth, tests >= 80% coverage for pipeline & ranking logic including fusion.
Nice to have: Streaming diff prototype, diversity filter, experiment configuration stub.

---
## 12. Action Selection
Reply with one or more task identifiers (e.g. "P0 fusion", "Artifact A", "tests ranking") to trigger automated implementation.

