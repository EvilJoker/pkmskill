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