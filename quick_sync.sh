#!/bin/bash

# Quick sync aliases for common operations
# Source this file to get convenient aliases: source quick_sync.sh

alias zpush='./sync.sh push'
alias zpull='./sync.sh pull'
alias zsync='./sync.sh sync'
alias zmount='./sync.sh mount'
alias zumount='./sync.sh umount'
alias zstatus='./sync.sh status'
alias zcheck='./sync.sh check'

# Quick file transfer functions
zupload() {
    if [ $# -eq 0 ]; then
        echo "Usage: zupload <file> [remote_path]"
        return 1
    fi
    local file="$1"
    local remote_path="${2:-.}"
    scp "$file" "cgbowen@beast3:/home/cgbowen/ZenGlow/$remote_path"
}

zdownload() {
    if [ $# -eq 0 ]; then
        echo "Usage: zdownload <remote_file> [local_path]"
        return 1
    fi
    local remote_file="$1"
    local local_path="${2:-.}"
    scp "cgbowen@beast3:/home/cgbowen/ZenGlow/$remote_file" "$local_path"
}

# Watch and sync (requires inotify-tools)
zwatch() {
    if ! command -v inotifywait >/dev/null 2>&1; then
        echo "inotify-tools not installed. Install with: sudo apt install inotify-tools"
        return 1
    fi

    echo "Watching for changes... (Ctrl+C to stop)"
    inotifywait -r -m -e modify,create,delete . --exclude '\.(git|pytest_cache|__pycache__|node_modules)' |
    while read path action file; do
        echo "$(date +'%H:%M:%S') $action $path$file"
        ./sync.sh push >/dev/null 2>&1 &
    done
}

echo "ZenGlow quick sync aliases loaded!"
echo "Available commands:"
echo "  zpush    - Push local changes to remote"
echo "  zpull    - Pull remote changes to local"
echo "  zsync    - Bidirectional sync"
echo "  zmount   - Mount remote directory"
echo "  zumount  - Unmount remote directory"
echo "  zstatus  - Show sync status"
echo "  zcheck   - Check SSH connection"
echo "  zupload  - Upload single file: zupload <file> [remote_path]"
echo "  zdownload- Download single file: zdownload <remote_file> [local_path]"
echo "  zwatch   - Watch for changes and auto-sync (requires inotify-tools)"
