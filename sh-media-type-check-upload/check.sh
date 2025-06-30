#!/bin/bash
check_file_type() {
   local file="$1"
   local mime_type
   local video_codec
   local image_format
   local audio_format
   
   # Get MIME type
   mime_type=$(file -b --mime-type "$file")
   
   # Check for image types
   if [[ "$mime_type" == image/* ]]; then
       # Verify image format using ImageMagick
       if ! image_format=$(identify -format "%m" "$file" 2>/dev/null); then
           return 1
       fi
       # Check for allowed image formats
       case "${image_format,,}" in  # Convert to lowercase for comparison
           jpeg|jpg|png|bmp)
               return 0
               ;;
           *)
               return 1
               ;;
       esac
   fi
   
   # Check for video
   if [[ "$mime_type" == video/* ]]; then
       # Get codec information
       video_codec=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_tag_string -of default=noprint_wrappers=1:nokey=1 "$file")
       if [[ "$video_codec" == "[0][0][0][0]" ]]; then
           video_codec=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$file")
       fi
       case "${video_codec,,}" in  # Convert to lowercase for comparison
           ap4h|avc1|hev1|hvc1|h264|h265|hevc|prores)
               return 0
               ;;
           *)
               return 1
               ;;
       esac
   fi
   
   # Check for audio
   if [[ "$mime_type" == audio/* ]]; then
       # Get audio format using ffprobe
       audio_format=$(ffprobe -v error -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$file")
       case "${audio_format,,}" in  # Convert to lowercase for comparison
           wav|pcm*|aiff|aif)
               return 0
               ;;
           *)
               return 1
               ;;
       esac
   fi
   
   return 1
}

if [[ -f $1 ]]; then
   file="$1"
   now=$(date +"%m-%d-%Y %T")
   relativefile=${file:44}
   # Check file type before uploading
   if check_file_type "$file"; then
       aws s3 mv --acl private "$file" "s3://${env_prefix}-bucket-${name}/$relativefile" \
           && echo "$now Uploaded: $file" >> /home/your_organization/data/logs/uploadscript.log \
           || rm "$file"
   else
       echo "$now Rejected (invalid type): $file" >> /home/your_organization/data/logs/uploadscript.log
       rm "$file"
   fi
fi