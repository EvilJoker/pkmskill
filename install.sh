#!/bin/bash
set -e

REPO="EvilJoker/pkmskill"
PKM_HOME="${PKM_HOME:-$HOME/.pkm}"
BACKUP_DIR="${HOME}/.pkm_backup"

show_help() {
    echo "Usage: $0 [snapshot|version] [-y]"
    echo ""
    echo "Options:"
    echo "  snapshot    Install snapshot version (latest commit build)"
    echo "  version     Install specific version (e.g., v0.1.0)"
    echo "  (default)  Install latest release version"
    echo "  -y         Skip backup confirmation"
    echo ""
    echo "Examples:"
    echo "  $0           # Install latest release"
    echo "  $0 snapshot  # Install latest snapshot"
    echo "  $0 v0.1.0   # Install specific version"
    echo "  $0 snapshot -y  # Install snapshot without confirmation"
}

get_latest_version() {
    curl -sSL "https://api.github.com/repos/${REPO}/releases/latest" 2>/dev/null | grep '"tag_name"' | sed 's/.*"tag_name": "//;s/",//' | tr -d ' '
}

is_pkm_installed() {
    [ -d "$PKM_HOME" ]
}

do_backup() {
    local backup_path="${BACKUP_DIR}/$(date +%Y%m%d_%H%M%S)"
    echo "=== Backing up existing PKM ==="
    mkdir -p "$BACKUP_DIR"
    cp -r "$PKM_HOME" "$backup_path"
    echo "Backup saved to: $backup_path"
}

confirm_backup() {
    if [ "$SKIP_CONFIRM" == "true" ]; then
        return 0
    fi
    echo ""
    echo "⚠️  PKM is already installed at $PKM_HOME"
    echo "⚠️  A backup will be created before upgrading."
    echo ""
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
}

start_docker() {
    echo "=== Starting PKM Server ==="
    cd "$PKM_HOME/pkm-server" 2>/dev/null || cd "$(pip show pkm 2>/dev/null | grep 'Location:' | cut -d' ' -f2)/pkm-server" 2>/dev/null || true
    if [ -f "docker-compose.yml" ]; then
        docker compose up -d
    elif [ -f "docker-compose.prod.yml" ]; then
        docker compose -f docker-compose.prod.yml up -d
    fi
}

test_pkm() {
    echo "=== Testing PKM ==="
    pkm status
}

install_pkm() {
    local release_tag="$1"
    local release_name="$2"
    local is_upgrade=false

    # Check if already installed
    if is_pkm_installed; then
        is_upgrade=true
        echo "=== PKM upgrade detected ==="
        confirm_backup
        do_backup

        echo "=== Stopping existing PKM Server ==="
        cd "$PKM_HOME/pkm-server" 2>/dev/null || cd "$(pip show pkm 2>/dev/null | grep 'Location:' | cut -d' ' -f2)/pkm-server" 2>/dev/null || true
        if [ -f "docker-compose.yml" ]; then
            docker compose down 2>/dev/null || true
        elif [ -f "docker-compose.prod.yml" ]; then
            docker compose -f docker-compose.prod.yml down 2>/dev/null || true
        fi

        echo "=== Removing old installation ==="
        rm -rf "$PKM_HOME"
    fi

    echo "=== Installing PKM ${release_name} ==="

    if [ "$release_tag" == "snapshot" ]; then
        WHEEL_URL="https://github.com/${REPO}/releases/download/${release_tag}/pkm-0.0.0-py3-none-any.whl"
    else
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
    if [ "$is_upgrade" == "true" ]; then
        echo "=== PKM upgraded successfully ==="
    else
        echo "=== PKM installed successfully ==="
    fi
    pkm --version
    echo ""

    start_docker
    test_pkm
}

# Parse arguments
SKIP_CONFIRM=false
TARGET_VERSION=""
TARGET_NAME=""

for arg in "$@"; do
    case "$arg" in
        -y|--yes)
            SKIP_CONFIRM=true
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            TARGET_VERSION="$arg"
            ;;
    esac
done

case "${TARGET_VERSION:-}" in
    snapshot)
        install_pkm "snapshot" "Snapshot"
        ;;
    "")
        LATEST_VERSION=$(get_latest_version)
        if [ -z "$LATEST_VERSION" ]; then
            echo "Error: Could not fetch latest version"
            exit 1
        fi
        install_pkm "$LATEST_VERSION" "Latest ($LATEST_VERSION)"
        ;;
    *)
        install_pkm "$TARGET_VERSION" "Version $TARGET_VERSION"
        ;;
esac
