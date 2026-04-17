"""Project commands"""

import click
import requests
import os
import shutil

from pkm.workspace import create_project_workspace


def project_add(name, description, api_base):
    """Add a new project"""
    payload = {"name": name}
    if description:
        payload["description"] = description
    r = requests.post(f"{api_base}/api/projects", json=payload)
    r.raise_for_status()
    project_data = r.json()
    project_id = project_data["id"]

    # Create workspace and update project with workspace_path
    workspace_path = create_project_workspace(project_id, name)
    requests.patch(f"{api_base}/api/projects/{project_id}", json={"workspace_path": workspace_path})

    click.echo(f"Project created: {project_id}")


def project_ls(status, show_path, api_base):
    """List projects"""
    params = {}
    if status:
        params["status"] = status
    r = requests.get(f"{api_base}/api/projects", params=params)
    r.raise_for_status()
    projects = r.json()

    if not projects:
        # 检查 default 项目工作区是否存在
        default_path = os.path.join(os.path.expanduser("~/.pkm"), "60_Projects")
        try:
            if os.path.isdir(default_path):
                for item in os.listdir(default_path):
                    if item.startswith("P_default"):
                        full_path = os.path.join(default_path, item)
                        if show_path:
                            click.echo(f"[default] P_default (active) -> {full_path}")
                        else:
                            click.echo(f"[default] P_default (active)")
                        return
        except OSError:
            pass
        click.echo("No projects found")
        return

    # 显示项目列表：default 单独一行，其他项目用序号
    default_project = None
    normal_projects = []
    for p in projects:
        if p["name"].lower() == "default":
            default_project = p
        else:
            normal_projects.append(p)

    # 先显示 default 项目
    if default_project:
        ws_path = default_project.get("workspace_path", "")
        if show_path and ws_path:
            click.echo(f"[default] {default_project['name']} ({default_project['status']}) -> {ws_path}")
        else:
            click.echo(f"[default] {default_project['name']} ({default_project['status']})")

    # 再显示其他项目，用序号
    for idx, p in enumerate(normal_projects, 1):
        ws_path = p.get("workspace_path", "")
        if show_path and ws_path:
            click.echo(f"[{idx}] {p['name']} ({p['status']}) -> {ws_path}")
        else:
            click.echo(f"[{idx}] {p['name']} ({p['status']})")


def project_get(project_id, api_base):
    """Get project details"""
    r = requests.get(f"{api_base}/api/projects/{project_id}")
    r.raise_for_status()
    p = r.json()
    click.echo(f"ID: {p['id']}")
    click.echo(f"Name: {p['name']}")
    click.echo(f"Status: {p['status']}")
    if p.get("description"):
        click.echo(f"Description: {p['description']}")


def project_update(project_id, name, description, api_base):
    """Update a project"""
    payload = {}
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description
    r = requests.patch(f"{api_base}/api/projects/{project_id}", json=payload)
    r.raise_for_status()
    click.echo("Project updated")


def project_delete(project_id, api_base):
    """Delete a project by ID, index, or 'default'"""
    # 如果是数字序号，需要计算正确的索引（跳过 default 项目）
    if project_id.isdigit():
        idx = int(project_id)
        r = requests.get(f"{api_base}/api/projects")
        projects = r.json()
        # 计算非 default 项目的序号
        normal_idx = 0
        target_project = None
        for p in projects:
            if p["name"].lower() != "default":
                normal_idx += 1
                if normal_idx == idx:
                    target_project = p
                    break
        if target_project is None:
            click.echo(f"Invalid index: {idx}", err=True)
            raise SystemExit(1)
        project_id = target_project["id"]
        workspace_path = target_project.get("workspace_path")
    elif project_id.lower() == "default":
        # 直接拒绝删除 default 项目
        click.echo("Cannot delete default project", err=True)
        raise SystemExit(1)
    else:
        # UUID 逻辑，先获取 project 信息
        r = requests.get(f"{api_base}/api/projects/{project_id}")
        if r.status_code == 404:
            click.echo(f"Project not found: {project_id}", err=True)
            raise SystemExit(1)
        r.raise_for_status()
        project = r.json()

        # 检查是否为 default 项目
        if project["name"].lower() == "default":
            click.echo("Cannot delete default project", err=True)
            raise SystemExit(1)

        project_id = project["id"]
        workspace_path = project.get("workspace_path")

    # 调用 API 删除
    r = requests.delete(f"{api_base}/api/projects/{project_id}")
    if r.status_code == 400:
        click.echo("Cannot delete default project", err=True)
        raise SystemExit(1)
    r.raise_for_status()

    # 删除 workspace
    if workspace_path and os.path.exists(workspace_path):
        shutil.rmtree(workspace_path)

    click.echo("Project deleted")


def project_archive(project_id, api_base):
    """Archive a project"""
    r = requests.post(f"{api_base}/api/projects/{project_id}/archive")
    r.raise_for_status()
    click.echo("Project archived")
