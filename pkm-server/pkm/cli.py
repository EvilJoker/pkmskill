import click
import requests
import os
import time
import signal
import sys
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from pkm.config import get_api_base, get_port
from pkm.workspace import create_task_workspace, create_project_workspace

# When using docker-compose, exposed port is 8890, server listens on 7890 internally
# CLI uses get_api_base() which respects PKM_API_BASE env var, host_port config, or port config
API_BASE = get_api_base()
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


# Inbox helper functions
def extract_urls(text):
    """从文本中提取 URL"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def parse_url_with_claude(url, user_note):
    """调用 Claude CLI 解析 URL 内容"""
    prompt = f"""请访问并解析以下链接的内容，提取：标题、正文要点、代码块（如有）。
以结构化 Markdown 格式输出。

链接：{url}
用户备注：{user_note}

请提取并总结内容。"""

    try:
        model = os.environ.get("CLAUDE_MODEL", "MiniMax-M2.7-highspeed")
        result = subprocess.run(
            ["claude", "-p", prompt,
             "--permission-mode", "acceptEdits",
             "--allowedTools", "WebFetch",
             "--effort", "medium",
             "--model", model],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except Exception:
        return None


def generate_inbox_filename(content):
    """生成 inbox 文件名: YYYYMMDD_HHMMSS_标题_inbox.md"""
    # 提取前50字符作为标题
    title = content[:50].replace("\n", " ").replace("#", "").replace("/", "_").strip()
    if len(content) > 50:
        title = title[:47] + "..."
    now = datetime.now()
    return now.strftime("%Y%m%d_%H%M%S") + "_" + title + "_inbox.md"


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
    server_port = get_port()
    with open(log_file, "w") as f:
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(server_port)],
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
    """PKM CLI - Task and Project Management

工作流示例：
  inbox     收集灵感 -> pkm inbox add "想法"
  task      创建任务 -> pkm task add "任务名" --priority high --project <项目ID>
  task ls   查看列表 -> pkm task ls / pkm task ls -p (显示路径)
  task get  查看详情 -> pkm task get <id>
  task update 更新   -> pkm task update <id> --title "新标题" --priority medium
  task approve 批准  -> pkm task approve <id> (done -> approved，回流知识)
  project   关联项目 -> pkm project add "项目名" / pkm project get <id>
  工作中    在工作区 ~/.pkm/10_Tasks/TASK_xxx/ 下编辑文件
  task done 完成     -> pkm task done <id>
  reflow    知识提炼 -> 自动每3小时执行，也可手动 pkm reflow run / stage2

Commands:
  inbox    Inbox commands for capturing notes
  project  Project management
  reflow   Knowledge reflow management
  server   Server management
  task     Task management
"""
    pass


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
      pkm inbox "Some notes"
      pkm inbox --parse "Check this https://example.com article"
    """
    if not content or not content.strip():
        click.echo("Error: 内容不能为空", err=True)
        return

    # 确定 50_Raw/inbox 路径
    inbox_dir = os.path.expanduser("~/.pkm/50_Raw/inbox")
    os.makedirs(inbox_dir, exist_ok=True)

    # 处理 --parse 模式
    final_content = content
    if parse:
        urls = extract_urls(content)
        if urls:
            # 只解析第一个 URL
            url = urls[0]
            user_note = content.replace(url, "").strip()
            parsed_content = parse_url_with_claude(url, user_note)
            if parsed_content:
                final_content = f"{content}\n\n## AI 解析结果\n\n{parsed_content}"
            else:
                click.echo("Warning: URL 解析失败，只保存用户输入", err=True)

    # 生成文件名
    filename = generate_inbox_filename(final_content)
    filepath = os.path.join(inbox_dir, filename)

    # 写入文件
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_content)
    except IOError as e:
        click.echo(f"Error: 无法写入文件: {e}", err=True)
        return

    click.echo(f"Captured to inbox: {filename}")


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
    """Task management"""
    pass


@task.command()
@click.argument("title")
@click.option("--priority", type=click.Choice(["high", "medium", "low"]), default="medium")
@click.option("--due")
@click.option("--project")
def add(title, priority, due, project):
    """Add a new task

    Examples:
      pkm task add "写周报" --priority high
      pkm task add "读书" --priority high
      pkm task add "会议" --due 2026-04-10"""
    payload = {"title": title, "priority": priority}
    if due:
        payload["due_date"] = due

    # 如果未指定 project，自动关联到 default 项目
    if not project:
        r = requests.get(f"{API_BASE}/api/projects")
        projects = r.json()
        for p in projects:
            if p["name"].lower() == "default":
                payload["project_id"] = p["id"]
                break
    else:
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
@click.option("-p", "--path", is_flag=True, help="显示工作空间路径")
def ls(status, project, path):
    """List tasks

    Examples:
      pkm task ls
      pkm task ls --status new
      pkm task ls -p"""
    params = {}
    if status:
        params["status"] = status
    if project:
        params["project_id"] = project
    r = requests.get(f"{API_BASE}/api/tasks", params=params)
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
def approve(task_id):
    """Approve task for knowledge reflow (done -> approved)

    Example:
      pkm task approve 3e3705f1"""
    r = requests.post(f"{API_BASE}/api/knowledge/approve/{task_id}")
    r.raise_for_status()
    click.echo("Task approved for reflow")


@task.command()
@click.argument("task_id")
def delete(task_id):
    """Delete a task by ID or index

    Examples:
      pkm task delete 3e3705f1
      pkm task delete 1"""
    # 如果是数字序号，先获取task列表，再获取对应的task_id
    if task_id.isdigit():
        idx = int(task_id)
        r = requests.get(f"{API_BASE}/api/tasks")
        tasks = r.json()
        if idx < 1 or idx > len(tasks):
            click.echo(f"Invalid index: {idx}", err=True)
            raise SystemExit(1)
        task = tasks[idx - 1]
        task_id = task["id"]
        workspace_path = task.get("workspace_path")
    else:
        # UUID 逻辑，先获取 task 信息
        r = requests.get(f"{API_BASE}/api/tasks/{task_id}")
        if r.status_code == 404:
            click.echo(f"Task not found: {task_id}", err=True)
            raise SystemExit(1)
        r.raise_for_status()
        task = r.json()
        workspace_path = task.get("workspace_path")

    # 删除数据
    r = requests.delete(f"{API_BASE}/api/tasks/{task_id}")
    r.raise_for_status()

    # 删除 workspace
    if workspace_path and os.path.exists(workspace_path):
        shutil.rmtree(workspace_path)

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
      pkm project add "PKM优化" --description "优化任务管理和CLI优化"

    # 完整示例
      pkm project add "新项目" --description "项目描述"""
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
@click.option("-p", "--path", "show_path", is_flag=True, help="Show full workspace path")
def ls(status, show_path):
    """List projects

    Examples:
      pkm project ls
      pkm project ls --status active
      pkm project ls --status archived
      pkm project ls -p
      pkm project ls --status active -p

    # 查看所有状态的项目
      pkm project ls --status active
      pkm project ls --status archived"""
    params = {}
    if status:
        params["status"] = status
    r = requests.get(f"{API_BASE}/api/projects", params=params)
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


@project.command()
@click.argument("project_id")
def get(project_id):
    """Get project details

    Examples:
      pkm project get ccec0f66
      pkm project get 1
      pkm project get default

    # 获取项目详情（可用 ID、序号或 default）
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
      pkm project update ccec0f66 --description "新描述"
      pkm project update ccec0f66 --name "名称" --description "描述"
      pkm project update 1 --name "新名称"

    # 修改项目名称
      pkm project update ccec0f66 --name "优化后的项目名"

    # 修改项目描述
      pkm project update ccec0f66 --description "项目用于XXX"

    # 同时修改名称和描述
      pkm project update ccec0f66 --name "新名称" --description "新描述"""
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
def delete(project_id):
    """Delete a project by ID, index, or 'default'

    Examples:
      pkm project delete ccec0f66
      pkm project delete 2
      pkm project delete default

    # 通过 ID 删除
      pkm project delete ccec0f66

    # 通过序号删除（删除列表中的第2个项目）
      pkm project delete 2

    # 注意：不能删除 default 项目"""
    # 如果是数字序号，需要计算正确的索引（跳过 default 项目）
    if project_id.isdigit():
        idx = int(project_id)
        r = requests.get(f"{API_BASE}/api/projects")
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
        r = requests.get(f"{API_BASE}/api/projects/{project_id}")
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
    r = requests.delete(f"{API_BASE}/api/projects/{project_id}")
    if r.status_code == 400:
        click.echo("Cannot delete default project", err=True)
        raise SystemExit(1)
    r.raise_for_status()

    # 删除 workspace
    if workspace_path and os.path.exists(workspace_path):
        shutil.rmtree(workspace_path)

    click.echo("Project deleted")


@project.command()
@click.argument("project_id")
def archive(project_id):
    """Archive a project

    Examples:
      pkm project archive ccec0f66
      pkm project archive 1

    # 归档项目（归档后可使用 --status archived 查看）
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

    # Stage2 status
    try:
        r2 = requests.get(f"{API_BASE}/api/knowledge/reflow/status/stage2")
        r2.raise_for_status()
        stage2_result = r2.json()
        click.echo(f"\n--- Stage2 ---")
        click.echo(f"Pending projects: {stage2_result['pending_projects']}")
    except:
        click.echo(f"\n--- Stage2 ---")
        click.echo("Stage2 not available")


@reflow.command()
@click.option("--batch-size", default=5, help="每批处理项目数")
def stage2(batch_size):
    """Manually trigger Stage2 knowledge distillation

    Example:
      pkm reflow stage2
      pkm reflow stage2 --batch-size 3"""
    click.echo("Starting Stage2 knowledge distillation...")
    r = requests.post(f"{API_BASE}/api/knowledge/reflow/stage2")
    r.raise_for_status()
    result = r.json()
    click.echo(f"Stage2 completed: {result['message']}")


if __name__ == "__main__":
    cli()