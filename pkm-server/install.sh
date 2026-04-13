#!/bin/bash
set -e

PKM_HOME="${PKM_HOME:-$HOME/.pkm}"
REPO="EvilJoker/pkmskill"
GH_DOWNLOAD="https://github.com/$REPO/releases/download"
IMAGE="ghcr.io/eviljoker/pkm"

usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  snapshot    Install latest snapshot (wheel + Docker image)"
    echo "  -h, --help  Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 snapshot    # Install latest snapshot version"
}

download_wheel() {
    local version=${1:-snapshot}
    # wheel 文件名格式: pkm-{version}-py3-none-any.whl
    # snapshot 版本对应 0.0.0
    local whl_name="pkm-0.0.0-py3-none-any.whl"
    local whl_url="$GH_DOWNLOAD/$version/$whl_name"

    echo "Downloading wheel from: $whl_url"
    curl -sL "$whl_url" -o "$PKM_HOME/pkm.whl" || {
        echo "Failed to download wheel from $whl_url"
        return 1
    }

    echo "Installing wheel..."
    pip install "$PKM_HOME/pkm.whl"
}

pull_docker_image() {
    local tag=${1:-snapshot}
    echo "Pulling Docker image: $IMAGE:$tag"
    docker pull "$IMAGE:$tag" || {
        echo "Docker pull failed"
        return 1
    }
}

do_snapshot() {
    echo "Installing PKM snapshot..."

    mkdir -p "$PKM_HOME"

    # Use snapshot tag directly (no API needed)
    local version="snapshot"
    echo "Version: $version"

    # Download and install wheel
    download_wheel "$version" || echo "Wheel download failed, continuing..."

    # Pull Docker image
    pull_docker_image "$version" || echo "Docker pull failed, continuing..."

    echo ""
    echo "Snapshot installation complete!"
    echo "Installed to: $PKM_HOME"
    echo "Wheel: $PKM_HOME/pkm.whl"
    echo "Docker image: $IMAGE:$version"
}

# Main
case "${1:-}" in
    -h|--help|help)
        usage
        exit 0
        ;;
    snapshot)
        do_snapshot
        exit 0
        ;;
    *)
        if [ -z "$1" ]; then
            usage
            exit 1
        else
            echo "Unknown command: $1"
            usage
            exit 1
        fi
        ;;
esac
