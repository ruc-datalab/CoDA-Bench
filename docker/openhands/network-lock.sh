#!/bin/bash
# network-lock.sh - Disable network tools to prevent data leakage

set -e

echo "[network-lock] Disabling network tools for agent terminal"

# Disable wget, curl (when used by agent), apt-get, apt
for tool in wget apt-get apt; do
    if command -v "$tool" &>/dev/null; then
        TOOL_PATH=$(which "$tool")
        mv "$TOOL_PATH" "${TOOL_PATH}.disabled" 2>/dev/null || true
        cat > "$TOOL_PATH" << 'TOOLEOF'
#!/bin/bash
echo "ERROR: Network access is disabled in this evaluation environment." >&2
echo "All required data is available in /data. Use local files only." >&2
exit 1
TOOLEOF
        chmod +x "$TOOL_PATH"
    fi
done

# Configure pip to refuse network operations
mkdir -p /root/.config/pip
cat > /root/.config/pip/pip.conf << 'PIPEOF'
[global]
no-index = true
index-url = file:///dev/null
PIPEOF

echo "[network-lock] Done. Network tools disabled, pip offline."
