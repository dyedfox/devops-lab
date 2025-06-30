
# AWS Lambda Function for Updating Registry Authentication

This AWS Lambda function retrieves an authentication token from Amazon Elastic Container Registry (ECR) and updates registry authentication via a GraphQL mutation.

## Prerequisites

- AWS Lambda environment
- Python 3.x
- Required Python libraries: `boto3`, `requests`
- Environment variables configured in AWS Lambda:
    - `GRAPHQL_ENDPOINT`: The endpoint for the GraphQL API.
    - `AUTH_ID`: The authentication ID for updating registry authentication.
    - `AWS_REGION`: The AWS region where the ECR is located.

## Setup

1. **Deploy the Lambda Function:**
    
2. **Configure Environment Variables:**
    
    - Set the environment variables `GRAPHQL_ENDPOINT`, `AUTH_ID`, and `AWS_REGION` in the Lambda function configuration.
3. **IAM Role:**
    
    - Ensure the IAM role attached to the Lambda function has permissions to call `ecr:GetAuthorizationToken`.

## Usage

- The Lambda function is triggered automatically if set up with an appropriate trigger (e.g., API Gateway, CloudWatch Events, EventBrodge Scheduler).
- Upon execution, the function retrieves an ECR authorization token and updates the registry authentication via a GraphQL mutation.

## Response

- On successful execution, the function returns a success message along with the GraphQL response.
- On failure, it returns an error message with details.