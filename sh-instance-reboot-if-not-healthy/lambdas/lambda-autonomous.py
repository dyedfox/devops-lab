import boto3
import os
import logging
import requests
from time import sleep

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Initialize EC2 client
    ec2 = boto3.client('ec2')

    # Get name prefix from environment variable
    name_prefix = os.environ.get('NAME_PREFIX', '')

    # API endpoint to check status
    api_url = os.environ.get('API_URL', '')

    if not api_url:
        logger.error("API_URL environment variable is not set")
        return {
            'statusCode': 500,
            'body': 'API_URL environment variable is not set'
        }

    def check_api_status():
        try:
            response = requests.get(api_url, timeout=3)
            if response.status_code == 200:
                status = response.json().get('status')
                if status == 'up':
                    # logger.info("API status is up, no need to reboot instances")
                    return True
                else:
                    logger.warning(f"API status is {status}, initiating reboot")
                    return False
            else:
                logger.warning(f"API returned unexpected status code: {response.status_code}, will retry once")
                return "retry"
        except requests.RequestException as e:
            logger.error(f"Error checking API status: {str(e)}", exc_info=True)
            return False

    # Check API status
    api_status = check_api_status()

    if api_status == "retry":
        sleep(5)  # Wait for 5 seconds before retrying
        api_status = check_api_status()

    if api_status:
        return {
            'statusCode': 200,
            'body': 'API status is up, no action taken'
        }

    # Prepare filters
    filters = [
        {
            'Name': 'instance-state-name',
            'Values': ['running']
        }
    ]

    if name_prefix:
        filters.append({
            'Name': 'tag:Name',
            'Values': [f'{name_prefix}*']
        })

    # Get instances matching the filters
    response = ec2.describe_instances(Filters=filters)

    instance_ids = [
        instance['InstanceId']
        for reservation in response['Reservations']
        for instance in reservation['Instances']
    ]

    if not instance_ids:
        logger.info(f"No instances found matching prefix: {name_prefix}")
        return {
            'statusCode': 200,
            'body': 'No instances found to reboot'
        }

    try:
        # Log instances that will be rebooted
        logger.info(f"Attempting to reboot instances: {instance_ids}")

        # Reboot the instances
        response = ec2.reboot_instances(InstanceIds=instance_ids)

        logger.info(f"Successfully initiated reboot for {len(instance_ids)} instances")
        return {
            'statusCode': 200,
            'body': f'Rebooted {len(instance_ids)} instances'
        }
    except Exception as e:
        logger.error(f"Error rebooting instances: {str(e)}", exc_info=True)
        raise e
