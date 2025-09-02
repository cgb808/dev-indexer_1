#!/usr/bin/env bash
set -euo pipefail

# Beast3 Bootstrap Script
# Idempotent setup for GPU model + RAG indexing environment.
# Safe to re-run; skips work when already applied.

log() { echo -e "[bootstrap] $*"; }

REQ_PKGS=(git curl build-essential python3 python3-venv python3-pip pkg-config libssl-dev)

if ! command -v sudo >/dev/null 2>&1; then
  log "sudo not found; install it manually then re-run."; exit 1
fi

log "Updating apt metadata..."
sudo apt-get update -y

TO_INSTALL=()
for p in "${REQ_PKGS[@]}"; do dpkg -s "$p" >/dev/null 2>&1 || TO_INSTALL+=("$p"); done
if [ ${#TO_INSTALL[@]} -gt 0 ]; then
  log "Installing base packages: ${TO_INSTALL[*]}"
  sudo apt-get install -y "${TO_INSTALL[@]}"
else
  log "Base packages already present."
fi

# NVIDIA stack check (informational only)
if command -v nvidia-smi >/dev/null 2>&1; then
  log "nvidia-smi detected:"; nvidia-smi | head -n 3 || true
else
  log "nvidia-smi not found. Install NVIDIA driver before heavy model inference. Skipping."
fi

PY_ENV_DIR=".venv"
if [ ! -d "$PY_ENV_DIR" ]; then
  log "Creating Python venv ($PY_ENV_DIR)"
  python3 -m venv "$PY_ENV_DIR"
fi

log "Activating venv"
set +u; source "$PY_ENV_DIR/bin/activate"; set -u
python -m pip install --upgrade pip

log "Installing core requirements"
pip install -r dev-indexer_1/requirements.txt

if [ -f dev-indexer_1/requirements-gpu.txt ]; then
  log "Installing optional GPU requirements (best-effort)"
  pip install -r dev-indexer_1/requirements-gpu.txt || log "GPU optional deps failed; continue."
fi

log "Writing .env template if missing"
if [ ! -f .env ]; then
  cat > .env <<EOF
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION=documents
EOF
fi

log "Bootstrap complete. To use: source $PY_ENV_DIR/bin/activate && uvicorn dev-indexer_1.app.main:app --host 0.0.0.0 --port 8000"
