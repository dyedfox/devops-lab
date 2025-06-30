#!/bin/sh
# Get the AI Models IP address
IP=$(hostname -I | awk '{print $1}')
# Check if the IP address matches 172.17.0.3
if [ "$IP" = "172.17.0.3" ]; then
    ANOTHER_CONTAINER_URL="http://172.17.0.2:8123"
else
    ANOTHER_CONTAINER_URL="http://172.17.0.3:8123"
fi

# Update the .env file at /var/www/.env with the new AI_MODELS_URL
sed -i "s|^ANOTHER_CONTAINER_URL=.*|ANOTHER_CONTAINER_URL=${ANOTHER_CONTAINER_URL}|" /var/www/.env

# Check if the service at localhost:8123 returns 404 and wait if it does
until curl -o /dev/null -s -w '%{http_code}\n' ${ANOTHER_CONTAINER_URL} | grep -q '404'; do
    echo "Waiting for the main service on port 8123..."
    sleep 10
done

# Start supervisord once the service is ready
/usr/bin/supervisord -c /etc/supervisord.conf