#!/bin/bash
set -e

PKM_HOME="${PKM_HOME:-$HOME/.pkm}"
REPO="EvilJoker/pkmskill"
GH_DOWNLOAD="https://github.com/$REPO/releases/download"
IMAGE="ghcr.io/eviljoker/pkm"
VERSION="snapshot"
WHL_NAME="pkm-0.0.0-py3-none-any.whl"

usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Install latest snapshot"
}

download_and_install_wheel() {
    local whl_url="$GH_DOWNLOAD/$VERSION/$WHL_NAME"
    echo "Downloading wheel from: $whl_url"
    curl -sL "$whl_url" -o "$PKM_HOME/$WHL_NAME" || {
        echo "Failed to download wheel from $whl_url"
        return 1
    }
    echo "Installing wheel..."
    pip install --force-reinstall --no-deps --ignore-installed --find-links "$PKM_HOME" "$PKM_HOME/$WHL_NAME"
}

pull_docker_image() {
    echo "Pulling Docker image: $IMAGE:$VERSION"
    docker pull "$IMAGE:$VERSION" || {
        echo "Docker pull failed"
        return 1
    }
}

setup_docker_compose() {
    echo "Setting up docker-compose.yml..."
    local compose_file="$PKM_HOME/docker-compose.yml"
    cat > "$compose_file" << 'EOF'
services:
  pkm:
    image: ghcr.io/eviljoker/pkm:snapshot
    container_name: pkm-server
    restart: unless-stopped
    ports:
      - "8890:8890"
    volumes:
      - ~/.pkm:/root/.pkm
    environment:
      - CLAUDECODE=1
      - ANTHROPIC_BASE_URL=${BASE_URL}
      - ANTHROPIC_AUTH_TOKEN=${API_KEY}
      - ANTHROPIC_MODEL=${MODEL}
EOF
    echo "Docker compose file created at: $compose_file"
}

cleanup_old_containers() {
    echo "Cleaning up old containers..."
    docker rm -f pkm-server pkm-server-dev 2>/dev/null || true
}

do_install() {
    echo "Installing PKM snapshot..."

    mkdir -p "$PKM_HOME"
    echo "Version: $VERSION"

    # Clean up old containers to avoid conflicts
    cleanup_old_containers

    # Download and install wheel
    download_and_install_wheel || echo "Wheel download failed, continuing..."

    # Pull Docker image
    pull_docker_image || echo "Docker pull failed, continuing..."

    # Setup docker-compose.yml with correct port mapping
    setup_docker_compose

    # Check if config exists - if so, skip config (preserve user data)
    if [ -f "$PKM_HOME/config.yaml" ]; then
        echo ""
        echo "Config already exists at $PKM_HOME/config.yaml"
        echo "Skipping configuration - preserving user data"
        echo ""
        echo "To configure manually, run: pkm config"
    else
        # First install - run config
        echo "First install - running pkm config..."
        pkm config
    fi

    echo ""
    echo "Installation complete!"
    echo "Installed to: $PKM_HOME"
    echo "Wheel: $PKM_HOME/$WHL_NAME"
    echo "Docker image: $IMAGE:$VERSION"
    echo ""
    echo "Services: pkm server start/stop/status"
}

# Main
case "${1:-}" in
    -h|--help|help)
        usage
        exit 0
        ;;
    *)
        do_install
        exit 0
        ;;
esac
