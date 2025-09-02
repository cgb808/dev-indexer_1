#!/bin/bash

# ZenGlow File Transfer Scripts
# Comprehensive file synchronization between local and CUDA host (beast3)

set -e

# Configuration
REMOTE_HOST="beast3"
REMOTE_USER="cgbowen"
REMOTE_PATH="/home/cgbowen/ZenGlow"
LOCAL_PATH="/mnt/DevBuilds/ZenGlow/ZenGlow/dev-indexer_1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
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

# Check SSH connection
check_connection() {
    info "Checking SSH connection to $REMOTE_HOST..."
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$REMOTE_USER@$REMOTE_HOST" "echo 'SSH connection successful'" >/dev/null 2>&1; then
        log "SSH connection to $REMOTE_HOST is working"
        return 0
    else
        error "Cannot connect to $REMOTE_HOST via SSH"
        echo "Please ensure:"
        echo "1. SSH service is running on $REMOTE_HOST"
        echo "2. SSH key is properly configured"
        echo "3. Network connectivity is available"
        return 1
    fi
}

# Create remote directory
create_remote_dir() {
    info "Creating remote directory structure..."
    ssh "$REMOTE_USER@$REMOTE_HOST" "mkdir -p '$REMOTE_PATH'"
    log "Remote directory created: $REMOTE_PATH"
}

# Sync files from local to remote
sync_to_remote() {
    local exclude_file="$LOCAL_PATH/.sync_exclude"

    info "Syncing files from local to remote..."

    # Create exclude file if it doesn't exist
    if [ ! -f "$exclude_file" ]; then
        cat > "$exclude_file" << 'EOF'
# Exclude patterns for rsync
node_modules/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.mypy_cache/
.vscode/
.venv/
*.log
.DS_Store
Thumbs.db
*.tmp
*.swp
*.swo
.expo/
.expo-shared/
EOF
        log "Created exclude file: $exclude_file"
    fi

    # Perform rsync
    rsync -avz --delete \
        --exclude-from="$exclude_file" \
        --exclude='.git/' \
        --exclude='*.log' \
        --exclude='tmp/' \
        --exclude='.expo/' \
        --exclude='node_modules/' \
        --exclude='__pycache__/' \
        --exclude='.pytest_cache/' \
        "$LOCAL_PATH/" \
        "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/"

    log "Local → Remote sync completed"
}

# Sync files from remote to local
sync_from_remote() {
    local exclude_file="$LOCAL_PATH/.sync_exclude"

    info "Syncing files from remote to local..."

    # Perform rsync
    rsync -avz --delete \
        --exclude-from="$exclude_file" \
        --exclude='.git/' \
        --exclude='*.log' \
        --exclude='tmp/' \
        "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/" \
        "$LOCAL_PATH/"

    log "Remote → Local sync completed"
}

# Bidirectional sync
sync_bidirectional() {
    info "Performing bidirectional sync..."

    # First, backup any conflicting files
    local backup_dir="$LOCAL_PATH/.sync_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    # Use unison or rsync with careful handling
    # For now, we'll do a careful bidirectional sync
    warn "Bidirectional sync requires careful conflict resolution"

    # Sync local changes to remote
    sync_to_remote

    # Sync remote changes to local (with backup)
    rsync -avz --backup --backup-dir="$backup_dir" \
        --exclude-from="$LOCAL_PATH/.sync_exclude" \
        "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/" \
        "$LOCAL_PATH/"

    if [ "$(ls -A "$backup_dir" 2>/dev/null)" ]; then
        warn "Some files were backed up to: $backup_dir"
        warn "Please review and merge any conflicts manually"
    fi

    log "Bidirectional sync completed"
}

# Mount remote directory using SSHFS
mount_remote() {
    local mount_point="$HOME/remote_zenglow"

    info "Mounting remote directory..."

    # Create mount point if it doesn't exist
    mkdir -p "$mount_point"

    # Check if already mounted
    if mount | grep -q "$mount_point"; then
        warn "Remote directory already mounted at $mount_point"
        return 0
    fi

    # Mount using SSHFS
    sshfs "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH" "$mount_point" \
        -o reconnect \
        -o ServerAliveInterval=15 \
        -o ServerAliveCountMax=3 \
        -o follow_symlinks \
        -o allow_other

    if [ $? -eq 0 ]; then
        log "Remote directory mounted at: $mount_point"
        info "You can now access remote files as if they were local"
        info "Use 'umount $mount_point' to unmount when done"
    else
        error "Failed to mount remote directory"
        return 1
    fi
}

# Unmount remote directory
unmount_remote() {
    local mount_point="$HOME/remote_zenglow"

    info "Unmounting remote directory..."

    if mount | grep -q "$mount_point"; then
        fusermount -u "$mount_point" 2>/dev/null || umount "$mount_point" 2>/dev/null
        if [ $? -eq 0 ]; then
            log "Remote directory unmounted successfully"
        else
            error "Failed to unmount remote directory"
            return 1
        fi
    else
        warn "Remote directory is not mounted"
    fi
}

# Show usage information
usage() {
    cat << EOF
ZenGlow File Transfer Tool

USAGE:
    $0 [COMMAND]

COMMANDS:
    check           Check SSH connection to remote host
    setup           Create remote directory structure
    push            Sync local files to remote (local → remote)
    pull            Sync remote files to local (remote → local)
    sync            Bidirectional sync with conflict handling
    mount           Mount remote directory using SSHFS
    umount          Unmount remote directory
    status          Show current sync status
    help            Show this help message

EXAMPLES:
    $0 check                    # Test SSH connection
    $0 push                     # Upload local changes
    $0 pull                     # Download remote changes
    $0 sync                     # Sync both directions
    $0 mount                    # Mount remote as local directory
    $0 umount                   # Unmount remote directory

CONFIGURATION:
    Remote Host: $REMOTE_HOST ($REMOTE_USER@$REMOTE_HOST)
    Remote Path: $REMOTE_PATH
    Local Path:  $LOCAL_PATH

NOTES:
    - Ensure SSH key authentication is set up
    - Remote host should have CUDA and required dependencies
    - Use 'mount' for real-time file access
    - Use 'push/pull/sync' for batch transfers
EOF
}

# Show sync status
show_status() {
    info "=== ZenGlow Sync Status ==="
    echo "Local Path:  $LOCAL_PATH"
    echo "Remote Host: $REMOTE_HOST"
    echo "Remote Path: $REMOTE_PATH"
    echo ""

    # Check connection
    if check_connection >/dev/null 2>&1; then
        echo "SSH Connection: ${GREEN}✓ Connected${NC}"
    else
        echo "SSH Connection: ${RED}✗ Disconnected${NC}"
    fi

    # Check remote directory
    if ssh "$REMOTE_USER@$REMOTE_HOST" "test -d '$REMOTE_PATH'" 2>/dev/null; then
        echo "Remote Directory: ${GREEN}✓ Exists${NC}"
    else
        echo "Remote Directory: ${RED}✗ Missing${NC}"
    fi

    # Check mount status
    local mount_point="$HOME/remote_zenglow"
    if mount | grep -q "$mount_point" 2>/dev/null; then
        echo "SSHFS Mount: ${GREEN}✓ Mounted at $mount_point${NC}"
    else
        echo "SSHFS Mount: ${YELLOW}○ Not mounted${NC}"
    fi

    echo ""
    info "Recent local changes:"
    (cd "$LOCAL_PATH" && git status --porcelain | head -10) 2>/dev/null || echo "Not a git repository"
}

# Main script logic
case "${1:-help}" in
    check)
        check_connection
        ;;
    setup)
        check_connection && create_remote_dir
        ;;
    push)
        check_connection && sync_to_remote
        ;;
    pull)
        check_connection && sync_from_remote
        ;;
    sync)
        check_connection && sync_bidirectional
        ;;
    mount)
        check_connection && mount_remote
        ;;
    umount)
        unmount_remote
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        error "Unknown command: $1"
        echo ""
        usage
        exit 1
        ;;
esac
