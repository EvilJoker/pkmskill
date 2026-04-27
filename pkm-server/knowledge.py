import os
import subprocess
import logging
import hashlib
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field


# 使用项目统一的日志配置（logging_config.py 已配置）
logger = logging.getLogger(__name__)

# Claude CLI 路径
CLAUDE_CMD = "claude"



def check_claude_environment() -> Tuple[bool, str]:
    """检查 Claude CLI 环境是否可用"""
    try:
        result = subprocess.run(
            [CLAUDE_CMD, "-p", "hello", "--permission-mode", "acceptEdits"],
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
    except (OSError, subprocess.CalledProcessError) as e:
        return False, f"Claude CLI 调用失败: {e}"


def get_reflow_status() -> dict:
    """获取回流状态"""
    return {
        "claude_available": check_claude_environment()[0]
    }


# ============ reflow: Project → Knowledge 自动流转 ============

# 知识库根目录
KNOWLEDGE_BASE = os.path.expanduser("~/.pkm/40_Knowledge")
WIKI_DIR = os.path.join(KNOWLEDGE_BASE, "_wiki")
SCHEMA_DIR = os.path.join(KNOWLEDGE_BASE, "_schema")
FILE_INDEX_PATH = os.path.join(KNOWLEDGE_BASE, "file_index.json")
INDEX_PATH = os.path.join(WIKI_DIR, "index.md")
INDEX_YAML_PATH = os.path.join(WIKI_DIR, "index.yaml")

# 项目空间根目录
PROJECTS_BASE = os.path.expanduser("~/.pkm/20_Projects")

# Raw 层根目录
RAW_BASE = os.path.expanduser("~/.pkm/30_Raw")

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


def find_related_entries(content: str, max_results: int = 3) -> list[dict]:
    """查找与内容相关的现有知识条目"""
    related = []
    if not os.path.exists(WIKI_DIR):
        return related

    for root, dirs, files in os.walk(WIKI_DIR):
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
将新知识条目写入 {WIKI_DIR}/{{topic}}/{{title}}.md
文件内容格式：
```markdown
---
title: {{title}}
type: concept
sources: [{rel_path}]
related: []
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
---

# {{title}}

## 核心概念
{{content摘要}}

## 相关
- [[相关条目]]
```

**action: update** 时：
将更新内容追加到现有条目文件，追加到 sources 并更新 updated 日期。

**action: skip 或 discard** 时：
无需文件操作。

### 重要约束
1. 串行执行，不允许并行
2. 直接写文件，不要只是输出计划
3. 一个文件只创建一个或更新一个知识条目
4. 使用中文标题，如 AI基础、职业发展等
5. topic 使用中文目录名，如 AI、编程、职业发展
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


def update_index() -> None:
    """扫描知识库所有条目，更新 index.md 和 index.yaml"""
    import yaml

    # 按 topic 组织条目
    topics: Dict[str, list] = {}

    if not os.path.exists(WIKI_DIR):
        return

    for root, dirs, files in os.walk(WIKI_DIR):
        for filename in files:
            if not filename.endswith(".md") or filename == "index.md":
                continue

            filepath = Path(root) / filename
            rel_dir = filepath.relative_to(WIKI_DIR).parent

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # 解析 frontmatter
                title = filename.replace(".md", "")
                entry_type = "concept"
                sources = []
                related = []

                if rel_dir != Path("."):
                    topic = str(rel_dir)
                else:
                    topic = "未分类"

                if "---" in content:
                    frontmatter_end = content.find("---", 2)
                    if frontmatter_end != -1:
                        frontmatter_text = content[3:frontmatter_end].strip()
                        try:
                            fm = yaml.safe_load(frontmatter_text)
                            if fm:
                                title = fm.get("title", title)
                                entry_type = fm.get("type", "concept")
                                sources = fm.get("sources", [])
                                related = fm.get("related", [])
                        except yaml.YAMLError:
                            pass

                if topic not in topics:
                    topics[topic] = []

                topics[topic].append({
                    "title": title,
                    "type": entry_type,
                    "sources": sources,
                    "related": related,
                    "path": str(filepath.relative_to(WIKI_DIR))
                })

            except (OSError, IOError):
                continue

    # 生成 index.md
    index_lines = ["# Knowledge Index\n", "\n## 按主题浏览\n"]

    for topic in sorted(topics.keys()):
        index_lines.append(f"\n### {topic}\n")
        for entry in sorted(topics[topic], key=lambda x: x["title"]):
            index_lines.append(f"- [[{entry['title']}]]")

    index_lines.append("\n## 最近更新\n")
    index_lines.append(f"- {datetime.now().strftime('%Y-%m-%d')}: 更新索引\n")

    os.makedirs(WIKI_DIR, exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines))

    # 生成 index.yaml
    concepts = {}
    for topic in topics:
        for entry in topics[topic]:
            concepts[entry["title"]] = {
                "path": entry["path"],
                "type": entry["type"],
                "sources": entry["sources"],
                "related": entry["related"]
            }

    yaml_data = {"concepts": concepts}
    with open(INDEX_YAML_PATH, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def run_reflow_cycle() -> dict:
    """
    执行一轮知识回流。
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