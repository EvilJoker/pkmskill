# PKM Reflow 两阶段知识提炼实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现两阶段知识提炼：Stage1（任务→项目）+ Stage2（项目→公共知识区），支持定时任务调度

**Architecture:**
- FastAPI 后端服务，内置 APScheduler 定时任务调度器
- Stage1 扫描所有 approved 任务追加到 project.md
- Stage2 扫描 60_Projects/ 提炼到 20_Areas/knowledge/，每批最多5个项目
- CLI 通过 Click 实现，API 通过 FastAPI 实现

**Tech Stack:** Python, FastAPI, APScheduler, Click, SQLite

---

## 文件修改映射

| 文件 | 操作 | 职责 |
|------|------|------|
| `pkm-server/database.py` | 修改 | 新增 refined/refined_at 字段及查询函数 |
| `pkm-server/knowledge.py` | 修改 | Stage2 提炼逻辑 |
| `pkm-server/main.py` | 修改 | 新增 API 端点、定时任务 |
| `pkm-server/pkm/cli.py` | 修改 | 新增 stage2 CLI 命令 |
| `pkm-server/models.py` | 修改 | Project 模型新增字段 |
| `pkm-server/tests/test_knowledge.py` | 创建 | Stage2 单元测试 |

---

## Task 1: 数据库扩展

**Files:**
- Modify: `pkm-server/database.py:14-26`
- Modify: `pkm-server/models.py`

- [ ] **Step 1: 修改 projects 表结构，添加 refined 和 refined_at 字段**

```python
# 在 database.py init_db() 的 CREATE TABLE projects 中添加：
# refined BOOLEAN DEFAULT FALSE,
# refined_at TEXT,
```

- [ ] **Step 2: 添加 get_projects_needing_reflow() 函数**

```python
def get_projects_needing_reflow(limit: int = 5) -> List[dict]:
    """获取需要提炼的项目（未提炼或已更新）"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM projects
            WHERE status = 'active'
            AND (refined = FALSE OR refined_at IS NULL OR updated_at > refined_at)
            ORDER BY updated_at DESC
            LIMIT ?
        """, (limit,))
        return [row_to_project(row) for row in cursor.fetchall()]
```

- [ ] **Step 3: 添加 mark_project_refined() 函数**

```python
def mark_project_refined(project_id: str) -> None:
    """标记项目已提炼"""
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE projects SET refined = TRUE, refined_at = ? WHERE id = ?",
            (now, project_id)
        )
```

- [ ] **Step 4: 修改 models.py 的 Project 模型**

```python
class Project(ProjectBase):
    id: str
    status: ProjectStatus = ProjectStatus.active
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    workspace_path: Optional[str] = None
    refined: bool = False          # 新增
    refined_at: Optional[str] = None  # 新增
```

- [ ] **Step 5: 更新 database.py init_db 添加新列（ALTER TABLE）**

在 `init_db()` 中 projects 表创建后添加：
```python
# 添加 refined 和 refined_at 字段（如果不存在）
cursor.execute("ALTER TABLE projects ADD COLUMN refined BOOLEAN DEFAULT 0")
cursor.execute("ALTER TABLE projects ADD COLUMN refined_at TEXT")
```

- [ ] **Step 6: 测试数据库改动**

```bash
cd /media/vdc/github/pkmSkill/pkm-server
python -c "from database import init_db, get_projects_needing_reflow, mark_project_refined; init_db(); print('DB OK')"
```

- [ ] **Step 7: 提交**

```bash
git add pkm-server/database.py pkm-server/models.py
git commit -m "feat(reflow): 扩展 projects 表支持 refined 字段"
```

---

## Task 2: Stage2 提炼逻辑

**Files:**
- Modify: `pkm-server/knowledge.py`

- [ ] **Step 1: 添加知识目录常量**

```python
# 公共知识区路径
KNOWLEDGE_BASE = os.path.expanduser("~/.pkm/20_Areas/knowledge")
PRINCIPLES_DIR = os.path.join(KNOWLEDGE_BASE, "01principles")
PLAYBOOKS_DIR = os.path.join(KNOWLEDGE_BASE, "02playbooks")
TEMPLATES_DIR = os.path.join(KNOWLEDGE_BASE, "02templates")
CASES_DIR = os.path.join(KNOWLEDGE_BASE, "02cases")
NOTES_DIR = os.path.join(KNOWLEDGE_BASE, "03notes")
```

- [ ] **Step 2: 添加知识分类函数**

```python
def classify_knowledge(content: str) -> str:
    """调用 Claude 判断知识类型，返回目录名"""
    prompt = f"""请判断以下内容属于哪种知识类型：
- 原则/方法论（principles）
- 流程/SOP（playbooks）
- 模板（templates）
- 案例（cases）
- 知识点（notes）

只回答目录名：principles, playbooks, templates, cases, 或 notes

内容：
{content[:500]}"""

    try:
        model = os.environ.get("CLAUDE_MODEL", "MiniMax-M2.7-highspeed")
        result = subprocess.run(
            [CLAUDE_CMD, "-p", prompt,
             "--permission-mode", "acceptEdits",
             "--allowedTools", "Read",
             "--effort", "max",
             "--model", model],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            classification = result.stdout.strip().lower()
            if classification in ["principles", "playbooks", "templates", "cases", "notes"]:
                return classification
        return "notes"  # 默认
    except:
        return "notes"
```

- [ ] **Step 3: 添加去重检查函数**

```python
def check_duplicate(content: str, target_dir: str) -> Tuple[bool, str]:
    """检查内容是否重复，返回 (is_duplicate, similarity_type)"""
    prompt = f"""比较以下两条内容，判断是否重复：
内容A（已有）：见下方
内容B（新增）：{content[:300]}

只回答：duplicate（完全重复）/similar（相似）/new（全新）
回答一个词。"""

    target_path = os.path.join(KNOWLEDGE_BASE, target_dir)
    if not os.path.exists(target_path):
        return False, "new"

    # 扫描已有文件
    for filename in os.listdir(target_path):
        filepath = os.path.join(target_path, filename)
        if not filename.endswith(".md"):
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                existing = f.read()[:300]
            # 调用 Claude 判断相似度
            compare_prompt = f"""比较以下两条内容：
内容A：{existing}
内容B：{content[:300]}

判断是否重复（相似度>80%）：回答 duplicate
相似但不同（50-80%）：回答 similar
完全不同（<50%）：回答 new

只回答一个词。"""
            model = os.environ.get("CLAUDE_MODEL", "MiniMax-M2.7-highspeed")
            result = subprocess.run(
                [CLAUDE_CMD, "-p", compare_prompt,
                 "--permission-mode", "acceptEdits",
                 "--model", model],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                resp = result.stdout.strip().lower()
                if resp == "duplicate":
                    return True, "duplicate"
                elif resp == "similar":
                    return True, "similar"
        except:
            pass
    return False, "new"
```

- [ ] **Step 4: 添加写入知识文件函数**

```python
def write_to_knowledge_base(content: str, classification: str, source_project: str) -> str:
    """写入知识到对应目录，返回写入的文件路径"""
    dir_map = {
        "principles": PRINCIPLES_DIR,
        "playbooks": PLAYBOOKS_DIR,
        "templates": TEMPLATES_DIR,
        "cases": CASES_DIR,
        "notes": NOTES_DIR,
    }

    target_dir = dir_map.get(classification, NOTES_DIR)
    os.makedirs(target_dir, exist_ok=True)

    # 生成文件名
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_content = content[:50].replace("\n", " ").replace("#", "").replace("/", "_")
    filename = f"{now}_{safe_content}.md"
    filepath = os.path.join(target_dir, filename)

    # 写入内容
    file_content = f"""---
source: {source_project}
created: {now}
type: {classification}
---

{content}
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(file_content)

    return filepath
```

- [ ] **Step 5: 添加 run_stage2_cycle() 函数**

```python
def run_stage2_cycle(batch_size: int = 5) -> Dict:
    """执行一轮 Stage2 提炼"""
    from database import get_projects_needing_reflow, mark_project_refined, get_project

    projects = get_projects_needing_reflow(limit=batch_size)

    processed = 0
    succeeded = 0
    failed = 0
    errors = []

    for proj in projects:
        project_id = proj["id"]
        workspace_path = proj.get("workspace_path")

        if not workspace_path or not os.path.exists(workspace_path):
            errors.append({"project_id": project_id, "message": "项目工作区不存在"})
            failed += 1
            continue

        try:
            # 读取 project.md 中的经验/方案索引
            project_md_path = os.path.join(workspace_path, "project.md")
            if not os.path.exists(project_md_path):
                errors.append({"project_id": project_id, "message": "project.md 不存在"})
                failed += 1
                continue

            with open(project_md_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 提取 ## 经验/方案索引 部分
            if "## 经验/方案索引" in content:
                knowledge_section = content.split("## 经验/方案索引")[1]
            else:
                knowledge_section = content

            # 分割各条知识（以 ### 开头）
            knowledge_items = []
            lines = knowledge_section.split("\n")
            current_item = ""
            for line in lines:
                if line.startswith("### ") and current_item:
                    knowledge_items.append(current_item.strip())
                    current_item = ""
                current_item += "\n" + line
            if current_item.strip():
                knowledge_items.append(current_item.strip())

            # 处理每条知识
            for item in knowledge_items:
                if len(item) < 20:  # 跳过太短的内容
                    continue

                # 分类
                classification = classify_knowledge(item)

                # 去重检查
                is_dup, dup_type = check_duplicate(item, classification)
                if is_dup and dup_type == "duplicate":
                    continue  # 完全重复，跳过

                # 写入
                write_to_knowledge_base(item, classification, proj["name"])

            # 标记项目已提炼
            mark_project_refined(project_id)
            processed += 1
            succeeded += 1

        except Exception as e:
            errors.append({"project_id": project_id, "message": str(e)})
            failed += 1

    return {
        "processed": processed,
        "succeeded": succeeded,
        "failed": failed,
        "errors": errors,
        "timestamp": datetime.now().isoformat()
    }
```

- [ ] **Step 6: 添加 get_stage2_status() 函数**

```python
def get_stage2_status() -> Dict:
    """获取 Stage2 状态"""
    from database import get_projects_needing_reflow

    pending_projects = get_projects_needing_reflow(limit=100)

    return {
        "pending_projects": len(pending_projects),
        "config": REFLOW_CONFIG,
        "claude_available": check_claude_environment()[0]
    }
```

- [ ] **Step 7: 提交**

```bash
git add pkm-server/knowledge.py
git commit -m "feat(reflow): 实现 Stage2 提炼逻辑"
```

---

## Task 3: API 端点

**Files:**
- Modify: `pkm-server/main.py`

- [ ] **Step 1: 添加 stage2 API 端点**

```python
@app.post("/api/knowledge/reflow/stage2")
def trigger_stage2():
    """手动触发 Stage2 提炼"""
    from knowledge import run_stage2_cycle
    result = run_stage2_cycle(batch_size=5)
    return {
        "triggered": True,
        "processed": result["processed"],
        "succeeded": result["succeeded"],
        "failed": result["failed"],
        "message": f"处理了 {result['processed']} 个项目，成功 {result['succeeded']}，失败 {result['failed']}"
    }
```

- [ ] **Step 2: 添加 stage2 status 端点**

```python
@app.get("/api/knowledge/reflow/status/stage2")
def get_stage2_status():
    """获取 Stage2 状态"""
    from knowledge import get_stage2_status as get_status
    return get_status()
```

- [ ] **Step 3: 提交**

```bash
git add pkm-server/main.py
git commit -m "feat(reflow): 添加 Stage2 API 端点"
```

---

## Task 4: 定时任务

**Files:**
- Modify: `pkm-server/main.py`

- [ ] **Step 1: 安装 APScheduler 依赖**

检查 `pkm-server/setup.py` 或 `pyproject.toml` 是否已有 APScheduler，如果没有则添加：
```python
# setup.py install_requires 添加
"apscheduler>=3.10.0",
```

- [ ] **Step 2: 修改 main.py startup，添加定时任务**

```python
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

@app.on_event("startup")
def startup():
    database.init_db()

    # 创建 default 项目工作区
    from pkm.workspace import create_default_project_workspace
    create_default_project_workspace()

    # 启动定时任务调度器
    from knowledge import run_reflow_cycle, run_stage2_cycle

    # Stage1: 每 3 小时整点执行
    scheduler.add_job(run_reflow_cycle, 'cron', minute=0)

    # Stage2: 每 3 小时 +30 分钟执行
    scheduler.add_job(run_stage2_cycle, 'cron', minute=30)

    scheduler.start()

@app.on_event("shutdown")
def shutdown():
    scheduler.shutdown()
```

- [ ] **Step 3: 测试定时任务启动**

```bash
cd /media/vdc/github/pkmSkill/pkm-server
python -c "from main import app; from database import init_db; init_db(); print('定时任务初始化 OK')"
```

- [ ] **Step 4: 提交**

```bash
git add pkm-server/setup.py pkm-server/main.py
git commit -m "feat(reflow): 添加 APScheduler 定时任务调度"
```

---

## Task 5: CLI 命令

**Files:**
- Modify: `pkm-server/pkm/cli.py`

- [ ] **Step 1: 添加 stage2 子命令**

```python
@reflow.command()
@click.option("--batch-size", default=5, help="每批处理项目数")
def stage2(batch_size):
    """手动触发 Stage2 提炼

    Example:
      pkm reflow stage2
      pkm reflow stage2 --batch-size 3"""
    click.echo("Starting Stage2 knowledge distillation...")
    r = requests.post(f"{API_BASE}/api/knowledge/reflow/stage2")
    r.raise_for_status()
    result = r.json()
    click.echo(f"Stage2 completed: {result['message']}")
```

- [ ] **Step 2: 修改 status 命令显示 stage2 信息**

```python
@reflow.command()
def status():
    """获取回流状态

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
    r2 = requests.get(f"{API_BASE}/api/knowledge/reflow/status/stage2")
    r2.raise_for_status()
    stage2_result = r2.json()
    click.echo(f"\n--- Stage2 ---")
    click.echo(f"Pending projects: {stage2_result['pending_projects']}")
```

- [ ] **Step 3: 提交**

```bash
git add pkm-server/pkm/cli.py
git commit -m "feat(reflow): 添加 stage2 CLI 命令"
```

---

## Task 6: 单元测试

**Files:**
- Create: `pkm-server/tests/test_knowledge.py`

- [ ] **Step 1: 创建测试文件**

```python
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# 设置测试环境
os.environ["PKM_HOME"] = tempfile.mkdtemp()

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from knowledge import (
    should_exclude_file,
    classify_knowledge,
    check_duplicate,
    write_to_knowledge_base,
    KNOWLEDGE_BASE
)


class TestShouldExcludeFile:
    def test_exclude_code_files(self):
        assert should_exclude_file("test.py") == True
        assert should_exclude_file("test.js") == True
        assert should_exclude_file("main.go") == True

    def test_include_markdown_files(self):
        assert should_exclude_file("readme.md") == False
        assert should_exclude_file("notes.txt") == False


class TestWriteToKnowledgeBase:
    def setup_method(self):
        self.test_knowledge_base = tempfile.mkdtemp()
        # 临时替换 KNOWLEDGE_BASE
        import knowledge
        self.original_base = knowledge.KNOWLEDGE_BASE
        knowledge.KNOWLEDGE_BASE = self.test_knowledge_base

    def teardown_method(self):
        import knowledge
        knowledge.KNOWLEDGE_BASE = self.original_base
        shutil.rmtree(self.test_knowledge_base, ignore_errors=True)

    def test_write_to_notes(self):
        content = "这是一条测试知识"
        result = write_to_knowledge_base(content, "notes", "测试项目")
        assert os.path.exists(result)
        with open(result, "r") as f:
            assert "这是一条测试知识" in f.read()
        assert "notes" in result


class TestClassifyKnowledge:
    @patch("subprocess.run")
    def test_classify_as_principles(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="principles")
        result = classify_knowledge("坚持用户至上原则")
        assert result == "principles"

    @patch("subprocess.run")
    def test_classify_as_notes_default(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="error")
        result = classify_knowledge("一些笔记内容")
        assert result == "notes"
```

- [ ] **Step 2: 运行测试验证**

```bash
cd /media/vdc/github/pkmSkill/pkm-server
pytest tests/test_knowledge.py -v
```

- [ ] **Step 3: 提交**

```bash
git add pkm-server/tests/test_knowledge.py
git commit -m "test(reflow): 添加 Stage2 单元测试"
```

---

## 实施顺序

1. Task 1: 数据库扩展
2. Task 2: Stage2 提炼逻辑
3. Task 3: API 端点
4. Task 4: 定时任务
5. Task 5: CLI 命令
6. Task 6: 单元测试

---
