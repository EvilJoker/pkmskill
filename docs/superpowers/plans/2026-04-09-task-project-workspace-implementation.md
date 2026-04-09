# 任务与项目工作区实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 CLI 创建任务/项目时自动创建物理工作区，生成 AI 记忆上下文文件

**Architecture:**
- 新增 `workspace.py` 模块处理工作区创建逻辑
- 修改 `database.py` 和 `models.py` 添加 `workspace_path` 字段
- CLI 创建任务/项目时调用工作区创建逻辑
- AI 记忆上下文文件（task.md/project.md）包含标准模板和 AI 使用指南

**Tech Stack:** Python 3, SQLite, FastAPI, Click CLI

---

## 文件结构

```
pkm-server/
├── database.py      # 修改: Task/Project 表增加 workspace_path 字段
├── models.py       # 修改: Task/Project 模型增加 workspace_path 字段
├── workspace.py    # 新建: 工作区创建逻辑
├── cli.py          # 修改: task add/project add 调用工作区创建
└── tests/
    └── test_workspace.py  # 新建: 工作区功能测试
```

---

## Task 1: 创建 workspace.py 工作区创建模块

**Files:**
- Create: `pkm-server/workspace.py`
- Test: `pkm-server/tests/test_workspace.py`

- [ ] **Step 1: 编写测试**

```python
# tests/test_workspace.py
import os
import tempfile
import pytest
from workspace import create_task_workspace, create_project_workspace, get_workspace_base_path

def test_get_workspace_base_path():
    """测试获取工作区根目录"""
    base = get_workspace_base_path()
    assert "10_Tasks" in base or base.endswith(".pkm")

def test_create_task_workspace():
    """测试创建任务工作区"""
    with tempfile.TemporaryDirectory() as tmpdir:
        task_id = "TASK_T20260409_01"
        title = "测试任务"
        workspace_path = create_task_workspace(
            task_id=task_id,
            title=title,
            base_dir=tmpdir
        )
        assert os.path.exists(workspace_path)
        assert os.path.exists(os.path.join(workspace_path, "task.md"))
        with open(os.path.join(workspace_path, "task.md")) as f:
            content = f.read()
            assert "测试任务" in content
            assert "TASK_T20260409_01" in content
            assert "AI 使用指南" in content

def test_create_project_workspace():
    """测试创建项目工作区"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_id = "P_20260409_项目A"
        name = "项目A"
        workspace_path = create_project_workspace(
            project_id=project_id,
            name=name,
            base_dir=tmpdir
        )
        assert os.path.exists(workspace_path)
        assert os.path.exists(os.path.join(workspace_path, "project.md"))
        with open(os.path.join(workspace_path, "project.md")) as f:
            content = f.read()
            assert "项目A" in content
            assert "AI 使用指南" in content
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_workspace.py -v`
Expected: FAIL - workspace module not found

- [ ] **Step 3: 实现 workspace.py**

```python
# workspace.py
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

WORKSPACE_BASE = os.path.expanduser("~/.pkm")
TASK_WORKSPACE_BASE = os.path.join(WORKSPACE_BASE, "10_Tasks")
PROJECT_WORKSPACE_BASE = os.path.join(WORKSPACE_BASE, "60_Projects")


def get_workspace_base_path() -> str:
    """获取工作区根目录"""
    return WORKSPACE_BASE


def get_task_workspace_base() -> str:
    """获取任务工作区根目录"""
    os.makedirs(TASK_WORKSPACE_BASE, exist_ok=True)
    return TASK_WORKSPACE_BASE


def get_project_workspace_base() -> str:
    """获取项目工作区根目录"""
    os.makedirs(PROJECT_WORKSPACE_BASE, exist_ok=True)
    return PROJECT_WORKSPACE_BASE


def generate_task_workspace_name() -> str:
    """生成任务工作区目录名: TASK_T{date}_{seq}"""
    today = datetime.now().strftime("%Y%m%d")
    # 查找今天已创建的任务数量
    base = get_task_workspace_base()
    existing = [d for d in os.listdir(base) if d.startswith(f"TASK_T{today}_")]
    seq = len(existing) + 1
    return f"TASK_T{today}_{seq:02d}"


def create_task_workspace(task_id: str, title: str, base_dir: Optional[str] = None) -> str:
    """创建任务工作区目录和 task.md 文件"""
    if base_dir is None:
        base_dir = get_task_workspace_base()
    else:
        os.makedirs(base_dir, exist_ok=True)

    workspace_name = generate_task_workspace_name()
    workspace_path = os.path.join(base_dir, workspace_name)
    os.makedirs(workspace_path, exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    task_md = f"""---
purpose: 任务 AI 记忆上下文
maintainer: AI assistant
last_updated: {now}
---

# Task: {title}
- ID: {task_id}
- 创建时间: {now}

## 背景与目标
任务的核心背景、目标、预期结果

## 上下文与思路
- 想法
- 实现思路
- 技术要点

## 计划
1. 第一步
2. 第二步

---
## AI 使用指南
- 本文件是任务的 AI 记忆上下文，存储任务相关的背景、思路、计划
- AI 应阅读此文件理解任务背景后再开始工作
- 任务进展、决策、关键发现应及时更新到此文件
- 保持简洁，聚焦对后续工作有价值的信息
"""
    with open(os.path.join(workspace_path, "task.md"), "w", encoding="utf-8") as f:
        f.write(task_md)

    return workspace_path


def create_project_workspace(project_id: str, name: str, base_dir: Optional[str] = None) -> str:
    """创建项目工作区目录和 project.md 文件"""
    if base_dir is None:
        base_dir = get_project_workspace_base()
    else:
        os.makedirs(base_dir, exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    workspace_name = f"P_{today}_{name}"
    workspace_path = os.path.join(base_dir, workspace_name)
    os.makedirs(workspace_path, exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    project_md = f"""---
purpose: 项目 AI 记忆上下文
maintainer: AI assistant
last_updated: {now}
---

# Project: {name}
- ID: {project_id}
- 创建时间: {now}

## 项目描述
项目背景、目标、范围

## 上下文
- 技术栈/领域
- 关键约束
- 相关资源

---
## AI 使用指南
- 本文件是项目的 AI 记忆上下文，存储项目相关的背景、上下文
- AI 应阅读此文件理解项目背景后再开始相关工作
- 项目的关键决策、技术方案、经验教训应及时更新到此文件
- 保持简洁，聚焦对后续工作有价值的信息
"""
    with open(os.path.join(workspace_path, "project.md"), "w", encoding="utf-8") as f:
        f.write(project_md)

    return workspace_path
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/test_workspace.py -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add pkm-server/workspace.py pkm-server/tests/test_workspace.py
git commit -m "feat: 添加工作区创建模块 workspace.py"
```

---

## Task 2: 修改 database.py 添加 workspace_path 字段

**Files:**
- Modify: `pkm-server/database.py:13-40` (init_db 函数)
- Modify: `pkm-server/database.py:68-88` (create_project 函数)
- Modify: `pkm-server/database.py:132-159` (create_task 函数)

- [ ] **Step 1: 编写测试**

```python
# 在 tests/test_database.py 中添加
def test_create_task_with_workspace_path():
    """测试创建任务时 workspace_path 被记录"""
    # 清理环境
    database.delete_task("test_ws_task_id")
    task = database.create_task(
        title="测试任务",
        priority="medium",
        quadrant=2,
        workspace_path="/tmp/test_task_workspace"
    )
    assert task["workspace_path"] == "/tmp/test_task_workspace"
    # 清理
    database.delete_task("test_ws_task_id")
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/test_database.py::test_create_task_with_workspace_path -v`
Expected: FAIL - workspace_path not in create_task

- [ ] **Step 3: 修改 database.py - init_db**

```python
# init_db 函数中修改 CREATE TABLE tasks 语句
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
        workspace_path TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        completed_at TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )
""")

# CREATE TABLE projects 语句也需要添加 workspace_path
cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'active',
        workspace_path TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        completed_at TEXT
    )
""")
```

- [ ] **Step 4: 修改 database.py - create_task 函数**

```python
def create_task(title: str, priority: str = "medium", quadrant: int = 2,
                project_id: Optional[str] = None, progress: Optional[str] = None,
                due_date: Optional[str] = None, workspace_path: Optional[str] = None) -> dict:
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
        "workspace_path": workspace_path,  # 新增字段
        "created_at": now,
        "updated_at": now,
        "completed_at": None
    }
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (id, title, status, priority, quadrant, project_id, progress, due_date, workspace_path, created_at, updated_at, completed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (task["id"], task["title"], task["status"], task["priority"], task["quadrant"],
             task["project_id"], task["progress"], task["due_date"], task["workspace_path"],
             task["created_at"], task["updated_at"], task["completed_at"])
        )
    return task
```

- [ ] **Step 5: 修改 database.py - create_project 函数**

```python
def create_project(name: str, description: Optional[str] = None, workspace_path: Optional[str] = None) -> dict:
    import uuid
    now = datetime.utcnow().isoformat()
    project = {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "status": "active",
        "workspace_path": workspace_path,  # 新增字段
        "created_at": now,
        "updated_at": now,
        "completed_at": None
    }
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (id, name, description, status, workspace_path, created_at, updated_at, completed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (project["id"], project["name"], project["description"], project["status"],
             project["workspace_path"], project["created_at"], project["updated_at"], project["completed_at"])
        )
    return project
```

- [ ] **Step 6: 运行测试验证通过**

Run: `pytest tests/test_database.py::test_create_task_with_workspace_path -v`
Expected: PASS

- [ ] **Step 7: 提交**

```bash
git add pkm-server/database.py pkm-server/tests/test_database.py
git commit -m "feat: database 添加 workspace_path 字段支持"
```

---

## Task 3: 修改 models.py 添加 workspace_path 字段

**Files:**
- Modify: `pkm-server/models.py`

- [ ] **Step 1: 修改 models.py**

```python
# TaskBase 类中添加
class TaskBase(BaseModel):
    title: str
    priority: TaskPriority = TaskPriority.medium
    quadrant: int = 2
    project_id: Optional[str] = None
    progress: Optional[str] = None
    due_date: Optional[date] = None
    workspace_path: Optional[str] = None  # 新增

# Task 类中添加
class Task(TaskBase):
    id: str
    status: TaskStatus = TaskStatus.pending
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    workspace_path: Optional[str] = None  # 新增

# ProjectBase 类中添加
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    workspace_path: Optional[str] = None  # 新增

# Project 类中添加
class Project(ProjectBase):
    id: str
    status: ProjectStatus = ProjectStatus.active
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    workspace_path: Optional[str] = None  # 新增
```

- [ ] **Step 2: 验证测试通过**

Run: `pytest tests/test_models.py -v`
Expected: PASS (如有问题需要修复)

- [ ] **Step 3: 提交**

```bash
git add pkm-server/models.py
git commit -m "feat: models 添加 workspace_path 字段"
```

---

## Task 4: 修改 cli.py 在创建任务/项目时调用工作区创建

**Files:**
- Modify: `pkm-server/cli.py:116-136` (task add 命令)
- Modify: `pkm-server/cli.py:246-260` (project add 命令)

- [ ] **Step 1: 修改 cli.py - 添加 import**

```python
# 在文件顶部添加
from workspace import create_task_workspace, create_project_workspace
```

- [ ] **Step 2: 修改 task add 命令**

```python
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

    # 调用 API 创建任务（返回包含 id）
    r = requests.post(f"{API_BASE}/api/tasks", json=payload)
    r.raise_for_status()
    task = r.json()

    # 创建物理工作区
    workspace_path = create_task_workspace(task_id=task["id"], title=title)
    task["workspace_path"] = workspace_path

    # 更新任务的 workspace_path
    update_payload = {"workspace_path": workspace_path}
    requests.patch(f"{API_BASE}/api/tasks/{task['id']}", json=update_payload)

    click.echo(f"Task created: {task['id']}")
    click.echo(f"Workspace: {workspace_path}")
```

- [ ] **Step 3: 修改 project add 命令**

```python
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

    # 调用 API 创建项目（返回包含 id）
    r = requests.post(f"{API_BASE}/api/projects", json=payload)
    r.raise_for_status()
    project = r.json()

    # 创建物理工作区
    workspace_path = create_project_workspace(project_id=project["id"], name=name)
    project["workspace_path"] = workspace_path

    # 更新项目的 workspace_path
    update_payload = {"workspace_path": workspace_path}
    requests.patch(f"{API_BASE}/api/projects/{project['id']}", json=update_payload)

    click.echo(f"Project created: {project['id']}")
    click.echo(f"Workspace: {workspace_path}")
```

- [ ] **Step 4: 验证测试通过**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add pkm-server/cli.py
git commit -m "feat: cli 在创建任务/项目时自动创建物理工作区"
```

---

## Task 5: 修改 main.py 支持 workspace_path 更新

**Files:**
- Modify: `pkm-server/main.py`

- [ ] **Step 1: 修改 TaskUpdate 模型处理 workspace_path**

```python
# 在 update_task 函数中确保 workspace_path 能被更新
@app.patch("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, update: TaskUpdate):
    data = update.model_dump(exclude_unset=True)
    if "priority" in data and data["priority"]:
        data["priority"] = data["priority"].value
    if "due_date" in data and data["due_date"]:
        data["due_date"] = str(data["due_date"])
    if "workspace_path" in data:
        # workspace_path 直接更新
        pass
    task = database.update_task(task_id, **data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# 在 update_project 函数中确保 workspace_path 能被更新
@app.patch("/api/projects/{project_id}", response_model=Project)
def update_project(project_id: str, update: ProjectUpdate):
    data = update.model_dump(exclude_unset=True)
    if "workspace_path" in data:
        # workspace_path 直接更新
        pass
    project = database.update_project(project_id, **data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
```

- [ ] **Step 2: 验证 API 测试通过**

Run: `pytest tests/test_api.py -v`
Expected: PASS

- [ ] **Step 3: 提交**

```bash
git add pkm-server/main.py
git commit -m "feat: main.py 支持 workspace_path 字段更新"
```

---

## Task 6: 端到端测试验证

- [ ] **Step 1: 启动服务并测试**

```bash
# 在容器中启动服务
docker-compose up -d

# 测试创建任务
docker exec pkm-server python -m pkm.cli task add "测试任务" --priority high

# 验证工作区创建
docker exec pkm-server ls -la ~/.pkm/10_Tasks/
docker exec pkm-server cat ~/.pkm/10_Tasks/*/task.md

# 测试创建项目
docker exec pkm-server python -m pkm.cli project add "测试项目"

# 验证项目工作区创建
docker exec pkm-server ls -la ~/.pkm/60_Projects/
docker exec pkm-server cat ~/.pkm/60_Projects/*/project.md
```

- [ ] **Step 2: 提交**

```bash
git add -A
git commit -m "feat: 完成任务与项目工作区功能实现"
```

---

## 实施顺序

1. Task 1: 创建 workspace.py
2. Task 2: 修改 database.py
3. Task 3: 修改 models.py
4. Task 4: 修改 cli.py
5. Task 5: 修改 main.py
6. Task 6: 端到端测试验证

---

## 自检清单

- [ ] 所有测试通过
- [ ] workspace.py 正确创建 task.md 和 project.md
- [ ] task.md 包含 AI 使用指南
- [ ] project.md 包含 AI 使用指南
- [ ] CLI 创建任务/项目时自动创建工作区
- [ ] 工作区文件挂载到 ~/.pkm 目录
