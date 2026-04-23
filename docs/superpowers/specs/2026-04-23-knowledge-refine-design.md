# Knowledge Refinement System Design

> **Project → Knowledge 自动流转系统**

## 背景

- **Task**: 临时性工作空间（毛坯）
- **Project**: 长期积累的知识空间（用户手动流转）
- **Knowledge**: 从 Project 中提取的结构化知识（自动流转）

Project → Knowledge 是系统自动化的知识提炼过程，每天 00:00 执行。

## 接口变更

- **移除**: Stage1 API（Task → Project 手动流转，暂不实现自动化）
- **重构**: Stage2 API 改名为 `reflow`，每天 00:00 定时执行

## 核心设计

### 目录结构

```
~/.pkm/
├── 10_Areas/           # 知识领域分类
│   └── index.md
├── 20_Areas/           # 知识领域分类
│   └── index.md
├── 60_Projects/        # 项目空间
│   ├── project-A/
│   └── project-B/
└── 90_Knowledge/       # 知识库（最终产出）
    ├── index.md        # 单一索引文件
    └── file_index.json # 文件哈希追踪（维护在此目录）
```

### file_index.json 结构

```json
{
  "files": {
    "project-A/file1.md": {
      "md5": "abc123...",
      "updated_at": "2026-04-22T10:00:00Z"
    }
  }
}
```

### ChangeSet 数据结构

```python
@dataclass
class ChangeSet:
    added: list[Path]      # 新增文件
    modified: list[Path]    # 修改文件
    deleted: list[Path]    # 删除文件（暂不处理）
```

### 两轮扫描流程

1. **第一轮扫描**: 遍历 Projects 下所有文件，计算 MD5
   - 若文件不在 `file_index.json` → 加入 `added`
   - 若文件 MD5 变化 → 加入 `modified`
   - 更新 `file_index.json` 中所有文件的哈希

2. **第二轮扫描**: 核对 `file_index.json`
   - 若文件记录存在但实际不存在 → 加入 `deleted`（暂不处理）

### Claude 单文件分析和写入

每个 changed（added/modified）文件单独调用一次 Claude，**分析+执行在同一次调用内完成**。

#### 提示词结构

```
## 知识提取任务

### 目标
将以下文件内容合并到知识库现有条目，或创建新条目。

### 文件路径
{file_path}

### 项目
{project_name}

### 文件内容
{fresh_content}

### 现有相关条目
{existing_entries}

### 任务
分析文件内容，判断：
- 是否需要创建新条目
- 是否需要更新现有条目
- 是否可以跳过（内容无关）
- 是否需要丢弃（不再是知识）

### 输出要求
直接写入知识文件，不要只输出计划：
- action: create | update | skip | discard
- 若 action=create：将新知识条目写入 {knowledge_dir}/{new_id}.md
- 若 action=update：将更新内容追加/合并到现有条目文件
- 若 action=skip 或 discard：无需文件操作

### 知识条目格式（写入文件时使用）
文件名：{id}.md

```markdown
### id
{id}

### title
{title}

### version
{version}

### sources
- {project_name}/{file_path} (v{version}, {date})

### type
经验 | 方案 | 概念 | 参考

### content
{content}
```

#### Claude 输出格式

```
action: create | update | skip | discard

## 知识条目（仅当 create/update 时）

### id
knowledge-id-001

### title
知识标题

### version
1

### sources
- project-A/file1.md (v1, 2026-04-22)

### type
经验 | 方案 | 概念 | 参考

### content
知识内容...
```

### 知识条目格式

```yaml
### id
knowledge-uuid

### title
知识标题

### version
1

### sources
- project-A/file1.md (v1, 2026-04-22)
- project-B/file2.md (v1, 2026-04-20)

### type
经验 | 方案 | 概念 | 参考

### content
知识内容...
```

### index.md 结构

```markdown
# Knowledge Index

## 经验

- [知识标题](knowledge-id.md) - 来源：project-A/file1.md - v1 - 2026-04-22

## 方案

- [知识标题](knowledge-id.md) - 来源：project-B/file2.md - v1 - 2026-04-20

## 概念

## 参考
```

## 执行流程

```
reflow()  # 每天 00:00 执行
    │
    └── scan_projects()  # 两轮扫描
        │
        ├── 第一轮扫描 → added + modified
        │   └── 打印: "扫描到 {n} 个新增/修改文件"
        │
        ├── 更新 file_index.json
        │
        └── 第二轮扫描 → deleted（暂不处理）

    # 串行处理每个文件（不可并行）
    for each file in added + modified:
        logger.info(f"[reflow] 处理文件: {file}")
        │
        analyze_and_merge(file)  # Claude 单次调用完成分析+写入
        │
        └── logger.info(f"[reflow] Claude 结果: {action} - {file}")

    update_index()  # 更新索引
```

**日志规范**:
- 扫描完成: `扫描到 {n} 个新增/修改文件: [file1, file2, ...]`
- 每处理一个文件: `[reflow] 处理文件: {file_path}`
- Claude 调用结果: `[reflow] Claude 结果: {action} - {file_path}`

**关键约束**：
- Claude 处理必须串行执行，不允许并行同时调用
- 每天 00:00 定时执行（通过 cron 或 scheduler）

## 待定项

- [ ] 删除文件处理策略（暂不实现）
- [ ] 冲突解决（多文件来源同一知识）
- [ ] 知识版本管理

## 关键决策

1. **MD5 追踪而非 Git**: 避免与 Claude Code 的 git 工作流冲突
2. **file_index.json 放在 Knowledge 目录**: 便于管理和备份
3. **单文件单独分析**: 保持分析的专注性和准确性
4. **分析和执行合并**: 减少 API 调用次数，提高效率
