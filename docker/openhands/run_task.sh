#!/bin/bash
# run_task.sh - Run a single CoDA-Bench task using OpenHands in Docker
#
# Usage:
#   ./run_task.sh <workspace_dir> <data_dir> <output_dir>
#
# Arguments:
#   workspace_dir - Directory containing task_description.txt (mounted as /workspace)
#   data_dir      - Community data directory (mounted read-only as /data)
#   output_dir    - Directory for output (mounted as /output)
#
# Environment variables (must be set):
#   LLM_MODEL    - Model name (e.g., gpt-5.5)
#   LLM_API_KEY  - API key for the model
#   LLM_BASE_URL - API base URL

set -e

WORKSPACE_DIR="${1:?Usage: $0 <workspace_dir> <data_dir> <output_dir>}"
DATA_DIR="${2:?Usage: $0 <workspace_dir> <data_dir> <output_dir>}"
OUTPUT_DIR="${3:?Usage: $0 <workspace_dir> <data_dir> <output_dir>}"

# Defaults
LLM_MODEL="${LLM_MODEL:-gpt-5.5}"
LLM_BASE_URL="${LLM_BASE_URL:-https://api.openai.com/v1}"

if [ -z "$LLM_API_KEY" ]; then
    echo "ERROR: LLM_API_KEY not set" >&2
    exit 1
fi

IMAGE_NAME="codabench-openhands:latest"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

echo "[$(date '+%H:%M:%S')] Running OpenHands task"
echo "  Workspace: $WORKSPACE_DIR"
echo "  Data: $DATA_DIR"
echo "  Output: $OUTPUT_DIR"

# Run container with security restrictions
docker run --rm \
    --name "codabench-oh-$$" \
    --network=host \
    --cap-add=NET_ADMIN \
    -v "$WORKSPACE_DIR:/workspace:rw" \
    -v "$DATA_DIR:/data:ro" \
    -v "$OUTPUT_DIR:/output:rw" \
    -e "LLM_MODEL=$LLM_MODEL" \
    -e "LLM_API_KEY=$LLM_API_KEY" \
    -e "LLM_BASE_URL=$LLM_BASE_URL" \
    --memory=8g \
    --cpus=2 \
    "$IMAGE_NAME"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date '+%H:%M:%S')] Task completed successfully"
else
    echo "[$(date '+%H:%M:%S')] Task failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE
