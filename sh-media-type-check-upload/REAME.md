# File Upload Script

Validates and uploads media files to S3 with type checking and logging.

## Usage

```bash
./upload-script.sh <file_path>
```

## Supported Formats

**Images:** JPEG, JPG, PNG, BMP  
**Video:** H.264, H.265/HEVC, ProRes (AP4H, AVC1, HEV1, HVC1)  
**Audio:** WAV, PCM, AIFF, AIF  

## Behavior

- **Valid files:** Upload to S3 and log success
- **Invalid files:** Delete and log rejection
- **Upload failure:** Delete file

## Configuration

Set environment variables:
- `env_prefix` - S3 bucket prefix
- `name` - Contributor name

## Requirements

- AWS CLI configured
- ImageMagick (`identify` command)
- FFmpeg (`ffprobe` command)
- S3 write permissions