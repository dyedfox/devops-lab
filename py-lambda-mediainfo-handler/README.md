# MediaInfo Lambda Function

AWS Lambda function that extracts technical metadata from uploaded media files using MediaInfo and stores it as S3 object metadata.

## How it works

1. **S3 Event Trigger** - Activated when files are uploaded to S3
2. **Generate Signed URL** - Creates temporary access URL for the uploaded file
3. **Extract Metadata** - Uses MediaInfo to analyze the file and output XML
4. **Parse & Store** - Extracts relevant metadata and updates S3 object metadata

## Extracted Metadata

**General:**
- File size, duration, bitrate, frame rate/count

**Video:**
- Format, profile, dimensions, aspect ratio
- Color space, chroma subsampling, bit depth, scan type
- Technical summary (e.g., "H.264 1920x1080 @ 30fps, 120s")

## Requirements

- MediaInfo binary included in deployment package (`./mediainfo`)
- S3 read/write permissions
- Lambda execution role with S3 access

## Configuration

- `SIGNED_URL_EXPIRATION` - URL validity period (default: 300 seconds)

## Usage

Deploy as Lambda function and configure S3 bucket event notifications to trigger on object creation.