#!/usr/bin/env bash
# Storage / ZFS validation helper.
# Safe (read-only) by default. To attempt pool creation set:
#   CREATE_POOL=1 ZPOOL_NAME=tank ZPOOL_DISK=/dev/sdX bash storage_validate.sh
# To create dataset for ollama models after pool exists:
#   CREATE_DATASET=1 DATASET=tank/ollama bash storage_validate.sh
set -euo pipefail

echo '[storage] Host:' $(hostname)
echo '[storage] Date:' $(date -Iseconds)

echo '\n[storage] Block devices (lsblk)' ; lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE | sed 's/^/  /'
echo '\n[storage] Filesystems (df -h | head)' ; df -h | head -n 20 | sed 's/^/  /'

if command -v zpool >/dev/null 2>&1; then
  echo '\n[storage] Existing ZFS pools (zpool status -x || true)'; zpool status -x || true
  echo '\n[storage] zpool list'; zpool list || true
  echo '\n[storage] zfs list (top)'; zfs list | head -n 30 || true
else
  echo '\n[storage] ZFS tools not installed (install: sudo apt-get install -y zfsutils-linux)'
fi

if [[ "${CREATE_POOL:-0}" == "1" ]]; then
  : "${ZPOOL_NAME:?Set ZPOOL_NAME}" ; : "${ZPOOL_DISK:?Set ZPOOL_DISK (e.g., /dev/sdb)}"
  echo "\n[storage] Creating pool $ZPOOL_NAME on $ZPOOL_DISK (force)"
  sudo zpool create -f "$ZPOOL_NAME" "$ZPOOL_DISK" || { echo '[storage] Pool creation failed'; exit 1; }
fi

if [[ "${CREATE_DATASET:-0}" == "1" ]]; then
  : "${DATASET:?Set DATASET (e.g., tank/ollama)}"
  if command -v zfs >/dev/null 2>&1; then
    if zfs list "$DATASET" >/dev/null 2>&1; then
      echo "[storage] Dataset $DATASET already exists"
    else
      echo "[storage] Creating dataset $DATASET (compression=zstd)"
      sudo zfs create -o compression=zstd -o atime=off "$DATASET" || { echo '[storage] Dataset creation failed'; exit 1; }
    fi
  else
    echo '[storage] Cannot create dataset; zfs not installed'
  fi
fi

echo '\n[storage] Candidate free disks (TYPE=disk, no mountpoint)'
lsblk -ndo NAME,TYPE,MOUNTPOINT,SIZE | awk '$2=="disk" && $3=="" {print "  /dev/"$1" "$4}' || true

echo '\n[storage] Done.'
