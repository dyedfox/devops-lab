import boto3
import os
import logging

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Initialize EC2 client
    ec2 = boto3.client('ec2')
    
    # Get name prefix from environment variable
    name_prefix = os.environ.get('NAME_PREFIX', '')
    
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