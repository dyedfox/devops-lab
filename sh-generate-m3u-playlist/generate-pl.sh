#!/bin/bash

# Playlist generator script
# Usage: ./script.sh [filename] [directory]
# Creates an M3U playlist from audio files in the specified directory

set -e

# Configuration
filename="${1:-playlist}"
search_dir="${2:-$(pwd)}"
output_file="${filename}.m3u"

# Supported audio formats
audio_extensions=("mp3" "ogg" "m4a" "flac" "wav" "aac" "wma")

# Validate directory exists
if [[ ! -d "$search_dir" ]]; then
    echo "Error: Directory '$search_dir' does not exist" >&2
    exit 1
fi

# Function to find audio files
find_audio_files() {
    local dir="$1"
    local find_cmd="find \"$dir\" -type f"
    
    # Build find command with OR conditions
    local first=true
    for ext in "${audio_extensions[@]}"; do
        if [[ $first == true ]]; then
            find_cmd+=" \\( -iname \"*.${ext}\""
            first=false
        else
            find_cmd+=" -o -iname \"*.${ext}\""
        fi
    done
    find_cmd+=" \\)"
    
    # Execute and sort
    eval "$find_cmd" | sort
}

# Create playlist
echo "Creating playlist: $output_file"
echo "Searching directory: $search_dir"

# Find and add audio files
audio_files=$(find_audio_files "$search_dir")

if [[ -z "$audio_files" ]]; then
    echo "Warning: No audio files found in '$search_dir'" >&2
    echo "Supported formats: ${audio_extensions[*]}" >&2
    echo "No playlist file created."
    exit 1
else
    # Write M3U header
    echo "#EXTM3U" > "$output_file"
    
    # Add files to playlist
    echo "$audio_files" >> "$output_file"
    file_count=$(echo "$audio_files" | wc -l)
    echo "Added $file_count audio files to playlist"
    echo "Playlist saved as: $output_file"
fi