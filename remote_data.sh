#!/bin/bash
# Remote dataset management helper for CUDA host (beast3)
# Non-destructive by default. Provides listing, sampling, subsetting, stats, staging.

set -euo pipefail

REMOTE_HOST="beast3"
REMOTE_USER="cgbowen"
REMOTE_ROOT="/home/cgbowen/ZenGlow"
REMOTE_DATA="$REMOTE_ROOT/data"
LOCAL_DATA="data"  # local lightweight samples live here

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log(){ echo -e "${GREEN}[INFO] $1${NC}"; }
warn(){ echo -e "${YELLOW}[WARN] $1${NC}"; }
err(){ echo -e "${RED}[ERROR] $1${NC}" >&2; }

require_ssh(){
  if ! ssh -o BatchMode=yes -o ConnectTimeout=5 "$REMOTE_USER@$REMOTE_HOST" 'echo ok' >/dev/null 2>&1; then
    err "SSH to $REMOTE_HOST failed"; exit 1; fi
}

remote(){ ssh "$REMOTE_USER@$REMOTE_HOST" "$*"; }

usage(){ cat <<EOF
Remote Data Tool

USAGE: $0 <command> [args]

Commands:
  list [subdir]          List files (non-recursive) in remote data (or subdir)
  tree [subdir]          Show directory tree (depth 2 by default)
  sizes [subdir]         Show sizes (top 20)
  stats <pattern>        Line count + size for matching files (glob)
  sample <remote_file> <n> [out]   Fetch first n lines to local sample (default out=local path under data/samples)
  head <remote_file> [n] Remote head (default 20)
  tail <remote_file> [n] Remote tail (default 20)
  grep <pattern> <remote_file>     Remote grep (case-insensitive)
  subset <remote_file> <every_k> [out]  Downsample by picking every k-th line
  stage_ft <pattern>     Build fine-tune manifest JSON (paths+sizes) for pattern into artifact/analysis/ft_manifest.json
  pull_subset <pattern> <max_bytes>  Pull only files smaller than threshold (e.g. 5M) matching pattern
  sync_sample_dir        Sync remote data/samples/ -> local data/remote_samples/ (small artifacts)
  compress <path>        Create .tar.zst on remote (returns path)
  fetch_archive <remote_tar> [local_dir]  Download archive (no auto-extract)
  rm_archive <remote_tar>  Remove remote archive
  help                   This help

Environment:
  REMOTE_DATA=$REMOTE_DATA
  LOCAL_DATA=$LOCAL_DATA (only receives curated samples)

SAFE DEFAULTS: No destructive operations provided.
EOF
}

cmd_list(){ remote "cd '$REMOTE_DATA/${1:-}' 2>/dev/null && ls -1A" || err "Path missing"; }
cmd_tree(){ remote "cd '$REMOTE_DATA/${1:-}' 2>/dev/null && find . -maxdepth 2 -type f | head -200" || err "Path missing"; }
cmd_sizes(){ remote "cd '$REMOTE_DATA/${1:-}' 2>/dev/null && find . -maxdepth 4 -type f -printf '%s %P\n' | sort -nr | head -20 | awk '{printf "%.2f MB\t%s\n", $1/1024/1024, $2}'"; }
cmd_stats(){ [ -z "${1:-}" ] && { err "pattern required"; exit 1; }; remote "cd '$REMOTE_DATA' && for f in $(echo $1); do [ -f \"$f\" ] && printf '%s|%s|%s\n' \"$f\" \"$(stat -c %s \"$f\")\" \"$(wc -l < \"$f\")\"; done" | column -t -s'|'; }
cmd_sample(){ remote_file="$1"; n="${2:-50}"; out="${3:-data/samples/$(basename "$remote_file").sample}"; mkdir -p "$(dirname "$out")"; remote "head -n $n '$REMOTE_DATA/$remote_file'" > "$out" && log "Sample saved -> $out"; }
cmd_head(){ remote_file="$1"; n="${2:-20}"; remote "head -n $n '$REMOTE_DATA/$remote_file'"; }
cmd_tail(){ remote_file="$1"; n="${2:-20}"; remote "tail -n $n '$REMOTE_DATA/$remote_file'"; }
cmd_grep(){ pattern="$1"; file="$2"; remote "grep -i --color=never -n '$pattern' '$REMOTE_DATA/$file' | head -100"; }
cmd_subset(){ src="$1"; k="$2"; out="${3:-data/samples/$(basename "$src").every${k}}"; mkdir -p "$(dirname "$out")"; remote "awk 'NR==1||NR % $k==0' '$REMOTE_DATA/$src' | head -50000" > "$out"; log "Subset saved -> $out"; }
cmd_stage_ft(){
  pattern="$1"
  manifest="artifact/analysis/ft_manifest.json"
  mkdir -p artifact/analysis
  tmp=$(mktemp)
  remote "cd '$REMOTE_DATA' && for f in $(echo $pattern); do [ -f \"$f\" ] && echo \"$f\"; done" > "$tmp"
  export REMOTE_DATA_PATH="$REMOTE_DATA"
  export TMP_FILE="$tmp"
  export MANIFEST_PATH="$manifest"
  export REMOTE_USER
  export REMOTE_HOST
  if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
  else
  PYTHON_BIN=python
  fi
  "$PYTHON_BIN" <<'PY'
import json, os, subprocess, sys
root = os.environ.get('REMOTE_DATA_PATH')
tmp_path = os.environ.get('TMP_FILE')
manifest = os.environ.get('MANIFEST_PATH')
remote_user = os.environ.get('REMOTE_USER')
remote_host = os.environ.get('REMOTE_HOST')
items = []
try:
  with open(tmp_path) as fh:
    for line in fh:
      p = line.strip()
      if not p:
        continue
      try:
        sz = subprocess.check_output([
          'ssh', f'{remote_user}@{remote_host}', f'stat -c %s {root}/{p}'
        ]).decode().strip()
        lines = subprocess.check_output([
          'ssh', f'{remote_user}@{remote_host}', f'wc -l < {root}/{p}'
        ]).decode().strip()
        items.append({'path': p, 'bytes': int(sz), 'lines': int(lines)})
      except Exception:
        pass
  out = {'remote_root': root, 'files': items}
  with open(manifest, 'w') as f:
    json.dump(out, f, indent=2)
  print('Manifest written', manifest, 'files:', len(items))
except FileNotFoundError:
  print('Temp file missing', file=sys.stderr)
PY
  rm "$tmp" || true
}
cmd_pull_subset(){ pattern="$1"; maxb="$2"; remote "cd '$REMOTE_DATA' && for f in $(echo $pattern); do [ -f \"$f\" ] && s=$(stat -c %s \"$f\") && [ $s -le $maxb ] && echo $f; done" | while read -r f; do mkdir -p "data/remote_subsets/$(dirname "$f")"; rsync -az "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DATA/$f" "data/remote_subsets/$f"; done; log "Pulled subsets under size $maxb"; }
cmd_sync_sample_dir(){ mkdir -p data/remote_samples; rsync -az --delete "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DATA/samples/" data/remote_samples/ 2>/dev/null || warn "No remote samples dir"; }
cmd_compress(){ path="$1"; base=$(basename "$path"); remote "cd '$REMOTE_ROOT' && tar -I 'zstd -T0 -19' -cf ${base}.tar.zst '$path' && echo ${base}.tar.zst"; }
cmd_fetch_archive(){ arc="$1"; dest="${2:-archives}"; mkdir -p "$dest"; rsync -az "$REMOTE_USER@$REMOTE_HOST:$REMOTE_ROOT/$arc" "$dest/" && log "Fetched -> $dest/$arc"; }
cmd_rm_archive(){ arc="$1"; remote "rm -f '$REMOTE_ROOT/$arc'" && log "Removed remote archive $arc"; }

main(){
  cmd="${1:-help}"; shift || true
  require_ssh
  case "$cmd" in
    list) cmd_list "$@";;
    tree) cmd_tree "$@";;
    sizes) cmd_sizes "$@";;
    stats) cmd_stats "$@";;
    sample) cmd_sample "$@";;
    head) cmd_head "$@";;
    tail) cmd_tail "$@";;
    grep) cmd_grep "$@";;
    subset) cmd_subset "$@";;
    stage_ft) cmd_stage_ft "$@";;
    pull_subset) cmd_pull_subset "$@";;
    sync_sample_dir) cmd_sync_sample_dir "$@";;
    compress) cmd_compress "$@";;
    fetch_archive) cmd_fetch_archive "$@";;
    rm_archive) cmd_rm_archive "$@";;
    help|--help|-h) usage;;
    *) err "Unknown command: $cmd"; usage; exit 1;;
  esac
}

main "$@"
