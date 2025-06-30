# ASG Management Script

Manages AWS Auto Scaling Group capacity for ECS cluster.

## Usage

```bash
./script.sh <desired_capacity>
```

- `0` - Disables ASG (sets min/max/desired to 0)
- `>0` - Sets desired capacity, waits for healthy containers

## Configuration

Set via environment variables or uses defaults:

| Variable | Default | Description |
|----------|---------|-------------|
| `AWS_PROFILE` | AWS CLI profile |
| `ASG_NAME` | Auto Scaling Group name |
| `CLUSTER_NAME` | ECS cluster name |
| `ID` | Task identifier |

## Examples

```bash
# Use defaults
./script.sh 2

# Override environment
AWS_PROFILE="prod" ASG_NAME="prod-asg" ./script.sh 1

# Disable ASG
./script.sh 0
```

## Requirements

- AWS CLI configured
- Appropriate IAM permissions for ASG and ECS operations