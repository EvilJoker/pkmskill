"""
PKM 常量定义
"""
import os

# PKM 根目录
PKM_BASE = os.path.expanduser("~/.pkm")

# 目录结构常量
DIR_TASKS = "10_Tasks"
DIR_PROJECTS = "20_Projects"
DIR_RAW = "30_Raw"
DIR_INBOX = "30_Raw/inbox"
DIR_KNOWLEDGE = "40_Knowledge"
DIR_ARCHIVES = "50_Archives"

# 完整路径
WORKSPACE_BASE = PKM_BASE
TASK_WORKSPACE_BASE = os.path.join(PKM_BASE, DIR_TASKS)
PROJECT_WORKSPACE_BASE = os.path.join(PKM_BASE, DIR_PROJECTS)
RAW_BASE = os.path.join(PKM_BASE, DIR_RAW)
INBOX_BASE = os.path.join(PKM_BASE, DIR_INBOX)
ARCHIVE_BASE = os.path.join(PKM_BASE, DIR_ARCHIVES)

# Default 项目名称
DEFAULT_PROJECT_PREFIX = "P_default"
DEFAULT_PROJECT_NAME = "default"
