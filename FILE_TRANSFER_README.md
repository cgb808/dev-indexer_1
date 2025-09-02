# ZenGlow File Transfer Setup

This guide covers setting up bidirectional file synchronization between your
local ZenGlow repository and the remote CUDA host (beast3).

## Prerequisites

1. **SSH Access**: Ensure SSH key authentication is configured for `beast3`
2. **Remote Directory**: The remote host should have the ZenGlow directory
   structure
3. **Dependencies** (optional for advanced features):
   - `rsync` (usually pre-installed)
   - `sshfs` for mounting remote directories
   - `inotify-tools` for file watching

## Quick Start

### 1. Test Connection

```bash
./sync.sh check
```

### 2. Initial Setup

```bash
./sync.sh setup
```

### 3. First Sync

```bash
./sync.sh push  # Upload local files to remote
```

## Available Commands

### Main Sync Script (`./sync.sh`)

| Command  | Description                                 |
| -------- | ------------------------------------------- |
| `check`  | Test SSH connection to remote host          |
| `setup`  | Create remote directory structure           |
| `push`   | Sync local files to remote (local → remote) |
| `pull`   | Sync remote files to local (remote → local) |
| `sync`   | Bidirectional sync with conflict handling   |
| `mount`  | Mount remote directory using SSHFS          |
| `umount` | Unmount remote directory                    |
| `status` | Show current sync status                    |
| `help`   | Show detailed help                          |

### Quick Aliases (`source quick_sync.sh`)

After sourcing the quick sync file, you get convenient aliases:

```bash
source quick_sync.sh

zpush     # Push changes
zpull     # Pull changes
zsync     # Bidirectional sync
zmount    # Mount remote
zumount   # Unmount remote
zstatus   # Show status
zcheck    # Check connection
```

### Single File Operations

```bash
# Upload single file
zupload path/to/local/file.txt [remote/path/]

# Download single file
zdownload remote/path/file.txt [local/destination/]
```

## Usage Examples

### Development Workflow

1. **Start development session**:

   ```bash
   ./sync.sh check  # Verify connection
   ./sync.sh status # Check current state
   ```

2. **Push local changes to remote**:

   ```bash
   ./sync.sh push
   ```

3. **Pull latest changes from remote**:

   ```bash
   ./sync.sh pull
   ```

4. **Bidirectional sync** (use carefully):
   ```bash
   ./sync.sh sync
   ```

### Real-time File Access

For real-time access to remote files:

```bash
./sync.sh mount   # Mount remote directory
# Files now accessible at ~/remote_zenglow
cd ~/remote_zenglow
# Work with files as if they were local
./sync.sh umount  # Unmount when done
```

### Auto-sync on Changes

To automatically sync when files change:

```bash
# Install inotify-tools if needed
sudo apt install inotify-tools

# Start watching
source quick_sync.sh
zwatch
```

## Configuration

The sync behavior can be customized via `sync_config.toml`:

- **Remote settings**: Host, user, path, SSH port
- **Local settings**: Local repository path
- **SSH settings**: Key file, config file, timeouts
- **Rsync options**: Exclude patterns, transfer options
- **Mount options**: SSHFS mount point and options
- **Logging**: Log file location and verbosity

## Excluded Files

The following file types/patterns are automatically excluded from sync:

- `node_modules/` - Node.js dependencies
- `__pycache__/` - Python cache files
- `.git/` - Git repository data
- `*.log` - Log files
- `.expo/` - Expo development files
- Temporary files (`*.tmp`, `*.swp`, etc.)
- Cache directories (`.pytest_cache/`, `.ruff_cache/`, etc.)

## Troubleshooting

### Connection Issues

1. **SSH key not working**:

   ```bash
   ssh-add ~/.ssh/id_ed25519  # Add key to agent
   ssh cgbowen@beast3         # Test connection
   ```

2. **Permission denied**:
   - Ensure SSH key is in `~/.ssh/authorized_keys` on remote host
   - Check file permissions: `chmod 600 ~/.ssh/id_ed25519`

### Sync Issues

1. **Files not syncing**:

   ```bash
   ./sync.sh status  # Check connection and paths
   rsync -avzn --exclude-from=.sync_exclude ./ cgbowen@beast3:/home/cgbowen/ZenGlow/  # Dry run
   ```

2. **Permission errors**:
   - Ensure write permissions on remote directory
   - Check remote user permissions

### Mount Issues

1. **SSHFS mount fails**:

   ```bash
   sudo apt install sshfs  # Install SSHFS
   mkdir -p ~/remote_zenglow  # Create mount point
   ./sync.sh mount
   ```

2. **Mount point busy**:
   ```bash
   ./sync.sh umount
   fusermount -u ~/remote_zenglow  # Force unmount if needed
   ```

## Performance Tips

1. **Use compression**: SSH config already includes compression
2. **Connection multiplexing**: Already configured in SSH config
3. **Exclude unnecessary files**: Large directories are already excluded
4. **Batch transfers**: Use `push`/`pull` for multiple files
5. **Mount for frequent access**: Use `mount` for real-time file access

## Security Notes

- SSH keys are used for authentication (no passwords)
- All transfers are encrypted via SSH
- File permissions are preserved during transfer
- Remote host access is restricted to configured user

## Integration with Development

### VS Code Integration

You can add VS Code tasks for sync operations by adding to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Push to Remote",
      "type": "shell",
      "command": "./sync.sh push",
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    }
  ]
}
```

### Git Integration

Consider adding sync scripts to git hooks for automatic sync on commits:

```bash
# .git/hooks/post-commit
#!/bin/bash
./sync.sh push  # Auto-push after commits
```

## Monitoring

Check sync logs at `~/.zenglow_sync.log` for detailed operation history.

## Support

If you encounter issues:

1. Run `./sync.sh status` to check current state
2. Verify SSH connection: `./sync.sh check`
3. Check logs for error details
4. Ensure remote host is accessible and has required permissions
