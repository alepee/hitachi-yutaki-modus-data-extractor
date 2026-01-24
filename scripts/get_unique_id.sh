#!/bin/bash
#
# Get Unique ID from Hitachi ATW-MBS-02 Gateway
#
# Usage:
#   ./scripts/get_unique_id.sh
#

set -e

# Go to project root
cd "$(dirname "$0")/.."

echo ""
echo "======================================================================"
echo "Hitachi ATW-MBS-02 Gateway - Unique ID Reader"
echo "======================================================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ 'uv' is not installed."
    echo ""
    echo "Install it with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    exit 1
fi

# Ask for gateway IP address
read -p "Enter your gateway IP address [192.168.0.4]: " gateway_ip

# Use default if empty
gateway_ip="${gateway_ip:-192.168.0.4}"

echo ""
echo "Connecting to $gateway_ip..."
echo ""

# Run the script with uv
uv run python get_gateway_unique_id.py --ip "$gateway_ip"

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "======================================================================"
    echo "Please share the unique ID above on GitHub issue #162"
    echo "https://github.com/alepee/hass-hitachi_yutaki/issues/162"
    echo "======================================================================"
fi

exit $exit_code
