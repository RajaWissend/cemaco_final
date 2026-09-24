#!/bin/bash
# Local test run of the scraper image (no EC2, no AWS needed).
# Usage: ./run_local.sh [input_file_name]   e.g. ./run_local.sh urls.xlsx
set -e

FNAME="${1:-urls.xlsx}"

if [ ! -f "$PWD/input/$FNAME" ]; then
    echo "ERROR: $PWD/input/$FNAME not found"
    exit 1
fi

mkdir -p "$PWD/output" "$PWD/logs"

docker build -t scraper-image .

docker run --rm \
    -v "$PWD/input/$FNAME:/app/input/$FNAME" \
    -v "$PWD/output:/app/output" \
    -v "$PWD/logs:/app/logs" \
    -e INPUT_FILE="/app/input/$FNAME" \
    -e OUTPUT_DIR="/app/output" \
    -e SERVER_ID=test \
    -e S3_BUCKET=your-bucket \
    -e S3_OUTPUT_PREFIX=test/ \
    scraper-image || echo "Container exited with an error (expected if only the S3 upload failed)"

echo "Output files:"
ls -l "$PWD/output"