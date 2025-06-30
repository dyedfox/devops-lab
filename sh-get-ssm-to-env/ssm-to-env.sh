#!/bin/bash

aws ssm get-parameter --with-decryption --name /stage/aws/ec2/test-test-env --region us-west-2 | jq -r '.Parameter.Value' > .env
