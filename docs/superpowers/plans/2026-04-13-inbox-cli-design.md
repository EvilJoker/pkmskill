# PKM CLI inbox 与 Stage2 Raw 处理实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 `pkm inbox` CLI 命令（支持 `--parse` 链接解析）和 Stage2 对 50_Raw 的提炼处理。

**Architecture:**
- inbox CLI: 在 `cli.py` 新增 `inbox` 命令组，直接调用 Claude CLI 解析链接
- Stage2 Raw 处理: 修改 `knowledge.py` 的 `run_stage2_cycle`，扫描 50_Raw 并提炼到 20_Areas 后删除原文件
- 使用现有 `workspace.py` 的路径模式，新增 `50_Raw` 相关路径常量

**Tech Stack:** Python Click CLI, subprocess 调用 Claude CLI, SQLite

---

## File Structure

```
pkm-server/pkm/
├── cli.py           # 修改: 新增 inbox 命令组
├── workspace.py     # 修改: 新增 50_Raw 路径常量
├── config.py        # 不变

pkm-server/
├── knowledge.py     # 修改: Stage2 增加 50_Raw 处理逻辑
├── main.py         # 不变

pkm-server/tests/
├── test_cli.py     # 修改: 新增 inbox 命令测试
├── test_knowledge.py  # 修改: 新增 Stage2 50_Raw 处理测试
```

---

## Task 1: 新增 inbox CLI 命令

**Files:**
- Modify: `pkm-server/pkm/cli.py:1-20`
- Modify: `pkm-server/pkm/cli.py:83-108` (cli group)
- Create: `pkm-server/pkm/cli.py:新增 inbox 命令组`

- [ ] **Step 1: 添加 inbox 命令组框架**

在 `cli.py` 的 `@cli.group()` 后面添加:

```python
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
    # TODO: 实现逻辑
    click.echo(f"inbox add: {content}, parse={parse}")
```

- [ ] **Step 2: 验证命令注册成功**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && python -m pkm.cli --help`
Expected: 输出包含 `inbox` 命令组

- [ ] **Step 3: 提交**

```bash
git add pkm-server/pkm/cli.py
git commit -m "feat(cli): add inbox command group skeleton"
```

---

## Task 2: 实现 inbox add 命令核心逻辑

**Files:**
- Modify: `pkm-server/pkm/cli.py:新增 inbox 命令实现`

- [ ] **Step 1: 添加必要的 import**

在 `cli.py` 顶部添加:
```python
import re
from datetime import datetime
import subprocess
```

- [ ] **Step 2: 实现 URL 提取和 AI 解析函数**

在 `cli.py` 中添加辅助函数:

```python
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
```

- [ ] **Step 3: 实现 inbox add 命令**

替换 Task 1 的 `add` 函数实现:

```python
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
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(final_content)

    click.echo(f"Captured to inbox: {filename}")
```

- [ ] **Step 4: 测试基本捕获**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && python -m pkm.cli inbox add "测试内容"`
Expected: 在 `~/.pkm/50_Raw/inbox/` 创建文件

- [ ] **Step 5: 提交**

```bash
git add pkm-server/pkm/cli.py
git commit -m "feat(cli): implement inbox add command with URL parsing"
```

---

## Task 3: 完善 inbox 命令错误处理和帮助信息

**Files:**
- Modify: `pkm-server/pkm/cli.py: inbox add 命令`

- [ ] **Step 1: 改进错误处理**

修改 `inbox add` 函数，增加:
1. 内容为空的检查（已完成）
2. 文件写入失败的错误处理
3. URL 解析超时的处理

- [ ] **Step 2: 验证帮助信息**

Run: `python -m pkm.cli inbox --help`
Expected: 显示 `add` 子命令和 `--parse` 选项说明

Run: `python -m pkm.cli inbox add --help`
Expected: 显示使用示例

- [ ] **Step 3: 提交**

```bash
git add pkm-server/pkm/cli.py
git commit -m "feat(cli): improve inbox error handling and help"
```

---

## Task 4: workspace.py 新增 50_Raw 路径常量

**Files:**
- Modify: `pkm-server/pkm/workspace.py`

- [ ] **Step 1: 添加 50_Raw 相关路径常量**

在 `workspace.py` 顶部添加:

```python
# 50_Raw 路径
RAW_BASE = os.path.join(WORKSPACE_BASE, "50_Raw")
INBOX_BASE = os.path.join(RAW_BASE, "inbox")
```

添加获取函数:

```python
def get_inbox_base():
    """获取 inbox 目录"""
    os.makedirs(INBOX_BASE, exist_ok=True)
    return INBOX_BASE


def get_raw_base():
    """获取 50_Raw 目录"""
    os.makedirs(RAW_BASE, exist_ok=True)
    return RAW_BASE
```

- [ ] **Step 2: 验证路径**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && python -c "from pkm.workspace import get_inbox_base, RAW_BASE; print(RAW_BASE, get_inbox_base())"`
Expected: 输出 `~/.pkm/50_Raw` 相关路径

- [ ] **Step 3: 提交**

```bash
git add pkm-server/pkm/workspace.py
git commit -m "feat(workspace): add 50_Raw path constants"
```

---

## Task 5: Stage2 增加 50_Raw 处理逻辑

**Files:**
- Modify: `pkm-server/knowledge.py:run_stage2_cycle`

- [ ] **Step 1: 添加 50_Raw 扫描和处理函数**

在 `knowledge.py` 中添加:

```python
# 50_Raw 路径
RAW_BASE = os.path.expanduser("~/.pkm/50_Raw")


def process_raw_inbox():
    """扫描并处理 50_Raw 目录下的所有 .md 文件"""
    if not os.path.exists(RAW_BASE):
        return {"processed": 0, "succeeded": 0, "failed": 0, "errors": []}

    processed = 0
    succeeded = 0
    failed = 0
    errors = []

    # 扫描所有子目录中的 .md 文件
    for root, dirs, files in os.walk(RAW_BASE):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            filepath = os.path.join(root, filename)
            try:
                # 读取内容
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                if not content.strip():
                    # 空文件直接删除
                    os.remove(filepath)
                    continue

                # 分类
                classification = classify_knowledge(content)

                # 去重检查
                is_dup, dup_type = check_duplicate(content, classification)

                if is_dup and dup_type == "duplicate":
                    # 完全重复，删除原文件
                    os.remove(filepath)
                    processed += 1
                    succeeded += 1
                    continue

                # 写入知识库
                if is_dup and dup_type == "similar":
                    # 类似内容合并到已有文件（追加到末尾）
                    # 先找到相似文件
                    target_path = find_similar_file(content, classification)
                    if target_path:
                        with open(target_path, "a", encoding="utf-8") as f:
                            f.write("\n\n---\n\n")
                            f.write(content)
                        os.remove(filepath)
                        processed += 1
                        succeeded += 1
                        continue

                # 新内容，写入新文件
                write_to_knowledge_base(content, classification, "50_Raw")
                os.remove(filepath)
                processed += 1
                succeeded += 1

            except Exception as e:
                errors.append({"file": filepath, "error": str(e)})
                failed += 1

    return {
        "processed": processed,
        "succeeded": succeeded,
        "failed": failed,
        "errors": errors
    }


def find_similar_file(content, classification):
    """找到相似内容的文件路径"""
    dir_map = {
        "principles": PRINCIPLES_DIR,
        "playbooks": PLAYBOOKS_DIR,
        "templates": TEMPLATES_DIR,
        "cases": CASES_DIR,
        "notes": NOTES_DIR,
    }
    target_dir = dir_map.get(classification, NOTES_DIR)
    if not os.path.exists(target_dir):
        return None

    for filename in os.listdir(target_dir):
        filepath = os.path.join(target_dir, filename)
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
                ["claude", "-p", compare_prompt,
                 "--permission-mode", "acceptEdits",
                 "--model", model],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                resp = result.stdout.strip().lower()
                if resp == "similar":
                    return filepath
        except:
            pass
    return None
```

- [ ] **Step 2: 修改 run_stage2_cycle 整合 50_Raw 处理**

修改 `run_stage2_cycle` 函数，在开头添加:

```python
def run_stage2_cycle(batch_size: int = 5) -> Dict:
    """执行一轮 Stage2 提炼"""
    logger.info("Stage2 triggered: Starting project reflow cycle")

    # 处理 50_Raw
    raw_result = process_raw_inbox()
    logger.info(f"50_Raw processed: {raw_result}")

    from database import get_projects_needing_reflow, mark_project_refined, get_project

    projects = get_projects_needing_reflow(limit=batch_size)
    # ... 后续逻辑保持不变 ...
```

- [ ] **Step 3: 更新返回值包含 50_Raw 处理结果**

修改 `run_stage2_cycle` 的返回值:

```python
return {
    "processed": processed + raw_result["processed"],
    "succeeded": succeeded + raw_result["succeeded"],
    "failed": failed + raw_result["failed"],
    "raw_processed": raw_result["processed"],
    "raw_succeeded": raw_result["succeeded"],
    "raw_failed": raw_result["failed"],
    "errors": errors + raw_result.get("errors", []),
    "timestamp": datetime.now().isoformat()
}
```

- [ ] **Step 4: 测试 50_Raw 处理**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && python -c "
from knowledge import process_raw_inbox
result = process_raw_inbox()
print(result)
"`
Expected: 返回处理统计

- [ ] **Step 5: 提交**

```bash
git add pkm-server/knowledge.py
git commit -m "feat(stage2): add 50_Raw processing to Stage2 cycle"
```

---

## Task 6: 完善 Stage2 50_Raw 处理错误处理

**Files:**
- Modify: `pkm-server/knowledge.py:process_raw_inbox`

- [ ] **Step 1: 添加日志记录**

在 `process_raw_inbox` 的关键步骤添加日志:

```python
logger.info(f"Processing raw file: {filepath}")
logger.info(f"Classified as: {classification}")
logger.info(f"Duplicate check: is_dup={is_dup}, dup_type={dup_type}")
logger.info(f"Deleting processed file: {filepath}")
```

- [ ] **Step 2: 处理空目录**

在 `process_raw_inbox` 结束后，清理空目录:

```python
# 清理空目录
for root, dirs, files in os.walk(RAW_BASE, topdown=False):
    for d in dirs:
        dirpath = os.path.join(root, d)
        if not os.listdir(dirpath):  # 空目录
            os.rmdir(dirpath)
            logger.info(f"Removed empty directory: {dirpath}")
```

- [ ] **Step 3: 测试空目录清理**

Run: `mkdir -p ~/.pkm/50_Raw/test_empty && python -c "from knowledge import process_raw_inbox; process_raw_inbox()"`
Expected: 空目录被删除

- [ ] **Step 4: 提交**

```bash
git add pkm-server/knowledge.py
git commit -m "fix(stage2): add logging and empty dir cleanup for 50_Raw processing"
```

---

## Task 7: inbox CLI 命令测试

**Files:**
- Modify: `pkm-server/tests/test_cli.py`

- [ ] **Step 1: 添加 inbox 测试类**

在 `test_cli.py` 末尾添加:

```python
class TestCLIInbox:
    """Test CLI inbox commands"""

    def test_inbox_help(self):
        """Inbox help should show available commands"""
        r = run_cli("inbox --help")
        assert r.returncode == 0
        assert "add" in r.stdout

    def test_inbox_add_help(self):
        """Inbox add help should show examples"""
        r = run_cli("inbox add --help")
        assert r.returncode == 0
        assert "Examples:" in r.stdout
        assert "--parse" in r.stdout

    def test_inbox_add_basic(self, wait_for_server):
        """Should add content to inbox"""
        r = run_cli('inbox add "测试 inbox 内容"')
        assert r.returncode == 0
        assert "Captured to inbox" in r.stdout
        assert "_inbox.md" in r.stdout

    def test_inbox_add_with_parse_flag(self, wait_for_server):
        """Should add content with parse flag (without actual URL)"""
        r = run_cli('inbox add --parse "测试带解析标记"')
        assert r.returncode == 0
        # 即使没有有效 URL 也应该能保存
        assert "Captured to inbox" in r.stdout or "Warning" in r.stdout

    def test_inbox_add_empty_content(self):
        """Should handle empty content"""
        r = run_cli('inbox add ""')
        # 应该返回错误或提示内容不能为空
        assert r.returncode != 0 or "Error" in r.stdout or "空" in r.stdout
```

- [ ] **Step 2: 运行测试验证**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && pytest tests/test_cli.py::TestCLIInbox -v`

- [ ] **Step 3: 提交**

```bash
git add pkm-server/tests/test_cli.py
git commit -m "test(cli): add inbox command tests"
```

---

## Task 8: Stage2 50_Raw 处理测试

**Files:**
- Modify: `pkm-server/tests/test_knowledge.py`

- [ ] **Step 1: 添加 50_Raw 处理测试类**

在 `test_knowledge.py` 末尾添加:

```python
class TestProcessRawInbox:
    """Test 50_Raw inbox processing"""

    def setup_method(self):
        """Create temp 50_Raw directory"""
        self.temp_raw = tempfile.mkdtemp()
        import knowledge
        self.original_raw_base = knowledge.RAW_BASE
        knowledge.RAW_BASE = self.temp_raw

        # Create inbox subdirectory
        self.inbox_dir = os.path.join(self.temp_raw, "inbox")
        os.makedirs(self.inbox_dir, exist_ok=True)

    def teardown_method(self):
        """Restore original 50_Raw base"""
        import knowledge
        knowledge.RAW_BASE = self.original_raw_base
        shutil.rmtree(self.temp_raw, ignore_errors=True)

    def test_empty_raw_returns_empty_result(self):
        """Should return empty result when no files"""
        result = knowledge.process_raw_inbox()
        assert result["processed"] == 0
        assert result["succeeded"] == 0
        assert result["failed"] == 0

    def test_process_single_file(self):
        """Should process single markdown file"""
        # Create test file in inbox
        test_file = os.path.join(self.inbox_dir, "test_inbox.md")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("这是一条测试笔记")

        result = knowledge.process_raw_inbox()

        assert result["processed"] == 1
        assert result["succeeded"] == 1
        # File should be deleted after processing
        assert not os.path.exists(test_file)

    @patch("knowledge.classify_knowledge")
    @patch("knowledge.check_duplicate")
    def test_duplicate_file_deleted(self, mock_check, mock_classify):
        """Should delete file when duplicate is found"""
        mock_classify.return_value = "notes"
        mock_check.return_value = (True, "duplicate")

        test_file = os.path.join(self.inbox_dir, "test_dup.md")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("重复内容")

        result = knowledge.process_raw_inbox()

        assert result["processed"] == 1
        assert result["succeeded"] == 1
        assert not os.path.exists(test_file)

    def test_non_md_file_ignored(self):
        """Should ignore non-markdown files"""
        test_file = os.path.join(self.inbox_dir, "test.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Some text")

        result = knowledge.process_raw_inbox()

        # .txt files should be ignored
        assert result["processed"] == 0
        assert os.path.exists(test_file)  # File should still exist


class TestRunStage2CycleWithRaw:
    """Test Stage2 cycle with 50_Raw processing"""

    def setup_method(self):
        """Create temp 50_Raw directory"""
        self.temp_raw = tempfile.mkdtemp()
        import knowledge
        self.original_raw_base = knowledge.RAW_BASE
        knowledge.RAW_BASE = self.temp_raw

        self.inbox_dir = os.path.join(self.temp_raw, "inbox")
        os.makedirs(self.inbox_dir, exist_ok=True)

    def teardown_method(self):
        """Restore original 50_Raw base"""
        import knowledge
        knowledge.RAW_BASE = self.original_raw_base
        shutil.rmtree(self.temp_raw, ignore_errors=True)

    @patch("knowledge.classify_knowledge")
    @patch("knowledge.check_duplicate")
    def test_stage2_processes_raw_first(self, mock_check, mock_classify, override_db_path):
        """Should process 50_Raw before projects"""
        mock_classify.return_value = "notes"
        mock_check.return_value = (False, "new")

        # Create inbox file
        test_file = os.path.join(self.inbox_dir, "test.md")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("测试内容")

        result = knowledge.run_stage2_cycle(batch_size=5)

        assert "raw_processed" in result
        assert result["raw_processed"] == 1
        assert result["raw_succeeded"] == 1
```

- [ ] **Step 2: 运行测试验证**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && pytest tests/test_knowledge.py::TestProcessRawInbox -v`
Run: `cd /media/vdc/github/pkmSkill/pkm-server && pytest tests/test_knowledge.py::TestRunStage2CycleWithRaw -v`

- [ ] **Step 3: 提交**

```bash
git add pkm-server/tests/test_knowledge.py
git commit -m "test(stage2): add 50_Raw processing tests"
```

---

## Task 9: 完整流程测试和最终验证

- [ ] **Step 1: 完整测试所有新功能**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && pytest tests/test_cli.py::TestCLIInbox tests/test_knowledge.py::TestProcessRawInbox tests/test_knowledge.py::TestRunStage2CycleWithRaw -v`

- [ ] **Step 2: 运行全部测试确保无回归**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && pytest tests/ -v --tb=short`

- [ ] **Step 3: 检查覆盖率**

Run: `cd /media/vdc/github/pkmSkill/pkm-server && pytest tests/ --cov=pkm --cov=knowledge --cov-report=term-missing`
Expected: 覆盖率不下降

- [ ] **Step 4: 提交最终变更**

```bash
git add -A
git commit -m "feat: complete inbox CLI and Stage2 50_Raw processing implementation"
```

---

## Self-Review Checklist

- [ ] 所有设计需求都有对应的任务实现
- [ ] 无 placeholder (TBD, TODO)
- [ ] 函数签名和类型一致
- [ ] 测试覆盖新功能
- [ ] 提交信息规范

---

## 执行方式选择

**1. Subagent-Driven (推荐)** - 每任务派遣一个 subagent，任务间 review，快速迭代

**2. Inline Execution** - 在当前 session 执行任务，使用 executing-plans skill

选择哪种方式？
