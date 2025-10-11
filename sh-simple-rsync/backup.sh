#!/bin/bash

# === CONFIGURATION ===
SRC="/home/yaroslav/"
DEST="/run/media/yaroslav/Seagate/BACKUP/"
SNAPSHOT_DIR="/run/media/yaroslav/Seagate/BACKUP/old_versions"
LOGFILE="rsync-backup.log"

# === CHECK IF MOUNTED ===
if ! mountpoint -q "$(dirname "$DEST")"; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Backup drive is not mounted." | tee -a "$LOGFILE"
    exit 1
fi

# === CREATE SNAPSHOT DIR ===
TODAY=$(date +%F)
BACKUP_DIR="$SNAPSHOT_DIR/$TODAY"
mkdir -p "$BACKUP_DIR"

# === RUN RSYNC ===
rsync -avh --delete \
  --backup --backup-dir="$BACKUP_DIR" \
  --exclude='.cache/' \
  --exclude='Downloads/' \
   --exclude='VirtualBox VMs/' \
  "$SRC" "$DEST" >> "$LOGFILE" 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') - Backup completed." | tee -a "$LOGFILE"