# 知识回流机制设计方案

## 1. 概述

**目标**：任务工作区完成后的知识和经验自动回流到项目工作区，形成闭环。

**核心原则**：
- 内容级回流：AI 提取经验/方案，生成结构化文档
- 项目记忆文件作为索引
- 找不到关联项目的任务回流到 default 项目
- 人工评审机制：回流清单需评审后才能执行回流

## 2. 整体流程

```
Task Done → 生成 completed.md（回流清单）
    ↓
人工评审 → 状态: done → approved
    ↓
定时任务扫描 approved 任务
    ↓
执行回流：
  1. 读取任务工作区内容
  2. claude -p "提取经验方案"（中文 prompt）
  3. 追加到项目记忆文件
  4. 任务状态: approved → archived
  5. 任务工作区 → 归档目录
```

**回流时机**：
- Server 启动时执行一次
- 后台定时任务（默认每 3600 秒）

## 3. 目录结构

```
~/.pkm/
├── 60_Projects/              # 独立项目工作区
│   ├── P_default/           # default 项目（初始化时创建）
│   │   └── project.md       # 项目记忆文件（索引）
│   └── P_项目名/
│       └── project.md
│
├── 10_Tasks/                # 任务工作区
│   ├── TASK_xxx/
│   │   ├── task.md
│   │   └── completed.md    # 回流清单（Task Done 时生成）
│   └── ...
│
└── 80_Archives/             # 归档目录（回流后任务移动至此）
    └── TASK_xxx/
```

## 4. 任务状态流转

```
pending → done → approved → archived
         ↑                  ↑
         └── 人工评审后改状态
```

- **pending**：新创建
- **done**：任务完成，已生成 completed.md（待评审）
- **approved**：评审通过，可以回流
- **archived**：已归档（回流完成）

## 5. 数据库 Schema

### 5.1 tasks 表（新增字段）

```sql
ALTER TABLE tasks ADD COLUMN status TEXT DEFAULT 'pending';
-- pending, done, approved, archived
```

### 5.2 knowledge_reflow 表

```sql
CREATE TABLE knowledge_reflow (
    id INTEGER PRIMARY KEY,
    task_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, processing, completed, failed
    reflowed_at TIMESTAMP,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reflow_status ON knowledge_reflow(status);
```

**判断任务是否已回流**：查询 `knowledge_reflow` 表，`status='completed'` 表示已回流。

## 6. PKM CLI 命令

### 6.1 手动触发回流命令

```
pkm reflow
```

**说明**：手动触发知识回流，扫描所有 approved 状态的任务并执行回流。

**路由**：PKM CLI 解析 `reflow` 子命令，调用 Server API `POST /api/knowledge/reflow`

---

## 7. API 设计

### 7.1 手动触发回流

```
POST /api/knowledge/reflow
```

**响应**：
```json
{
  "triggered": true,
  "processed": 3,
  "message": "处理了 3 个任务"
}
```

### 7.2 查询回流状态

```
GET /api/knowledge/status
```

**响应**：
```json
{
  "last_run": "2026-04-09T10:00:00",
  "pending": 5,
  "approved": 2,
  "config": {
    "interval": 3600,
    "content_types": ["经验", "方案"],
    "exclude_patterns": ["*.py", "*.js", "task.md", "completed.md"]
  }
}
```

### 7.3 配置回流参数

```
PATCH /api/knowledge/config
```

**请求体**：
```json
{
  "interval": 3600,
  "content_types": ["经验", "方案"],
  "exclude_patterns": ["*.py", "*.js", "task.md", "completed.md"]
}
```

### 7.4 评审任务（批准回流）

```
POST /api/knowledge/approve/{task_id}
```

**说明**：将任务状态从 `done` 改为 `approved`，允许定时任务执行回流。

## 8. Claude CLI 集成

### 8.1 环境检查

**初始化时检查**：
- 执行 `claude -p "hello"` 测试环境
- 检查返回是否正常
- 如果失败，记录错误日志

### 8.2 调用方式

**回流时调用 Claude CLI**：
```bash
claude -p "请从以下内容中提取经验和方案，用中文回答：

{content}"
```

**限制工具权限**：
```bash
claude -p "..." --allowedTools "Read,Edit,Write,Bash"
```

### 8.3 输出解析

- Claude CLI 输出为自然语言
- Server 解析输出，提取关键信息
- 追加到项目记忆文件

## 9. 回流配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `回流触发间隔` | 3600 秒 | 后台定时任务间隔 |
| `回流内容类型` | ["经验", "方案"] | 只回流这两类 |
| `排除模式` | ["*.py", "*.js", "task.md", "completed.md"] | 跳过的文件 |

## 10. 回流内容格式

**追加到项目记忆文件（project.md）的索引条目**：

```markdown
## 经验/方案索引

### 2026-04-09 任务：XXX
- **类型**：经验
- **摘要**：...
- **来源文件**：文件A.md | 文件B.md
```

**回流内容组织**：具体内容由 AI 自行判断存放在项目工作区内。

## 11. 错误处理

| 场景 | 处理方式 |
|------|----------|
| 任务无关联项目 | 使用 default 项目 |
| default 项目不存在 | 初始化时已创建，不会出现 |
| 项目记忆文件不存在 | 创建空文件 |
| Claude CLI 调用失败 | 重试 3 次，失败则标记 `failed` |
| 文件读取失败 | 跳过该文件，继续处理 |
| 回流进行中任务 | 跳过（根据 `knowledge_reflow.status`） |

## 12. 日志

- 每次回流记录开始/结束时间
- 记录处理的任务数、提取的条目数
- 错误详细记录

## 13. 初始化

**Server 初始化时**：
1. 创建 `~/.pkm/60_Projects/P_default/` 目录
2. 创建 `P_default/project.md` 记忆文件
3. 初始化 `knowledge_reflow` 表
4. 检查 Claude CLI 环境：`claude -p "hello"`

## 14. 实施步骤

1. 数据库层：tasks 表新增 status 字段，新增 `knowledge_reflow` 表
2. 项目管理：新增 default 项目创建逻辑
3. 环境检查：新增 Claude CLI 环境检查
4. 回流核心：实现定时扫描和回流逻辑
5. API 层：新增 `/api/knowledge/*` 端点
6. 测试：单元测试 + API 测试
