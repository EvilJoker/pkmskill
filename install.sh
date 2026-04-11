#!/bin/bash
set -e

REPO="EvilJoker/pkmskill"

show_help() {
    echo "Usage: $0 [snapshot]"
    echo ""
    echo "Options:"
    echo "  snapshot    Install snapshot version (latest commit build)"
    echo "  (default)  Install latest release version"
    echo ""
    echo "Examples:"
    echo "  $0           # Install latest release"
    echo "  $0 snapshot  # Install latest snapshot"
}

install_from_release() {
    local release_tag="$1"
    local release_name="$2"

    if [ "$release_tag" == "latest" ]; then
        ASSETS_URL="https://api.github.com/repos/${REPO}/releases/${release_tag}"
    else
        ASSETS_URL="https://api.github.com/repos/${REPO}/releases/tags/${release_tag}"
    fi

    echo "=== Installing PKM ${release_name} ==="

    WHEEL_URL=$(curl -sSL "$ASSETS_URL" | grep "browser_download_url" | grep "\.whl" | head -1 | cut -d '"' -f 4)

    if [ -z "$WHEEL_URL" ]; then
        echo "Error: No wheel found in ${release_name}"
        exit 1
    fi

    echo "Downloading: $WHEEL_URL"
    pip install "$WHEEL_URL"

    echo ""
    echo "=== Downloading PKM Docker Image ==="
    if [ "$release_tag" == "snapshot" ]; then
        docker pull ghcr.io/${REPO}:snapshot
    else
        docker pull ghcr.io/${REPO}:latest
    fi

    echo ""
    echo "=== PKM installed successfully ==="
    pkm --version
}

case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    snapshot)
        install_from_release "snapshot" "Snapshot"
        ;;
    *)
        install_from_release "latest" "Latest"
        ;;
esac
