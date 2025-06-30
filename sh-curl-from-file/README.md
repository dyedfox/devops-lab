# URL Processor Script

Processes URLs from a file and sends them to an API endpoint (image embedding as an example).

## Usage

```bash
./script.sh <url_file>
```

## Input File Format

Create a text file with one URL per line:
```
https://example.com/image1.jpg
https://example.com/image2.png
# This is a comment - will be skipped
https://example.com/image3.gif

https://example.com/image4.jpg
```

- Empty lines and comments (`#`) are ignored
- Leading/trailing whitespace is trimmed

## Output

Shows per-URL results with:
- HTTP status code
- Response time
- Success/error response body
- Final summary with counts and timing

## Time Measurement

Individual request timing with millisecond precision
Total execution time for all requests
Average time per request calculation

## Example

```bash
./process-urls.sh urls.txt
```

```
Processing URLs from: urls.txt
==================================
[1] Processing: https://example.com/image1.jpg
 ✓ Success (HTTP 200) - 1.234s
 Response: {"status":"embedded"}
 ---
[2] Processing: https://example.com/image2.png
 ✗ Failed (HTTP 404) - 0.567s
 Error: {"error":"not found"}
 ---
==================================
Processing complete!
Total URLs processed: 2
Successful requests: 1
Failed requests: 1
Total execution time: 0m 2s
Average time per request: 1.00s
```

## Requirements

- `curl` command
- `bc` command (for calculations)
- Read access to input file