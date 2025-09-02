"""FastAPI entrypoint for ZenGlow Indexer API.
Order of operations on import:
    1. Apply env backward compatibility shim (old -> new names).
    2. Bootstrap secrets (may populate SUPABASE_KEY).
    3. Validate required env vars (fail fast if missing).
Then import remainder of modules relying on configuration.
"""

import logging
import os
from typing import Any, Dict, Generator

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.core import log_buffer as _log_buffer
from app.core.config import (apply_backward_compat_env, config_router,
                             validate_required_env)
from app.core.diagnostics_router import router as diagnostics_router
from app.core.logging import init_logging, with_ctx
from app.core.metrics_router import router as metrics_router
from app.core.secrets import bootstrap_supabase_key
from app.health.health_router import health_router
from app.personas import DEFAULT_PERSONA_KEY, PERSONAS, resolve_persona
from app.rag.schemas import RAGQueryRequest, RAGQueryResponse

# 1. Backward compatibility env translation
_applied_compat = apply_backward_compat_env()
# 2. Load Supabase indexer key early (may populate SUPABASE_KEY from Vault)
bootstrap_supabase_key()
# 3. Validate required envs (raises RuntimeError if missing)
try:
    validate_required_env(fail_fast=True)
except RuntimeError:  # pragma: no cover - startup failure path
    # Re-raise to prevent app from starting with invalid config
    raise

from fastapi.responses import FileResponse, RedirectResponse

from app.audio import devices_router, transcription_router, tts_router
from app.audio.speaker_router import router as speaker_router
from app.audio.wake_router import router as wake_router
from app.audio.xtts_router import router as xtts_router
from app.central_control.switchr_router import router as switchr_router
from app.core import metrics as inproc_metrics
from app.leonardo.audio_router import router as leonardo_router
from app.metrics.metrics_router import metrics_router as ws_metrics_router
from app.rag.db_client import DBClient
# Legacy imports (can be deprecated once new pipeline stable)
# Legacy direct embedding/retrieval removed; use ranking_router logic instead. Edge LLM kept for answer generation.
from app.rag.edge_llm import get_edge_model_response  # Legacy fallback
from app.rag.embed_router import router as embed_router
from app.rag.embedder import Embedder
from app.rag.llm_client import LLMClient
from app.rag.llm_probe_router import router as llm_probe_router
from app.rag.pipeline import RAGPipeline
from app.rag.ranking_router import (  # reuse logic for legacy endpoint refactor
    Query2Payload, rag_query2)
from app.rag.ranking_router import router as ranking_router
from app.rag.streaming_router import \
    router as streaming_router  # SSE phased diff (Artifact D)

init_logging()
app: FastAPI = FastAPI(title="ZenGlow Indexer API")
_log_buffer.install()  # enable in-memory log capture for UI debugging
log = with_ctx(logging.getLogger(__name__), component="startup")
log("app constructing")
app.include_router(health_router)
app.include_router(ranking_router)
app.include_router(llm_probe_router)
app.include_router(transcription_router.router)
app.include_router(tts_router.router)
app.include_router(devices_router.router)
app.include_router(speaker_router)
app.include_router(xtts_router)
app.include_router(leonardo_router)
app.include_router(switchr_router)
app.include_router(wake_router)
app.include_router(embed_router)
app.include_router(streaming_router)
app.include_router(config_router)
app.include_router(metrics_router)
app.include_router(ws_metrics_router)  # WebSocket metrics streaming
app.include_router(diagnostics_router)
log("routers registered")

# Static assets (voice UI)
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    # Dedicated mount for dashboard assets when built references absolute /assets path
    assets_dir = "app/static/dashboard/assets"
    if os.path.isdir(assets_dir):  # pragma: no branch
        app.mount("/assets", StaticFiles(directory=assets_dir), name="dashboard_assets")
    log(
        "static mounts complete",
        assets_dir=assets_dir,
        assets_present=os.path.isdir(assets_dir),
    )
except Exception:
    # Directory might not exist in some deploy contexts; fail soft
    pass


def get_rag_pipeline() -> Generator[RAGPipeline, None, None]:
    db_client = DBClient()
    embedder = Embedder()
    llm = LLMClient()
    pipeline = RAGPipeline(db_client=db_client, embedder=embedder, llm_client=llm)
    try:
        yield pipeline
    finally:
        db_client.close()


@app.on_event("startup")
def _on_startup():  # pragma: no cover - runtime path
    log("startup event", applied_compat=_applied_compat, required_env_missing=[])


@app.post(
    "/rag/query"
)  # Refactored legacy endpoint: delegates scoring to /rag/query2 logic; now supports backend preference
async def rag_query(request: Request) -> Dict[str, Any]:
    total_timer = inproc_metrics.Timer()
    inproc_metrics.inc("requests_total")
    body = await request.json()
    query = body.get("query")
    top_k = body.get("top_k", 5)
    prefer = body.get("prefer", "auto")  # auto|edge|llama|ollama
    persona_key = body.get("persona_key")  # optional predefined persona key
    session_id = body.get("session_id")  # opaque client-provided id
    if not query:
        return {"error": "Missing query"}

    # Reuse rag_query2 internal logic for retrieval + scoring (simulate payload)
    ranking_payload = Query2Payload(query=query, top_k=top_k)
    retrieval_error: str | None = None
    try:
        ranked = await rag_query2(ranking_payload)  # returns dict with results/items
    except (
        Exception
    ) as e:  # graceful fallback: continue with empty context & note error
        ranked = {"results": [], "timings": {}}
        retrieval_error = str(e)
        inproc_metrics.inc("errors_total")

    # Build answer using fused ranked chunks
    ranked_results = ranked.get("results", [])[:top_k]
    context = "\n---\n".join([r.get("text_preview", "") for r in ranked_results])
    # Persona resolution (predefined key or env override)
    env_override = os.getenv("ASSISTANT_PERSONA")
    base_persona = resolve_persona(persona_key, env_override)
    safety_tail = " Always be honest about uncertainty. Do not invent citations or sources."  # short safety guidance
    persona_full = base_persona + safety_tail
    prompt = (
        f"{persona_full}\n\n"
        f"Use the provided context chunks if relevant. If context is empty or irrelevant, say so briefly and answer from general knowledge if appropriate.\n"
        f"Context:\n{context}\nQuestion: {query}\nAnswer:"
    )
    # Prefer new unified client so user can experiment with backends; fallback to legacy if generation fails
    llm_client = LLMClient()
    gen_meta: Dict[str, Any]
    llm_timer = inproc_metrics.Timer()
    try:
        gen_meta = llm_client.generate_with_metadata(prompt, prefer=prefer)
    except Exception as e:  # pragma: no cover - defensive
        inproc_metrics.inc("errors_total")
        # Fallback to legacy edge-only path
        answer = get_edge_model_response(prompt)
        gen_meta = {"text": answer, "backend": "edge_legacy", "errors": [str(e)]}
    llm_elapsed = llm_timer.ms()
    inproc_metrics.inc("llm_calls_total")

    answer = gen_meta.get("text", "")
    if not answer:
        # Provide a minimal fallback answer so UI doesn't show error blob
        base_fallback = (
            "I can still answer from general knowledge, but retrieval is temporarily unavailable."
            if retrieval_error
            else ""
        )
        answer = base_fallback or "(no answer generated)"
    answer_backend = gen_meta.get("backend")
    answer_latency = gen_meta.get("total_latency_ms")
    answer_errors = gen_meta.get("errors")
    token_estimate = len(answer.split()) if answer else 0
    # Return legacy shape + new scoring metadata
    legacy_chunks = [
        {
            "id": r.get("chunk_id"),
            "chunk": r.get("text_preview"),
            "score": r.get("fused_score"),
            "ltr_score": r.get("ltr_score"),
            "conceptual_score": r.get("conceptual_score"),
            "distance": r.get("distance"),
        }
        for r in ranked_results
    ]
    timings = ranked.get("timings", {}) or {}
    # Observe latency metrics (best-effort); include new per-stage breakdown
    try:
        if timings:
            stage_map = {
                "embed_ms": "embed_ms",
                "retrieve_ms": "retrieval_ms",  # normalize naming
                "feature_ms": "feature_ms",
                "ltr_ms": "ltr_ms",
                "fusion_ms": "fusion_ms",
                "total_ms": "pipeline_ms",
            }
            for src_key, metric_key in stage_map.items():
                val = timings.get(src_key)
                if val is not None:
                    try:
                        inproc_metrics.observe(metric_key, float(val))
                    except Exception:
                        pass
        if answer_latency is not None:
            try:
                inproc_metrics.observe("llm_ms", float(answer_latency))
            except Exception:
                pass
        # Overall end-to-end (from request ingress to response build)
        try:
            inproc_metrics.observe("total_ms", total_timer.ms())
        except Exception:
            pass
    except Exception:
        pass

    return {
        "chunks": legacy_chunks,
        "answer": answer,
        "answer_meta": {
            "backend": answer_backend,
            "latency_ms": answer_latency,
            "token_estimate": token_estimate,
            "errors": answer_errors,
            "prefer": prefer,
            "persona_key": persona_key
            or ("env_override" if env_override else DEFAULT_PERSONA_KEY),
            "retrieval_error": retrieval_error,
            "rag_used": retrieval_error is None and len(legacy_chunks) > 0,
            "timings": timings,
        },
        "fusion_weights": ranked.get("fusion_weights"),
        "feature_schema_version": ranked.get("feature_schema_version"),
        "feature_names": ranked.get("feature_names"),
        "scoring_version": ranked.get("scoring_version"),
        "session_id": session_id,
    }


@app.get("/config/personas")
def list_personas():
    return {"personas": list(PERSONAS.keys()), "default": DEFAULT_PERSONA_KEY}


@app.get("/dashboard")
def dashboard_page():
    """Serve built React dashboard (copied into app/static/dashboard)."""
    path = "app/static/dashboard/index.html"
    if os.path.exists(path):  # pragma: no branch
        return FileResponse(path)
    return {"error": "dashboard_not_found"}


@app.get("/")
def root_redirect():  # pragma: no cover - simple redirect
    return RedirectResponse(url="/dashboard")


@app.get("/logs/recent")
def logs_recent(since: int = 0, limit: int = 400):
    """Return recent log lines since id (polling model)."""
    buf = _log_buffer.get_buffer()
    lines = buf.since(since, limit)
    next_id = lines[-1]["id"] if lines else since
    return {"lines": lines, "next": next_id}


@app.post("/rag/pipeline", response_model=RAGQueryResponse)
async def rag_pipeline_endpoint(
    payload: RAGQueryRequest, pipeline: RAGPipeline = Depends(get_rag_pipeline)
) -> RAGQueryResponse:
    answer = pipeline.run(query=payload.query, top_k=payload.top_k)
    # For now we don't surface chunk scores since db_client stub doesn't provide them
    return RAGQueryResponse(answer=answer, chunks=[])
