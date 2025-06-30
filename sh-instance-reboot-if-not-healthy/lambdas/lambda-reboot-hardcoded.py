import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Initialize the EC2 client
    ec2_client = boto3.client('ec2')

    # Define the name prefix to filter instances
    name_prefix = "prefix_name"

    try:
        # Describe instances with the specified name prefix
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': [f'{name_prefix}*']}
            ]
        )

        # Extract instance IDs
        instance_ids = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])

        # Check if there are instances to reboot
        if not instance_ids:
            logger.info(f"No instances found with name prefix '{name_prefix}'.")
            return {
                'statusCode': 200,
                'body': f"No instances found with name prefix '{name_prefix}'."
            }

        # Reboot the instances
        logger.info(f"Rebooting instances: {instance_ids}")
        ec2_client.reboot_instances(InstanceIds=instance_ids)
        logger.info(f"Reboot initiated for instances: {instance_ids}")

        return {
            'statusCode': 200,
            'body': f'Reboot initiated for instances with name prefix "{name_prefix}".'
        }

    except Exception as e:
        logger.error(f"Error rebooting instances: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error rebooting instances: {str(e)}"
        }
