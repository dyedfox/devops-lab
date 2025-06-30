import json
import boto3
import os
import base64
import requests
from botocore.exceptions import ClientError

def make_graphql_request(token):
    """Make GraphQL request to update registry authentication."""
    
    # GraphQL endpoint should be set as environment variable
    graphql_endpoint = os.environ['GRAPHQL_ENDPOINT']
    
    # GraphQL mutation matching the exact format provided
    mutation = """
    mutation UpdateRegistryAuth($input: UpdateRegistryAuthInput) {
        updateRegistryAuth(input: $input) {
            id
            name
        }
    }
    """
    
    # Variables matching the exact format provided
    variables = {
        "input": {
            "id": os.environ['AUTH_ID'],  # Set this in Lambda environment variables
            "username": "AWS",
            "password": token
        }
    }
    
    # Headers for GraphQL request
    headers = {
        'Content-Type': 'application/json',
        #'Authorization': f"Bearer {os.environ['API_KEY']}"  # If you're using API key authentication = NOT USED, because we pass the key in the address
    }
    
    # Make the request
    response = requests.post(
        graphql_endpoint,
        json={'query': mutation, 'variables': variables},
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"GraphQL request failed: {response.text}")
    
    return response.json()

def lambda_handler(event, context):
    try:
        # Create ECR client
        ecr_client = boto3.client('ecr', region_name=os.environ['AWS_REGION'])
        
        # Get ECR token
        response = ecr_client.get_authorization_token()
        
        if not response['authorizationData']:
            raise Exception("No authorization data received from ECR")
            
        # Get the token
        token = response['authorizationData'][0]['authorizationToken']
        decoded_token = base64.b64decode(token).decode('utf-8')
        username, password = decoded_token.split(':')
        
        # Update registry auth via GraphQL
        graphql_response = make_graphql_request(password)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully updated registry authentication',
                'graphqlResponse': graphql_response
            })
        }
        
    except ClientError as e:
        print(f"AWS error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to get ECR token',
                'details': str(e)
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to update registry authentication',
                'details': str(e)
            })
        }