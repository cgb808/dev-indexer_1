#!/bin/bash

# ZenGlow Remote CUDA Execution Script
# Execute commands on remote CUDA host (beast3) from local workspace

REMOTE_HOST="beast3"
REMOTE_USER="cgbowen"
REMOTE_ZENGLOW="/home/cgbowen/ZenGlow"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}" >&2; }
warn() { echo -e "${YELLOW}[WARNING] $1${NC}"; }

check_connection() {
    log "Checking SSH connection to $REMOTE_HOST..."
    if ssh -o ConnectTimeout=5 "$REMOTE_USER@$REMOTE_HOST" "echo 'SSH OK'" >/dev/null 2>&1; then
        log "SSH connection successful"
        return 0
    else
        error "Cannot connect to $REMOTE_HOST"
        return 1
    fi
}

run_remote() {
    local cmd="$*"
    if [ -z "$cmd" ]; then
        error "No command specified"
        return 1
    fi

    log "Executing on $REMOTE_HOST: $cmd"
    echo -e "${BLUE}┌─ Remote Execution ──────────────────────────────────────${NC}"
    ssh "$REMOTE_USER@$REMOTE_HOST" "cd '$REMOTE_ZENGLOW' && $cmd"
    local exit_code=$?
    echo -e "${BLUE}└─────────────────────────────────────────────────────────${NC}"

    if [ $exit_code -eq 0 ]; then
        log "Command completed successfully"
    else
        error "Command failed with exit code $exit_code"
    fi
    return $exit_code
}

run_python() {
    local script="$1"
    shift
    local args="$*"

    if [ -z "$script" ]; then
        error "No Python script specified"
        return 1
    fi

    if [ ! -f "$script" ]; then
        error "Script not found: $script"
        return 1
    fi

    log "Running Python script: $script $args"
    rsync -az "$script" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_ZENGLOW/" 2>/dev/null || true
    run_remote "python $(basename "$script") $args"
}

run_training() {
    local script="$1"
    shift
    local args="$*"

    if [ -z "$script" ]; then
        error "No training script specified"
        return 1
    fi

    log "Running CUDA training: $script"
    run_remote "CUDA_VISIBLE_DEVICES=0 python $script $args"
}

show_info() {
    log "Remote system information:"
    echo -e "${BLUE}┌─ System Info ──────────────────────────────────────────${NC}"
    ssh "$REMOTE_USER@$REMOTE_HOST" "
        echo 'Hostname: $(hostname)'
        echo 'OS: $(lsb_release -d 2>/dev/null | cut -f2 || uname -s)'
        echo 'Kernel: $(uname -r)'
        echo 'CPU: $(nproc) cores'
        echo 'Memory: $(free -h | grep \"^Mem:\" | awk \"{print \\\$2}\") total'
        echo 'CUDA: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits 2>/dev/null || echo \"Not installed\")'
        echo 'Python: $(python --version 2>&1)'
    "
    echo -e "${BLUE}└─────────────────────────────────────────────────────────${NC}"
}

case "${1:-help}" in
    check)
        check_connection
        ;;
    run)
        shift
        run_remote "$@"
        ;;
    python)
        shift
        run_python "$@"
        ;;
    train)
        shift
        run_training "$@"
        ;;
    info)
        show_info
        ;;
    help|--help|-h)
        echo "ZenGlow Remote CUDA Execution Tool"
        echo ""
        echo "USAGE: $0 <COMMAND> [OPTIONS]"
        echo ""
        echo "COMMANDS:"
        echo "  check           Check SSH connection"
        echo "  run <cmd>       Execute command on remote"
        echo "  python <script> Run Python script with CUDA"
        echo "  train <script>  Run training script with CUDA"
        echo "  info            Show remote system info"
        echo "  help            Show this help"
        echo ""
        echo "EXAMPLES:"
        echo "  $0 check"
        echo "  $0 run 'nvidia-smi'"
        echo "  $0 python train.py --epochs 10"
        echo "  $0 train train.py --gpu 0"
        ;;
    *)
        error "Unknown command: $1"
        $0 help
        exit 1
        ;;
esac
