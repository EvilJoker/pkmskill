# PKM Server 设计文档

## 概述

将 PKM 从纯 Skill 改造为 **CLI + 守护进程服务** 架构，核心聚焦**任务/项目持久化存储**。

## 架构

```
pkm-server/           # 根目录
├── main.py           # FastAPI 单文件（路由 + 业务逻辑）
├── models.py         # Pydantic 数据模型
├── database.py       # SQLite 连接 + CRUD
├── Dockerfile        # 容器化
├── requirements.txt
└── pkm/              # CLI 包
    ├── __init__.py
    └── cli.py        # Click CLI（调用 API）
```

**通信**：CLI 通过 HTTP REST API 与守护进程通信。
**存储**：`~/.pkm/pkm.db`（SQLite）
**日志**：`~/.pkm/logs/pkm-server.log`

## 数据模型

### Task

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | UUID |
| title | string | 任务描述 |
| status | enum | pending / in_progress / completed |
| priority | enum | high / medium / low |
| quadrant | int | 1-4 象限 |
| project_id | string? | 所属项目 ID |
| progress | string? | 进展描述 |
| due_date | date? | 截止日期 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |
| completed_at | datetime? | 完成时间 |

### Project

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | UUID |
| name | string | 项目名称 |
| description | string? | 描述 |
| status | enum | active / completed / archived |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |
| completed_at | datetime? | 完成时间 |

## API 设计

### Tasks

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/tasks | 创建任务 |
| GET | /api/tasks | 列表（支持 filter） |
| GET | /api/tasks/{id} | 获取单个 |
| PATCH | /api/tasks/{id} | 更新 |
| DELETE | /api/tasks/{id} | 删除 |
| POST | /api/tasks/{id}/done | 完成任务 |

### Projects

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/projects | 创建项目 |
| GET | /api/projects | 列表 |
| GET | /api/projects/{id} | 获取单个 |
| PATCH | /api/projects/{id} | 更新 |
| DELETE | /api/projects/{id} | 删除 |
| POST | /api/projects/{id}/archive | 归档项目 |

### System

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /health | 健康检查 |

## CLI 命令

```bash
pkm task add "任务描述" [--priority high] [--due 2026-04-10] [--project 项目名]
pkm task ls [--status pending] [--project 项目名] [--quadrant 1]
pkm task get <id>
pkm task update <id> [--title "新描述"] [--priority low] [--progress "完成了xxx"]
pkm task done <id>
pkm task delete <id>

pkm project add "项目名" [--description "描述"]
pkm project ls [--status active]
pkm project get <id>
pkm project update <id> [--name "新名称"]
pkm project archive <id>

pkm server start   # 启动守护进程
pkm server stop    # 停止守护进程
pkm server status  # 查看服务状态
```

## 服务管理

- 进程文件：`~/.pkm/pkm-server.pid`
- 默认端口：`7890`
- 启动：`pkm server start`（后台运行）
- 停止：`pkm server stop`

## Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

容器内数据挂载到 `~/.pkm`，确保数据持久化。

## MVP 范围

1. CLI 和服务的基本增删改查
2. SQLite 持久化
3. Docker 容器化
4. 服务守护进程模式

**暂不做**：organize/distill 等知识整理功能（保持 PKM Skill 侧实现）。
