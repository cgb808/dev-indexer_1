## Switchr Router (Central Control Heuristic Layer)

Purpose: Provide a fast (<150ms) routing decision layer that selects the appropriate backend (Leonardo / Jarvis / Edge) and optional tool classification via the Tiny Tool Controller.

### Endpoints

POST /switchr/route
Request body fields:
  - text (str): user query
  - allow_tools (bool): permit tool planning
  - prefer (str|optional): hard override backend
  - require_reasoning (bool): force deeper reasoning model (Leonardo)
  - classify_tools (bool): attempt tiny tool classification

Response:
  - backend: chosen backend string
  - confidence: 0..1 heuristic confidence
  - reasons: list of rationale tokens
  - latency_ms: elapsed processing time
  - tool_classification (optional): domain/tools/confidence
  - features: availability flags

GET /switchr/health -> basic readiness & flags

### Heuristic Overview
Scoring signals:
  - Length buckets (short -> edge, long -> leonardo)
  - Keyword families (code/math/science -> jarvis)
  - Reasoning verbs (explain/analyze/compare) -> leonardo
  - require_reasoning flag (strong bias)
  - trivial short question -> slight edge boost

Confidence = best_score / total_scores (bounded)

### Tool Classification Integration
If `classify_tools=true` the router attempts to load `TinyToolController` from `app.audio.integrated_audio_pipeline`. Failure is non-fatal; a rationale note is added.

### Extension Points
Planned enhancements:
  - Feedback endpoint to record actual outcome quality
  - Adaptive weight adjustment based on rolling success metrics
  - Optional lightweight embedding similarity gating for domain detection
  - Latency SLA tracking per backend

### Rationale
Centralizing early routing logic prevents each downstream component from re-implementing heuristics and enables telemetry / A/B experimentation for classification quality vs. user satisfaction.

### Version
v1 (heuristic baseline) – August 30, 2025
