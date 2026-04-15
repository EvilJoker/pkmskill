import os
import subprocess
import re
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime

from database import (
    list_tasks, get_task, update_task, get_project,
    create_reflow, get_reflow_by_task, update_reflow_status, list_pending_reflows
)
from pkm.workspace import get_default_project_workspace, archive_task_workspace, get_project_workspace_base

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Claude CLI 路径
CLAUDE_CMD = "claude"

# 50_Raw 路径
RAW_BASE = os.path.expanduser("~/.pkm/50_Raw")

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


def extract_knowledge_with_claude(content: str, max_retries: int = 3) -> str:
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

    for attempt in range(max_retries):
        try:
            # 从环境变量获取 model 名称
            model = os.environ.get("CLAUDE_MODEL", "MiniMax-M2.7-highspeed")
            result = subprocess.run(
                [CLAUDE_CMD, "-p", prompt,
                 "--permission-mode", "acceptEdits",
                 "--allowedTools", "Read",
                 "--effort", "max",
                 "--model", model],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                return result.stdout
            elif attempt < max_retries - 1:
                continue  # 重试
            else:
                return f"[Claude 调用失败: {result.stderr}]"
        except subprocess.TimeoutExpired:
            if attempt < max_retries - 1:
                continue  # 重试
            return "[Claude 调用超时]"
        except Exception as e:
            return f"[Claude 调用异常: {str(e)}"
    return "[Claude 调用失败]"


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
        reflow_project_id = project_id if project_id else "default"
        reflow = create_reflow(task_id, reflow_project_id)

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
    logger.info("Stage1 triggered: Starting task reflow cycle")

    # 获取所有 approved 状态的任务
    tasks = list_tasks(status="approved")
    logger.info(f"Found {len(tasks)} approved tasks to process")

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
        logger.info(f"Processing task: {task_id} - {task.get('title', 'unknown')}")
        success, message = process_single_task_reflow(task_id)
        if success:
            succeeded += 1
            logger.info(f"Task reflow succeeded: {task_id}")
        else:
            failed += 1
            errors.append({"task_id": task_id, "message": message})
            logger.warning(f"Task reflow failed: {task_id} - {message}")

    logger.info(f"Stage1 completed: processed={processed}, succeeded={succeeded}, failed={failed}")

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


# ============ Stage2: 项目 → 公共知识区 ============

# 公共知识区路径
KNOWLEDGE_BASE = os.path.expanduser("~/.pkm/20_Areas/knowledge")
PRINCIPLES_DIR = os.path.join(KNOWLEDGE_BASE, "01principles")
PLAYBOOKS_DIR = os.path.join(KNOWLEDGE_BASE, "02playbooks")
TEMPLATES_DIR = os.path.join(KNOWLEDGE_BASE, "02templates")
CASES_DIR = os.path.join(KNOWLEDGE_BASE, "02cases")
NOTES_DIR = os.path.join(KNOWLEDGE_BASE, "03notes")


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
                    logger.info(f"Deleted empty file: {filepath}")
                    continue

                # 分类
                classification = classify_knowledge(content)
                logger.info(f"Processing raw file: {filepath}, classified as: {classification}")

                # 去重检查
                is_dup, dup_type = check_duplicate(content, classification)
                logger.info(f"Duplicate check: is_dup={is_dup}, dup_type={dup_type}")

                if is_dup and dup_type == "duplicate":
                    # 完全重复，删除原文件
                    os.remove(filepath)
                    logger.info(f"Deleted duplicate file: {filepath}")
                    processed += 1
                    succeeded += 1
                    continue

                # 写入知识库
                if is_dup and dup_type == "similar":
                    # 类似内容合并到已有文件（追加到末尾）
                    target_path = find_similar_file(content, classification)
                    if target_path:
                        with open(target_path, "a", encoding="utf-8") as f:
                            f.write("\n\n---\n\n")
                            f.write(content)
                        os.remove(filepath)
                        logger.info(f"Merged similar file into: {target_path}, deleted: {filepath}")
                        processed += 1
                        succeeded += 1
                        continue

                # 新内容，写入新文件
                write_to_knowledge_base(content, classification, "50_Raw")
                os.remove(filepath)
                logger.info(f"Deleting processed file: {filepath}")
                processed += 1
                succeeded += 1

            except Exception as e:
                errors.append({"file": filepath, "error": str(e)})
                failed += 1

    # 清理空目录
    for root, dirs, files in os.walk(RAW_BASE, topdown=False):
        for d in dirs:
            dirpath = os.path.join(root, d)
            if os.path.exists(dirpath) and not os.listdir(dirpath):  # 空目录
                os.rmdir(dirpath)
                logger.info(f"Removed empty directory: {dirpath}")

    return {
        "processed": processed,
        "succeeded": succeeded,
        "failed": failed,
        "errors": errors
    }


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


def check_duplicate(content: str, target_dir: str) -> Tuple[bool, str]:
    """检查内容是否重复，返回 (is_duplicate, similarity_type)"""
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


def run_stage2_cycle(batch_size: int = 5) -> Dict:
    """执行一轮 Stage2 提炼"""
    logger.info("Stage2 triggered: Starting project reflow cycle")

    # 处理 50_Raw
    raw_result = process_raw_inbox()
    logger.info(f"50_Raw processed: {raw_result}")

    from database import get_projects_needing_reflow, mark_project_refined, get_project

    projects = get_projects_needing_reflow(limit=batch_size)
    logger.info(f"Found {len(projects)} projects needing reflow")

    processed = 0
    succeeded = 0
    failed = 0
    errors = []

    for proj in projects:
        project_id = proj["id"]
        project_name = proj.get("name", "unknown")
        workspace_path = proj.get("workspace_path")

        logger.info(f"Refining project: {project_name} (id={project_id})")

        if not workspace_path or not os.path.exists(workspace_path):
            logger.warning(f"Project workspace not found: {project_id}")
            errors.append({"project_id": project_id, "message": "项目工作区不存在"})
            failed += 1
            continue

        try:
            # 读取 project.md 中的经验/方案索引
            project_md_path = os.path.join(workspace_path, "project.md")
            if not os.path.exists(project_md_path):
                logger.warning(f"project.md not found: {project_id}")
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
            items_written = 0
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
                items_written += 1

            # 标记项目已提炼
            mark_project_refined(project_id)
            processed += 1
            succeeded += 1
            logger.info(f"Project refined: {project_name}, wrote {items_written} knowledge items")

        except Exception as e:
            logger.error(f"Project reflow error: {project_id} - {str(e)}")
            errors.append({"project_id": project_id, "message": str(e)})
            failed += 1

    logger.info(f"Stage2 completed: processed={processed}, succeeded={succeeded}, failed={failed}")

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


def get_stage2_status() -> Dict:
    """获取 Stage2 状态"""
    from database import get_projects_needing_reflow

    pending_projects = get_projects_needing_reflow(limit=100)

    return {
        "pending_projects": len(pending_projects),
        "config": REFLOW_CONFIG,
        "claude_available": check_claude_environment()[0]
    }