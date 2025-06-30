#!/bin/bash
set -e

# Default values
DRY_RUN=true
PREFIXES=()
KEEP_COUNT=10

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS] [PREFIXES...]"
    echo ""
    echo "Options:"
    echo "  --dry-run          Show what would be deregistered without actually doing it (default)"
    echo "  --live             Actually deregister the AMIs and delete associated snapshots"
    echo "  --keep COUNT       Number of most recent AMIs to keep per prefix (default: 10)"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 api-v2- me-worker-                    # Dry run with custom prefixes"
    echo "  $0 --live api-v2- me-worker-             # Live mode with custom prefixes"
    echo "  $0 --live --keep 5 api-v2-               # Keep only 5 most recent"
    echo "  $0 --dry-run                             # Use default prefixes (api-v2-, me-worker-)"
    echo ""
    echo "Note: AMIs with '@default' in their Name tag will be excluded"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --live)
            DRY_RUN=false
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --keep)
            if [[ -n $2 && $2 =~ ^[0-9]+$ ]]; then
                KEEP_COUNT="$2"
                shift 2
            else
                echo "Error: --keep requires a numeric value"
                exit 1
            fi
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
        *)
            # Remaining arguments are prefixes
            PREFIXES+=("$1")
            shift
            ;;
    esac
done

# Set default prefixes if none provided
if [ ${#PREFIXES[@]} -eq 0 ]; then
    PREFIXES=("api-v2-" "me-worker-")
    echo "No prefixes specified, using defaults: ${PREFIXES[*]}"
fi

# Display current mode
echo "========================================"
if [ "$DRY_RUN" = true ]; then
    echo "=== DRY RUN MODE - No AMIs will be deregistered ==="
    echo "Use --live flag to actually deregister AMIs"
else
    echo "=== LIVE MODE - AMIs will be permanently deregistered ==="
    echo "Press Ctrl+C within 5 seconds to cancel..."
    sleep 5
fi
echo "Keeping $KEEP_COUNT most recent AMIs per prefix"
echo "Prefixes to process: ${PREFIXES[*]}"
echo "========================================"
echo ""

# Function to process and deregister images
preview_images() {
    local images=("${@}")
    echo "Images to be deregistered:"
    echo "   Tag(Name)                   |    Name                     |    ImageId                        |    Creation Date"
    for image in "${images[@]}"; do
        aws ec2 describe-images --image-ids "$image" --output text \
            --query 'Images[0].[Tags[?Key==`Name`].Value | [0], Name, ImageId, CreationDate]'
    done
}

process_images() {
    local images=("${@}")
    for image in "${images[@]}"; do
        echo "Deregistering $image..."
        # !!!! Comment/Uncomment the line below to perform the deregistration or not
        aws ec2 deregister-image --image-id "$image" --delete-associated-snapshots
    done
}

for prefix in "${PREFIXES[@]}"; do
    ## Retrieve image IDs for images with names starting with prefix and tags not containing @default,
    ## and exclude the last KEEP_COUNT images based on creation date
    echo "> Prefix: $prefix"
    images=($(aws ec2 describe-images --owner self --output text \
        --query "sort_by(Images[?starts_with(Name, \`$prefix\`) && !contains(Tags[?Key==\`Name\`].Value | [0], \`@default\`)], &CreationDate)[:-${KEEP_COUNT}].ImageId"))

    # Process the images
    if [ ! -z "$images" ]; then
        preview_images "${images[@]}"
        if [[ $DRY_RUN == false ]]; then
            process_images "${images[@]}"
        else
            echo "Running in dry-run mode. Skipping...".
        fi
    else
        echo "Images that satisfy the criteria $prefix not found. 
Try changing the prefix, check if images exist or specify a different --keep count."
    fi
done

if [ "$DRY_RUN" = true ]; then
    echo "=== DRY RUN COMPLETED ==="
    echo "No images were actually deregistered."
    echo "Run with --live flag to perform actual deregistrations."
else
    echo "=== CLEANUP COMPLETED ==="
    echo "All specified images have been deregistered."
fi