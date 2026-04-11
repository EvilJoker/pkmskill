#!/bin/bash
set -e

REPO="EvilJoker/pkmskill"

show_help() {
    echo "Usage: $0 [snapshot|version]"
    echo ""
    echo "Options:"
    echo "  snapshot    Install snapshot version (latest commit build)"
    echo "  version     Install specific version (e.g., v0.1.0)"
    echo "  (default)  Install latest release version"
    echo ""
    echo "Examples:"
    echo "  $0           # Install latest release"
    echo "  $0 snapshot  # Install latest snapshot"
    echo "  $0 v0.1.0   # Install specific version"
}

get_latest_version() {
    curl -sSL "https://api.github.com/repos/${REPO}/releases/latest" 2>/dev/null | grep '"tag_name"' | sed 's/.*"tag_name": "//;s/",//' | tr -d ' '
}

install_pkm() {
    local release_tag="$1"
    local release_name="$2"

    echo "=== Installing PKM ${release_name} ==="

    if [ "$release_tag" == "snapshot" ]; then
        WHEEL_URL="https://github.com/${REPO}/releases/download/${release_tag}/pkm-0.0.0-py3-none-any.whl"
    else
        # For latest or specific version, construct URL directly
        WHEEL_URL="https://github.com/${REPO}/releases/download/${release_tag}/pkm-release-${release_tag}-py3-none-any.whl"
    fi

    echo "Downloading: $WHEEL_URL"
    pip install "$WHEEL_URL"

    echo ""
    echo "=== Downloading PKM Docker Image ==="
    if [ "$release_tag" == "snapshot" ]; then
        docker pull ghcr.io/eviljoker/pkm:snapshot
    else
        docker pull ghcr.io/eviljoker/pkm:latest
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
        install_pkm "snapshot" "Snapshot"
        ;;
    "")
        # Default: get latest version and install
        LATEST_VERSION=$(get_latest_version)
        if [ -z "$LATEST_VERSION" ]; then
            echo "Error: Could not fetch latest version"
            exit 1
        fi
        install_pkm "$LATEST_VERSION" "Latest ($LATEST_VERSION)"
        ;;
    *)
        install_pkm "$1" "Version $1"
        ;;
esac
