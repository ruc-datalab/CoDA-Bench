#!/bin/bash
# Build OpenHands Docker image for CoDA-Bench evaluation

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Building CoDA-Bench Docker image..."
echo "======================================"

echo ""
echo "Building OpenHands..."
cd "$SCRIPT_DIR/openhands"
docker build -t codabench-openhands:latest .
echo "✓ codabench-openhands:latest built"

echo ""
echo "======================================"
echo "Build complete!"
echo ""
echo "To run evaluation:"
echo "  cd .."
echo "  export LLM_API_KEY='your-api-key'"
echo "  python scripts/run_evaluation.py --model gpt-5.5 --output results/test"
