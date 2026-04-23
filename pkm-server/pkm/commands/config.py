"""Config command for PKM setup and management"""

import click
import subprocess
import time
import yaml
from pathlib import Path

PKM_DIR = Path("~/.pkm").expanduser()
CONFIG_PATH = PKM_DIR / "config.yaml"
ENV_PATH = PKM_DIR / ".env"
IMAGE_NAME = "ghcr.io/eviljoker/pkm:snapshot"

DEFAULT_CONFIG = {
    "port": 8890,
    "host_port": 8890,
    "log_level": "info",
}

DOCKER_COMPOSE_CONTENT = """services:
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
"""

CONFIG_ITEMS = [
    {"key": "API_KEY", "prompt": "API_KEY", "default": ""},
    {"key": "BASE_URL", "prompt": "BASE_URL", "default": "https://api.anthropic.com"},
    {"key": "MODEL", "prompt": "MODEL", "default": "anthropic/claude-3.5-sonnet"},
]


def _ensure_pkm_dir():
    """Ensure ~/.pkm directory exists"""
    PKM_DIR.mkdir(parents=True, exist_ok=True)


def _check_image_exists():
    """Check if Docker image exists"""
    result = subprocess.run(
        ["docker", "image", "ls", IMAGE_NAME, "-q"],
        capture_output=True, text=True
    )
    return bool(result.stdout.strip())


def _ensure_config_files():
    """Ensure config files exist with defaults"""
    _ensure_pkm_dir()

    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f)

    if not ENV_PATH.exists():
        with open(ENV_PATH, "w") as f:
            f.write("# PKM Configuration\n")
            f.write(f"# API_KEY=your-api-key-here\n")
            f.write(f"# BASE_URL=https://api.anthropic.com\n")
            f.write(f"# MODEL=anthropic/claude-3.5-sonnet\n")


def _get_value(key):
    """从 .env 读取指定 key 的值"""
    if not ENV_PATH.exists():
        return None
    content = ENV_PATH.read_text()
    for line in content.splitlines():
        if line.startswith(f"{key}="):
            value = line.split("=", 1)[1].strip()
            if value and not value.startswith("#"):
                return value
    return None


def _update_value(key, value):
    """更新 .env 中指定 key 的值"""
    lines = []
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text().splitlines()

    new_lines = []
    found = False
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}")

    ENV_PATH.write_text("\n".join(new_lines) + "\n")


def _ensure_docker_compose_file():
    """确保 docker-compose.yml 存在"""
    compose_path = PKM_DIR / "docker-compose.yml"
    if not compose_path.exists():
        with open(compose_path, "w") as f:
            f.write(DOCKER_COMPOSE_CONTENT)
    return compose_path


def _restart_container():
    """Stop and start the container using docker compose"""
    compose_path = _ensure_docker_compose_file()

    # Stop and remove old container
    subprocess.run(
        ["docker", "compose", "-f", str(compose_path), "down"],
        capture_output=True
    )

    # Start new container
    subprocess.run(
        ["docker", "compose", "-f", str(compose_path), "up", "-d"],
        check=True
    )


def _wait_for_service(timeout=30):
    """Wait for service to be ready"""
    import requests
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get("http://localhost:8890/health", timeout=1)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False


def config_default():
    """Non-interactive default configuration"""
    _ensure_pkm_dir()

    if not _check_image_exists():
        click.echo("Error: Docker image not found. Please run install.sh first.")
        return

    _ensure_config_files()
    _restart_container()

    if _wait_for_service():
        click.echo("✓ Server started successfully")
        click.echo("  Use 'pkm server status' to check status")
    else:
        click.echo("✗ Server failed to start, check with 'docker logs pkm-server'")


def config_interactive():
    """Interactive configuration"""
    _ensure_pkm_dir()

    if not _check_image_exists():
        click.echo("Error: Docker image not found. Please run install.sh first.")
        return

    _ensure_config_files()

    click.echo("=== PKM Configuration ===")
    click.echo("** only support anthropic like **\n")

    for item in CONFIG_ITEMS:
        current = _get_value(item["key"])
        click.echo(f"Current {item['prompt']}: {current or '(not set)'}")
        new_value = click.prompt(
            f"Enter {item['prompt']} (press Enter to keep current)"
        ).strip()
        if new_value:
            _update_value(item["key"], new_value)

    # Restart service
    click.echo("\nRestarting server...")
    _restart_container()

    if _wait_for_service():
        click.echo("✓ Configuration complete!")
        click.echo("✓ Server is running")
        click.echo("  Use 'pkm status' to view status")
        click.echo("  Use 'pkm server start/stop/status' to manage")
    else:
        click.echo("✗ Server failed to start")


@click.command()
@click.option("--default", is_flag=True, help="非交互式默认配置")
def config(default):
    """引导配置 PKM

    示例:
      pkm config              # 交互式引导
      pkm config --default   # 使用默认配置启动
    """
    if default:
        config_default()
    else:
        config_interactive()
