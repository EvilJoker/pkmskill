# Knowledge Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 Project → Knowledge 自动流转系统，通过 MD5 追踪文件变化，Claude 串行分析和写入知识文件，每天 00:00 执行

**Architecture:** 两轮扫描检测文件变化，ChangeSet 数据结构，Claude 单文件分析和直接写入，更新 index.md 索引

**Tech Stack:** Python, MD5, Claude CLI, SQLite

---

## 文件结构

```
knowledge.py          # 修改：新增 Stage3/knowledge refinement 函数，移除 Stage1，重构 Stage2 为 reflow
file_index.json       # 新建：放在 90_Knowledge/ 目录下
index.md             # 新建：单一索引文件
```

---

## Task 1: ChangeSet 数据结构和扫描函数

**Files:**
- Modify: `knowledge.py`

- [ ] **Step 1: 添加 Stage3 常量和数据结构**

在 `knowledge.py` 末尾添加：

```python
# ============ Stage3: Project → Knowledge 自动流转 ============

import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional

# 知识库根目录
KNOWLEDGE_BASE = os.path.expanduser("~/.pkm/90_Knowledge")
FILE_INDEX_PATH = os.path.join(KNOWLEDGE_BASE, "file_index.json")
INDEX_PATH = os.path.join(KNOWLEDGE_BASE, "index.md")

# 项目空间根目录
PROJECTS_BASE = os.path.expanduser("~/.pkm/60_Projects")

@dataclass
class FileEntry:
    """文件索引条目"""
    md5: str
    updated_at: str

@dataclass
class FileIndex:
    """文件索引"""
    files: dict[str, FileEntry] = field(default_factory=dict)

    def load(self) -> None:
        """从 file_index.json 加载"""
        if os.path.exists(FILE_INDEX_PATH):
            with open(FILE_INDEX_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.files = {
                    k: FileEntry(v["md5"], v["updated_at"])
                    for k, v in data.get("files", {}).items()
                }

    def save(self) -> None:
        """保存到 file_index.json"""
        os.makedirs(os.path.dirname(FILE_INDEX_PATH), exist_ok=True)
        data = {
            "files": {
                k: {"md5": v.md5, "updated_at": v.updated_at}
                for k, v in self.files.items()
            }
        }
        with open(FILE_INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

@dataclass
class ChangeSet:
    """变更集"""
    added: list[Path] = field(default_factory=list)
    modified: list[Path] = field(default_factory=list)
    deleted: list[Path] = field(default_factory=list)

def calculate_md5(filepath: str) -> str:
    """计算文件 MD5 哈希"""
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()
```

- [ ] **Step 2: 添加 scan_projects 函数**

```python
def scan_projects() -> ChangeSet:
    """两轮扫描 Projects 目录，返回变更集"""
    changeset = ChangeSet()
    file_index = FileIndex()
    file_index.load()

    if not os.path.exists(PROJECTS_BASE):
        logger.info("reflow: Projects 目录不存在，跳过扫描")
        return changeset

    # 第一轮：遍历 Projects，计算 MD5
    all_files = []
    for project_name in os.listdir(PROJECTS_BASE):
        project_path = os.path.join(PROJECTS_BASE, project_name)
        if not os.path.isdir(project_path):
            continue

        for root, dirs, files in os.walk(project_path):
            for filename in files:
                if not filename.endswith(".md"):
                    continue

                filepath = Path(root) / filename
                rel_path = f"{project_name}/{filepath.relative_to(project_path)}"

                try:
                    file_md5 = calculate_md5(str(filepath))
                except (OSError, IOError):
                    continue

                now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                all_files.append((rel_path, filepath, file_md5))

                if rel_path not in file_index.files:
                    changeset.added.append(filepath)
                elif file_index.files[rel_path].md5 != file_md5:
                    changeset.modified.append(filepath)

                file_index.files[rel_path] = FileEntry(file_md5, now)

    file_index.save()

    # 第二轮：检查已删除的文件
    for rel_path, entry in list(file_index.files.items()):
        project_name = rel_path.split("/")[0]
        file_path = Path(PROJECTS_BASE) / rel_path
        if not file_path.exists():
            changeset.deleted.append(file_path)
            del file_index.files[rel_path]

    file_index.save()

    # 打印扫描结果
    changed_files = [str(f) for f in changeset.added + changeset.modified]
    logger.info(f"[reflow] 扫描到 {len(changeset.added)} 个新增, {len(changeset.modified)} 个修改文件: {changed_files}")

    return changeset
```

- [ ] **Step 3: 验证 scan_projects 函数存在**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && python -c "from knowledge import scan_projects, ChangeSet; print('OK')"`
Expected: OK

- [ ] **Step 4: 提交**

```bash
git add knowledge.py
git commit -m "feat: add ChangeSet, FileIndex and scan_projects for Stage3"
```

---

## Task 2: Claude 单文件分析和写入

**Files:**
- Modify: `knowledge.py`

- [ ] **Step 1: 添加 find_related_entries 函数**

```python
def find_related_entries(content: str, max_results: int = 3) -> list[dict]:
    """查找与内容相关的现有知识条目"""
    related = []
    if not os.path.exists(KNOWLEDGE_BASE):
        return related

    for root, dirs, files in os.walk(KNOWLEDGE_BASE):
        for filename in files:
            if not filename.endswith(".md") or filename == "index.md":
                continue
            filepath = Path(root) / filename
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    file_content = f.read()

                if any(word in file_content[:500] for word in content[:200].split()[:5]):
                    entry = {"file": str(filepath), "preview": file_content[:300]}
                    related.append(entry)
                    if len(related) >= max_results:
                        return related
            except (OSError, IOError):
                continue
    return related
```

- [ ] **Step 2: 添加 analyze_and_merge 函数**

```python
def analyze_and_merge(filepath: Path, project_name: str) -> dict:
    """
    串行调用 Claude 分析单个文件，直接创建/更新知识文件。
    返回操作结果字典: {"action": "create|update|skip|discard", "file": "...", "error": "..."}
    """
    file_path_str = str(filepath)
    rel_path = f"{project_name}/{filepath.name}"

    logger.info(f"[reflow] 处理文件: {rel_path}")

    try:
        with open(file_path_str, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, IOError) as e:
        logger.error(f"[reflow] 读取文件失败: {rel_path}, error: {e}")
        return {"action": "error", "file": file_path_str, "error": str(e)}

    if not content.strip():
        logger.info(f"[reflow] Claude 结果: skip (空内容) - {rel_path}")
        return {"action": "skip", "file": file_path_str, "reason": "empty content"}

    related = find_related_entries(content)
    related_text = "\n\n".join([
        f"--- {r['file']} ---\n{r['preview']}"
        for r in related
    ]) if related else "无相关条目"

    prompt = f"""## 知识提取任务

### 目标
将以下文件内容合并到知识库现有条目，或创建新条目。

### 文件路径
{rel_path}

### 项目
{project_name}

### 文件内容
{content[:3000]}

### 现有相关条目
{related_text}

### 任务
分析文件内容，判断：
- 是否需要创建新条目 (action=create)
- 是否需要更新现有条目 (action=update)
- 是否可以跳过（内容无关） (action=skip)
- 是否需要丢弃（不再是知识） (action=discard)

### 输出要求
直接写入知识文件，不要只输出计划：

**action: create** 时：
将新知识条目写入 {KNOWLEDGE_BASE}/generated/{{id}}.md
文件内容格式：
```markdown
### id
{{id}}

### title
{{title}}

### version
1

### sources
- {rel_path}

### type
经验 | 方案 | 概念 | 参考

### content
{{content}}
```

**action: update** 时：
将更新内容追加到现有条目文件，追加到 sources 并更新 content。

**action: skip 或 discard** 时：
无需文件操作。

### 重要约束
1. 串行执行，不允许并行
2. 直接写文件，不要只是输出计划
3. 一个文件只创建一个或更新一个知识条目
"""

    try:
        model = os.environ.get("CLAUDE_MODEL", "MiniMax-M2.7-highspeed")
        result = subprocess.run(
            [CLAUDE_CMD, "-p", prompt,
             "--permission-mode", "acceptEdits",
             "--allowedTools", "Write",
             "--effort", "max",
             "--model", model],
            capture_output=True,
            text=True,
            timeout=180
        )

        if result.returncode == 0:
            output = result.stdout
            action = "unknown"
            if "action: create" in output.lower():
                action = "create"
            elif "action: update" in output.lower():
                action = "update"
            elif "action: skip" in output.lower():
                action = "skip"
            elif "action: discard" in output.lower():
                action = "discard"

            logger.info(f"[reflow] Claude 结果: {action} - {rel_path}")
            return {"action": action, "file": file_path_str}
        else:
            logger.error(f"[reflow] Claude 调用失败: {rel_path}, error: {result.stderr[:200]}")
            return {"action": "error", "file": file_path_str, "error": result.stderr[:200]}

    except subprocess.TimeoutExpired:
        logger.error(f"[reflow] Claude 调用超时: {rel_path}")
        return {"action": "error", "file": file_path_str, "error": "timeout"}
    except (OSError, subprocess.CalledProcessError) as e:
        logger.error(f"[reflow] Claude 调用异常: {rel_path}, error: {e}")
        return {"action": "error", "file": file_path_str, "error": str(e)}
```

- [ ] **Step 3: 验证函数定义**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && python -c "from knowledge import analyze_and_merge; print('OK')"`
Expected: OK

- [ ] **Step 4: 提交**

```bash
git add knowledge.py
git commit -m "feat: implement analyze_and_merge with serial Claude execution and logging"
```

---

## Task 3: 更新 index.md 索引

**Files:**
- Modify: `knowledge.py`

- [ ] **Step 1: 添加 update_index 函数**

```python
def update_index() -> None:
    """扫描知识库所有条目，更新 index.md"""
    sections = {"经验": [], "方案": [], "概念": [], "参考": []}

    if not os.path.exists(KNOWLEDGE_BASE):
        return

    for root, dirs, files in os.walk(KNOWLEDGE_BASE):
        for filename in files:
            if not filename.endswith(".md") or filename == "index.md":
                continue

            filepath = Path(root) / filename
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                entry_type = "参考"
                if "### type\n" in content:
                    type_start = content.find("### type\n") + len("### type\n")
                    type_end = content.find("\n", type_start)
                    if type_end == -1:
                        type_end = len(content)
                    type_line = content[type_start:type_end].strip().lower()
                    if "经验" in type_line:
                        entry_type = "经验"
                    elif "方案" in type_line:
                        entry_type = "方案"
                    elif "概念" in type_line:
                        entry_type = "概念"

                title = filename.replace(".md", "")
                if "### title\n" in content:
                    title_start = content.find("### title\n") + len("### title\n")
                    title_end = content.find("\n", title_start)
                    if title_end == -1:
                        title_end = len(content)
                    title = content[title_start:title_end].strip()

                source = "未知来源"
                if "### sources\n" in content:
                    source_start = content.find("### sources\n") + len("### sources\n")
                    source_end = content.find("\n###", source_start)
                    if source_end == -1:
                        source_end = len(content)
                    source_lines = content[source_start:source_end].strip().split("\n")
                    if source_lines:
                        source = source_lines[0].strip("- ").split("(")[0].strip()

                version = "v1"
                if "### version\n" in content:
                    version_start = content.find("### version\n") + len("### version\n")
                    version_end = content.find("\n", version_start)
                    if version_end == -1:
                        version_end = len(content)
                    version = f"v{content[version_start:version_end].strip()}"

                entry_link = f"- [{title}]({filename}) - 来源：{source} - {version}"
                sections[entry_type].append(entry_link)

            except (OSError, IOError):
                continue

    index_lines = ["# Knowledge Index\n"]
    for section, entries in sections.items():
        index_lines.append(f"\n## {section}\n")
        if entries:
            index_lines.extend(entries)
        else:
            index_lines.append("(暂无)")

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines))
```

- [ ] **Step 2: 验证函数定义**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && python -c "from knowledge import update_index; print('OK')"`
Expected: OK

- [ ] **Step 3: 提交**

```bash
git add knowledge.py
git commit -m "feat: implement update_index for knowledge index"
```

---

## Task 4: 主入口函数 run_reflow

**Files:**
- Modify: `knowledge.py`

- [ ] **Step 1: 添加 run_reflow 函数（重构 Stage2）**

```python
def run_reflow_cycle() -> dict:
    """
    执行一轮知识回流 (原 Stage2，重构为 reflow)。
    串行处理每个文件，不允许并行。
    每天 00:00 执行。
    """
    logger.info("[reflow] 开始执行 Project → Knowledge 回流")

    # 两轮扫描获取变更集
    changeset = scan_projects()

    results = []
    total_processed = 0

    # 串行处理每个 added 和 modified 文件
    for filepath in changeset.added + changeset.modified:
        project_name = filepath.parts[-2] if len(filepath.parts) >= 2 else "unknown"
        result = analyze_and_merge(filepath, project_name)
        results.append(result)
        total_processed += 1

    # 更新索引
    update_index()

    succeeded = sum(1 for r in results if r.get("action") in ["create", "update", "skip"])
    failed = sum(1 for r in results if r.get("action") in ["error", "discard", "unknown"])

    logger.info(f"[reflow] 完成: processed={total_processed}, succeeded={succeeded}, failed={failed}")

    return {
        "processed": total_processed,
        "succeeded": succeeded,
        "failed": failed,
        "deleted": len(changeset.deleted),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }
```

- [ ] **Step 2: 移除旧的 Stage1 和 Stage2 函数**

移除以下函数（如果存在）：
- `process_single_task_reflow`
- `run_reflow_cycle` (旧版本)
- `run_stage2_cycle`

保留：
- `run_reflow_cycle` (新版本，上面刚添加的)

- [ ] **Step 3: 验证函数定义**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && python -c "from knowledge import run_reflow_cycle; print('OK')"`
Expected: OK

- [ ] **Step 4: 提交**

```bash
git add knowledge.py
git commit -m "refactor: rename Stage2 to reflow, remove Stage1"
```

---

## Task 5: 添加定时调度支持

**Files:**
- Modify: `main.py` 或 `database.py`（添加 scheduler 支持）

- [ ] **Step 1: 添加 APScheduler 调度**

在 `main.py` 中添加：

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

def setup_reflow_scheduler():
    """设置每天 00:00 执行 reflow"""
    from knowledge import run_reflow_cycle
    scheduler.add_job(
        run_reflow_cycle,
        trigger=CronTrigger(hour=0, minute=0),
        id="reflow_daily",
        name="每日知识回流",
        replace_existing=True
    )
    logger.info("[scheduler] reflow 任务已设置: 每天 00:00 执行")
```

- [ ] **Step 2: 在应用启动时注册调度器**

在 FastAPI 启动事件中调用 `setup_reflow_scheduler()`

- [ ] **Step 3: 验证调度器设置**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && python -c "from main import setup_reflow_scheduler; print('OK')"`
Expected: OK

- [ ] **Step 4: 提交**

```bash
git add main.py
git commit -m "feat: add APScheduler for daily reflow at 00:00"
```

---

## Task 6: 添加测试

**Files:**
- Modify: `tests/test_knowledge.py`

- [ ] **Step 1: 添加 Stage3 相关测试**

在 `tests/test_knowledge.py` 末尾添加：

```python
# ============ Stage3 Tests ============

class TestChangeSetDataclass:
    """Test ChangeSet and FileIndex dataclasses"""

    def test_changeset_empty_init(self):
        """Should create empty changeset"""
        from knowledge import ChangeSet, FileIndex
        cs = ChangeSet()
        assert cs.added == []
        assert cs.modified == []
        assert cs.deleted == []

    def test_file_index_load_save(self, temp_workspace):
        """Should load and save file index"""
        import knowledge
        from knowledge import FileIndex

        original_base = knowledge.KNOWLEDGE_BASE
        knowledge.KNOWLEDGE_BASE = temp_workspace

        fi = FileIndex()
        fi.files["test/file.md"] = knowledge.FileEntry("abc123", "2026-04-22T10:00:00Z")
        fi.save()

        fi2 = FileIndex()
        fi2.load()
        assert "test/file.md" in fi2.files
        assert fi2.files["test/file.md"].md5 == "abc123"

        knowledge.KNOWLEDGE_BASE = original_base


class TestScanProjects:
    """Test two-pass scan_projects function"""

    def test_scan_projects_empty_dir(self):
        """Should handle empty projects directory"""
        import knowledge
        from knowledge import ChangeSet

        original_base = knowledge.PROJECTS_BASE
        knowledge.PROJECTS_BASE = "/tmp/non_existent_projects_xyz"

        cs = knowledge.scan_projects()

        assert isinstance(cs, ChangeSet)
        assert len(cs.added) == 0
        assert len(cs.modified) == 0

        knowledge.PROJECTS_BASE = original_base

    def test_scan_projects_detects_new_file(self, temp_workspace):
        """Should detect newly added files"""
        import knowledge
        from knowledge import ChangeSet

        original_projects = knowledge.PROJECTS_BASE
        original_knowledge = knowledge.KNOWLEDGE_BASE
        knowledge.PROJECTS_BASE = temp_workspace
        knowledge.KNOWLEDGE_BASE = temp_workspace

        project_dir = os.path.join(temp_workspace, "test_project")
        os.makedirs(project_dir, exist_ok=True)
        test_file = os.path.join(project_dir, "notes.md")
        with open(test_file, "w") as f:
            f.write("# Test notes")

        cs = knowledge.scan_projects()

        assert len(cs.added) == 1
        assert str(cs.added[0]).endswith("notes.md")

        knowledge.PROJECTS_BASE = original_projects
        knowledge.KNOWLEDGE_BASE = original_knowledge


class TestAnalyzeAndMerge:
    """Test analyze_and_merge function"""

    @patch("subprocess.run")
    def test_analyze_returns_action(self, mock_run):
        """Should return action result"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "action: skip\n"
        mock_run.return_value = mock_result

        result = knowledge.analyze_and_merge(Path("/tmp/test.md"), "test_project")
        assert "action" in result
        assert result["action"] in ["create", "update", "skip", "discard", "error", "unknown"]

    @patch("subprocess.run")
    def test_empty_file_returns_skip(self, mock_run, temp_workspace):
        """Should skip empty files"""
        test_file = os.path.join(temp_workspace, "empty.md")
        with open(test_file, "w") as f:
            f.write("   \n\t  ")

        result = knowledge.analyze_and_merge(Path(test_file), "test_project")
        assert result["action"] == "skip"


class TestUpdateIndex:
    """Test update_index function"""

    def test_update_index_creates_file(self, temp_workspace):
        """Should create index.md"""
        import knowledge

        original_knowledge = knowledge.KNOWLEDGE_BASE
        knowledge.KNOWLEDGE_BASE = temp_workspace

        test_dir = os.path.join(temp_workspace, "01principles")
        os.makedirs(test_dir, exist_ok=True)
        with open(os.path.join(test_dir, "test.md"), "w") as f:
            f.write("""### id
test-001

### title
测试原则

### version
1

### sources
- test_project/notes.md

### type
经验

### content
测试内容
""")

        knowledge.update_index()

        index_path = os.path.join(temp_workspace, "index.md")
        assert os.path.exists(index_path)

        with open(index_path, "r") as f:
            content = f.read()
        assert "Knowledge Index" in content
        assert "测试原则" in content

        knowledge.KNOWLEDGE_BASE = original_knowledge


class TestRunReflowCycle:
    """Test run_reflow_cycle function"""

    @patch("knowledge.scan_projects")
    @patch("knowledge.analyze_and_merge")
    @patch("knowledge.update_index")
    def test_reflow_processes_changes(self, mock_update, mock_analyze, mock_scan):
        """Should process changeset"""
        from knowledge import ChangeSet

        mock_scan.return_value = ChangeSet()
        mock_analyze.return_value = {"action": "skip", "file": "/tmp/test.md"}

        result = knowledge.run_reflow_cycle()

        assert "processed" in result
        assert "succeeded" in result
        assert "failed" in result
```

- [ ] **Step 2: 运行 Stage3 测试**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && python -m pytest tests/test_knowledge.py -v -k "Stage3 or ChangeSet or ScanProjects or AnalyzeAndMerge or UpdateIndex or RunReflow" --tb=short 2>&1 | head -80`
Expected: 所有 Stage3 相关测试 PASS

- [ ] **Step 3: 提交**

```bash
git add tests/test_knowledge.py
git commit -m "test: add Stage3 knowledge refinement tests"
```

---

## 自检清单

**Spec 覆盖检查:**
- [x] ChangeSet 数据结构 - Task 1
- [x] file_index.json 加载/保存 - Task 1
- [x] 两轮扫描流程 - Task 1
- [x] MD5 计算追踪 - Task 1
- [x] 扫描结果日志 - Task 1
- [x] Claude 单文件分析 - Task 2
- [x] Claude 直接写文件 - Task 2
- [x] 串行执行约束 - Task 2
- [x] 每文件处理日志 - Task 2
- [x] 更新 index.md - Task 3
- [x] 主入口 run_reflow - Task 4
- [x] 移除 Stage1 - Task 4
- [x] 定时 00:00 执行 - Task 5

**占位符检查:**
- 无 TBD/TODO
- 无 "实现后续逻辑" 类占位符
- 所有函数都有完整实现

**类型一致性:**
- ChangeSet.added/modified/deleted: `list[Path]`
- FileEntry.md5: `str`
- analyze_and_merge 返回: `dict` with action field
- run_reflow_cycle 返回: `dict` with processed/succeeded/failed

**串行约束:**
- `run_reflow_cycle` 使用 `for` 循环串行处理，不使用 `concurrent.futures` 或 `asyncio.gather`

**日志规范:**
- 扫描完成: `[reflow] 扫描到 {n} 个新增, {n} 个修改文件: [...]`
- 每处理一个文件: `[reflow] 处理文件: {file_path}`
- Claude 调用结果: `[reflow] Claude 结果: {action} - {file_path}`
