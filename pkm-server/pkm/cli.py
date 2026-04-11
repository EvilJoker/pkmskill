import click
import requests
import os
import time
import signal
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from pkm.config import get_port
from workspace import create_task_workspace, create_project_workspace

# Note: When using docker-compose, exposed port is 8890, server listens on 7890 internally
# Use PKM_API_BASE env var or create ~/.pkm/config.yaml to override
API_BASE = os.environ.get("PKM_API_BASE", f"http://localhost:{get_port()}")
PID_FILE = os.path.expanduser("~/.pkm/pkm-server.pid")


def get_pid():
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            return f.read().strip()
    return None


def save_pid(pid):
    os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
    with open(PID_FILE, "w") as f:
        f.write(str(pid))


def is_server_running():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=1)
        return r.status_code == 200
    except:
        return False


def server_start():
    if is_server_running():
        click.echo("Server is already running")
        return
    import subprocess
    log_dir = os.path.expanduser("~/.pkm/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "pkm-server.log")
    with open(log_file, "w") as f:
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7890"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            stdout=f, stderr=f
        )
    save_pid(proc.pid)
    time.sleep(1)
    if is_server_running():
        click.echo(f"Server started (PID: {proc.pid})")
    else:
        click.echo("Server failed to start, check logs")


def server_stop():
    pid = get_pid()
    if not pid:
        click.echo("Server not running")
        return
    try:
        os.kill(int(pid), signal.SIGTERM)
        click.echo("Server stopped")
    except ProcessLookupError:
        click.echo("Server not found")
    os.remove(PID_FILE)


def server_status():
    if is_server_running():
        click.echo("Server is running")
    else:
        click.echo("Server is not running")


@click.group()
def cli():
    """PKM CLI - Task and Project Management"""
    pass


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


# Task commands
@cli.group()
def task():
    """Task management (Quadrant: Q1=urgent+important, Q2=important, Q3=urgent, Q4=other)"""
    pass


@task.command()
@click.argument("title")
@click.option("--priority", type=click.Choice(["high", "medium", "low"]), default="medium")
@click.option("--due")
@click.option("--project")
@click.option("--quadrant", type=int, default=2, help="Q1=1, Q2=2, Q3=3, Q4=4")
def add(title, priority, due, project, quadrant):
    """Add a new task

    Examples:
      pkm task add "写周报" --priority high
      pkm task add "读书" --quadrant 1 --priority high
      pkm task add "会议" --due 2026-04-10"""
    payload = {"title": title, "priority": priority, "quadrant": quadrant}
    if due:
        payload["due_date"] = due
    if project:
        payload["project_id"] = project
    r = requests.post(f"{API_BASE}/api/tasks", json=payload)
    r.raise_for_status()
    task_data = r.json()
    task_id = task_data["id"]

    # Create workspace and update task with workspace_path
    workspace_path = create_task_workspace(task_id, title)
    requests.patch(f"{API_BASE}/api/tasks/{task_id}", json={"workspace_path": workspace_path})

    click.echo(f"Task created: {task_id}")


@task.command()
@click.option("--status")
@click.option("--project")
@click.option("--quadrant", type=int, help="Q1=1, Q2=2, Q3=3, Q4=4")
def ls(status, project, quadrant):
    """List tasks

    Examples:
      pkm task ls
      pkm task ls --status pending
      pkm task ls --quadrant 1
      pkm task ls --status pending --quadrant 2"""
    params = {}
    if status:
        params["status"] = status
    if project:
        params["project_id"] = project
    if quadrant is not None:
        params["quadrant"] = quadrant
    r = requests.get(f"{API_BASE}/api/tasks", params=params)
    r.raise_for_status()
    tasks = r.json()
    if not tasks:
        click.echo("No tasks found")
        return
    for t in tasks:
        click.echo(f"[{t['id'][:8]}] {t['title']} ({t['status']}) - Q{t['quadrant']} [{t['priority']}]")


@task.command()
@click.argument("task_id")
def get(task_id):
    """Get task details

    Example:
      pkm task get 3e3705f1"""
    r = requests.get(f"{API_BASE}/api/tasks/{task_id}")
    r.raise_for_status()
    t = r.json()
    click.echo(f"ID: {t['id']}")
    click.echo(f"Title: {t['title']}")
    click.echo(f"Status: {t['status']}")
    click.echo(f"Priority: {t['priority']}")
    click.echo(f"Quadrant: {t['quadrant']}")
    if t.get("progress"):
        click.echo(f"Progress: {t['progress']}")
    if t.get("due_date"):
        click.echo(f"Due: {t['due_date']}")


@task.command()
@click.argument("task_id")
@click.option("--title")
@click.option("--status")
@click.option("--priority")
@click.option("--progress")
def update(task_id, title, status, priority, progress):
    """Update a task

    Examples:
      pkm task update 3e3705f1 --title "新标题"
      pkm task update 3e3705f1 --status completed --progress 100"""
    payload = {}
    if title:
        payload["title"] = title
    if status:
        payload["status"] = status
    if priority:
        payload["priority"] = priority
    if progress:
        payload["progress"] = progress
    r = requests.patch(f"{API_BASE}/api/tasks/{task_id}", json=payload)
    r.raise_for_status()
    click.echo("Task updated")


@task.command()
@click.argument("task_id")
def done(task_id):
    """Mark task as completed

    Example:
      pkm task done 3e3705f1"""
    r = requests.post(f"{API_BASE}/api/tasks/{task_id}/done")
    r.raise_for_status()
    click.echo("Task completed")


@task.command()
@click.argument("task_id")
def delete(task_id):
    """Delete a task

    Example:
      pkm task delete 3e3705f1"""
    r = requests.delete(f"{API_BASE}/api/tasks/{task_id}")
    r.raise_for_status()
    click.echo("Task deleted")


# Project commands
@cli.group()
def project():
    """Project management"""
    pass


@project.command()
@click.argument("name")
@click.option("--description")
def add(name, description):
    """Add a new project

    Examples:
      pkm project add "我的项目"
      pkm project add "PKM优化" --description "优化任务管理"""
    payload = {"name": name}
    if description:
        payload["description"] = description
    r = requests.post(f"{API_BASE}/api/projects", json=payload)
    r.raise_for_status()
    project_data = r.json()
    project_id = project_data["id"]

    # Create workspace and update project with workspace_path
    workspace_path = create_project_workspace(project_id, name)
    requests.patch(f"{API_BASE}/api/projects/{project_id}", json={"workspace_path": workspace_path})

    click.echo(f"Project created: {project_id}")


@project.command()
@click.option("--status")
def ls(status):
    """List projects

    Examples:
      pkm project ls
      pkm project ls --status active"""
    params = {}
    if status:
        params["status"] = status
    r = requests.get(f"{API_BASE}/api/projects", params=params)
    r.raise_for_status()
    projects = r.json()
    if not projects:
        click.echo("No projects found")
        return
    for p in projects:
        click.echo(f"[{p['id'][:8]}] {p['name']} ({p['status']})")


@project.command()
@click.argument("project_id")
def get(project_id):
    """Get project details

    Example:
      pkm project get ccec0f66"""
    r = requests.get(f"{API_BASE}/api/projects/{project_id}")
    r.raise_for_status()
    p = r.json()
    click.echo(f"ID: {p['id']}")
    click.echo(f"Name: {p['name']}")
    click.echo(f"Status: {p['status']}")
    if p.get("description"):
        click.echo(f"Description: {p['description']}")


@project.command()
@click.argument("project_id")
@click.option("--name")
@click.option("--description")
def update(project_id, name, description):
    """Update a project

    Examples:
      pkm project update ccec0f66 --name "新名称"
      pkm project update ccec0f66 --description "新描述"""
    payload = {}
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description
    r = requests.patch(f"{API_BASE}/api/projects/{project_id}", json=payload)
    r.raise_for_status()
    click.echo("Project updated")


@project.command()
@click.argument("project_id")
def archive(project_id):
    """Archive a project

    Example:
      pkm project archive ccec0f66"""
    r = requests.post(f"{API_BASE}/api/projects/{project_id}/archive")
    r.raise_for_status()
    click.echo("Project archived")


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
    click.echo("Starting knowledge reflow...")
    r = requests.post(f"{API_BASE}/api/knowledge/reflow")
    r.raise_for_status()
    result = r.json()
    click.echo(f"Reflow completed: {result['message']}")


@reflow.command()
def status():
    """Get reflow status

    Example:
      pkm reflow status"""
    r = requests.get(f"{API_BASE}/api/knowledge/status")
    r.raise_for_status()
    result = r.json()
    click.echo(f"Pending approved tasks: {result['pending_approved_tasks']}")
    click.echo(f"Pending reflows: {result['pending_reflows']}")
    click.echo(f"Claude CLI available: {result['claude_available']}")
    click.echo(f"Config: {result['config']}")


if __name__ == "__main__":
    cli()