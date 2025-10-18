#!/bin/bash

# === CONFIGURATION ===
SRC="/home/my-username/"
DEST="/run/media/my-username/Seagate/BACKUP-home-my-username/"
SNAPSHOT_DIR="/run/media/my-username/Seagate/BACKUP-home-my-username/old_versions"
TODAY=$(date +%F)
LOGFILE="rsync-backup-$TODAY.log"

# === CHECK IF MOUNTED ===
if ! mountpoint -q "$(dirname "$DEST")"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Backup drive is not mounted." | tee -a "$LOGFILE"
    exit 1
fi

# === CREATE SNAPSHOT DIR ===
BACKUP_DIR="$SNAPSHOT_DIR/$TODAY"
mkdir -p "$BACKUP_DIR"

# === RUN RSYNC ===
rsync -avh --delete \
  --backup --backup-dir="$BACKUP_DIR" \
  --exclude='.cache/' \
  --exclude='old_versions' \
  --exclude='Downloads/' \
   --exclude='VirtualBox VMs/' \
  "$SRC" "$DEST" >> "$LOGFILE" 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') - Backup completed." | tee -a "$LOGFILE"
