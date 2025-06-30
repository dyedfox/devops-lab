#!/bin/bash

send_slack_notification() {
    # Slack webhook URL
    local webhook_url="https://hooks.slack.com/services/GGKJLGJLK/BGJHGKJ2CW/hfkjhdfkjhkjhfdkjhf"
    # Message to send
    local message="$1"
    # Payload
    local payload="payload={\"text\": \"${message}\"}"
    # Send notification
    curl -X POST --data-urlencode "${payload}" "${webhook_url}"
}

# Call the function
send_slack_notification "$1"