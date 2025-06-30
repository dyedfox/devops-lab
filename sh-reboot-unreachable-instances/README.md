# EC2 Status Checker

Monitors EC2 instances and reboots failed ones based on status checks and CloudWatch metrics.

## Usage

```bash
./ec2-status-checker.sh [--live] [--prefix PREFIX]
```

**Options:**
- `--live` - Actually reboot instances (default: dry-run)
- `--prefix` - Instance name filter

**Examples:**
```bash
# Dry run with default prefix
./ec2-status-checker.sh

# Live mode with custom prefix
./ec2-status-checker.sh --live --prefix "stage-ftp*"
```

## How it works

1. Finds instances matching name prefix
2. Checks instance status and CloudWatch StatusCheckFailed metric (last 5 minutes)
3. Reboots instances that fail either check (in live mode)

## Requirements

- AWS CLI configured
- EC2 and CloudWatch permissions