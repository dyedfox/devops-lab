# AWS Cleanup Scripts

### 1. Snapshot Cleanup (`snapshot-cleanup.sh`)
Deletes old EBS snapshots while keeping recent ones per volume.

**Usage:**
```bash
./snapshot-cleanup.sh [--dry-run|--live] [--keep COUNT]
```

**Options:**
- `--dry-run` - Preview mode (default)
- `--live` - Actually delete snapshots
- `--keep N` - Keep N most recent snapshots per volume (default: 3)

### 2. AMI Cleanup (`ami-cleanup.sh`)
Deregisters old AMIs and associated snapshots by prefix.

**Usage:**
```bash
./ami-cleanup.sh [--dry-run|--live] [--keep COUNT] [PREFIXES...]
```

**Options:**
- `--dry-run` - Preview mode (default)
- `--live` - Actually deregister AMIs
- `--keep N` - Keep N most recent AMIs per prefix (default: 10)
- Default prefixes: `api-v2-`, `me-worker-`

## Safety Features

- **Dry run by default** - All scripts preview changes before execution
- **AMI protection** - Snapshots skip deletion if associated with AMIs
- **Default exclusion** - AMIs tagged with `@default` are excluded
- **Confirmation delays** - Live mode includes safety pauses

## Examples

```bash
# Scale ASG to 2 instances
./asg-script.sh 2

# Preview snapshot cleanup, keep 5 per volume
./snapshot-cleanup.sh --keep 5

# Actually clean AMIs, keep 3 most recent
./ami-cleanup.sh --live --keep 3 api-v2- worker-

# Disable ASG
./asg-script.sh 0
```

## Requirements

- AWS CLI configured with appropriate permissions
- IAM permissions for EC2, ASG, and ECS operations