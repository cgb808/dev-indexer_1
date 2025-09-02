#!/usr/bin/env bash
set -euo pipefail

# Multi-Repository Selective Sync Tool
# Purpose: Keep a clean, curated subset of this workspace mirrored into a second repo
# (e.g. AIWorkshop) without dragging along large data or transient artifacts.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR"
# Default manifest (can override with --manifest)
MANIFEST="$ROOT/repo_sync_manifest.txt"

# Destination repo path (clone of git@github.com:cgb808/AIWorkshop.git on desired branch)
DEST_REPO="${AIWORKSHOP_PATH:-}"  # Can export AIWORKSHOP_PATH or pass --dest/--dest
RSYNC_OPTS=("-av" "--prune-empty-dirs")

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_RESET='\033[0m'

log(){ echo -e "${COLOR_GREEN}[$(date +'%H:%M:%S')] $*${COLOR_RESET}"; }
warn(){ echo -e "${COLOR_YELLOW}[WARN] $*${COLOR_RESET}"; }
err(){ echo -e "${COLOR_RED}[ERROR] $*${COLOR_RESET}" >&2; }

need_dest() {
  if [[ -z "$DEST_REPO" ]]; then
    err "Destination repo path not set. Export AIWORKSHOP_PATH or pass --dest /path/to/AIWorkshop";
    exit 1
  fi
  if [[ ! -d "$DEST_REPO/.git" ]]; then
    err "Destination path '$DEST_REPO' is not a git repository"; exit 1; fi
}

parse_manifest() {
  local mode="" line
  INCLUDE_PATTERNS=()
  EXCLUDE_PATTERNS=()
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    if [[ "$line" == "[includes]" ]]; then mode="inc"; continue; fi
    if [[ "$line" == "[excludes]" ]]; then mode="exc"; continue; fi
    case $mode in
      inc) INCLUDE_PATTERNS+=("$line") ;;
      exc) EXCLUDE_PATTERNS+=("$line") ;;
    esac
  done < "$MANIFEST"
  if (( ${#INCLUDE_PATTERNS[@]} == 0 )); then err "No include patterns parsed"; exit 1; fi
}

build_rsync_filters() {
  RSYNC_FILTERS=()
  # Start by excluding everything, then re-include what we want
  RSYNC_FILTERS+=("--filter=- /*")
  for p in "${INCLUDE_PATTERNS[@]}"; do
    RSYNC_FILTERS+=("--filter=+ $p")
    # If it's a directory pattern (ends with /) re-include contents
    if [[ $p == */ ]]; then
      RSYNC_FILTERS+=("--filter=+ $p**")
    fi
  done
  for p in "${EXCLUDE_PATTERNS[@]}"; do
    RSYNC_FILTERS+=("--filter=- $p")
  done
}

cmd_plan() {
  need_dest; parse_manifest; build_rsync_filters
  log "Planning sync (dry-run) -> $DEST_REPO"
  rsync -ain --delete "${RSYNC_FILTERS[@]}" "${RSYNC_OPTS[@]}" "$ROOT/" "$DEST_REPO/" | sed '1,2d'
}

cmd_push() {
  need_dest; parse_manifest; build_rsync_filters
  local delete_flag="";
  if [[ "${ALLOW_DELETE:-0}" == "1" ]]; then delete_flag="--delete"; else warn "Skipping deletions (set ALLOW_DELETE=1 to enable)"; fi
  log "Pushing curated subset to $DEST_REPO"
  rsync -a "${RSYNC_FILTERS[@]}" ${delete_flag} "${RSYNC_OPTS[@]}" "$ROOT/" "$DEST_REPO/"
  log "Push complete. Review & commit in destination repo."
}

cmd_pull() {
  need_dest; parse_manifest; build_rsync_filters
  warn "Pull will copy destination files back into this workspace (only included patterns)."
  rsync -a "${RSYNC_FILTERS[@]}" "${RSYNC_OPTS[@]}" "$DEST_REPO/" "$ROOT/"
  log "Pull complete. Review changes locally."
}

cmd_diff() {
  need_dest; parse_manifest; build_rsync_filters
  log "Diff (rsync dry-run)"
  rsync -ain --delete "${RSYNC_FILTERS[@]}" "${RSYNC_OPTS[@]}" "$ROOT/" "$DEST_REPO/" | sed '1,2d'
}

cmd_status() {
  need_dest; parse_manifest
  echo "Destination: $DEST_REPO"; echo "Includes (${#INCLUDE_PATTERNS[@]}):"; printf '  %s\n' "${INCLUDE_PATTERNS[@]}"; echo "Excludes (${#EXCLUDE_PATTERNS[@]}):"; printf '  %s\n' "${EXCLUDE_PATTERNS[@]}"
  echo "Git status (destination):"; (cd "$DEST_REPO" && git status --short | head -50)
  echo "Git status (source):"; (cd "$ROOT" && git status --short | head -50 || true)
}

usage(){ cat <<EOF
Multi-Repo Selective Sync

Environment:
  AIWORKSHOP_PATH   Destination repo path (or use --dest)
  ALLOW_DELETE=1    Enable deletion in push (mirrors removals)

Commands:
  plan              Dry-run show what would change
  push              Sync curated subset to destination
  pull              Copy curated subset from destination back
  diff              Show rsync-style diff (dry-run)
  status            Show manifest & git status snapshot
  help              This help

Examples:
  AIWORKSHOP_PATH=~/dev/AIWorkshop ./multi_repo_sync.sh plan
  ALLOW_DELETE=1 AIWORKSHOP_PATH=~/dev/AIWorkshop ./multi_repo_sync.sh push
  ./multi_repo_sync.sh --dest ~/dev/AIWorkshop diff
EOF
}

# Argument parsing (simple)
ARGS=()
OVERRIDE_MANIFEST=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --dest) DEST_REPO=$2; shift 2;;
    --manifest) OVERRIDE_MANIFEST=$2; shift 2;;
    -h|--help) usage; exit 0;;
    *) ARGS+=("$1"); shift;;
  esac
done
set -- "${ARGS[@]:-}"

if [[ -n "$OVERRIDE_MANIFEST" ]]; then
  if [[ -f "$OVERRIDE_MANIFEST" ]]; then
    MANIFEST="$OVERRIDE_MANIFEST"
  elif [[ -f "$ROOT/$OVERRIDE_MANIFEST" ]]; then
    MANIFEST="$ROOT/$OVERRIDE_MANIFEST"
  else
    err "Specified manifest not found: $OVERRIDE_MANIFEST"; exit 1
  fi
fi

CMD="${1:-help}"; shift || true

if [[ ! -f "$MANIFEST" ]]; then err "Manifest not found: $MANIFEST"; exit 1; fi

case "$CMD" in
  plan)   cmd_plan ;;
  push)   cmd_push ;;
  pull)   cmd_pull ;;
  diff)   cmd_diff ;;
  status) cmd_status ;;
  help|*) usage ;;
esac
