#!/bin/bash

set -e

# Set live mode. Default is dry-run
live=0
if [[ $1 == "--live" ]]; then
    live=1
    echo ">>>> Running in LIVE MODE! Command/Ctrl+C to cancel."
else
    echo ">>>> Running in dry-run mode."
fi

# Webhook URL for invoking reboot
reboot_webhook_url="https://your-reboot-webhook-url.com"

# Checking the health status
response=$(curl -s https://www.myendpoint123.com/health/ready)

# Check the response and invoke reboot webhook if not healthy
if [[ $response == '{"status":"up"}' ]]; then
    echo "Great news! The system is healthy. Aborting..."
    exit 0
else
    if [[ $live -eq 1 ]]; then
        echo "Invoking reboot webhook..."
        # Send webhook to invoke reboot
        curl -X POST -H "Content-Type: application/json" -d '{"action":"reboot"}' $reboot_webhook_url
    else
        echo "Instances should be rebooted. Running in dry-run mode. Skipping..."
    fi
fi
