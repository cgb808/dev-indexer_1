<!-- Relocated from repository root on 2025-08-30 -->
[Back to Docs Index](../../DOCS_INDEX.md)

# Production Deployment Guide

## Kong Gateway + WebSocket Metrics Setup

### 1. Kong Configuration
```bash
docker run -d --name kong-gateway \
  --network="bridge" \
  -v $(pwd)/kong.yml:/kong/declarative/kong.yml \
  -e "KONG_DATABASE=off" \
  -e "KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml" \
  -e "KONG_PROXY_ACCESS_LOG=/dev/stdout" \
  -e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" \
  -e "KONG_PROXY_ERROR_LOG=/dev/stderr" \
  -e "KONG_ADMIN_ERROR_LOG=/dev/stderr" \
  -e "KONG_ADMIN_LISTEN=0.0.0.0:8001" \
  -p 8000:8000 -p 8443:8443 -p 8001:8001 -p 8444:8444 \
  kong:latest
```

### 2. Environment Configuration
```
cp .env.backend.example .env.backend
cp frontend/dashboard/.env.example frontend/dashboard/.env
```
Edit values (DB URLs, Supabase creds, API endpoints, Kong addresses).

### 3. Health Monitoring Endpoints
`GET /health/aggregated` returns full system health JSON.
`WS /ws/metrics` streams real-time metrics every 5s.

### 4. Frontend Integration
WebSocket URL: `${VITE_GATEWAY_BASE}/ws/metrics`.
Health URL: `${VITE_RAG_API_BASE}/health/aggregated`.

### 5. Production Checklist
- [ ] Kong gateway up
- [ ] Backend .env configured
- [ ] Frontend .env configured
- [ ] Health endpoint responds
- [ ] Metrics WebSocket streams
- [ ] Model(s) loaded (ollama list)
- [ ] Voice integration operational

### 6. Monitoring
- Health Dashboard (aggregated)
- Metrics stream (charts)
- Kong logs for request tracing
- System metrics (CPU, memory, uptime)

This completes the deployment setup baseline.
