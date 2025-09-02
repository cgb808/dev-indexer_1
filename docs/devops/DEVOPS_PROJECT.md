<!-- High-level DevOps project strategy distinct from tactical backlog in DEVOPS.md -->
[Back: DevOps Practices](./DEVOPS.md) | [Docs Index](../DOCS_INDEX.md)

# DevOps Project Strategy

Focus: Provide a forward-looking operational architecture roadmap across CI/CD, observability, reliability, security, and data lifecycle—complementing the tactical checklist in `DEVOPS.md`.

## Objectives
1. Fast Feedback: <10 min CI (lint+tests) + optional extended integration lane.
2. Protected Reliability: Progressive delivery (staging → prod) with automated health & regression signals.
3. Deep Visibility: Unified metrics + tracing + structured logs enabling 90% of incidents diagnosable in <15 min.
4. Secure by Default: Principle-of-least-privilege, auditable policies, secrets never stored in repo.
5. Data Integrity: Reproducible ingestion & index rebuilds, versioned snapshots, drift detection.
6. Model Governance: Track model hash, quantization, fusion weights, LTR feature schema version.

## Pipeline Blueprint
Stage | Actions | Exit Criteria
------|---------|--------------
Pre-commit | ruff/black/isort/mypy (fast) | Clean diff, no type errors (non-block optional warn)
CI (core) | Install deps cache -> lint -> unit tests -> coverage | >=95% critical path coverage (rag core, audio routers)
CI (extended) | Integration tests (Postgres/Redis), embedding smoke | All green, reuses service containers
Security | Dependency scan (pip-audit), secret scan (gitleaks) | No HIGH vulns / secrets
Build | Multi-arch image (cpu,gpu variant) with SBOM | SBOM uploaded, image signed (cosign planned)
Deploy Staging | Apply migrations, warm caches, run synthetic queries | Health SLOs pass (latency, error %)
Promote Prod | Canary 10% traffic with weight gating | No regressions after observation window

## Observability Stack (Planned Target)
Layer | Tooling | Notes
------|---------|------
Metrics | Prometheus + exporter integration | Stage latency histograms, cache ratios
Tracing | OpenTelemetry -> Tempo/Jaeger | Pipeline spans (embed→retrieve→features→ltr→fusion)
Logging | Structured JSON -> Loki | Correlation / trace IDs
Dashboards | Grafana + React dashboard | Ops + product side-by-side
Alerting | Alertmanager + PagerDuty webhook | Multi-signal (latency p95, error rate, cache hit dip)

## Reliability Patterns
- Weighted fusion gating for safe experimentation (adjust LTR weight without redeploy).
- Readiness gate ensures: DB connectivity, model registry seeded, min GPU memory free, mandatory env validated.
- Cache tier fallback: if feature cache cold, degrade gracefully with direct similarity scoring.

## Security / Compliance Roadmap
Phase | Focus
------|------
1 | API key middleware + rate limiting
2 | RLS policies (already drafted) -> incremental activation
3 | Audit logging (immutable append in DB)
4 | PII scrubbing & redaction pipeline
5 | Secrets rotation automation & Vault leases enforcement

## Data Lifecycle
Aspect | Plan
-------|-----
Vector Index | Rebuild nightly diff script; store build manifest with commit hash
Snapshots | Knowledge graph + model registry snapshot after major merges
Drift Detection | Compare top-k distribution shift across week ranges
Feature Schema Versioning | Embed schema_version in each cached feature blob

## Model Governance
- Record (model_name, quantization, source_hash, loaded_at) at registry seed.
- Fusion weight change emits audit log entry (user, old, new, reason, issue link).
- LTR feature schema migrations accompanied by compatibility adapter for N-1.

## Automation Hooks (Future)
Trigger | Action
--------|-------
Project index change | Regenerate runtime index & embed into Memory MCP
Model registry delta | Persist snapshot JSON + push to artifact store
Fusion weight update | Emit event -> optional Slack/pager low-priority notice

## KPIs / SLOs
Category | Metric | Target
---------|--------|-------
Latency | /rag/query2 p95 | < 1500 ms
Stability | Error rate | < 1% 5m rolling
Cache | Feature cache hit | > 70%
Quality | LTR uplift vs baseline | +8% NDCG@10
Ops | MTTR | < 15 min

## Open Design Questions
- Adopt TimescaleDB for time-series vs. push metrics to Prometheus remote-write only?
- Introduce feature store abstraction or maintain lightweight Redis + SQL hybrid.
- Standardize synthetic queries set for canary analysis (YAML vs. code-driven).

## Timeline (Indicative)
Week 1-2: CI core + structured logging + basic tracing skeleton
Week 3-4: Metrics expansion (stage histograms) + canary deploy workflow
Week 5-6: Security phase 1 (API keys + rate limit) + model governance logging
Week 7+: TimescaleDB evaluation & advanced drift detection

---
Evolves with platform maturity; update when major operational capability lands.