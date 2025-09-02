#!/usr/bin/env bash
# One-shot remote bootstrap for Ollama + gemma:2b (and quant variant) without /tank present.
# Run AFTER cloning ZenGlow repo on the target host:
#   bash dev-indexer_1/scripts/remote_ollama_bootstrap.sh
# Idempotent: safe to re-run.
set -euo pipefail

log(){ printf '\n[bootstrap] %s\n' "$*"; }

if [[ "${OLLAMA_MODELS_DIR:-}" == "" ]]; then
  if [[ -d /tank/ollama/models ]]; then
    OLLAMA_MODELS_DIR=/tank/ollama/models
  else
    OLLAMA_MODELS_DIR="$HOME/ollama-models"
  fi
fi
export OLLAMA_MODELS_DIR

log "Using model directory: $OLLAMA_MODELS_DIR"
mkdir -p "$OLLAMA_MODELS_DIR"
ls -ld "$OLLAMA_MODELS_DIR" || true

log "Ensuring curl present"
if ! command -v curl >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -y && sudo apt-get install -y curl
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y curl
  elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y curl
  fi
fi

log "Installing/upgrading Ollama (if not present)"
if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
else
  ollama --version || true
fi

log "Enable/start service"
if systemctl list-unit-files | grep -q '^ollama.service'; then
  sudo systemctl enable --now ollama || true
  sleep 2
fi

log "Apply systemd override to set OLLAMA_MODELS_DIR"
sudo mkdir -p /etc/systemd/system/ollama.service.d
cat <<EOF | sudo tee /etc/systemd/system/ollama.service.d/override.conf >/dev/null
[Service]
Environment=OLLAMA_MODELS=${OLLAMA_MODELS_DIR}
Environment=OLLAMA_KEEP_ALIVE=${OLLAMA_KEEP_ALIVE:-300}
Environment=OLLAMA_MAX_LOADED_MODELS=${OLLAMA_MAX_LOADED_MODELS:-1}
EOF
sudo systemctl daemon-reload || true
sudo systemctl restart ollama || true

log "Pulling base model gemma:2b"
if ollama list 2>/dev/null | grep -q '^gemma:2b'; then
  log "gemma:2b already present"
else
  ollama pull gemma:2b
fi

log "Creating quantized variant (gemma2b-q4) if missing"
if ! ollama list 2>/dev/null | grep -q '^gemma2b-q4'; then
  WORKDIR=$(mktemp -d)
  cat <<'MODF' > "$WORKDIR/Modelfile"
FROM gemma:2b
PARAMETER quantize q4_0
MODF
  ollama create gemma2b-q4 -f "$WORKDIR/Modelfile" || true
  rm -rf "$WORKDIR"
else
  log "gemma2b-q4 already exists"
fi

log "Smoke test (generate ping)"
curl -s http://localhost:11434/api/generate -d '{"model":"gemma:2b","prompt":"ping"}' | head -n 5 || true

log "Installed models:"
ollama list || true

log "ENV suggestions"
cat <<ENV
OLLAMA_MODEL=gemma:2b
OLLAMA_HOST=127.0.0.1
OLLAMA_PORT=11434
# For quantized: OLLAMA_MODEL=gemma2b-q4
ENV

log "Done"
