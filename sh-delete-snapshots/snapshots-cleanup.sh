#!/bin/bash
set -e

# Default mode is dry run
DRY_RUN=true
KEEP_COUNT=3

usage() {
    echo "Usage: $0 [--dry-run|--live] [--keep COUNT]"
    echo "  --dry-run    Show what would be deleted without actually deleting (default)"
    echo "  --live       Actually delete the snapshots"
    echo "  --keep       Number of most recent snapshots to keep per volume (default: $KEEP_COUNT)"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --keep 5                              # Dry run with keeping 5 most recent snapshots"
    echo "  $0 --dry-run --keep 5                    # Dry run with keeping 5 most recent snapshots"
    echo "  $0 --live keep 5                         # Live mode with keeping 5 most recent snapshots"
    echo "  $0                                       # Use default values (dry run, 5 most recent snapshots)"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --live)
            DRY_RUN=false
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --keep)
            if [[ -n $2 && $2 =~ ^[0-9]+$ ]]; then
             KEEP_COUNT="$2"
             shift 2
            else
              echo "Error: --keep requires a numeric value"
              exit 1
            fi
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Display current mode
echo "========================================"
if [ "$DRY_RUN" = true ]; then
    echo "=== DRY RUN MODE - No snapshots will be deleted ==="
    echo "Use --live flag to actually delete snapshots"
else
    echo "=== LIVE MODE - Snapshots will be permanently deleted ==="
    echo "Press Ctrl+C within 5 seconds to cancel..."
    sleep 5
fi
echo "Keeping $KEEP_COUNT most recent snapshots per volume"
echo "========================================"
echo ""

# Get the Volume ids - Unique!
volumeids=($(aws ec2 describe-snapshots --owner-ids self --query "sort_by(Snapshots, &VolumeId)[*].[VolumeId]" --output text | sort -u))

echo "Found ${#volumeids[@]} unique volume(s)"
echo ""

# Loop each Volume ID
for volumeid in "${volumeids[@]}"; do
    echo "Processing Volume: $volumeid"
    
    # Get the Snapshot ids associated with the Volume id and store them in an array, bypassing 3 newest snapshots
    snapshotids=($(aws ec2 describe-snapshots --owner-ids self --filters Name=volume-id,Values="$volumeid" --query "sort_by(Snapshots, &StartTime)[:-${KEEP_COUNT}].[SnapshotId]" --output text))
    
    if [ ${#snapshotids[@]} -eq 0 ]; then
        echo "  No snapshots to delete (keeping $KEEP_COUNT most recent)"
    else
        echo "  Found ${#snapshotids[@]} snapshot(s) to delete (keeping $KEEP_COUNT most recent)"
        
        # Delete/Show Snapshot ID
        for snap in "${snapshotids[@]}"; do
            if [ "$DRY_RUN" = true ]; then
                echo "  Checking if snapshot $snap is not associated with any AMI..."
                # Check if the snapshot is associated with any AMI
                associated_ami=$(aws ec2 describe-images --filters "Name=block-device-mapping.snapshot-id,Values=$snap" --query "Images[0].ImageId" --output text)
                if [ "$associated_ami" != "None" ]; then
                    echo "  Snapshot $snap is associated with AMI: $associated_ami"
                    echo "  Skipping deletion of snapshot $snap"
                    continue
                fi
                echo "  [DRY RUN] Would delete snapshot: $snap"
            else
                echo "  Checking if snapshot $snap is not associated with any AMI..."
                # Check if the snapshot is associated with any AMI
                associated_ami=$(aws ec2 describe-images --filters "Name=block-device-mapping.snapshot-id,Values=$snap" --query "Images[0].ImageId" --output text)
                if [ "$associated_ami" != "None" ]; then
                    echo "  Snapshot $snap is associated with AMI: $associated_ami"
                    echo "  Skipping deletion of snapshot $snap"
                    continue
                fi
                echo "  Deleting snapshot: $snap"
                aws ec2 delete-snapshot --snapshot-id "$snap"
                echo "  Successfully deleted: $snap"
            fi
        done
    fi
    echo ""
done

if [ "$DRY_RUN" = true ]; then
    echo "=== DRY RUN COMPLETED ==="
    echo "No snapshots were actually deleted."
    echo "Run with --live flag to perform actual deletions."
else
    echo "=== CLEANUP COMPLETED ==="
    echo "All specified snapshots have been deleted."
fi