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
    click.echo(f"Pending approved tasks: {result['pending_approved_tasks']}")
    click.echo(f"Pending reflows: {result['pending_reflows']}")
    click.echo(f"Claude CLI available: {result['claude_available']}")
    click.echo(f"Config: {result['config']}")

    # Stage2 status
    try:
        r2 = requests.get(f"{api_base}/api/knowledge/reflow/status/stage2")
        r2.raise_for_status()
        stage2_result = r2.json()
        click.echo(f"\n--- Stage2 ---")
        click.echo(f"Pending projects: {stage2_result['pending_projects']}")
    except requests.RequestException:
        click.echo(f"\n--- Stage2 ---")
        click.echo("Stage2 not available")


def reflow_stage2(batch_size, api_base):
    """Manually trigger Stage2 knowledge distillation"""
    click.echo("Starting Stage2 knowledge distillation...")
    r = requests.post(f"{api_base}/api/knowledge/reflow/stage2")
    r.raise_for_status()
    result = r.json()
    click.echo(f"Stage2 completed: {result['message']}")
