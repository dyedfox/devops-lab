import boto3
import os
import logging
import json

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Initialize clients
    asg_client = boto3.client('autoscaling')
    
    # Get ASG name from environment variable
    asg_name = os.environ.get('ASG_NAME', '')
    
    if not asg_name:
        logger.error("ASG_NAME environment variable is not set")
        return {
            'statusCode': 400,
            'body': 'ASG_NAME environment variable is required'
        }
    
    try:
        # Get ASG details to check desired capacity
        asg_response = asg_client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[asg_name]
        )
        
        if not asg_response['AutoScalingGroups']:
            logger.error(f"Auto Scaling Group '{asg_name}' not found")
            return {
                'statusCode': 404,
                'body': f"Auto Scaling Group '{asg_name}' not found"
            }
        
        # Get desired capacity and determine MinHealthyPercentage
        desired_capacity = asg_response['AutoScalingGroups'][0]['DesiredCapacity']
        min_healthy_percentage = 0 if desired_capacity == 1 else 50
        
        logger.info(f"ASG '{asg_name}' has desired capacity {desired_capacity}, setting MinHealthyPercentage to {min_healthy_percentage}")
        
        # Start an instance refresh
        logger.info(f"Starting instance refresh for ASG: {asg_name}")
        
        refresh_response = asg_client.start_instance_refresh(
            AutoScalingGroupName=asg_name,
            Preferences={
                'MinHealthyPercentage': min_healthy_percentage,
                'InstanceWarmup': 300
            }
        )
        
        refresh_id = refresh_response['InstanceRefreshId']
        logger.info(f"Instance refresh initiated successfully. Refresh ID: {refresh_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Instance refresh started for ASG: {asg_name}",
                'refreshId': refresh_id,
                'desiredCapacity': desired_capacity,
                'minHealthyPercentage': min_healthy_percentage
            })
        }
    except Exception as e:
        logger.error(f"Error starting instance refresh: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': f"Error starting instance refresh: {str(e)}"
        }