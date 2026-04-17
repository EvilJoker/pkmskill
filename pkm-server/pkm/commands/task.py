"""Task commands"""

import click
import requests
import os
import shutil

from pkm.workspace import create_task_workspace


def task_add(title, priority, due, project, api_base):
    """Add a new task"""
    payload = {"title": title, "priority": priority}
    if due:
        payload["due_date"] = due

    # 如果未指定 project，自动关联到 default 项目
    if not project:
        r = requests.get(f"{api_base}/api/projects")
        projects = r.json()
        for p in projects:
            if p["name"].lower() == "default":
                payload["project_id"] = p["id"]
                break
    else:
        payload["project_id"] = project

    r = requests.post(f"{api_base}/api/tasks", json=payload)
    r.raise_for_status()
    task_data = r.json()
    task_id = task_data["id"]

    # Create workspace and update task with workspace_path
    workspace_path = create_task_workspace(task_id, title)
    requests.patch(f"{api_base}/api/tasks/{task_id}", json={"workspace_path": workspace_path})

    click.echo(f"Task created: {task_id}")


def task_ls(status, project, path, api_base):
    """List tasks"""
    params = {}
    if status:
        params["status"] = status
    if project:
        params["project_id"] = project
    r = requests.get(f"{api_base}/api/tasks", params=params)
    r.raise_for_status()
    tasks = r.json()
    if not tasks:
        click.echo("No tasks found")
        return
    priority_map = {"high": "h", "medium": "m", "low": "l"}
    for idx, t in enumerate(tasks, 1):
        pri = priority_map.get(t.get("priority", "medium"), "m")
        if path:
            ws_path = t.get("workspace_path", "")
            click.echo(f"[{idx}] {t['title']} ({t['status']}) [{pri}]")
            if ws_path:
                click.echo(f"    -> {ws_path}")
        else:
            click.echo(f"[{idx}] {t['title']} ({t['status']}) [{pri}]")


def task_get(task_id, api_base):
    """Get task details"""
    r = requests.get(f"{api_base}/api/tasks/{task_id}")
    r.raise_for_status()
    t = r.json()
    click.echo(f"ID: {t['id']}")
    click.echo(f"Title: {t['title']}")
    click.echo(f"Status: {t['status']}")
    click.echo(f"Priority: {t['priority']}")
    if t.get("progress"):
        click.echo(f"Progress: {t['progress']}")
    if t.get("due_date"):
        click.echo(f"Due: {t['due_date']}")


def task_update(task_id, title, status, priority, progress, api_base):
    """Update a task"""
    payload = {}
    if title:
        payload["title"] = title
    if status:
        payload["status"] = status
    if priority:
        payload["priority"] = priority
    if progress:
        payload["progress"] = progress
    r = requests.patch(f"{api_base}/api/tasks/{task_id}", json=payload)
    r.raise_for_status()
    click.echo("Task updated")


def task_done(task_id, api_base):
    """Mark task as completed"""
    r = requests.post(f"{api_base}/api/tasks/{task_id}/done")
    r.raise_for_status()
    click.echo("Task completed")


def task_approve(task_id, api_base):
    """Approve task for knowledge reflow"""
    r = requests.post(f"{api_base}/api/knowledge/approve/{task_id}")
    r.raise_for_status()
    click.echo("Task approved for reflow")


def task_delete(task_id, api_base):
    """Delete a task by ID or index"""
    # 如果是数字序号，先获取task列表，再获取对应的task_id
    if task_id.isdigit():
        idx = int(task_id)
        r = requests.get(f"{api_base}/api/tasks")
        tasks = r.json()
        if idx < 1 or idx > len(tasks):
            click.echo(f"Invalid index: {idx}", err=True)
            raise SystemExit(1)
        task = tasks[idx - 1]
        task_id = task["id"]
        workspace_path = task.get("workspace_path")
    else:
        # UUID 逻辑，先获取 task 信息
        r = requests.get(f"{api_base}/api/tasks/{task_id}")
        if r.status_code == 404:
            click.echo(f"Task not found: {task_id}", err=True)
            raise SystemExit(1)
        r.raise_for_status()
        task = r.json()
        workspace_path = task.get("workspace_path")

    # 删除数据
    r = requests.delete(f"{api_base}/api/tasks/{task_id}")
    r.raise_for_status()

    # 删除 workspace
    if workspace_path and os.path.exists(workspace_path):
        shutil.rmtree(workspace_path)

    click.echo("Task deleted")
