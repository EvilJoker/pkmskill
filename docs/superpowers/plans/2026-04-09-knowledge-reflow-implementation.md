# 知识回流实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现知识回流机制，任务完成后经验/方案自动回流到项目工作区

**Architecture:**
- Server 定时扫描 approved 状态任务，执行回流
- Claude CLI `claude -p` 调用 AI 提取经验方案
- 任务状态：pending → done → approved → archived

**Tech Stack:** FastAPI, SQLite, Click CLI, Claude CLI

---

## 文件结构

```
pkm-server/
├── main.py                    # FastAPI 应用，新增 /api/knowledge/* 端点
├── database.py                # SQLite 操作，新增 knowledge_reflow 表
├── models.py                 # Pydantic 模型，扩展 TaskStatus
├── workspace.py             # 工作区操作，新增 create_default_project()
├── knowledge.py              # 新增：知识回流核心逻辑
├── tests/
│   ├── test_knowledge.py     # 新增：知识回流测试
│   └── test_database.py      # 修改：扩展测试覆盖新表
└── pkm/
    └── cli.py                # Click CLI，新增 pkm reflow 命令
```

---

## Task 1: 扩展 TaskStatus 和数据库

**Files:**
- Modify: `pkm-server/models.py:1-60`
- Modify: `pkm-server/database.py:1-225`

- [ ] **Step 1: 扩展 TaskStatus 枚举**

打开 `models.py`，在 `TaskStatus` 枚举中添加新状态：

```python
class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"           # 新增：已完成，待评审
    approved = "approved"    # 新增：评审通过，可回流
    archived = "archived"   # 新增：已归档
```

- [ ] **Step 2: 运行测试确认无破坏**

Run: `pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 3: 数据库新增 knowledge_reflow 表**

打开 `database.py`，在 `init_db()` 函数中添加：

```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_reflow (
        id INTEGER PRIMARY KEY,
        task_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        reflowed_at TEXT,
        error TEXT,
        created_at TEXT NOT NULL
    )
""")
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_reflow_status ON knowledge_reflow(status)
""")
```

- [ ] **Step 4: 新增 knowledge_reflow 表操作函数**

在 `database.py` 末尾添加：

```python
# Knowledge Reflow CRUD
def create_reflow(task_id: str, project_id: str) -> dict:
    now = datetime.utcnow().isoformat()
    reflow = {
        "id": None,
        "task_id": task_id,
        "project_id": project_id,
        "status": "pending",
        "reflowed_at": None,
        "error": None,
        "created_at": now
    }
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO knowledge_reflow (task_id, project_id, status, created_at) VALUES (?, ?, ?, ?)",
            (task_id, project_id, "pending", now)
        )
        reflow["id"] = cursor.lastrowid
    return reflow


def get_reflow_by_task(task_id: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM knowledge_reflow WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_reflow_status(reflow_id: int, status: str, error: Optional[str] = None) -> None:
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        if status == "completed":
            cursor.execute(
                "UPDATE knowledge_reflow SET status = ?, reflowed_at = ? WHERE id = ?",
                (status, now, reflow_id)
            )
        elif error:
            cursor.execute(
                "UPDATE knowledge_reflow SET status = ?, error = ? WHERE id = ?",
                (status, error, reflow_id)
            )
        else:
            cursor.execute(
                "UPDATE knowledge_reflow SET status = ? WHERE id = ?",
                (status, reflow_id)
            )


def list_pending_reflows() -> List[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM knowledge_reflow WHERE status IN ('pending', 'processing') ORDER BY created_at"
        )
        return [dict(row) for row in cursor.fetchall()]
```

- [ ] **Step 5: 修改 complete_task 状态为 done**

在 `database.py` 的 `complete_task` 函数中：

```python
def complete_task(task_id: str) -> Optional[dict]:
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = 'done', updated_at = ?, completed_at = ? WHERE id = ?",
            (now, now, task_id)
        )
    return get_task(task_id)
```

- [ ] **Step 6: 运行测试**

Run: `pytest tests/test_database.py -v`
Expected: PASS

- [ ] **Step 7: 提交**

```bash
git add pkm-server/models.py pkm-server/database.py
git commit -m "feat: 扩展 TaskStatus，新增 knowledge_reflow 表

- TaskStatus 新增 done, approved, archived 状态
- knowledge_reflow 表新增 pending, processing, completed, failed 状态
- complete_task 状态改为 done

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: Default 项目工作区

**Files:**
- Modify: `pkm-server/workspace.py:1-126`

- [ ] **Step 1: 新增 create_default_project_workspace 函数**

在 `workspace.py` 末尾添加：

```python
DEFAULT_PROJECT_NAME = "default"
ARCHIVE_BASE = os.path.join(WORKSPACE_BASE, "80_Archives")


def get_archive_base() -> str:
    """获取归档目录根目录"""
    os.makedirs(ARCHIVE_BASE, exist_ok=True)
    return ARCHIVE_BASE


def create_default_project_workspace() -> str:
    """创建 default 项目工作区（如果不存在）"""
    base_dir = get_project_workspace_base()
    default_name = f"P_default"

    # 检查是否已存在
    for item in os.listdir(base_dir):
        if item == default_name or item.startswith("P_default"):
            return os.path.join(base_dir, item)

    # 创建 default 项目
    workspace_path = os.path.join(base_dir, default_name)
    os.makedirs(workspace_path, exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    project_md = f"""---
purpose: Default 项目工作区
maintainer: system
last_updated: {now}
---

# Project: Default

所有找不到关联项目的任务都会回流到这里。

## 项目描述
用于接收无法归属到特定项目的任务经验。

---
"""
    with open(os.path.join(workspace_path, "project.md"), "w", encoding="utf-8") as f:
        f.write(project_md)

    return workspace_path


def get_default_project_workspace() -> str:
    """获取 default 项目工作区路径（必须已存在）"""
    base_dir = get_project_workspace_base()
    for item in os.listdir(base_dir):
        if item == "P_default" or item.startswith("P_default"):
            return os.path.join(base_dir, item)
    # 如果不存在，创建它
    return create_default_project_workspace()


def archive_task_workspace(workspace_path: str) -> str:
    """将任务工作区移动到归档目录"""
    if not workspace_path or not os.path.exists(workspace_path):
        return None

    archive_dir = get_archive_base()
    task_name = os.path.basename(workspace_path)
    archive_path = os.path.join(archive_dir, task_name)

    # 如果已存在，加时间戳
    if os.path.exists(archive_path):
        task_name = f"{task_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        archive_path = os.path.join(archive_dir, task_name)

    import shutil
    shutil.move(workspace_path, archive_path)
    return archive_path
```

- [ ] **Step 2: 运行测试确认无破坏**

Run: `pytest tests/test_workspace.py -v`
Expected: PASS

- [ ] **Step 3: 提交**

```bash
git add pkm-server/workspace.py
git commit -m "feat: 新增 default 项目和归档目录支持

- create_default_project_workspace() 创建 default 项目
- get_default_project_workspace() 获取 default 项目路径
- archive_task_workspace() 移动任务到归档目录

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: 知识回流核心逻辑

**Files:**
- Create: `pkm-server/knowledge.py`
- Modify: `pkm-server/main.py:1-133`

- [ ] **Step 1: 创建 knowledge.py 回流核心逻辑**

创建 `pkm-server/knowledge.py`：

```python
import os
import subprocess
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime

from database import (
    list_tasks, get_task, update_task, get_project,
    create_reflow, get_reflow_by_task, update_reflow_status, list_pending_reflows
)
from workspace import get_default_project_workspace, archive_task_workspace, get_project_workspace_base

# Claude CLI 路径
CLAUDE_CMD = "claude"

# 回流配置
REFLOW_CONFIG = {
    "interval": 3600,
    "exclude_patterns": ["*.py", "*.js", "*.ts", "*.go", "*.java",
                        "task.md", "completed.md", "*.sh", "*.yaml", "*.json"],
    "content_types": ["经验", "方案"]
}


def check_claude_environment() -> Tuple[bool, str]:
    """检查 Claude CLI 环境是否可用"""
    try:
        result = subprocess.run(
            [CLAUDE_CMD, "-p", "hello"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True, "Claude CLI 环境正常"
        else:
            return False, f"Claude CLI 返回错误: {result.stderr}"
    except FileNotFoundError:
        return False, "Claude CLI 未安装，请先安装 Claude Code"
    except subprocess.TimeoutExpired:
        return False, "Claude CLI 调用超时"
    except Exception as e:
        return False, f"Claude CLI 调用失败: {str(e)}"


def should_exclude_file(filename: str) -> bool:
    """判断文件是否应该被排除"""
    for pattern in REFLOW_CONFIG["exclude_patterns"]:
        if pattern.startswith("*."):
            ext = pattern[1:]
            if filename.endswith(ext):
                return True
        elif filename == pattern:
            return True
    return False


def read_task_workspace_content(workspace_path: str) -> str:
    """读取任务工作区内容（排除指定文件）"""
    if not os.path.exists(workspace_path):
        return ""

    contents = []
    for root, dirs, files in os.walk(workspace_path):
        for filename in files:
            if should_exclude_file(filename):
                continue
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    rel_path = os.path.relpath(filepath, workspace_path)
                    contents.append(f"=== {rel_path} ===\n{f.read()}\n")
            except Exception:
                pass

    return "\n".join(contents)


def extract_knowledge_with_claude(content: str) -> str:
    """调用 Claude CLI 提取经验和方案"""
    if not content.strip():
        return ""

    prompt = f"""请从以下内容中提取经验和方案，用中文回答。

{content}

请以结构化的方式输出，格式如下：
## 经验
- 经验点1
- 经验点2

## 方案
- 方案点1
- 方案点2

如果没有找到明显的经验或方案，请说明内容的主要信息。
"""

    try:
        result = subprocess.run(
            [CLAUDE_CMD, "-p", prompt, "--allowedTools", "Read,Edit,Write,Bash"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return f"[Claude 调用失败: {result.stderr}]"
    except subprocess.TimeoutExpired:
        return "[Claude 调用超时]"
    except Exception as e:
        return f"[Claude 调用异常: {str(e)}]"


def append_to_project_memory(project_workspace: str, task_info: dict, knowledge: str) -> None:
    """追加知识到项目记忆文件"""
    project_md_path = os.path.join(project_workspace, "project.md")

    # 读取现有内容
    existing_content = ""
    if os.path.exists(project_md_path):
        with open(project_md_path, "r", encoding="utf-8") as f:
            existing_content = f.read()

    # 构建新条目
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    task_title = task_info.get("title", "未知任务")
    task_id = task_info.get("id", "")

    new_entry = f"""
### {now} 任务：{task_title}

- **任务ID**: {task_id}
- **类型**: 经验/方案
- **内容**:
{knowledge}
"""

    # 追加到文件
    with open(project_md_path, "w", encoding="utf-8") as f:
        if "## 经验/方案索引" in existing_content:
            # 在现有索引后追加
            f.write(existing_content.split("## 经验/方案索引")[0])
            f.write("## 经验/方案索引\n")
            parts = existing_content.split("## 经验/方案索引")[1]
            if "### " in parts:
                idx = parts.index("### ")
                f.write(parts[:idx])
                f.write(new_entry)
                f.write("\n" + parts[idx:])
            else:
                f.write(parts)
                f.write(new_entry)
        else:
            # 文件中没有索引，追加到末尾
            f.write(existing_content)
            f.write("\n\n## 经验/方案索引\n")
            f.write(new_entry)


def process_single_task_reflow(task_id: str) -> Tuple[bool, str]:
    """处理单个任务的知识回流"""
    task = get_task(task_id)
    if not task:
        return False, "任务不存在"

    if task["status"] != "approved":
        return False, f"任务状态不是 approved: {task['status']}"

    workspace_path = task.get("workspace_path")
    if not workspace_path:
        return False, "任务没有工作区"

    # 确定目标项目
    project_id = task.get("project_id")
    if project_id:
        project = get_project(project_id)
        if project and project.get("workspace_path"):
            project_workspace = project["workspace_path"]
        else:
            project_workspace = get_default_project_workspace()
    else:
        project_workspace = get_default_project_workspace()

    # 创建回流记录
    reflow = get_reflow_by_task(task_id)
    if not reflow:
        reflow = create_reflow(task_id, project.get("id") if project else "default")

    # 更新状态为 processing
    update_reflow_status(reflow["id"], "processing")

    try:
        # 读取任务工作区内容
        content = read_task_workspace_content(workspace_path)
        if not content.strip():
            update_reflow_status(reflow["id"], "failed", "任务工作区没有内容")
            return False, "任务工作区没有内容"

        # 调用 Claude 提取知识
        knowledge = extract_knowledge_with_claude(content)

        # 追加到项目记忆
        append_to_project_memory(project_workspace, task, knowledge)

        # 更新任务状态为 archived
        update_task(task_id, status="archived")

        # 更新回流状态为 completed
        update_reflow_status(reflow["id"], "completed")

        # 移动任务工作区到归档目录
        archive_task_workspace(workspace_path)

        return True, "回流成功"

    except Exception as e:
        update_reflow_status(reflow["id"], "failed", str(e))
        return False, f"回流失败: {str(e)}"


def run_reflow_cycle() -> Dict:
    """执行一轮知识回流"""
    # 获取所有 approved 状态的任务
    tasks = list_tasks(status="approved")

    processed = 0
    succeeded = 0
    failed = 0
    errors = []

    for task in tasks:
        task_id = task["id"]
        reflow = get_reflow_by_task(task_id)

        # 跳过正在处理或已完成的
        if reflow and reflow["status"] in ("processing", "completed"):
            continue

        processed += 1
        success, message = process_single_task_reflow(task_id)
        if success:
            succeeded += 1
        else:
            failed += 1
            errors.append({"task_id": task_id, "message": message})

    return {
        "processed": processed,
        "succeeded": succeeded,
        "failed": failed,
        "errors": errors,
        "timestamp": datetime.now().isoformat()
    }


def get_reflow_status() -> Dict:
    """获取回流状态"""
    tasks = list_tasks(status="approved")
    pending_reflows = list_pending_reflows()

    return {
        "pending_approved_tasks": len(tasks),
        "pending_reflows": len(pending_reflows),
        "config": REFLOW_CONFIG,
        "claude_available": check_claude_environment()[0]
    }
```

- [ ] **Step 2: 修改 main.py 添加 API 端点**

在 `main.py` 末尾添加：

```python
# Knowledge Reflow APIs
@app.post("/api/knowledge/reflow")
def trigger_reflow():
    """手动触发知识回流"""
    from knowledge import run_reflow_cycle
    result = run_reflow_cycle()
    return {
        "triggered": True,
        "processed": result["processed"],
        "succeeded": result["succeeded"],
        "failed": result["failed"],
        "message": f"处理了 {result['processed']} 个任务，成功 {result['succeeded']}，失败 {result['failed']}"
    }


@app.get("/api/knowledge/status")
def get_reflow_status():
    """获取回流状态"""
    from knowledge import get_reflow_status as get_status
    return get_status()


@app.patch("/api/knowledge/config")
def update_reflow_config(interval: Optional[int] = None, exclude_patterns: Optional[List[str]] = None):
    """配置回流参数"""
    from knowledge import REFLOW_CONFIG
    if interval is not None:
        REFLOW_CONFIG["interval"] = interval
    if exclude_patterns is not None:
        REFLOW_CONFIG["exclude_patterns"] = exclude_patterns
    return {"config": REFLOW_CONFIG}


@app.post("/api/knowledge/approve/{task_id}")
def approve_task_reflow(task_id: str):
    """批准任务回流（将状态从 done 改为 approved）"""
    from database import get_task, update_task
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] != "done":
        raise HTTPException(status_code=400, detail=f"Task status is {task['status']}, expected done")
    updated = update_task(task_id, status="approved")
    return updated
```

- [ ] **Step 3: 运行测试**

Run: `pytest tests/test_api.py -v`
Expected: PASS

- [ ] **Step 4: 提交**

```bash
git add pkm-server/knowledge.py pkm-server/main.py
git commit -m "feat: 知识回流核心逻辑

- knowledge.py 实现回流核心逻辑
- /api/knowledge/reflow 手动触发回流
- /api/knowledge/status 获取回流状态
- /api/knowledge/config 配置回流参数
- /api/knowledge/approve/{task_id} 批准任务回流

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: PKM CLI reflow 命令

**Files:**
- Modify: `pkm-server/pkm/cli.py:1-349`

- [ ] **Step 1: 添加 reflow 命令**

在 `cli.py` 末尾添加：

```python
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
```

- [ ] **Step 2: 运行测试确认 CLI 无破坏**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 3: 提交**

```bash
git add pkm-server/pkm/cli.py
git commit -m "feat: 新增 pkm reflow CLI 命令

- pkm reflow run 手动触发回流
- pkm reflow status 查看回流状态

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: Server 初始化检查

**Files:**
- Modify: `pkm-server/main.py:24-26`

- [ ] **Step 1: 添加启动时检查**

修改 `main.py` 的 `startup` 函数：

```python
@ app.on_event("startup")
def startup():
    database.init_db()

    # 初始化 default 项目工作区
    from workspace import create_default_project_workspace, check_claude_environment
    create_default_project_workspace()

    # 检查 Claude CLI 环境
    claude_ok, claude_msg = check_claude_environment()
    if not claude_ok:
        import logging
        logging.warning(f"Claude CLI 环境检查失败: {claude_msg}")
```

- [ ] **Step 2: 提交**

```bash
git add pkm-server/main.py
git commit -m "feat: Server 启动时初始化检查

- 启动时创建 default 项目工作区
- 检查 Claude CLI 环境

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 6: 单元测试

**Files:**
- Create: `pkm-server/tests/test_knowledge.py`

- [ ] **Step 1: 创建知识回流测试**

创建 `tests/test_knowledge.py`：

```python
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# 确保导入路径正确
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge import (
    should_exclude_file,
    read_task_workspace_content,
    REFLOW_CONFIG
)


class TestShouldExcludeFile:
    def test_exclude_py_files(self):
        assert should_exclude_file("test.py") == True
        assert should_exclude_file("main.js") == True
        assert should_exclude_file("app.ts") == True

    def test_exclude_task_and_completed(self):
        assert should_exclude_file("task.md") == True
        assert should_exclude_file("completed.md") == True

    def test_include_markdown(self):
        assert should_exclude_file("readme.md") == False
        assert should_exclude_file("notes.md") == False

    def test_exclude_config_files(self):
        assert should_exclude_file("config.yaml") == True
        assert should_exclude_file("settings.json") == True


class TestReadTaskWorkspaceContent:
    def test_read_content_excludes_patterns(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建文件
            with open(os.path.join(tmpdir, "task.md"), "w") as f:
                f.write("task content")
            with open(os.path.join(tmpdir, "notes.md"), "w") as f:
                f.write("notes content")
            with open(os.path.join(tmpdir, "script.py"), "w") as f:
                f.write("print('hello')")

            content = read_task_workspace_content(tmpdir)

            assert "task content" not in content  # 排除
            assert "notes content" in content  # 包含
            assert "print('hello')" not in content  # 排除

    def test_empty_workspace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = read_task_workspace_content(tmpdir)
            assert content == ""


class TestReflowConfig:
    def test_default_config(self):
        assert REFLOW_CONFIG["interval"] == 3600
        assert "*.py" in REFLOW_CONFIG["exclude_patterns"]
        assert "task.md" in REFLOW_CONFIG["exclude_patterns"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

- [ ] **Step 2: 运行测试**

Run: `pytest tests/test_knowledge.py -v`
Expected: PASS

- [ ] **Step 3: 提交**

```bash
git add tests/test_knowledge.py
git commit -m "test: 知识回流单元测试

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## 实施检查清单

- [ ] Task 1: TaskStatus 扩展完成
- [ ] Task 2: Default 项目工作区创建完成
- [ ] Task 3: 知识回流核心逻辑完成
- [ ] Task 4: CLI reflow 命令完成
- [ ] Task 5: Server 初始化检查完成
- [ ] Task 6: 单元测试完成
- [ ] 所有测试通过: `pytest tests/ -v`
