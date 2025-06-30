#!/bin/bash
set -e

# Default values
live=0
prefix="prod worker*"

usage() {
    echo "Usage: $0 [--live] [--prefix PREFIX]"
    echo "  --live       Actually reboot instances (default: dry-run)"
    echo "  --prefix     Instance name prefix filter (default: '$prefix')"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Dry run with default prefix"
    echo "  $0 --prefix 'stage-ftp*'             # Dry run with custom prefix"
    echo "  $0 --live --prefix 'prod worker*'    # Live mode with custom prefix"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --live)
            live=1
            shift
            ;;
        --prefix)
            if [[ -n $2 ]]; then
                prefix="$2"
                shift 2
            else
                echo "Error: --prefix requires a value"
                usage
                exit 1
            fi
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

if [[ $live == 1 ]]; then
    echo ">>>> Running in LIVE MODE! Command/Ctrl+C to cancel."
else
    echo ">>>> Running in dry-run mode."
fi

echo "Using prefix filter: '$prefix'"
echo ""

# Check the EC2 instance status
check_status_instance_reach() {
    instance_id=$1
    result=$(aws ec2 describe-instance-status \
        --instance-ids $instance_id \
        --query "InstanceStatuses[0].InstanceStatus.Status" \
        --output text)
    if [ "$result" != "ok" ]; then
        return 1  # Status check failed
    else
        return 0  # Status check passed
    fi
}   

# Check the Cloudwatch metric StatusCheckFailed > 1 last 5 minutes
check_status_failed_metric() {
    instance_id=$1
    result=$(aws cloudwatch get-metric-statistics \
        --namespace AWS/EC2 \
        --metric-name StatusCheckFailed \
        --period 60 \
        --statistics Maximum \
        --dimensions Name=InstanceId,Value=$instance_id \
        --start-time $(date -u +"%Y-%m-%dT%H:%M:%SZ" -d "5 minutes ago") \
        --end-time $(date -u +"%Y-%m-%dT%H:%M:%SZ") \
        --query 'Datapoints[0].Maximum' \
        --output text)
    if [ "$result" != "0.0" ]; then
        return 1  # Status check failed
    else
        return 0  # Status check passed
    fi
}

# Get instance IDs
if ! instance_ids=$(aws ec2 describe-instances --filters "Name=tag:Name,Values='$prefix'" \
--output text --query 'Reservations[*].Instances[*].InstanceId'); then
    echo "Failed to retrieve instance IDs. Exiting."
    exit 1
fi

if [[ -z "$instance_ids" ]]; then
    echo "No instances found matching prefix: '$prefix'"
    exit 0
fi

echo "Found instances: $instance_ids"
echo ""

# If one check fails or both of them fail - reboot the instance
for id in $instance_ids; do
    if ! ( check_status_failed_metric "$id" && check_status_instance_reach "$id" ); then
        if [[ $live == 1 ]]; then
            echo "Instance $id FAILED status check. Rebooting..."
            aws ec2 reboot-instances --instance-ids "$id" || continue
            sleep 1
        else
            echo "Instance $id FAILED status check. Running in dry-run mode. Skipping..."
        fi
    else
        echo "Instance $id passed status check."
    fi
done