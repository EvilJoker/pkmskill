"""Task commands"""

import click
import requests
import os
import shutil

from pkm.workspace import create_task_workspace


def _select_project(projects: list, api_base: str) -> str | None:
    """交互式选择项目，返回项目ID"""
    # 确保 default 项目在最前面
    default_project = None
    other_projects = []
    for p in projects:
        if p["name"].lower() == "default":
            default_project = p
        else:
            other_projects.append(p)
    sorted_projects = ([default_project] if default_project else []) + other_projects

    click.echo("\n选择关联项目（直接回车选择 default）:")
    for idx, p in enumerate(sorted_projects, 1):
        click.echo(f"  [{idx}] {p['name']}")

    while True:
        choice = click.prompt("\n请输入序号", default="1", type=str).strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(sorted_projects):
                return sorted_projects[idx - 1]["id"]
        click.echo("无效选择，请重新输入")


def task_add_interactive(api_base: str):
    """交互式添加任务"""
    # 1. 输入标题
    while True:
        title = click.prompt("\n请输入任务名称", type=str).strip()
        if title:
            break
        click.echo("任务名称不能为空，请重新输入")

    # 2. 选择优先级
    click.echo("\n选择优先级:")
    click.echo("  [1] high")
    click.echo("  [2] medium (默认)")
    click.echo("  [3] low")

    while True:
        choice = click.prompt("请输入序号", default="3", type=str).strip()
        priority_map = {"1": "high", "2": "medium", "3": "low"}
        if choice in priority_map:
            priority = priority_map[choice]
            break
        click.echo("无效选择，请重新输入")

    # 3. 输入截止日期（可选）
    click.echo("\n输入截止日期（格式: 2026-04-25，可直接回车跳过）:")
    due = click.prompt("截止日期", default="", type=str).strip()
    if due:
        due = due if due else None
    else:
        due = None

    # 4. 选择项目
    r = requests.get(f"{api_base}/api/projects")
    r.raise_for_status()
    projects = r.json()
    project_id = _select_project(projects, api_base)

    # 调用原有的 task_add
    task_add(title, priority, due, project_id, api_base)


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


def task_ls(status, project, show_all, api_base):
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

    # Get project names for mapping project_id to name
    proj_r = requests.get(f"{api_base}/api/projects")
    proj_r.raise_for_status()
    projects = {p["id"]: p["name"] for p in proj_r.json()}

    for idx, t in enumerate(tasks, 1):
        pri = priority_map.get(t.get("priority", "medium"), "m")
        if show_all:
            proj_id = t.get("project_id")
            proj_name = f"[{projects.get(proj_id, '') or 'default'}]"
            ws_path = t.get("workspace_path", "")
            click.echo(f"[{idx}] {t['title']} [{pri}] {t['id'][:10]} {proj_name} {ws_path}")
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


def task_update_interactive(api_base: str):
    """交互式更新任务"""
    # 1. 选择要更新的任务
    click.echo("\n请选择要更新的任务:")

    # 获取任务列表
    r = requests.get(f"{api_base}/api/tasks")
    r.raise_for_status()
    tasks = r.json()

    if not tasks:
        click.echo("没有任务可更新")
        return

    # 获取项目名称映射
    proj_r = requests.get(f"{api_base}/api/projects")
    proj_r.raise_for_status()
    projects_map = {p["id"]: p["name"] for p in proj_r.json()}

    # 显示任务列表
    priority_map = {"high": "h", "medium": "m", "low": "l"}
    for idx, t in enumerate(tasks, 1):
        pri = priority_map.get(t.get("priority", "medium"), "m")
        proj_name = projects_map.get(t.get("project_id"), "default")
        click.echo(f"  [{idx}] {t['title']} [{pri}] [{proj_name}]")

    # 选择任务
    while True:
        choice = click.prompt("\n请输入任务序号", type=str).strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(tasks):
                task = tasks[idx - 1]
                break
        click.echo("无效序号，请重新输入")

    task_id = task["id"]
    click.echo(f"\n已选择任务: {task['title']}")

    # 2. 更新标题
    click.echo(f"\n当前标题: {task['title']}")
    new_title = click.prompt("新标题（直接回车跳过）", default="", type=str).strip()
    if not new_title:
        new_title = None

    # 3. 更新优先级
    current_pri = task.get("priority", "medium")
    pri_map = {"high": "1", "medium": "2", "low": "3"}
    current_pri_num = pri_map.get(current_pri, "3")
    click.echo(f"\n当前优先级: {current_pri}")
    click.echo("  [1] high")
    click.echo("  [2] medium")
    click.echo("  [3] low (默认)")

    new_priority = None
    while True:
        choice = click.prompt("新优先级（直接回车跳过）", default="", type=str).strip()
        if not choice:
            break
        priority_map_rev = {"1": "high", "2": "medium", "3": "low"}
        if choice in priority_map_rev:
            new_priority = priority_map_rev[choice]
            break
        click.echo("无效选择，请重新输入")

    # 4. 更新进度
    current_progress = task.get("progress", 0)
    click.echo(f"\n当前进度: {current_progress}%")
    new_progress_str = click.prompt("新进度 0-100（直接回车跳过）", default="", type=str).strip()

    new_progress = None
    if new_progress_str:
        if new_progress_str.isdigit():
            new_progress = int(new_progress_str)
            if not (0 <= new_progress <= 100):
                click.echo("进度必须在 0-100 之间")
                new_progress = None
        else:
            click.echo("无效输入，进度必须是数字")

    # 调用更新
    task_update(task_id, new_title, None, new_priority, new_progress, api_base)


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
