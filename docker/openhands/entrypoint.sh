#!/bin/bash
set -e

# Validate task file exists
if [ ! -f /workspace/task_description.txt ]; then
    echo "ERROR: /workspace/task_description.txt not found"
    exit 1
fi

# Apply network restrictions (requires --cap-add=NET_ADMIN)
# Only the LLM API endpoint will be reachable
if [ "${DISABLE_NETWORK_LOCK:-0}" != "1" ]; then
    /opt/network-lock.sh || echo "WARNING: network-lock failed (missing NET_ADMIN?), running without network isolation"
fi

# Run OpenHands via SDK script
python3 /opt/openhands-sdk.py

exit $?
