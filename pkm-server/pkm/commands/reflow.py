"""Reflow commands"""

import click
import requests


def reflow_run(api_base):
    """Manually trigger knowledge reflow"""
    click.echo("Starting knowledge reflow...")
    r = requests.post(f"{api_base}/api/knowledge/reflow")
    r.raise_for_status()
    result = r.json()
    click.echo(f"Reflow completed: {result['message']}")


def reflow_status(api_base):
    """Get reflow status"""
    r = requests.get(f"{api_base}/api/knowledge/status")
    r.raise_for_status()
    result = r.json()
    click.echo(f"Claude CLI available: {result['claude_available']}")
