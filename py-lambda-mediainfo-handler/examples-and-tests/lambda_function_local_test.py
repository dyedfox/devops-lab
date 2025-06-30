import logging
import json
import subprocess
import boto3
from botocore.exceptions import ClientError
import xml.etree.ElementTree as ET
from typing import Dict, Any

# def extract_metadata_from_xml(xml_output: str) -> Dict[str, str]:
#     """
#     Extract relevant metadata from MediaInfo XML output.
    
#     Args:
#         xml_output: MediaInfo XML output as string
    
#     Returns:
#         Dictionary containing formatted metadata
#     """
#     try:
#         # Parse XML
#         root = ET.fromstring(xml_output)
        
#         # Initialize metadata dictionary
#         metadata = {}
        
#         # Find General track
#         general_track = root.find(".//track[@type='General']")
#         if general_track is not None:
#             metadata['file_size'] = general_track.find('FileSize').text if general_track.find('FileSize') is not None else ''
#             metadata['duration'] = general_track.find('Duration').text if general_track.find('Duration') is not None else ''
#             metadata['overall_bitrate'] = general_track.find('OverallBitRate').text if general_track.find('OverallBitRate') is not None else ''
#             metadata['frame_rate'] = general_track.find('FrameRate').text if general_track.find('FrameRate') is not None else ''
#             metadata['frame_count'] = general_track.find('FrameCount').text if general_track.find('FrameCount') is not None else ''
        
#         # Find Video track
#         video_track = root.find(".//track[@type='Video']")
#         if video_track is not None:
#             metadata['video_format'] = video_track.find('Format').text if video_track.find('Format') is not None else ''
#             metadata['video_profile'] = video_track.find('Format_Profile').text if video_track.find('Format_Profile') is not None else ''
#             metadata['width'] = video_track.find('Width').text if video_track.find('Width') is not None else ''
#             metadata['height'] = video_track.find('Height').text if video_track.find('Height') is not None else ''
#             metadata['aspect_ratio'] = video_track.find('DisplayAspectRatio').text if video_track.find('DisplayAspectRatio') is not None else ''
#             metadata['color_space'] = video_track.find('ColorSpace').text if video_track.find('ColorSpace') is not None else ''
#             metadata['chroma_subsampling'] = video_track.find('ChromaSubsampling').text if video_track.find('ChromaSubsampling') is not None else ''
#             metadata['bit_depth'] = video_track.find('BitDepth').text if video_track.find('BitDepth') is not None else ''
#             metadata['scan_type'] = video_track.find('ScanType').text if video_track.find('ScanType') is not None else ''
        
#         # Create a summary string with key technical details
#         summary = (f"{metadata.get('video_format', '')} {metadata.get('width', '')}x{metadata.get('height', '')} "
#                   f"@ {metadata.get('frame_rate', '')}fps, {metadata.get('duration', '')}s")
#         metadata['technical_summary'] = summary
        
#         return {k: str(v) for k, v in metadata.items()}
        
#     except ET.ParseError as e:
#         logger.error(f"Failed to parse XML: {str(e)}")
#         raise
#     except Exception as e:
#         logger.error(f"Error extracting metadata: {str(e)}")
#         raise

import xml.etree.ElementTree as ET
import logging
from typing import Dict

# Initialize logger
logger = logging.getLogger(__name__)

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

signed_url = "/home/temp/mediainfo-handler/1.mp4"
xml_output = subprocess.check_output(["/home/temp/mediainfo", "--full", "--output=XML", signed_url]).decode('utf-8')
print(xml_output)
processed = extract_metadata_from_xml(xml_output)
print(processed)