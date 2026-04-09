# PKM Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 pkm-server MVP，提供 CLI + 守护进程服务的任务/项目管理能力。

**Architecture:** Python FastAPI 单文件 + Click CLI，通过 HTTP REST API 通信，SQLite 持久化，Docker 容器化。

**Tech Stack:** Python 3.11 / FastAPI / Pydantic / Click / SQLite / Uvicorn / Docker

---

## 文件结构

```
pkm-server/
├── requirements.txt    # 依赖
├── Dockerfile          # 容器化
├── models.py          # Pydantic 模型
├── database.py        # SQLite 连接 + CRUD
├── main.py            # FastAPI 服务
└── pkm/               # CLI 包
    ├── __init__.py
    └── cli.py         # Click CLI
```

---

### Task 1: 项目初始化

**Files:**
- Create: `pkm-server/requirements.txt`
- Create: `pkm-server/Dockerfile`
- Create: `pkm-server/.gitignore`

- [ ] **Step 1: 创建 requirements.txt**

```txt
fastapi==0.109.2
uvicorn[standard]==0.27.1
pydantic==2.6.1
click==8.1.7
requests==2.31.0
```

- [ ] **Step 2: 创建 Dockerfile**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7890"]
```

- [ ] **Step 3: 创建 .gitignore**

```gitignore
__pycache__/
*.pyc
.pkm/
```

- [ ] **Step 4: Commit**

```bash
git add pkm-server/requirements.txt pkm-server/Dockerfile pkm-server/.gitignore
git commit -m "feat(pkm-server): initial project structure"
```

---

### Task 2: 数据模型

**Files:**
- Create: `pkm-server/models.py`

- [ ] **Step 1: 创建 models.py**

```python
from datetime import datetime, date
from enum import Enum
from typing import Optional
from pydantic import BaseModel
import uuid


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskPriority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class ProjectStatus(str, Enum):
    active = "active"
    completed = "completed"
    archived = "archived"


class TaskBase(BaseModel):
    title: str
    priority: TaskPriority = TaskPriority.medium
    quadrant: int = 2
    project_id: Optional[str] = None
    progress: Optional[str] = None
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    quadrant: Optional[int] = None
    project_id: Optional[str] = None
    progress: Optional[str] = None
    due_date: Optional[date] = None


class Task(TaskBase):
    id: str
    status: TaskStatus = TaskStatus.pending
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class Project(ProjectBase):
    id: str
    status: ProjectStatus = ProjectStatus.active
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

- [ ] **Step 2: Commit**

```bash
git add pkm-server/models.py
git commit -m "feat(pkm-server): add data models"
```

---

### Task 3: 数据库层

**Files:**
- Create: `pkm-server/database.py`

- [ ] **Step 1: 创建 database.py**

```python
import sqlite3
import os
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager

DB_PATH = os.path.expanduser("~/.pkm/pkm.db")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'medium',
                quadrant INTEGER DEFAULT 2,
                project_id TEXT,
                progress TEXT,
                due_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        """)
        conn.commit()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def row_to_task(row) -> dict:
    if not row:
        return None
    return dict(row)


def row_to_project(row) -> dict:
    if not row:
        return None
    return dict(row)


# Project CRUD
def create_project(name: str, description: Optional[str] = None) -> dict:
    import uuid
    now = datetime.utcnow().isoformat()
    project = {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "completed_at": None
    }
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (id, name, description, status, created_at, updated_at, completed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (project["id"], project["name"], project["description"], project["status"],
             project["created_at"], project["updated_at"], project["completed_at"])
        )
    return project


def get_project(project_id: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        return row_to_project(cursor.fetchone())


def list_projects(status: Optional[str] = None) -> List[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute("SELECT * FROM projects WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        return [row_to_project(row) for row in cursor.fetchall()]


def update_project(project_id: str, **kwargs) -> Optional[dict]:
    allowed = ["name", "description", "status"]
    kwargs = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not kwargs:
        return get_project(project_id)
    kwargs["updated_at"] = datetime.utcnow().isoformat()
    if "status" in kwargs and kwargs["status"] == "completed":
        kwargs["completed_at"] = datetime.utcnow().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values()) + [project_id]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", values)
    return get_project(project_id)


def delete_project(project_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        return cursor.rowcount > 0


# Task CRUD
def create_task(title: str, priority: str = "medium", quadrant: int = 2,
                project_id: Optional[str] = None, progress: Optional[str] = None,
                due_date: Optional[str] = None) -> dict:
    import uuid
    now = datetime.utcnow().isoformat()
    task = {
        "id": str(uuid.uuid4()),
        "title": title,
        "status": "pending",
        "priority": priority,
        "quadrant": quadrant,
        "project_id": project_id,
        "progress": progress,
        "due_date": due_date,
        "created_at": now,
        "updated_at": now,
        "completed_at": None
    }
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (id, title, status, priority, quadrant, project_id, progress, due_date, created_at, updated_at, completed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (task["id"], task["title"], task["status"], task["priority"], task["quadrant"],
             task["project_id"], task["progress"], task["due_date"], task["created_at"],
             task["updated_at"], task["completed_at"])
        )
    return task


def get_task(task_id: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return row_to_task(cursor.fetchone())


def list_tasks(status: Optional[str] = None, project_id: Optional[str] = None,
               quadrant: Optional[int] = None) -> List[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        if quadrant is not None:
            query += " AND quadrant = ?"
            params.append(quadrant)
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        return [row_to_task(row) for row in cursor.fetchall()]


def update_task(task_id: str, **kwargs) -> Optional[dict]:
    allowed = ["title", "status", "priority", "quadrant", "project_id", "progress", "due_date"]
    kwargs = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not kwargs:
        return get_task(task_id)
    kwargs["updated_at"] = datetime.utcnow().isoformat()
    if "status" in kwargs and kwargs["status"] == "completed":
        kwargs["completed_at"] = datetime.utcnow().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values()) + [task_id]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
    return get_task(task_id)


def delete_task(task_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0


def complete_task(task_id: str) -> Optional[dict]:
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = 'completed', updated_at = ?, completed_at = ? WHERE id = ?",
            (now, now, task_id)
        )
    return get_task(task_id)
```

- [ ] **Step 2: Commit**

```bash
git add pkm-server/database.py
git commit -m "feat(pkm-server): add database layer"
```

---

### Task 4: FastAPI 服务

**Files:**
- Create: `pkm-server/main.py`

- [ ] **Step 1: 创建 main.py**

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List

from models import Task, TaskCreate, TaskUpdate, Project, ProjectCreate, ProjectUpdate
import database

app = FastAPI(title="PKM Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    database.init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


# Projects
@app.post("/api/projects", response_model=Project)
def create_project(project: ProjectCreate):
    return database.create_project(project.name, project.description)


@app.get("/api/projects", response_model=List[Project])
def list_projects(status: Optional[str] = None):
    return database.list_projects(status)


@app.get("/api/projects/{project_id}", response_model=Project)
def get_project(project_id: str):
    project = database.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.patch("/api/projects/{project_id}", response_model=Project)
def update_project(project_id: str, update: ProjectUpdate):
    project = database.update_project(project_id, **update.model_dump(exclude_unset=True))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str):
    if not database.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "deleted"}


@app.post("/api/projects/{project_id}/archive", response_model=Project)
def archive_project(project_id: str):
    project = database.update_project(project_id, status="archived")
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# Tasks
@app.post("/api/tasks", response_model=Task)
def create_task(task: TaskCreate):
    return database.create_task(
        title=task.title,
        priority=task.priority.value,
        quadrant=task.quadrant,
        project_id=task.project_id,
        progress=task.progress,
        due_date=str(task.due_date) if task.due_date else None
    )


@app.get("/api/tasks", response_model=List[Task])
def list_tasks(status: Optional[str] = None, project_id: Optional[str] = None,
               quadrant: Optional[int] = None):
    return database.list_tasks(status, project_id, quadrant)


@app.get("/api/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    task = database.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, update: TaskUpdate):
    data = update.model_dump(exclude_unset=True)
    if "priority" in data and data["priority"]:
        data["priority"] = data["priority"].value
    if "due_date" in data and data["due_date"]:
        data["due_date"] = str(data["due_date"])
    task = database.update_task(task_id, **data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str):
    if not database.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "deleted"}


@app.post("/api/tasks/{task_id}/done", response_model=Task)
def done_task(task_id: str):
    task = database.complete_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7890)
```

- [ ] **Step 2: Commit**

```bash
git add pkm-server/main.py
git commit -m "feat(pkm-server): add FastAPI server"
```

---

### Task 5: CLI 客户端

**Files:**
- Create: `pkm-server/pkm/__init__.py`
- Create: `pkm-server/pkm/cli.py`

- [ ] **Step 1: 创建 pkm/__init__.py**

```python
__version__ = "0.1.0"
```

- [ ] **Step 2: 创建 pkm/cli.py**

```python
import click
import requests
import os
import time
import signal
import sys

API_BASE = os.environ.get("PKM_API_BASE", "http://localhost:7890")
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
    """Task management"""
    pass


@task.command()
@click.argument("title")
@click.option("--priority", type=click.Choice(["high", "medium", "low"]), default="medium")
@click.option("--due")
@click.option("--project")
@click.option("--quadrant", type=int, default=2)
def add(title, priority, due, project, quadrant):
    """Add a new task"""
    payload = {"title": title, "priority": priority, "quadrant": quadrant}
    if due:
        payload["due_date"] = due
    if project:
        payload["project_id"] = project
    r = requests.post(f"{API_BASE}/api/tasks", json=payload)
    r.raise_for_status()
    click.echo(f"Task created: {r.json()['id']}")


@task.command()
@click.option("--status")
@click.option("--project")
@click.option("--quadrant", type=int)
def ls(status, project, quadrant):
    """List tasks"""
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
    """Get task details"""
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
    r = requests.patch(f"{API_BASE}/api/tasks/{task_id}", json=payload)
    r.raise_for_status()
    click.echo("Task updated")


@task.command()
@click.argument("task_id")
def done(task_id):
    """Mark task as completed"""
    r = requests.post(f"{API_BASE}/api/tasks/{task_id}/done")
    r.raise_for_status()
    click.echo("Task completed")


@task.command()
@click.argument("task_id")
def delete(task_id):
    """Delete a task"""
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
    """Add a new project"""
    payload = {"name": name}
    if description:
        payload["description"] = description
    r = requests.post(f"{API_BASE}/api/projects", json=payload)
    r.raise_for_status()
    click.echo(f"Project created: {r.json()['id']}")


@project.command()
@click.option("--status")
def ls(status):
    """List projects"""
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
    """Get project details"""
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
    """Update a project"""
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
    """Archive a project"""
    r = requests.post(f"{API_BASE}/api/projects/{project_id}/archive")
    r.raise_for_status()
    click.echo("Project archived")


if __name__ == "__main__":
    cli()
```

- [ ] **Step 3: 创建 pkm/__main__.py（支持 python -m pkm）**

```python
from pkm.cli import cli
if __name__ == "__main__":
    cli()
```

- [ ] **Step 4: Commit**

```bash
git add pkm-server/pkm/__init__.py pkm-server/pkm/cli.py pkm-server/pkm/__main__.py
git commit -m "feat(pkm-server): add CLI"
```

---

### Task 6: 服务管理脚本（辅助）

**Files:**
- Create: `pkm-server/scripts/start-server.sh`

- [ ] **Step 1: 创建 start-server.sh**

```bash
#!/bin/bash
cd "$(dirname "$0")/.."
python -m uvicorn main:app --host 0.0.0.0 --port 7890
```

- [ ] **Step 2: Commit**

```bash
git add pkm-server/scripts/start-server.sh
git commit -m "feat(pkm-server): add server start script"
```

---

### Task 7: 安装脚本

**Files:**
- Create: `pkm-server/install.sh`

- [ ] **Step 1: 创建 install.sh**

```bash
#!/bin/bash
set -e

# 安装到 ~/.pkm
PKM_HOME="${PKM_HOME:-$HOME/.pkm}"
mkdir -p "$PKM_HOME"

# 复制文件
cp -r "$(dirname "$0")"/* "$PKM_HOME/"

# 安装 Python 依赖
pip install -r "$PKM_HOME/requirements.txt"

# 安装 CLI
pip install -e "$PKM_HOME"

echo "PKM installed to $PKM_HOME"
```

- [ ] **Step 2: Commit**

```bash
git add pkm-server/install.sh
git commit -m "feat(pkm-server): add install script"
```

---

## 自检清单

1. **Spec 覆盖**：所有 API 端点、CLI 命令均已实现
2. **无占位符**：所有步骤均有完整代码
3. **类型一致性**：Task/Project 模型字段在各文件中一致
4. **MVP 范围**：仅实现 CRUD + 服务管理，不含知识整理功能

---

**Plan complete.** Saved to `docs/superpowers/plans/2026-04-08-pkm-server-implementation.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - dispatch fresh subagent per task, review between tasks

**2. Inline Execution** - execute tasks in this session, batch with checkpoints

Which approach?
