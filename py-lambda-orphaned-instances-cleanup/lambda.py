# Lambda for cleaning up orphaned instances, e.g. Jenkins workers

import boto3
import os
import logging
import json
import datetime

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_jenkins_worker_instances(region=None):
    instance_names_raw = os.environ.get('INSTANCE_NAMES')
    instance_names = [name.strip() for name in instance_names_raw.split(',')]
    ec2 = boto3.client('ec2', region_name=region) if region else boto3.client('ec2')
    filters = [
        {'Name': 'tag:Name', 'Values': instance_names},
        {'Name': 'instance-state-name', 'Values': ['running']}
    ]
    resp = ec2.describe_instances(Filters=filters)
    instances = []
    for reservation in resp.get('Reservations', []):
        for inst in reservation.get('Instances', []):
            instances.append({
                'InstanceId': inst.get('InstanceId'),
                # 'State': inst.get('State', {}).get('Name'),
                'LaunchTime': (inst.get('LaunchTime').strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                               if isinstance(inst.get('LaunchTime'), datetime.datetime)
                               else inst.get('LaunchTime'))
                # 'PrivateIp': inst.get('PrivateIpAddress'),
                # 'PublicIp': inst.get('PublicIpAddress'),
                # 'Tags': inst.get('Tags', [])
            })
    return instances

def lambda_handler(event, context):
    region = os.environ.get('AWS_REGION')
    time_running_threshold_seconds = os.environ.get('TIME_RUNNING_THRESHOLD_SECONDS', '10800') # Default to 3 hours
    try:
        instances = get_jenkins_worker_instances(region)
        logging.info('Found %d instances', len(instances))

        for instance in instances:
            launch_time = instance['LaunchTime']
            if isinstance(launch_time, str):
                launch_time = datetime.datetime.fromisoformat(launch_time.replace('Z', '+00:00'))
            time_running = datetime.datetime.now(datetime.timezone.utc) - launch_time
            if time_running.total_seconds() > time_running_threshold_seconds:
                ec2 = boto3.client('ec2', region_name=region)
                ec2.terminate_instances(InstanceIds=[instance['InstanceId']])
                logging.info(f"Terminated instance {instance['InstanceId']} running for {time_running}")

        return {
            'statusCode': 200,
            'body': json.dumps(instances)
        }
    except Exception as e:
        logging.exception('Failed to retrieve instances')
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }