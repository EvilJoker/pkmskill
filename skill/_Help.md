# Skill: _Help (帮助信息)

## 角色定位

你是 PKM 知识管理系统的**帮助模块**，负责显示完整的帮助信息，确保用户能够快速了解 PKM 的使用方法。

---

## 触发时机

- 用户执行 `@pkm help` 时

---

## 前置要求

⚠️ **无需调用 `Verifier`**：帮助信息是只读操作，不需要验证知识库结构。

---

## 执行步骤

### 步骤 1：输出帮助信息

直接输出以下帮助内容：

---

## PKM 帮助信息

> **数据存储路径**：`${DATA_HOME}`（默认 `~/.pkm/data`）

### 命令列表

#### 🚀 一键整理

```
@pkm
```

自动执行：Verify → Archive → Organize → Distill

```
@pkm verify              # 检查知识库结构
@pkm organize            # 分类整理 50_Raw/
@pkm distill             # 提炼知识
@pkm task archive        # 归档已完成任务，回流知识
```

---

#### 📥 快速捕获

```
@pkm inbox <内容>                 # 快速捕获，默认不解析链接内容
@pkm inbox --parse <内容>        # 先解析链接内容，再捕获
```

---

#### 🤔 智能咨询

```
@pkm advice <问题>                          # 默认模式（common + local）
@pkm advice --scope <范围> <问题>           # 指定范围模式
```

- `scope: common` - AI 通用知识
- `scope: local` - 知识库
- `scope: task` - 指定任务

---

#### 📋 任务管理

```
@pkm task add <内容>        # 添加新任务，创建工作空间和 描述文件 task.md
@pkm task ls                # 列出所有任务
@pkm task ls --all          # 含已归档
@pkm task use <name>        # 加载任务资料
@pkm task edit <id>          # 编辑任务
@pkm task update <id>        # 更新进展
@pkm task done <id>          # 完成任务, 追问总结（内容、收益、价值评分）并生成 `completed.md`（含需回流资料与知识清单）
@pkm task delete <id>        # 删除任务
@pkm task archive            # 归档并回流知识， 被 @pkm 自动调用，扫描已完成的任务，并进行归档并回流知识
```

---

#### 📁 长期项目管理

对长期维护的项目经常需要增量开发，这时可以创建一个项目。增量工作可以创建一个任务，和项目关联起来，这样任务完成后，知识会自动回流到对应的项目中。

```
@pkm project ls             # 列出所有项目
@pkm project add <名称>     # 添加新项目
@pkm project delete <名称>  # 删除项目
```

**工作流示例**：

```
# 添加一个长期项目
@pkm project add 我的项目

# 在项目中添加任务
@pkm task add 完成项目调研

# 任务完成后归档，自动回流知识到项目
@pkm task done T-xxxx-001```

---

#### 🔧 自管理

```
@pkm status                 # 查看状态
@pkm upgrade                # 更新版本
@pkm help                   # 显示帮助
```

---

### 目录结构

```
~/.pkm/
├── .config              # 配置文件
├── data/               # 知识数据
│   ├── 10_Tasks/       # 任务
│   ├── 20_Areas/       # 领域（Projects/knowledge/manual）
│   ├── 30_Resources/   # 资源库
│   ├── 40_Archives/    # 归档
│   └── 50_Raw/        # 素材（inbox/merged）
├── skill/              # Skills
└── command/            # Commands（Cursor）
```

---

---


### 工作流

```
# 早上：快速捕获想法
@pkm inbox 想到的新点子...

# 工作中：实时记录
@pkm inbox 学习到的知识点...

# 添加任务
@pkm task add 实现某个功能

# 查看所有任务
@pkm task ls

# 在会话里加载某个任务
@pkm task use T-xxxx-001

# 更新任务进展
@pkm task update T-xxxx-001 已完成初稿

# 完成任务，并生成 知识回流清单
@pkm task done T-xxxx-001

# 晚上：一键整理（推荐每天执行）
@pkm
```

---

### 详细文档

- 架构设计：`docs/ARCHITECTURE.md`

---

💡 提示：如需了解特定模块的详细用法，请查阅对应文档。
