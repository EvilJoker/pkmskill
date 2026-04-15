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
    curl -sL "$whl_url" -o "$PKM_HOME/$whl_name" || {
        echo "Failed to download wheel from $whl_url"
        return 1
    }

    echo "Installing wheel..."
    pip install "$PKM_HOME/$whl_name"
}

pull_docker_image() {
    local tag=${1:-snapshot}
    echo "Pulling Docker image: $IMAGE:$tag"
    docker pull "$IMAGE:$tag" || {
        echo "Docker pull failed"
        return 1
    }
}

start_container() {
    local tag=${1:-snapshot}
    local container_name="pkm-server"
    local port="8890:7890"
    local pkm_home="${PKM_HOME:-$HOME/.pkm}"

    echo "Starting container with restart policy..."

    # Stop existing container if exists
    docker stop "$container_name" 2>/dev/null || true
    docker rm "$container_name" 2>/dev/null || true

    # Run container with restart unless-stopped (auto-restart on failure and boot)
    docker run -d \
        --name "$container_name" \
        --restart unless-stopped \
        -p "$port" \
        -v "$pkm_home:/root/.pkm" \
        "$IMAGE:$tag"

    echo "Container started: $container_name"
}

do_snapshot() {
    echo "Installing PKM snapshot..."

    mkdir -p "$PKM_HOME"

    # Use snapshot tag directly (no API needed)
    local version="snapshot"
    local whl_name="pkm-0.0.0-py3-none-any.whl"
    echo "Version: $version"

    # Download and install wheel
    download_wheel "$version" || echo "Wheel download failed, continuing..."

    # Pull Docker image
    pull_docker_image "$version" || echo "Docker pull failed, continuing..."

    # Start container with auto-restart
    start_container "$version"

    echo ""
    echo "Snapshot installation complete!"
    echo "Installed to: $PKM_HOME"
    echo "Wheel: $PKM_HOME/$whl_name"
    echo "Docker image: $IMAGE:$version"
    echo "Container: $container_name (restart: unless-stopped)"
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
