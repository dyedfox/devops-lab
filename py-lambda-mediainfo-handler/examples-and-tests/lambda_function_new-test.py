import logging
import json
import subprocess
import boto3
from botocore.exceptions import ClientError
import xml.etree.ElementTree as ET
from typing import Dict, Any

SIGNED_URL_EXPIRATION = 600     # The number of seconds that the Signed URL is valid

logger = logging.getLogger('boto3')
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    :param event:
    :param context:
    """
    # Loop through records provided by S3 Event trigger
    # Extract the Key and Bucket names for the asset uploaded to S3
    key = "Big_Buck_Bunny_1080_10s_5MB-hev1-h265.mp4"
    bucket = "stage-test-upload-bucket"
    logger.info("Bucket: {} \t Key: {}".format(bucket, key))
    # Generate a signed URL for the uploaded asset
    signed_url = get_signed_url(SIGNED_URL_EXPIRATION, bucket, key)
    logger.info("Signed URL: {}".format(signed_url))
    xml_output = subprocess.check_output(["./mediainfo", "--full", "--output=XML", signed_url]).decode('utf-8')
    logger.info("Output: {}".format(xml_output))
    save_record(bucket, key, xml_output)
    
def extract_metadata_from_xml(xml_output: str) -> Dict[str, str]:
    """
    Extract relevant metadata from MediaInfo XML output.

    Args:
        xml_output: MediaInfo XML output as a string

    Returns:
        Dictionary containing formatted metadata
    """
    try:
        # Parse XML with namespaces
        root = ET.fromstring(xml_output)
        ns = {'mi': 'https://mediaarea.net/mediainfo'}  # Define namespace
        
        # Initialize metadata dictionary
        metadata = {}

        # Find General track
        general_track = root.find(".//mi:track[@type='General']", ns)
        if general_track is not None:
            metadata['file_size'] = general_track.find('mi:FileSize', ns).text if general_track.find('mi:FileSize', ns) is not None else ''
            metadata['duration'] = general_track.find('mi:Duration', ns).text if general_track.find('mi:Duration', ns) is not None else ''
            metadata['overall_bitrate'] = general_track.find('mi:OverallBitRate', ns).text if general_track.find('mi:OverallBitRate', ns) is not None else ''
            metadata['frame_rate'] = general_track.find('mi:FrameRate', ns).text if general_track.find('mi:FrameRate', ns) is not None else ''
            metadata['frame_count'] = general_track.find('mi:FrameCount', ns).text if general_track.find('mi:FrameCount', ns) is not None else ''

        # Find Video track
        video_track = root.find(".//mi:track[@type='Video']", ns)
        if video_track is not None:
            metadata['video_format'] = video_track.find('mi:Format', ns).text if video_track.find('mi:Format', ns) is not None else ''
            metadata['video_profile'] = video_track.find('mi:Format_Profile', ns).text if video_track.find('mi:Format_Profile', ns) is not None else ''
            metadata['width'] = video_track.find('mi:Width', ns).text if video_track.find('mi:Width', ns) is not None else ''
            metadata['height'] = video_track.find('mi:Height', ns).text if video_track.find('mi:Height', ns) is not None else ''
            metadata['aspect_ratio'] = video_track.find('mi:DisplayAspectRatio', ns).text if video_track.find('mi:DisplayAspectRatio', ns) is not None else ''
            metadata['color_space'] = video_track.find('mi:ColorSpace', ns).text if video_track.find('mi:ColorSpace', ns) is not None else ''
            metadata['chroma_subsampling'] = video_track.find('mi:ChromaSubsampling', ns).text if video_track.find('mi:ChromaSubsampling', ns) is not None else ''
            metadata['bit_depth'] = video_track.find('mi:BitDepth', ns).text if video_track.find('mi:BitDepth', ns) is not None else ''
            metadata['scan_type'] = video_track.find('mi:ScanType', ns).text if video_track.find('mi:ScanType', ns) is not None else ''

        # Create a summary string
        summary = (f"{metadata.get('video_format', '')} {metadata.get('width', '')}x{metadata.get('height', '')} "
                   f"@ {metadata.get('frame_rate', '')}fps, {metadata.get('duration', '')}s")
        metadata['technical_summary'] = summary

        return {k: str(v) for k, v in metadata.items()}

    except ET.ParseError as e:
        logger.error(f"Failed to parse XML: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error extracting metadata: {str(e)}")
        raise

def save_record(bucket: str, key: str, xml_output: str) -> None:
    """
    Write the metadata to the S3 bucket
    
    Args:
        bucket: S3 Bucket Name
        key: S3 Key Name
        xml_output: Technical Metadata in XML Format
    
    Raises:
        ClientError: If there's an error updating S3 metadata
    """
    s3_client = boto3.client("s3")
    
    try:
        # Extract metadata from XML
        technical_metadata = extract_metadata_from_xml(xml_output)
        
        # Retrieve the existing metadata
        response = s3_client.head_object(Bucket=bucket, Key=key)
        existing_metadata = response.get('Metadata', {})
        
        # Update the metadata with the technical metadata
        new_metadata = {
            k: v  # Removed the x-amz-meta- prefix
            for k, v in technical_metadata.items()
            if v  # Only include non-empty values
        }
        
        # Preserve existing metadata
        preserved_metadata = {
            k: v 
            for k, v in existing_metadata.items() 
            if k not in technical_metadata.keys()  # Changed this condition
        }
        
        # Combine preserved and new metadata
        final_metadata = {**preserved_metadata, **new_metadata}
        
        logger.debug(f"Final metadata to be updated: {json.dumps(final_metadata, indent=2)}")


        # Copy the object to itself with the updated metadata
        s3_client.copy_object(
            Bucket=bucket,
            CopySource={'Bucket': bucket, 'Key': key},
            Key=key,
            Metadata=final_metadata,
            MetadataDirective='REPLACE'
        )
        
        logger.info(f"Successfully updated metadata for s3://{bucket}/{key}")
        logger.debug(f"Updated metadata: {json.dumps(final_metadata, indent=2)}")
        
    except ClientError as e:
        logger.error(f"Failed to update metadata for S3 object: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating metadata: {str(e)}")
        raise


def get_signed_url(expires_in, bucket, obj):
    """
    Generate a signed URL
    :param expires_in:  URL Expiration time in seconds
    :param bucket:
    :param obj:         S3 Key name
    :return:            Signed URL
    """
    s3_cli = boto3.client("s3")
    presigned_url = s3_cli.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': obj},
                                                  ExpiresIn=expires_in)
    return presigned_url