#!/bin/bash

# ZenGlow Remote CUDA Execution Script
# Execute commands on remote CUDA host (beast3) from local workspace

set -e

# Configuration
REMOTE_HOST="beast3"
REMOTE_USER="cgbowen"
REMOTE_HOME="/home/cgbowen"
REMOTE_ZENGLOW="$REMOTE_HOME/ZenGlow"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# Check SSH connection and CUDA availability
check_remote_setup() {
    info "Checking remote CUDA setup..."

    # Test SSH connection
    if ! ssh -o ConnectTimeout=5 "$REMOTE_USER@$REMOTE_HOST" "echo 'SSH OK'" >/dev/null 2>&1; then
        error "Cannot connect to $REMOTE_HOST"
        return 1
    fi

    # Check if CUDA is available
    local cuda_check
    cuda_check=$(ssh "$REMOTE_USER@$REMOTE_HOST" "nvidia-smi --query-gpu=name --format=csv,noheader,nounits" 2>/dev/null || echo "No CUDA")

    if [[ "$cuda_check" == "No CUDA" ]]; then
        warn "CUDA not detected on remote host"
        warn "Make sure NVIDIA drivers and CUDA toolkit are installed"
    else
        success "CUDA GPU detected: $cuda_check"
    fi

    # Check if ZenGlow directory exists
    if ssh "$REMOTE_USER@$REMOTE_HOST" "test -d '$REMOTE_ZENGLOW'"; then
        success "ZenGlow directory exists on remote"
    else
        warn "ZenGlow directory not found on remote"
        info "Run './sync.sh push' to sync files first"
    fi
}

# Execute command on remote host
run_remote() {
    local cmd="$*"
    if [ -z "$cmd" ]; then
        error "No command specified"
        echo "Usage: $0 run <command>"
        return 1
    fi

    info "Executing on $REMOTE_HOST: $cmd"
    echo -e "${CYAN}┌─ Remote Execution ──────────────────────────────────────${NC}"
    ssh "$REMOTE_USER@$REMOTE_HOST" "cd '$REMOTE_ZENGLOW' && $cmd"
    local exit_code=$?
    echo -e "${CYAN}└─────────────────────────────────────────────────────────${NC}"

    if [ $exit_code -eq 0 ]; then
        success "Command completed successfully"
    else
        error "Command failed with exit code $exit_code"
    fi

    return $exit_code
}

# Execute Python script on remote
run_python() {
    local script="$1"
    shift
    local args="$*"

    if [ -z "$script" ]; then
        error "No Python script specified"
        echo "Usage: $0 python <script.py> [args...]"
        return 1
    fi

    # Check if script exists locally first
    if [ ! -f "$script" ]; then
        error "Script not found locally: $script"
        return 1
    fi

    info "Running Python script on remote: $script $args"

    # Sync the script first (in case it's been modified)
    rsync -az --exclude='__pycache__' --exclude='*.pyc' "$script" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_ZENGLOW/"

    # Run on remote
    run_remote "python $(basename "$script") $args"
}

# Execute Jupyter notebook on remote
run_jupyter() {
    local port="${1:-8888}"
    local notebook="${2:-}"

    info "Starting Jupyter on remote host (port $port)"

    # Check if jupyter is installed on remote
    if ! ssh "$REMOTE_USER@$REMOTE_HOST" "which jupyter >/dev/null 2>&1"; then
        warn "Jupyter not found on remote. Installing..."
        ssh "$REMOTE_USER@$REMOTE_HOST" "pip install jupyter notebook"
    fi

    # Start Jupyter in background
    ssh -f "$REMOTE_USER@$REMOTE_HOST" "cd '$REMOTE_ZENGLOW' && jupyter notebook --no-browser --port=$port --ip=0.0.0.0"

    # Set up port forwarding
    info "Setting up SSH tunnel for Jupyter..."
    info "Access Jupyter at: http://localhost:$port"
    info "Token: $(ssh "$REMOTE_USER@$REMOTE_HOST" "jupyter notebook list" | grep -o 'token=[a-z0-9]*' | head -1)"

    # Keep tunnel open
    ssh -N -f -L "localhost:$port:localhost:$port" "$REMOTE_USER@$REMOTE_HOST"
    success "Jupyter tunnel established. Press Ctrl+C to stop."
    wait
}

# Set up SSH tunnel for any service
tunnel_service() {
    local local_port="$1"
    local remote_port="$2"
    local service_name="${3:-service}"

    if [ -z "$local_port" ] || [ -z "$remote_port" ]; then
        error "Usage: $0 tunnel <local_port> <remote_port> [service_name]"
        return 1
    fi

    info "Setting up SSH tunnel: localhost:$local_port → $REMOTE_HOST:$remote_port"

    # Kill any existing tunnel on this port
    pkill -f "ssh.*-L.*$local_port:" || true

    # Create new tunnel
    ssh -N -f -L "localhost:$local_port:localhost:$remote_port" "$REMOTE_USER@$REMOTE_HOST"

    if [ $? -eq 0 ]; then
        success "$service_name tunnel established"
        info "Access $service_name at: http://localhost:$local_port"
        info "Press Ctrl+C to stop tunnel"
        wait
    else
        error "Failed to establish tunnel"
    fi
}

# Execute training command with CUDA
run_training() {
    local script="$1"
    shift
    local args="$*"

    if [ -z "$script" ]; then
        error "No training script specified"
        echo "Usage: $0 train <script.py> [args...]"
        return 1
    fi

    info "Running CUDA training on remote: $script"

    # Set CUDA environment variables
    local cuda_cmd="export CUDA_VISIBLE_DEVICES=0 && python $script $args"

    run_remote "$cuda_cmd"
}

# Monitor remote GPU usage
monitor_gpu() {
    info "Monitoring remote GPU usage (Ctrl+C to stop)..."

    echo -e "${CYAN}┌─ GPU Monitor ──────────────────────────────────────────${NC}"
    while true; do
        ssh "$REMOTE_USER@$REMOTE_HOST" "nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits" 2>/dev/null || echo "No CUDA GPU found"
        sleep 2
        echo -e "${CYAN}─────────────────────────────────────────────────────────${NC}"
    done
}

# Show remote system info
show_remote_info() {
    info "Remote system information:"

    echo -e "${CYAN}┌─ System Info ──────────────────────────────────────────${NC}"
    ssh "$REMOTE_USER@$REMOTE_HOST" "
        echo 'Hostname: $(hostname)'
        echo 'OS: $(lsb_release -d 2>/dev/null | cut -f2 || uname -s)'
        echo 'Kernel: $(uname -r)'
        echo 'CPU: $(nproc) cores'
        echo 'Memory: $(free -h | grep '^Mem:' | awk '{print \$2}')"
        echo 'Disk: $(df -h / | tail -1 | awk '{print \$4 \" available\"}')"
        echo 'CUDA: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits 2>/dev/null || echo \"Not installed\")'
        echo 'Python: $(python --version 2>&1)'
        echo 'PyTorch: $(python -c "import torch; print(torch.__version__)" 2>/dev/null || echo "Not installed")'
    "
    echo -e "${CYAN}└─────────────────────────────────────────────────────────${NC}"
}

# Interactive remote shell
remote_shell() {
    info "Starting interactive shell on $REMOTE_HOST"
    info "Type 'exit' to return to local shell"

    ssh "$REMOTE_USER@$REMOTE_HOST"
}

# Setup VS Code remote development
setup_vscode_remote() {
    info "Setting up VS Code Remote SSH configuration..."

    local config_dir="$HOME/.vscode-remote"
    mkdir -p "$config_dir"

    # Create VS Code settings for remote
    cat > "$config_dir/settings.json" << EOF
{
    "remote.SSH.configFile": "~/.ssh/config",
    "remote.SSH.remotePlatform": {
        "beast3": "linux"
    },
    "python.defaultInterpreterPath": "python",
    "python.terminal.activateEnvironment": true
}
EOF

    success "VS Code remote configuration created"
    info "In VS Code:"
    info "1. Install 'Remote SSH' extension"
    info "2. Cmd+Shift+P → 'Remote-SSH: Connect to Host'"
    info "3. Select 'beast3'"
    info "4. Open folder: $REMOTE_ZENGLOW"
}

# Main script logic
case "${1:-help}" in
    check)
        check_remote_setup
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
    jupyter)
        shift
        run_jupyter "$@"
        ;;
    tunnel)
        shift
        tunnel_service "$@"
        ;;
    monitor)
        monitor_gpu
        ;;
    info)
        show_remote_info
        ;;
    shell)
        remote_shell
        ;;
    vscode)
        setup_vscode_remote
        ;;
    help|--help|-h)
        echo "ZenGlow Remote CUDA Execution Tool"
        echo ""
        echo "USAGE:"
        echo "    \$0 <COMMAND> [OPTIONS]"
        echo ""
        echo "COMMANDS:"
        echo "    check           Check remote CUDA setup and connection"
        echo "    run <cmd>       Execute command on remote host"
        echo "    python <script> Run Python script on remote with CUDA"
        echo "    train <script>  Run training script with CUDA acceleration"
        echo "    jupyter [port]  Start Jupyter notebook on remote (default port 8888)"
        echo "    tunnel <lport> <rport> [name]  Create SSH tunnel for service"
        echo "    monitor         Monitor remote GPU usage in real-time"
        echo "    info            Show remote system information"
        echo "    shell           Start interactive shell on remote host"
        echo "    vscode          Setup VS Code remote development configuration"
        echo "    help            Show this help message"
        echo ""
        echo "EXAMPLES:"
        echo "    \$0 check                           # Check remote setup"
        echo "    \$0 run \"nvidia-smi\"               # Run nvidia-smi on remote"
        echo "    \$0 python train_model.py --gpu 0  # Run Python script with CUDA"
        echo "    \$0 train train.py --epochs 10     # Run training with CUDA"
        echo "    \$0 jupyter 8889                   # Start Jupyter on port 8889"
        echo "    \$0 tunnel 8080 8080 tensorboard   # Tunnel TensorBoard"
        echo "    \$0 monitor                        # Monitor GPU usage"
        echo "    \$0 info                           # Show system info"
        echo "    \$0 shell                          # Interactive shell"
        echo "    \$0 vscode                         # Setup VS Code remote"
        echo ""
        echo "SHORTCUTS:"
        echo "    Create alias: alias cuda='./remote_cuda.sh'"
        echo "    Then use: cuda run 'python -c \"import torch; print(torch.cuda.is_available())\"'"
        echo ""
        echo "NOTES:"
        echo "    - All commands execute in the remote ZenGlow directory"
        echo "    - CUDA environment variables are automatically set for training"
        echo "    - Use './sync.sh push' to sync local changes before running"
        echo "    - For long-running processes, use 'nohup' or background execution"
        ;;
    *)
        error "Unknown command: $1"
        echo ""
        $0 help
        exit 1
        ;;
esac
