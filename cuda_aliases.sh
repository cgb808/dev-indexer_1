#!/bin/bash

# Quick CUDA command aliases
# Source this file to get convenient aliases: source cuda_aliases.sh

alias cuda='./remote_cuda.sh'
alias cudacheck='cuda check'
alias cudarun='cuda run'
alias cudapy='cuda python'
alias cudatrain='cuda train'
alias cudajup='cuda jupyter'
alias cudatunnel='cuda tunnel'
alias cudamonitor='cuda monitor'
alias cudainfo='cuda info'
alias cudashell='cuda shell'

# Common CUDA operations
cudatest() {
    cuda run "python -c 'import torch; print(f\"PyTorch: {torch.__version__}\"); print(f\"CUDA available: {torch.cuda.is_available()}\"); print(f\"GPU count: {torch.cuda.device_count()}\"); print(f\"Current GPU: {torch.cuda.current_device() if torch.cuda.is_available() else \"None\"}\")'"
}

cudagpu() {
    cuda run "nvidia-smi"
}

cudatemp() {
    cuda run "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits"
}

# Training shortcuts
train_pytorch() {
    local script="${1:-train.py}"
    shift
    cuda train "$script" "$@"
}

train_tensorflow() {
    local script="${1:-train.py}"
    shift
    cuda run "python $script $@"
}

# Jupyter shortcuts
jupyter_start() {
    local port="${1:-8888}"
    cuda jupyter "$port"
}

jupyter_list() {
    cuda run "jupyter notebook list"
}

jupyter_stop() {
    cuda run "pkill -f jupyter"
}

# Development shortcuts
sync_and_run() {
    local cmd="$*"
    echo "Syncing files to remote..."
    ./sync.sh push >/dev/null 2>&1
    echo "Running on remote: $cmd"
    cuda run "$cmd"
}

# Environment setup
setup_conda() {
    local env_name="${1:-zenglow}"
    cuda run "conda create -n $env_name python=3.10 -y 2>/dev/null || echo 'Environment $env_name already exists'"
    cuda run "conda activate $env_name"
}

# File operations
edit_remote() {
    local file="$1"
    if [ -z "$file" ]; then
        echo "Usage: edit_remote <file>"
        return 1
    fi
    # Mount remote directory and open file
    ./sync.sh mount
    code "~/remote_zenglow/$file"
}

# Port forwarding for common services
tensorboard_tunnel() {
    local port="${1:-6006}"
    cudatunnel "$port" "$port" "TensorBoard"
}

mlflow_tunnel() {
    local port="${1:-5000}"
    cudatunnel "$port" "$port" "MLflow"
}

wandb_tunnel() {
    local port="${1:-8080}"
    cudatunnel "$port" "$port" "Weights & Biases"
}

# GPU memory monitoring
gpu_memory() {
    cuda run "nvidia-smi --query-gpu=memory.used,memory.free --format=csv"
}

# Quick training status
training_status() {
    echo "=== Training Status ==="
    cudarun "ps aux | grep python | grep -v grep" | cat
    echo ""
    echo "=== GPU Usage ==="
    cudagpu | cat
}

echo "ZenGlow CUDA aliases loaded!"
echo ""
echo "Available commands:"
echo "  cuda*         - Remote CUDA operations"
echo "  cudatest      - Test PyTorch CUDA setup"
echo "  cudagpu       - Show GPU information"
echo "  train_*       - Training shortcuts"
echo "  jupyter_*     - Jupyter notebook operations"
echo "  sync_and_run  - Sync then run command"
echo "  *tunnel       - Port forwarding for services"
echo "  gpu_memory    - Show GPU memory usage"
echo "  training_status - Show training processes"
echo ""
echo "Examples:"
echo "  cudatest                    # Test CUDA setup"
echo "  train_pytorch model.py      # Run PyTorch training"
echo "  jupyter_start 8889          # Start Jupyter on port 8889"
echo "  tensorboard_tunnel 6006     # Forward TensorBoard"
echo "  sync_and_run python train.py # Sync and run training"
