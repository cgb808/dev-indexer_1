# ZenGlow Remote CUDA Development Guide

This guide covers how to leverage CUDA GPUs on the remote host (beast3) from
your local development environment.

## Quick Start

### 1. Load CUDA Aliases

```bash
source cuda_aliases.sh
```

### 2. Test Remote Setup

```bash
cudacheck          # Check connection and CUDA availability
cudatest           # Test PyTorch CUDA setup
cudagpu           # Show GPU information
```

### 3. Run Commands Remotely

```bash
cudarun "nvidia-smi"                    # Run any command
cudapy train_model.py --gpu 0           # Run Python script
cudatrain train.py --epochs 10          # Run training with CUDA
```

## Remote Command Execution

### Basic Usage

**Execute any command on remote:**

```bash
./remote_cuda.sh run "command here"
# Or with alias:
cudarun "command here"
```

**Run Python scripts:**

```bash
./remote_cuda.sh python script.py arg1 arg2
# Or:
cudapy script.py arg1 arg2
```

**Run training scripts:**

```bash
./remote_cuda.sh train train.py --batch-size 32
# Or:
cudatrain train.py --batch-size 32
```

### Examples

```bash
# Check GPU status
cudarun "nvidia-smi"

# Test PyTorch CUDA
cudatest

# Run a specific script
cudapy fine_tuning/training/train_tiny_tool_controller.py

# Start Jupyter notebook
cudajup 8889

# Monitor GPU usage
cudamonitor

# Get system information
cudainfo
```

## VS Code Remote Development

### Setup

1. **Install VS Code Extension:**
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Remote SSH"
   - Install `ms-vscode-remote.remote-ssh`

2. **Connect to Remote:**
   - Press `F1` or `Ctrl+Shift+P`
   - Type "Remote-SSH: Connect to Host"
   - Select `beast3` from the list
   - Choose the platform (Linux)

3. **Open Remote Folder:**
   - Once connected, open the ZenGlow directory: `/home/cgbowen/ZenGlow`
   - All your files will be available with full IDE features

### Benefits

- **Full IDE Experience:** Code completion, debugging, linting
- **Local-like Performance:** Extensions run on remote host
- **GPU Access:** Direct access to CUDA GPUs
- **Environment Consistency:** Use remote Python environment

## SSH Tunneling for Services

### Common Services

**TensorBoard:**

```bash
# Start TensorBoard on remote
cudarun "tensorboard --logdir ./logs --port 6006"

# Create tunnel
cudatunnel 6006 6006 tensorboard
# Access at: http://localhost:6006
```

**MLflow:**

```bash
# Start MLflow on remote
cudarun "mlflow ui --port 5000"

# Create tunnel
cudatunnel 5000 5000 mlflow
# Access at: http://localhost:5000
```

**Jupyter Notebook:**

```bash
# Start Jupyter
cudajup 8888
# Access at: http://localhost:8888
```

**Custom Service:**

```bash
cudatunnel <local_port> <remote_port> <service_name>
```

## Development Workflow

### 1. Sync and Develop

**Option A: File Sync Approach**

```bash
# Edit locally
code some_script.py

# Sync to remote
./sync.sh push

# Run on remote
cudapy some_script.py
```

**Option B: Remote Development**

```bash
# Connect VS Code to remote
# Edit and run directly on remote
# Files stay in sync automatically
```

### 2. Training Workflow

```bash
# Prepare training script locally
code train_model.py

# Sync to remote
./sync.sh push

# Run training with CUDA
cudatrain train_model.py --gpu 0 --epochs 100

# Monitor progress
cudamonitor
```

### 3. Interactive Development

```bash
# Start remote shell
cudashell

# Or run commands interactively
cudarun "python -c 'import torch; print(torch.cuda.is_available())'"
```

## GPU Management

### Monitor GPU Usage

```bash
# Real-time monitoring
cudamonitor

# Quick GPU status
cudagpu

# GPU temperature
cudatemp

# Memory usage
gpu_memory
```

### Multi-GPU Support

```bash
# Use specific GPU
cudarun "CUDA_VISIBLE_DEVICES=0 python train.py"

# Use multiple GPUs
cudarun "CUDA_VISIBLE_DEVICES=0,1 python -m torch.distributed.launch --nproc_per_node=2 train.py"
```

## Environment Management

### Python Environments

```bash
# Create conda environment on remote
cudarun "conda create -n myenv python=3.10 -y"
cudarun "conda activate myenv && pip install torch torchvision"

# Use specific environment
cudarun "conda activate myenv && python train.py"
```

### Dependencies

```bash
# Install requirements on remote
cudarun "pip install -r requirements.txt"

# Install specific packages
cudarun "pip install torch==2.0.0 torchvision --index-url https://download.pytorch.org/whl/cu118"
```

## Advanced Features

### Background Processes

```bash
# Run long training in background
cudarun "nohup python train.py > train.log 2>&1 &"

# Check running processes
cudarun "ps aux | grep python"

# Kill process
cudarun "pkill -f train.py"
```

### File Synchronization

```bash
# Sync before running
sync_and_run "python train.py"

# Sync specific files
rsync -avz train.py cgbowen@beast3:/home/cgbowen/ZenGlow/
```

### Port Forwarding

```bash
# Forward multiple ports
ssh -L 8888:localhost:8888 -L 6006:localhost:6006 cgbowen@beast3

# Use tmux for persistent sessions
cudarun "tmux new -s training"
cudarun "tmux attach -t training"
```

## Troubleshooting

### Connection Issues

```bash
# Test connection
cudacheck

# Check SSH config
cat ~/.ssh/config

# Test SSH manually
ssh cgbowen@beast3
```

### CUDA Issues

```bash
# Check CUDA installation
cudarun "nvcc --version"
cudarun "nvidia-smi"

# Test PyTorch CUDA
cudatest

# Check GPU memory
cudarun "nvidia-smi --query-gpu=memory.used,memory.free --format=csv"
```

### Performance Issues

```bash
# Check network speed
./sync.sh check

# Use compression for transfers
rsync -avz --compress-level=9 large_file.dat cgbowen@beast3:/home/cgbowen/ZenGlow/

# Monitor transfer progress
rsync -avz --progress large_file.dat cgbowen@beast3:/home/cgbowen/ZenGlow/
```

## Integration Examples

### PyTorch Training

```python
# train.py
import torch
import torch.nn as nn

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Your training code here
model = nn.Linear(10, 1).to(device)
# ... training loop
```

Run with:

```bash
cudapy train.py
```

### TensorFlow/Keras

```python
# train_tf.py
import tensorflow as tf

print("GPU Available:", tf.config.list_physical_devices('GPU'))

# Your TensorFlow code here
with tf.device('/GPU:0'):
    # ... training code
```

Run with:

```bash
cudapy train_tf.py
```

### Jupyter Notebook

```bash
# Start Jupyter on remote
cudajup 8888

# In notebook, check GPU:
import torch
print(torch.cuda.is_available())
print(torch.cuda.device_count())
```

## Best Practices

1. **Sync Before Running:** Always sync your latest changes before running on
   remote
2. **Use Aliases:** Load `cuda_aliases.sh` for convenient commands
3. **Monitor Resources:** Use `cudamonitor` to track GPU usage
4. **Background Processes:** Use `nohup` or `tmux` for long-running tasks
5. **Version Control:** Keep track of which version is running on remote
6. **Environment Consistency:** Ensure remote environment matches local setup

## Security Notes

- SSH keys are used for authentication (no passwords in scripts)
- All connections are encrypted via SSH
- Remote access is limited to configured user account
- GPU access is controlled by remote host permissions

This setup provides seamless access to CUDA GPUs while maintaining your local
development workflow!
