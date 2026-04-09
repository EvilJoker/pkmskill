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
