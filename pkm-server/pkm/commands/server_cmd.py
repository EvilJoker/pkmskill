"""Server commands - Docker compose based container management"""

import click
import requests
import subprocess
from pathlib import Path

PKM_DIR = Path("~/.pkm").expanduser()
COMPOSE_PATH = PKM_DIR / "docker-compose.yml"


def is_server_running(api_base=None):
    """Check if container is running and service is healthy"""
    if api_base is None:
        from pkm.config import get_api_base
        api_base = get_api_base()
    try:
        r = requests.get(f"{api_base}/health", timeout=1)
        return r.status_code == 200
    except requests.RequestException:
        return False


def _is_container_running():
    """Check if container is running via docker compose ps"""
    result = subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_PATH), "ps", "-q"],
        capture_output=True, text=True
    )
    return bool(result.stdout.strip())


def server_start(api_base=None):
    """Start the container using docker compose"""
    if not COMPOSE_PATH.exists():
        click.echo("Error: docker-compose.yml not found. Run 'pkm config' first.")
        return

    # Check if already running
    if _is_container_running():
        click.echo("Server is already running")
        return

    result = subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_PATH), "up", "-d"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        click.echo("Server started")
    else:
        click.echo(f"Failed to start server: {result.stderr}")


def server_stop(api_base=None):
    """Stop the container using docker compose"""
    if not COMPOSE_PATH.exists():
        click.echo("Error: docker-compose.yml not found.")
        return

    subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_PATH), "down"],
        capture_output=True
    )
    click.echo("Server stopped")


def server_status(api_base=None):
    """Check container status"""
    if api_base is None:
        from pkm.config import get_api_base
        api_base = get_api_base()

    if not COMPOSE_PATH.exists():
        click.echo("Server not configured (docker-compose.yml not found)")
        return

    if _is_container_running():
        click.echo("Server is running")
        if is_server_running(api_base):
            click.echo("Service is ready")
        else:
            click.echo("Service is not ready")
    else:
        click.echo("Server is not running")
