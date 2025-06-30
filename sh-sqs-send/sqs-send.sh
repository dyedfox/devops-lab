#!/bin/bash

# Check if required parameters are provided
# if [ "$#" -ne 2 ]; then
#     echo "Usage: $0 <queue-url> <message-body>"
#     exit 1
# fi

# QUEUE_URL="$1"
# MESSAGE_BODY="$2"

QUEUE_URL="https://sqs.us-west-2.amazonaws.com/123456789012/dev-test"
MESSAGE_BODY="Just a message"

# Send message to SQS queue      
for ((i = 0 ; i < 25 ; i++)); do
    echo "$i"
      aws sqs send-message \
        --queue-url "$QUEUE_URL" \
        --message-body "$MESSAGE_BODY $i"
    sleep 3
done

# # Check if the message was sent successfully
# if [ $? -eq 0 ]; then
#     echo "Message sent successfully to $QUEUE_URL"
# else
#     echo "Failed to send message to $QUEUE_URL"
#     exit 1
# fi