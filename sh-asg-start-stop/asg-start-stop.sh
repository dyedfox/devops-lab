#!/bin/bash

# Get configuration from environment variables with fallbacks
AWS_PROFILE="${AWS_PROFILE:-stage-terraform}"
ASG_NAME="${ASG_NAME:-stage-ecs-ai-models-asg-20240926173123093800000004}"
CLUSTER_NAME="${CLUSTER_NAME:-stage-ai-cluster}"
ID="${ID:-160614412378}"

usage() {
    echo "Usage: $0 <desired_capacity>"
    echo " desired_capacity: A number >= 0"
    echo " 0 will set min and max to 0, disabling the ASG"
    echo " Any number > 0 will set desired capacity and update min/max"
    echo ""
    echo "Environment variables (with current values):"
    echo " AWS_PROFILE=$AWS_PROFILE"
    echo " ASG_NAME=$ASG_NAME"
    echo " CLUSTER_NAME=$CLUSTER_NAME"
    echo " ID=$ID"
}

update_asg() {
    local desired=$1
    local min=$2
    local max=$3
    
    aws autoscaling update-auto-scaling-group \
        --auto-scaling-group-name "$ASG_NAME" \
        --min-size "$min" \
        --max-size "$max" \
        --profile "$AWS_PROFILE"
    
    aws autoscaling set-desired-capacity \
        --auto-scaling-group-name "$ASG_NAME" \
        --desired-capacity "$desired" \
        --profile "$AWS_PROFILE"
}

check_running_tasks(){
    until aws ecs list-tasks \
        --cluster $CLUSTER_NAME \
        --desired-status RUNNING \
        --output text | grep -q $ID; do
        echo "Task is not running yet. Checking again in 10 seconds..."
        sleep 10
    done
    
    sleep 4
    
    TASK_ARN=$(aws ecs list-tasks \
        --cluster $CLUSTER_NAME \
        --desired-status RUNNING \
        --output text | awk '/TASKARNS/ {print $2}')
    
    echo "Found task ARN: $TASK_ARN"
    
    # Loop until the task status is RUNNING for all containers
    until [ $(aws ecs describe-tasks \
        --cluster $CLUSTER_NAME \
        --tasks $TASK_ARN | grep -o '"healthStatus": "HEALTHY"' | wc -l) -ge 2 ]; do
        echo "Containers are not ready yet. Checking again in 10 seconds..."
        sleep 10
    done
    
    echo "Containers are READY. We are good to go!"
    exit 0
}

# Check if an argument is provided
if [ $# -eq 0 ]; then
    usage
    exit 1
fi

# Check if the argument is a number
if ! [[ $1 =~ ^[0-9]+$ ]]; then
    echo "Error: Argument must be a number."
    usage
    exit 1
fi

if [ "$1" -eq 0 ]; then
    update_asg 0 0 0
    echo "ASG desired capacity set to 0."
elif [ "$1" -ge 1 ]; then
    update_asg "$1" 1 3
    echo "Updating the ASG desired capacity to $1"
    sleep 180
    check_running_tasks
else
    echo "Error: Argument must be 0 or greater."
    usage
    exit 1
fi