import os
os.environ["COLUMNS"] = "200"

import click
import requests
import subprocess

from pkm.config import get_api_base
from pkm.commands.task import (
    task_add, task_ls, task_get, task_update,
    task_done, task_approve, task_delete
)
from pkm.commands.project import (
    project_add, project_ls, project_get, project_update,
    project_delete, project_archive
)
from pkm.commands.inbox import inbox_add, extract_urls, generate_inbox_filename, parse_url_with_claude
from pkm.commands.reflow import reflow_run, reflow_status, reflow_stage2
from pkm.commands.config import config_default, config_interactive
from pkm.commands.server_cmd import (
    server_start as _server_start,
    server_stop as _server_stop,
    server_status as _server_status,
    is_server_running as _is_server_running,
    _is_container_running
)
from pkm.workspace import (
    get_workspace_base_path, get_task_workspace_base,
    get_project_workspace_base, get_inbox_base
)

API_BASE = get_api_base()


# Wrapper functions that call server_cmd implementations
# These wrappers exist so that tests can monkeypatch pkm.cli.is_server_running
def server_start():
    _server_start(API_BASE)


def server_stop():
    """Stop the PKM server using docker compose"""
    _server_stop()


def server_status():
    """Display server status"""
    if _is_container_running():
        click.echo("Server is running")
        if is_server_running():
            click.echo("Service is ready")
        else:
            click.echo("Service is not ready")
    else:
        click.echo("Server is not running")


def is_server_running():
    """Check if server is running"""
    return _is_server_running(API_BASE)


@click.group(context_settings=dict(max_content_width=200))
def cli():
    """PKM CLI - Task and Project Management

工作流示例:

  inbox 收集灵感 -> pkm inbox add "想法"

  task 创建任务 -> pkm task add "任务名" --priority high --project <项目ID>

  task ls 查看列表 -> pkm task ls / pkm task ls -p (显示路径)

  task get 查看详情 -> pkm task get <id>

  task update 更新 -> pkm task update <id> --title "新标题" --priority medium

  task approve 批准 -> pkm task approve <id> (done -> approved，回流知识)

  project 关联项目 -> pkm project add "项目名" / pkm project get <id>

  工作中 编辑文件 -> 在工作区 ~/.pkm/10_Tasks/TASK_xxx/ 下编辑文件

  task done 完成 -> pkm task done <id>

  reflow 知识提炼 -> 自动每3小时执行，也可手动 pkm reflow run / stage2

Commands:
  inbox    Inbox commands for capturing notes
  project  Project management
  reflow   Knowledge reflow management
  server   Server management
  task     Task management
"""
    pass


# Config command
@cli.command()
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


# Inbox commands
@cli.group()
def inbox():
    """Inbox commands for capturing notes"""
    pass


@inbox.command()
@click.argument("content")
@click.option("--parse", is_flag=True, help="Parse URLs in content using AI")
def add(content, parse):
    """Capture content to inbox

    Examples:
      pkm inbox add "想法"
      pkm inbox add "Some notes"
      pkm inbox add --parse "Check this https://example.com article"
    """
    inbox_add(content, parse)


# Server commands
@cli.group()
def server():
    """Server management"""
    pass


@server.command()
def start():
    server_start()


@server.command()
def stop():
    server_stop()


@server.command()
def status():
    server_status()


@cli.command()
def status():
    """Show PKM status

    Display server, tasks, projects, knowledge reflow, and workspace info.
    """
    click.echo("PKM Status")
    click.echo("==========")

    # Server info
    if _is_container_running():
        click.echo(f"Server:      Running")
        if is_server_running():
            click.echo("Service:    Ready")
        else:
            click.echo("Service:    Not ready")
    else:
        click.echo("Server:      Not running")
    click.echo(f"API:         {API_BASE}")

    # Get all status from single API call
    try:
        r = requests.get(f"{API_BASE}/api/status", timeout=5)
        r.raise_for_status()
        data = r.json()

        # Tasks count
        tasks = data.get("tasks", {})
        total = tasks.get("total", 0)
        by_status = tasks.get("by_status", {})
        status_str = ", ".join(f"{v} {k}" for k, v in sorted(by_status.items()))
        click.echo(f"Tasks:       {total} total, {status_str}")

        # Projects count
        projects = data.get("projects", {})
        total = projects.get("total", 0)
        by_status = projects.get("by_status", {})
        status_str = ", ".join(f"{v} {k}" for k, v in sorted(by_status.items()))
        click.echo(f"Projects:    {total} total, {status_str}")

        # Knowledge info
        click.echo("\nKnowledge:")
        knowledge = data.get("knowledge", {})
        click.echo(f"  Pending approved: {knowledge.get('pending_approved_tasks', 0)}")
        click.echo(f"  Pending reflows: {knowledge.get('pending_reflows', 0)}")
        claude = "Available" if knowledge.get("claude_available") else "Not available"
        click.echo(f"  Claude CLI: {claude}")

        if data.get("last_updated"):
            click.echo(f"  Last updated: {data['last_updated']}")

    except requests.RequestException as e:
        click.echo(f"  Unable to fetch: {e}")

    # Workspace paths
    click.echo("\nWorkspace:")
    click.echo(f"  Base:     {get_workspace_base_path()}")
    click.echo(f"  Tasks:    {get_task_workspace_base()}")
    click.echo(f"  Projects: {get_project_workspace_base()}")
    click.echo(f"  Inbox:    {get_inbox_base()}")

    # Logs
    click.echo("\nLogs:")
    log_dir = os.path.expanduser("~/.pkm/logs")
    click.echo(f"  Path:     {log_dir}")

    # GitHub remote
    click.echo("\nGitHub:")
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            remote_url = result.stdout.strip()
            remote_url = remote_url.replace(".git", "")
            if "github.com" in remote_url:
                remote_url = remote_url.replace("git@github.com:", "https://github.com/")
            click.echo(f"  Remote:   {remote_url}")
        else:
            click.echo("  Remote:    Not configured")
    except Exception:
        click.echo("  Remote:    Not available")

    # Version info
    click.echo("\nVersion:")
    click.echo("  Client:   snapshot")
    click.echo("  Server:   snapshot")


# Task commands
@cli.group()
def task():
    """Task management"""
    pass


@task.command()
@click.argument("title", required=False)
@click.option("--priority", type=click.Choice(["high", "medium", "low"]), default="medium")
@click.option("--due")
@click.option("--project")
def add(title, priority, due, project):
    """Add a new task  eg: pkm task add "写周报" --priority high --due 2026-04-20 --project 1"""
    if not title:
        from pkm.commands.task import task_add_interactive
        task_add_interactive(API_BASE)
    else:
        task_add(title, priority, due, project, API_BASE)


@task.command()
@click.option("--status")
@click.option("--project")
@click.option("-a", "--all", "show_all", is_flag=True, help="显示完整信息")
def ls(status, project, show_all):
    """List tasks  eg: pkm task ls --status new --project 1 -a"""
    task_ls(status, project, show_all, API_BASE)


@task.command()
@click.argument("task_id")
def get(task_id):
    """Get task details  eg: pkm task get 1"""
    task_get(task_id, API_BASE)


@task.command()
@click.argument("task_id", required=False)
@click.option("--title")
@click.option("--priority")
@click.option("--progress")
def update(task_id, title, priority, progress):
    """Update a task  eg: pkm task update 1 --title "新标题" --priority high --progress 100"""
    if not task_id:
        from pkm.commands.task import task_update_interactive
        task_update_interactive(API_BASE)
    else:
        task_update(task_id, title, None, priority, progress, API_BASE)


@task.command()
@click.argument("task_id")
def done(task_id):
    """Mark task as completed  eg: pkm task done 1"""
    task_done(task_id, API_BASE)


@task.command()
@click.argument("task_id")
def approve(task_id):
    """Approve task for knowledge reflow (done -> approved)  eg: pkm task approve 1"""
    task_approve(task_id, API_BASE)


@task.command()
@click.argument("task_id")
def delete(task_id):
    """Delete a task by ID or index  eg: pkm task delete 1"""
    task_delete(task_id, API_BASE)


# Project commands
@cli.group()
def project():
    """Project management"""
    pass


@project.command()
@click.argument("name")
@click.option("--description")
def add(name, description):
    """Add a new project  eg: pkm project add "项目名" --description "描述" """
    project_add(name, description, API_BASE)


@project.command()
@click.option("--status")
@click.option("-a", "--all", "show_all", is_flag=True, help="显示完整信息")
def ls(status, show_all):
    """List projects  eg: pkm project ls --status active"""
    project_ls(status, show_all, API_BASE)


@project.command()
@click.argument("project_id")
def get(project_id):
    """Get project details  eg: pkm project get 1"""
    project_get(project_id, API_BASE)


@project.command()
@click.argument("project_id")
@click.option("--name")
@click.option("--description")
def update(project_id, name, description):
    """Update a project  eg: pkm project update 1 --name "新名称" --description "新描述" """
    project_update(project_id, name, description, API_BASE)


@project.command()
@click.argument("project_id")
def delete(project_id):
    """Delete a project by ID, index, or 'default'  eg: pkm project delete 1"""
    project_delete(project_id, API_BASE)


@project.command()
@click.argument("project_id")
def archive(project_id):
    """Archive a project  eg: pkm project archive 1"""
    project_archive(project_id, API_BASE)


# Knowledge Reflow commands
@cli.group()
def reflow():
    """Knowledge reflow management"""
    pass


@reflow.command()
def run():
    """Manually trigger knowledge reflow

    Example:
      pkm reflow run"""
    reflow_run(API_BASE)


@reflow.command()
def status():
    """Get reflow status

    Example:
      pkm reflow status"""
    reflow_status(API_BASE)


@reflow.command()
@click.option("--batch-size", default=5, help="每批处理项目数")
def stage2(batch_size):
    """Manually trigger Stage2 knowledge distillation

    Example:
      pkm reflow stage2
      pkm reflow stage2 --batch-size 3
    """
    reflow_stage2(batch_size, API_BASE)


if __name__ == "__main__":
    cli()
