# PKM Skill - 智能知识管理工具包

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/EvilJoker/pkmskill)

> 基于 **PARA + CODE + 金字塔原理** 的 AI 驱动知识管理系统，让 AI 成为你的知识管家

**快速开始**：`@pkm help` 查看所有命令

---

## 📖 什么是 PKM Skill？

PKM Skill 是一个智能知识管理工具包，通过 AI 自动化处理知识的捕获、组织、蒸馏和表达。你只需专注于思考和验证，繁琐的知识整理工作交给 AI。

### 核心理念：PARA + CODE + 金字塔原理

#### 🗂️ PARA（知识组织结构）

五层生命周期管理，让知识自然流动：

- **10_Tasks（任务）**：短期目标，有明确截止日期，任务清单为 tasks.md / tasks_archive.md
- **20_Areas（领域）**：长期关注，持续积累的知识领域
- **30_Resources（资源）**：参考资料
- **40_Archives（归档）**：已完成项目，保持系统轻量
- **50_Raw（素材区）**：统一的新鲜素材捕捉起点，包含 inbox 和待分类的碎片

#### 🔄 CODE（知识工作流）

完整的知识处理闭环：

- **📥 Capture（捕获）**：快速记录到 `50_Raw/inbox/`，零心理负担
- **📋 Organize（组织）**：AI 自动分类整理 `50_Raw/` 中的内容
- **💎 Distill（提炼）**：按金字塔原理提炼 `20_Areas/03notes/` 中的知识
- **✨ Express（表达）**：通过智能咨询、项目归档等方式输出应用知识

#### 🏛️ 金字塔原理（知识组织）

知识在 `20_Areas/` 中按金字塔结构流动：

- **🏛️ 原则层**（`01principles/`）：顶层智慧、方法论、框架
- **📋 应用层**（`02playbooks/`、`02templates/`、`02cases/`）：标准化流程、模版、案例
- **📝 整理知识层**（`03notes/<领域>/`）：零散知识点，按领域分类

**知识流动方向**：零散知识 → 应用知识 → 原则知识

#### 🛡️ 受保护区机制

- **📜 manual/（受保护区）**：项目金标准、架构决策、全域共用素材区；AI 只读，人工维护
- **🤖 AI 可写区**：`20_Areas/03notes/`、`02playbooks/`、`02templates/`、`02cases/`、`01principles/` 等，AI 可以自由创建和修改

---

## ✨ 核心特性

- 🎯 **统一命令入口**：通过 `@pkm` 一键管理知识库
- 📥 **快速捕获**：`@pkm inbox` 快速记录，降低捕获门槛
- 📋 **任务管理**：`@pkm task add/ls/done/archive` 管理任务，支持 4 象限，任务数据在 10_Tasks/
- 🏗️ **项目管理**：`@pkm project add/ls` 管理长期项目（20_Areas/Projects/）
- 🤖 **智能自动化**：自动分类、蒸馏落地、归档
- 🔌 **Organizer 插件**：可选按内容类型用模版预处理（如故障总结、会议纪要），再分类归位
- 🔒 **安全防护**：严格的范围守卫，保护人工知识区域
- 🔄 **CODE 闭环**：完整的 Capture → Organize → Distill → Express 流程
- 📦 **全局安装**：一次安装，任意项目使用

## 安装

### 快速安装

```bash
# 1. 克隆仓库
git clone https://github.com/EvilJoker/pkmskill.git ~/.pkm

# 2. 运行安装脚本（会自动检测并安装到可用的AI工具）
bash ~/.pkm/scripts/install.sh
```

### 手动安装

如需手动安装，参考以下路径：

| 工具 | Skill 路径 | 命令格式 |
|------|-----------|---------|
| Cursor | `~/.cursor/skills/PKM` → `~/.pkm/skill` | `@pkm` 或 `/pkm` |
| Claude Code | `~/.claude/skills/pkm` → `~/.pkm/skill` | `@pkm` |
| Gemini CLI | `~/.gemini/skills/pkm` → `~/.pkm/skill` | `/pkm` |
| OpenCLAW | `~/.openclaw/skills/pkm` → `~/.pkm/skill` | `@pkm` |

详细安装说明见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

### 开始使用

安装完成后，按顺序尝试：

```text
@pkm help        # 查看所有命令
@pkm inbox 测试   # 录入一条信息
@pkm             # 触发一次整理
@pkm status      # 查看知识库状态
```

## 配置

首次使用时，`@pkm` 会自动检查并创建缺失的数据目录（DATA_HOME 下的 PARA 结构），无需手动初始化。

### 从旧项目格式迁移

若你之前使用过 **10_Projects**（项目目录）或 **30_Resources/todo.md、todo_archive.md**，可一键迁移到新的 **10_Tasks**（任务）格式：

```bash
# 在 PKM 仓库根目录（如 ~/.pkm）执行
bash scripts/migrate-projects-to-tasks.sh
```

- **10_Projects/YYYYMMDD_HHMMSS_xxx/** → 每个目录会变成 **10_Tasks/TASK_WORKSPACE_YYYYMMDD_HHMMSS_xxx/**，并生成 `task.md`；若目录内有 `COMPLETED.md`，会转为 `completed.md` 并写入 `tasks_archive.md`。
- **todo.md / todo_archive.md** → 内容会并入 `tasks.md`、`tasks_archive.md` 作为参考块，便于你后续整理为正式任务索引。
- 执行后原 **10_Projects** 会备份为 **10_Projects.bak.<时间戳>**，确认无误后可删除。

预览不写入：`bash scripts/migrate-projects-to-tasks.sh --dry-run`

### 常用命令

| 命令 | 功能 | 使用场景 |
| ---- | ---- | -------- |
| **任务管理** | | |
| `@pkm task add <内容>` | 添加任务 | 创建任务空间与 task.md，写入 tasks.md 索引 |
| `@pkm task ls` | 列出任务 | 按 4 象限，含进展核查与延期提示 |
| `@pkm task use <id>` | 切换任务 | 加载任务区信息到当前上下文 |
| `@pkm task done <id>` | 完成任务 | 生成 completed.md，写入 tasks_archive.md |
| `@pkm task archive` | 归档任务 | 自动扫描含 completed.md 的任务，回流知识并移至 40_Archives/ |
| **长期项目** | | |
| `@pkm project add <名称>` | 添加长期项目 | 在 20_Areas/Projects/ 下创建 |
| `@pkm project ls` | 列出长期项目 | 查看 20_Areas/Projects/ |
| **智能咨询** | | |
| `@pkm advice <问题>` | 智能咨询 | 默认：AI + 知识库 |
| `@pkm advice --scope <范围> <问题>` | 指定范围 | scope: common/local/项目名 |
| **一键整理** | | |
| `@pkm` | 主流程 | 自动完成所有整理工作 |
| `@pkm organize` | 组织分类 | 处理 50_Raw/ |
| `@pkm distill` | 提炼知识 | 处理 20_Areas/03notes/ |
| **自管理** | | |
| `@pkm status` | 查看状态 | 配置、知识库概况、版本等 |
| `@pkm upgrade` | 更新版本 | git pull 更新 |
| `@pkm help` | 查看帮助 | 命令列表 |


### @pkm 一键整理

`@pkm` 是最常用的命令，会自动检测并执行：

1. **Verify** - 验证知识库目录结构（10_Tasks、20_Areas、30_Resources、40_Archives、50_Raw）
2. **Archive** - 归档已完成任务（扫描 10_Tasks 中含 completed.md 的，回流知识并移至 40_Archives/）
3. **Organize** - 分类归位 50_Raw/ → 20_Areas/knowledge/、Projects/、30_Resources/Library
4. **Distill** - 提炼 20_Areas/knowledge/03notes/ → 应用层/原则层

推荐：每天结束前执行一次 `@pkm`

详细说明见 [架构文档](docs/ARCHITECTURE.md)。

## pkm 项目升级

使用 `@pkm upgrade` 命令，或者在 PKM 安装目录执行 `git pull` 更新项目。

## 🤝 支持的 AI 工具

- ✅ **Cursor** - 通过 `.cursor/commands/pkm.md` 配置（使用 `/pkm` 命令）
- ✅ **Claude Code** - 通过 Skills 目录（使用 `@pkm` 命令）
- ✅ **Gemini CLI** - 通过 Skills 目录（使用 `/pkm` 命令）
- ✅ **OpenCLAW** - 通过 Skills 目录（使用 `/pkm` 命令）

## 💡 日常工作流

### 早上：快速捕获

```text
@pkm inbox 昨晚想到的新点子...
@pkm inbox --parse 这篇文章很有用 https://example.com
```

### 工作中：实时记录

```text
@pkm inbox Bug修复：邮件发送超时问题
@pkm inbox React性能优化技巧...
```

### 日常工作流

```text
# 1. 添加任务
@pkm task add 实现用户认证功能

# 2. 可选：添加关联的长期项目
@pkm project add 用户认证系统

# 3. 更新任务进展
@pkm task update T-20260113-143000-001

# 4. 完成任务（追问总结：内容、收益、价值评分，生成 completed.md）
@pkm task done T-20260113-143000-001

# 5. 自动归档已完成任务 + 整理知识（推荐每天执行）
@pkm
```

**@pkm 自动执行**：归档含 completed.md 的任务（回流知识到 20_Areas/）+ 组织分类 50_Raw/ + 提炼 20_Areas/knowledge/03notes/

### 遇到问题：智能咨询

```text
@pkm advice React 性能优化有哪些最佳实践？
@pkm advice --scope common React 18 新特性有哪些？
@pkm advice --scope local 上次 Redis 连接池问题怎么解决的？
@pkm advice --scope task 这个任务的架构设计是什么？
@pkm advice 这篇关于微服务的笔记应该放到哪个目录？
```

### 晚上：一键整理知识（推荐）

```text
@pkm
# 一键整理知识会自动：
# 1. 验证知识库结构（Verify）
# 2. 归档已完成的项目（Archive）
# 3. 组织分类 50_Raw/ 中的内容（Organize）
# 4. 提炼 20_Areas/03notes/ 中的知识（Distill）
```

**💡 提示**：这是最常用的命令，一条命令完成所有整理工作！

### 迁移旧笔记

将旧笔记放入 `50_Raw/`，系统会自动整理。


## 📚 文档

- [架构设计](docs/ARCHITECTURE.md) - 完整架构与命令说明

## 🛠️ 开发

```bash
# 克隆仓库
git clone https://github.com/EvilJoker/pkmskill.git
cd pkmskill

# 本地测试安装
bash scripts/install.sh
```

## 🎯 核心原则

1. **简单至上**：不追求繁琐的流程，保证核心的机制简单易用
2. **相信AI**：相信AI的能力，将判断和决策交给AI，用户负责后期纠偏，保证流程的自动化
3. **渐进提炼**：从碎片到知识，从知识到经验，是渐进式提炼的过程
4. **安全至上**：先验证后操作，永不越界
5. **可追溯**：所有操作都有日志和报告

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 🙏 致谢

基于以下方法论：

- **PARA**：Tiago Forte 的项目组织方法（Projects, Areas, Resources, Archives, Raw）
- **CODE**：Capture, Organize, Distill, Express 工作流
- **金字塔原理**：知识从零散到凝练的渐进式提炼（notes → playbooks/templates/cases → principles）

## 📮 反馈

遇到问题或有建议？请[提交 Issue](https://github.com/EvilJoker/pkmskill/issues)

---

**让知识管理更简单** 🚀
