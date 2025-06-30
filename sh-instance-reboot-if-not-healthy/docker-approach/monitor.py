import requests
import logging
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def check_health(retries=3, timeout=5):
    for attempt in range(retries):
        try:
            response = requests.get("https://www.myendpoint123.com/health/ready", timeout=timeout)
            response.raise_for_status()
            return response.text == '{"status":"up"}'
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(5)  # Wait before retrying
    logger.error("All health check attempts failed.")
    return False

def send_webhook(url, payload, retries=3, timeout=5):
    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            logger.info("Webhook sent successfully.")
            return True
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(5)  # Wait before retrying
    logger.error("All webhook attempts failed.")
    return False

def main():
    logger.info("Started!")

    # Get configuration from environment variables or use default values
    reboot_webhook_url = os.getenv('REBOOT_WEBHOOK_URL', "https://webhook-url.com")
    retries = int(os.getenv('RETRIES', 3))
    timeout = int(os.getenv('TIMEOUT', 5))
    sleep_time = int(os.getenv('SLEEP_TIME', 60))

    while True:
        if check_health(retries, timeout):
            continue
        else:
            logger.info("System is not healthy. Invoking reboot webhook...")
            if not send_webhook(reboot_webhook_url, {"action": "reboot"}, retries, timeout):
                logger.error("Failed to send reboot webhook after retries.")

        # Wait before the next health check
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
