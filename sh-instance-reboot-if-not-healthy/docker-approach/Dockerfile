# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables (optional, can be overridden at runtime)
ENV REBOOT_WEBHOOK_URL="https://webhook-url.com"
ENV RETRIES=3
ENV TIMEOUT=5
ENV SLEEP_TIME=60

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY monitor.py /app

# Install the requests library
RUN pip install --no-cache-dir requests

# Run the script
CMD ["python", "monitor.py"]