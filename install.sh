#!/bin/bash
set -e

REPO="EvilJoker/pkmskill"
ASSETS_URL="https://api.github.com/repos/${REPO}/releases/latest"

echo "=== Installing PKM CLI ==="

WHEEL_URL=$(curl -sSL "$ASSETS_URL" | grep "browser_download_url" | grep "\.whl" | head -1 | cut -d '"' -f 4)

if [ -z "$WHEEL_URL" ]; then
    echo "Error: No wheel found in latest release"
    exit 1
fi

echo "Downloading: $WHEEL_URL"
pip install "$WHEEL_URL"

echo ""
echo "=== Downloading PKM Docker Image ==="
docker pull ghcr.io/${REPO}:latest

echo ""
echo "=== PKM installed successfully ==="
pkm --version
