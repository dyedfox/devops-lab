# devops-lab
A collection of useful scripts and tools for DevOps workflows, built from years of experience in my DevOps journey.

For each item, see the dedicated README.md inside its directory  (some still need to be added).

## MediaInfo Lambda Function
`py-lambda-mediainfo-handler`

AWS Lambda function that extracts technical metadata from uploaded media files using MediaInfo and stores it as S3 object metadata.

## Lambda Function for Updating Registry (ECR) Authentication
`py-lambda-runpod-graphql-send`

This AWS Lambda function retrieves an authentication token from Amazon Elastic Container Registry (ECR) and updates registry authentication via a GraphQL mutation.

## ASG Management Script
`sh-asg-start-stop`

Manages AWS Auto Scaling Group capacity for ECS cluster.

## URL Processor Script
`sh-curl-from-file`

Processes URLs from a file and sends them to an API endpoint (image embedding as an example).

## AMI/Snapshot Cleanup Scripts
`sh-delete-snapshots`

### 1. Snapshot Cleanup (`snapshot-cleanup.sh`)
Deletes old EBS snapshots while keeping recent ones per volume.

### 2. AMI Cleanup (`ami-cleanup.sh`)
Deregisters old AMIs and associated snapshots by prefix.

## Service Discovery Lite 😀
`sh-get-ecs-ip-without-service-discovery`

This is a basic hardcoded replacement for proper service discovery—useful if you don't need the full setup. 😀

## File Upload Script
`sh-media-type-check-upload`

Validates and uploads media files to S3 with type checking and logging.

## EC2 Status Checker
`sh-reboot-unreachable-instances`

Monitors EC2 instances and reboots failed ones based on status checks and CloudWatch metrics.

## Slack Notification Script
`sh-slack-notifications`

Simple Bash script to send notifications to Slack via webhook.

## Simple Rsync Script
`sh-simple-rsync`

A simple Bash script for backing up data.

## Playlist Generator
`sh-generate-m3u-playlist`

Creates M3U playlists from audio files in a directory.