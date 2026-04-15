# PKM Reflow 两阶段知识提炼设计

## 概述

PKM 知识提炼采用两阶段闭环设计：

```
10_Tasks → 60_Projects → 20_Areas/knowledge/
```

- **Stage1**：任务 → 项目（经验追加到 project.md）
- **Stage2**：项目 → 公共知识区（金字塔分类沉淀）

## 目录结构

```
~/.pkm/
├── 10_Tasks/              # 任务工作区
├── 60_Projects/           # 项目工作区（经验沉淀终点）
│   └── P_xxx/
│       └── project.md     # 包含 ## 经验/方案索引
├── 20_Areas/              # 公共知识区（金字塔结构）
│   ├── knowledge/
│   │   ├── 01principles/  # 原则层
│   │   ├── 02playbooks/   # 流程/SOP
│   │   ├── 02templates/   # 模板
│   │   ├── 02cases/       # 案例
│   │   └── 03notes/       # 知识点
│   └── manual/            # 受保护区
└── 80_Archives/           # 归档
```

## 任务状态机

```
pending → in_progress → done → approved → archived
                              ↑
                              │ pkm reflow approve
```

## Stage1: 任务 → 项目

### 流程

```
1. 用户执行 pkm task done <task_id>           # 任务完成，状态→done
2. 用户执行 pkm reflow approve <task_id>      # 审批通过，状态→approved
3. 定时任务或 pkm reflow run                 # 扫描 approved 任务，执行回流
4. 读取任务工作区内容                         # 排除代码文件，只读文本
5. Claude 提取经验/方案                       # 结构化输出
6. 追加到 60_Projects/<project>/project.md    # 追加到 ## 经验/方案索引
7. 任务状态→archived                          # 归档
8. 移动任务工作区 → 80_Archives/
```

### 处理逻辑

```python
# 每次扫描所有 approved 状态任务，全量处理
tasks = list_tasks(status="approved")
for task in tasks:
    content = read_task_workspace(task.workspace_path)
    knowledge = extract_knowledge_with_claude(content)  # 调用 Claude CLI
    append_to_project_memory(project_workspace, task, knowledge)
    update_task_status(task.id, "archived")
    move_to_archive(task.workspace_path)
```

## Stage2: 项目 → 公共知识区

### 流程

```
1. 定时任务或 pkm reflow stage2              # 扫描 60_Projects/
2. 筛选未提炼或更新的项目                      # refined=false 或 updated_at > refined_at
3. 分批处理（每批最多 5 个项目）
4. 对每个项目：
   a. 读取 project.md 中 ## 经验/方案索引
   b. Claude 分析知识类型                      # 判断属于哪一层
   c. 去重检查                                # 检查是否已存在相似内容
   d. 追加到 20_Areas/knowledge/<对应目录>    # 分类沉淀
5. 标记项目为已提炼                          # refined=true, refined_at=now
```

### 知识金字塔分类规则

AI 根据内容判断分类到：

| 目录 | 判断标准 |
|------|---------|
| 01principles | 通用方法论、价值观、最佳实践、原则 |
| 02playbooks | 标准化流程、SOP、操作手册 |
| 02templates | 可复用模板、格式 |
| 02cases | 具体案例、实例 |
| 03notes | 领域知识点、零散笔记 |

### 去重规则

- 相似度 > 80%：跳过（已存在）
- 相似度 50-80%：合并或加交叉引用
- 相似度 < 50%：新增

## 定时任务

### 时间表

| 时间点 | stage1 | stage2 |
|--------|--------|--------|
| 00:00 | ✅ | |
| 00:30 | | ✅ |
| 03:00 | ✅ | |
| 03:30 | | ✅ |
| 06:00 | ✅ | |
| 06:30 | | ✅ |
| 09:00 | ✅ | |
| 09:30 | | ✅ |
| 12:00 | ✅ | |
| 12:30 | | ✅ |
| 15:00 | ✅ | |
| 15:30 | | ✅ |
| 18:00 | ✅ | |
| 18:30 | | ✅ |
| 21:00 | ✅ | |
| 21:30 | | ✅ |

Stage1 每 3 小时执行，Stage2 晚 30 分钟（每 3 小时 +30 分钟）。

### 实现

FastAPI 启动时创建后台定时任务调度器：

```python
# main.py startup
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

# Stage1: 每 3 小时
scheduler.add_job(run_reflow_cycle, 'cron', minute=0)

# Stage2: 每 3 小时 +30 分钟
scheduler.add_job(run_stage2_cycle, 'cron', minute=30)

scheduler.start()
```

## 数据库扩展

### projects 表新增字段

```sql
ALTER TABLE projects ADD COLUMN refined BOOLEAN DEFAULT FALSE;
ALTER TABLE projects ADD COLUMN refined_at DATETIME;
```

### reflows 表扩展

```sql
ALTER TABLE reflows ADD COLUMN stage INT DEFAULT 1;  -- 1=任务回流, 2=项目提炼
```

## API 设计

### 新增端点

```bash
# Stage2 手动触发
POST /api/knowledge/reflow/stage2

# Stage2 状态
GET /api/knowledge/reflow/status/stage2
```

### 配置端点扩展

```bash
PATCH /api/knowledge/config
{
  "stage2_interval": 10800,      # 定时周期（秒），默认 3 小时
  "stage2_batch_size": 5,        # 每批处理项目数
  "auto_stage2": true            # 是否自动执行
}
```

## CLI 命令

```bash
# Stage1
pkm reflow run                   # 手动触发 stage1

# Stage2
pkm reflow stage2                # 手动触发 stage2

# 状态
pkm reflow status                # 查看整体状态
pkm reflow status --stage2       # 查看 stage2 详情

# 配置
pkm reflow config --stage2-batch-size 5
pkm reflow config --stage2-interval 10800
```

## 错误处理

### Stage1 失败

- 单个任务失败不影响其他任务
- 失败任务状态不变（仍为 approved），下次定时任务重试
- 记录失败原因到 reflows 表

### Stage2 失败

- 单个项目失败不影响其他项目
- 失败项目不标记为已提炼，下次定时任务重试
- 部分成功的项目仍标记为已提炼

## 安全机制

- Stage2 只处理 `~/.pkm/60_Projects/` 目录
- Stage2 只写入 `~/.pkm/20_Areas/knowledge/` 目录
- 禁止跨目录操作
