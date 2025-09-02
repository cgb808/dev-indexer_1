#!/usr/bin/env bash
set -euo pipefail

# Bootstrap / refresh Python virtual environment for RAG ingest + memory bridge.
# Usage:
#   bash dev-indexer_1/scripts/bootstrap_ingest_env.sh            # create/update .venv
#   ENV_DIR=.venv_ingest bash dev-indexer_1/scripts/bootstrap_ingest_env.sh
#   bash dev-indexer_1/scripts/bootstrap_ingest_env.sh --gpu       # include GPU deps
#   bash dev-indexer_1/scripts/bootstrap_ingest_env.sh --force     # recreate venv
#
# Flags:
#   --gpu      Install additional packages from requirements-gpu.txt
#   --force    Remove existing venv before creating
#   --upgrade  Run pip install --upgrade for base requirements
#
# Environment Variables:
#   ENV_DIR   (default .venv) target virtual environment directory
#
ENV_DIR=${ENV_DIR:-.venv}
REQ_BASE="dev-indexer_1/requirements.txt"
REQ_GPU="dev-indexer_1/requirements-gpu.txt"
PYTHON_BIN=${PYTHON_BIN:-python3}
DO_GPU=0
DO_FORCE=0
DO_UPGRADE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --gpu) DO_GPU=1; shift;;
    --force) DO_FORCE=1; shift;;
    --upgrade) DO_UPGRADE=1; shift;;
    *) echo "[warn] unknown arg $1"; shift;;
  esac
done

if [[ ! -f "$REQ_BASE" ]]; then
  echo "[error] requirements file not found: $REQ_BASE" >&2
  exit 1
fi

if [[ $DO_FORCE -eq 1 && -d "$ENV_DIR" ]]; then
  echo "[info] removing existing venv $ENV_DIR";
  rm -rf "$ENV_DIR"
fi

if [[ ! -d "$ENV_DIR" ]]; then
  echo "[info] creating venv $ENV_DIR"
  $PYTHON_BIN -m venv "$ENV_DIR"
fi

source "$ENV_DIR/bin/activate"
python -m pip install --upgrade pip wheel setuptools >/dev/null

INSTALL_CMD="python -m pip install -r $REQ_BASE"
if [[ $DO_UPGRADE -eq 1 ]]; then
  INSTALL_CMD+=" --upgrade"
fi
echo "[info] installing base requirements"
eval "$INSTALL_CMD"

if [[ $DO_GPU -eq 1 ]]; then
  if [[ -f "$REQ_GPU" ]]; then
    echo "[info] installing gpu requirements"
    python -m pip install -r "$REQ_GPU"
  else
    echo "[warn] gpu requirements file missing: $REQ_GPU"
  fi
fi

# Verify critical modules for ingest pipeline
MISSING=()
for mod in psycopg2 redis msgpack requests; do
  python - <<PY || MISSING+=("$mod")
try:
    import $mod  # type: ignore
except Exception as e:
    raise SystemExit(1)
PY
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo "[error] missing modules after install: ${MISSING[*]}" >&2
  exit 2
fi

echo "[ok] venv ready: $ENV_DIR"
echo "[ok] to activate: source $ENV_DIR/bin/activate"

echo "[hint] offline ingest example:"
echo "       source $ENV_DIR/bin/activate && python dev-indexer_1/scripts/rag_ingest.py --source docs --glob 'docs/**/*.md' --offline --msgpack-out data/msgpack"
