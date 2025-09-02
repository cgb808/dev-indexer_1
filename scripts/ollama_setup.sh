#!/usr/bin/env bash
# Idempotent Ollama install + gemma:2b setup + optional quantized variant.
# Run this directly ON beast3 (RDP terminal) or via SSH once restored:
#   bash dev-indexer_1/scripts/ollama_setup.sh
# Tunables (override by exporting before running):
#   OLLAMA_MODELS_DIR (default: /tank/ollama/models if /tank exists else $HOME/ollama-models)
#   OLLAMA_KEEP_ALIVE (default: 300)
#   OLLAMA_MAX_LOADED_MODELS (default: 1)
#   CREATE_ZFS_DATASET=1 (attempt zfs create if path on ZFS pool desired)
#   CREATE_Q4_VARIANT=1 (build gemma2b-q4 variant)
set -euo pipefail

log(){ printf '\n[ollama-setup] %s\n' "$*"; }

# Decide model directory
if [[ -z "${OLLAMA_MODELS_DIR:-}" ]]; then
  if [[ -d /tank ]]; then
    OLLAMA_MODELS_DIR=/tank/ollama/models
  else
    OLLAMA_MODELS_DIR="$HOME/ollama-models"
  fi
fi
export OLLAMA_MODELS_DIR

if [[ "${CREATE_ZFS_DATASET:-0}" == "1" ]]; then
  if command -v zfs >/dev/null 2>&1; then
    DATASET=$(dirname "$OLLAMA_MODELS_DIR")
    if ! zfs list | grep -q "$DATASET" 2>/dev/null; then
      PARENT_POOL=${DATASET%%/*}
      if zfs list "$PARENT_POOL" >/dev/null 2>&1; then
        log "Creating ZFS dataset $DATASET with compression=zstd"
        sudo zfs create -o compression=zstd -o atime=off "$DATASET" || true
      else
        log "Pool $PARENT_POOL not found; skipping dataset creation"
      fi
    fi
  else
    log "zfs not installed; skipping dataset creation"
  fi
fi

log "Ensuring model directory exists: $OLLAMA_MODELS_DIR"
mkdir -p "$OLLAMA_MODELS_DIR"

if ! command -v ollama >/dev/null 2>&1; then
  log "Installing Ollama"
  curl -fsSL https://ollama.com/install.sh | sh
else
  log "Ollama already installed: $(ollama --version 2>/dev/null || echo present)"
fi

log "Enable/start ollama service"
if systemctl list-units --type=service | grep -q ollama.service; then
  sudo systemctl enable --now ollama
else
  log "ollama.service not found yet (installer may still be running); proceeding"
fi

log "Apply systemd override for model dir + tunables"
sudo mkdir -p /etc/systemd/system/ollama.service.d
cat <<EOF | sudo tee /etc/systemd/system/ollama.service.d/override.conf >/dev/null
[Service]
Environment=OLLAMA_MODELS=${OLLAMA_MODELS_DIR}
Environment=OLLAMA_KEEP_ALIVE=${OLLAMA_KEEP_ALIVE:-300}
Environment=OLLAMA_MAX_LOADED_MODELS=${OLLAMA_MAX_LOADED_MODELS:-1}
EOF
sudo systemctl daemon-reload || true
sudo systemctl restart ollama || true

log "Pulling base model gemma:2b (skip if already present)"
if ollama list 2>/dev/null | grep -q '^gemma:2b'; then
  log "gemma:2b already present"
else
  ollama pull gemma:2b
fi

if [[ "${CREATE_Q4_VARIANT:-1}" == "1" ]]; then
  if ollama list 2>/dev/null | grep -q '^gemma2b-q4'; then
    log "Quantized variant gemma2b-q4 already exists"
  else
    log "Creating quantized variant gemma2b-q4 (q4_0)"
    WORKDIR=$(mktemp -d)
    cat <<'MODF' > "$WORKDIR/Modelfile"
FROM gemma:2b
PARAMETER quantize q4_0
MODF
    ollama create gemma2b-q4 -f "$WORKDIR/Modelfile"
    rm -rf "$WORKDIR"
  fi
fi

log "Smoke test generate (one short prompt)"
curl -s http://localhost:11434/api/generate -d '{"model":"gemma:2b","prompt":"ping"}' | head -n 5 || true

log "Done. Export for FastAPI (.env):"
cat <<ENV
OLLAMA_MODEL=gemma:2b
OLLAMA_HOST=127.0.0.1
OLLAMA_PORT=11434
# Alternative quantized variant:
# OLLAMA_MODEL=gemma2b-q4
ENV
