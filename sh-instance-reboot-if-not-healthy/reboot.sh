#!/bin/bash

set -e
instance_ids=("i-08d1fb7012fb1906a" "i-0684895d32d22cfd2")

# Set live mode. Default is dry-run
live=0
if [[ $1 == "--live" ]]; then
    live=1 
    echo ">>>> Running in LIVE MODE! Command/Ctrl+C to cancel."
else
    echo ">>>> Running in dry-run mode."
fi

# Checking the health status
response=$(curl -s https://www.myendpoint123.com/health/ready)

# Check the response and reboot instances if not healthy
if [[ $response == '{"status":"up"}' ]]; then
    echo "Great news! The system is healthy. Aborting..."
    exit 0
else
    if [[ $live -eq 1 ]]; then
        echo "Rebooting instances: ${instance_ids[@]}"
        for id in ${instance_ids[@]}; do
            aws ec2 reboot-instances --instance-ids "$id" || echo "Reboot failed for instance: $id"
        done
    else
        echo "Instances ${instance_ids[@]} should be rebooted. Running in dry-run mode. Skipping..."
    fi
fi