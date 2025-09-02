#!/usr/bin/env bash
set -euo pipefail

# Simple helper to establish an SSH local forward to the remote Postgres (bound locally on host).
# Usage:
#   ./scripts/db_ssh_tunnel.sh user@beast3 5433           # forward local :5433 -> remote 127.0.0.1:5432
#   DB_PORT=15432 ./scripts/db_ssh_tunnel.sh user@beast3  # change local port via env var
#
# Then connect:
#   psql postgresql://postgres:PASS@127.0.0.1:<local_port>/rag_db

REMOTE="${1:-}"
LOCAL_PORT="${DB_PORT:-${2:-5433}}"
REMOTE_DB_PORT=5432

if [[ -z "$REMOTE" ]]; then
  echo "Usage: $0 user@remote-host [local_port]" >&2
  exit 2
fi

echo "[tunnel] Forwarding localhost:${LOCAL_PORT} -> ${REMOTE}:127.0.0.1:${REMOTE_DB_PORT}" >&2
set -x
ssh -N -L ${LOCAL_PORT}:127.0.0.1:${REMOTE_DB_PORT} "${REMOTE}"