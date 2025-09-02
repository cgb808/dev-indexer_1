<!-- Directory Index: app/ -->
# app/ Service Code

FastAPI application implementing RAG, audio (TTS/STT), metrics, health, and control logic.

Key Subpackages:
- `rag/` – Retrieval pipeline (retrieval, feature assembly, ranking, fusion, LLM invocation).
- `core/` – Config, metrics, logging, diagnostics, caching, secrets.
- `audio/` – Transcription & TTS endpoints and helpers.
- `health/` – Health & readiness probes.
- `central_control/` – (Planned) orchestration / routing logic.

See also:
- Project Overview: `../README.md`
- DevOps Practices: `../docs/devops/DEVOPS.md`
- RAG Integration: `../docs/integration/MCP_RAG_INTEGRATION.md`