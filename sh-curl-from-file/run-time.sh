#!/bin/bash

# Check if file argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <url_file>"
    echo "Example: $0 urls.txt"
    exit 1
fi

URL_FILE="$1"

# Check if file exists
if [ ! -f "$URL_FILE" ]; then
    echo "Error: File '$URL_FILE' not found!"
    exit 1
fi

# Check if file is readable
if [ ! -r "$URL_FILE" ]; then
    echo "Error: Cannot read file '$URL_FILE'!"
    exit 1
fi

# API endpoint and headers
API_URL="http://54.187.207.86:8000/embed/image"
API_KEY="1234567.embed_key"

echo "Processing URLs from: $URL_FILE"
echo "=================================="

# Start total time measurement
total_start_time=$(date +%s)

# Counter for processed URLs
count=0
success_count=0
error_count=0

# Read file line by line
while IFS= read -r url || [ -n "$url" ]; do
    # Skip empty lines and lines starting with #
    if [[ -z "$url" || "$url" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # Remove leading/trailing whitespace
    url=$(echo "$url" | xargs)
    
    # Skip if still empty after trimming
    if [[ -z "$url" ]]; then
        continue
    fi
    
    ((count++))
    echo "[$count] Processing: $url"
    
    # Start time measurement for this URL
    start_time=$(date +%s.%3N)
    
    # Execute curl command
    response=$(curl --location "$API_URL" \
        --header 'Content-Type: application/json' \
        --header "x-api-key: $API_KEY" \
        --data "{\"url\":\"$url\"}" \
        --silent \
        --write-out "HTTPSTATUS:%{http_code}" 2>&1)
    
    # End time measurement
    end_time=$(date +%s.%3N)
    duration=$(echo "$end_time - $start_time" | bc)
    
    # Extract HTTP status code
    http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    response_body=$(echo "$response" | sed 's/HTTPSTATUS:[0-9]*$//')
    
    # Check if request was successful
    if [[ "$http_code" =~ ^2[0-9][0-9]$ ]]; then
        echo "  ✓ Success (HTTP $http_code) - ${duration}s"
        echo "  Response: $response_body"
        ((success_count++))
    else
        echo "  ✗ Failed (HTTP $http_code) - ${duration}s"
        echo "  Error: $response_body"
        ((error_count++))
    fi
    
    echo "  ---"
    
    # Optional: Add delay between requests to avoid overwhelming the server
    # sleep 1
    
done < "$URL_FILE"

# Calculate total execution time
total_end_time=$(date +%s)
total_duration=$((total_end_time - total_start_time))
minutes=$((total_duration / 60))
seconds=$((total_duration % 60))

echo "=================================="
echo "Processing complete!"
echo "Total URLs processed: $count"
echo "Successful requests: $success_count"
echo "Failed requests: $error_count"
echo "Total execution time: ${minutes}m ${seconds}s"
if [ $count -gt 0 ]; then
    avg_time=$(echo "scale=2; $total_duration / $count" | bc)
    echo "Average time per request: ${avg_time}s"
fi
