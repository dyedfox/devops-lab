import json
#import boto3
import os
import requests
#from botocore.exceptions import ClientError

def make_graphql_request(token):
    """Make GraphQL request to update registry authentication."""
    
    # GraphQL endpoint should be set as environment variable
    graphql_endpoint = 'https://<URL>/graphql?api_key=<API_KEY>' # test if it fails with wrong key
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
            "id": "cm5p1bxaq0001mk07mws2k8c4",  # Set this in Lambda environment variables
            "username": "AWS",
            "password": token
        }
    }
    
    # Headers for GraphQL request
    headers = {
        'Content-Type': 'application/json',
        # 'Authorization': f"Bearer {os.environ['API_KEY']}"  # If you're using API key authentication - схоже, цього не треба, бо ми передаємо ключ в адресі
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

make_graphql_request ("fdjljfdlkjfdlkfjlkfdjlkn68764n4hiuvchkf689u4nkjhlkfhdk69845u=")

# def lambda_handler(event, context):
#     try:
#         # Create ECR client
#         ecr_client = boto3.client('ecr', region_name=os.environ['AWS_REGION'])
        
#         # Get ECR token
#         response = ecr_client.get_authorization_token()
        
#         if not response['authorizationData']:
#             raise Exception("No authorization data received from ECR")
            
#         # Get the token
#         token = response['authorizationData'][0]['authorizationToken']
        
#         # Update registry auth via GraphQL
#         graphql_response = make_graphql_request(token)
        
#         return {
#             'statusCode': 200,
#             'body': json.dumps({
#                 'message': 'Successfully updated registry authentication',
#                 'graphqlResponse': graphql_response
#             })
#         }
        
#     except ClientError as e:
#         print(f"AWS error: {str(e)}")
#         return {
#             'statusCode': 500,
#             'body': json.dumps({
#                 'error': 'Failed to get ECR token',
#                 'details': str(e)
#             })
#         }
        
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return {
#             'statusCode': 500,
#             'body': json.dumps({
#                 'error': 'Failed to update registry authentication',
#                 'details': str(e)
#             })
#         }
