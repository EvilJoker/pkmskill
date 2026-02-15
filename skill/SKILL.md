---
name: PKM
description: 当用户显示的使用 @pkm /pkm 时，或者想要"整理知识"、"管理笔记"、"捕获想法"、"归档项目"、"组织 PARA"、"知识提炼"、"整理知识库"、"任务管理"、"项目开发"、"项目归档"时，应使用此技能。
---

# Skill: PKM (Personal Knowledge Management)

> 统一的知识管理入口，基于 **PARA**（Projects/Areas/Resources/Archives）和 **CODE**（Capture/Organize/Distill/Express）方法论。
> 本文档内容以 `docs/ARCHITECTURE.md` 架构设计为准，与之冲突时以架构文档为准。

---

## 自动定位知识库

**AI 自动执行**：每次调用 PKM Skill 时，会自动从配置文件读取知识库位置。

```bash
# 自动检测 PKM 配置
CONFIG_FILE="${HOME}/.pkm/.config"
if [ -f "$CONFIG_FILE" ]; then
    # 读取 DATA_HOME（知识数据目录）
    DATA_HOME=$(grep "^DATA_HOME=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    # 读取各平台 HOME
    CURSOR_HOME=$(grep "^CURSOR_HOME=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    CLAUDE_HOME=$(grep "^CLAUDE_HOME=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    GEMINI_HOME=$(grep "^GEMINI_HOME=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    OPENCLAW_HOME=$(grep "^OPENCLAW_HOME=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
fi
# 如果配置不存在，使用默认目录
PKM_HOME="${PKM_HOME:-${HOME}/.pkm}"
DATA_HOME="${DATA_HOME:-${HOME}/.pkm/data}"
```

**配置文件位置**：`~/.pkm/.config`（安装后由 `.config.template` 复制为 `.config` 并按需修改）

**知识库位置**：配置文件中 `DATA_HOME` 指定的目录（默认为 `~/.pkm/data`），即 PARA 的 10_50 目录所在根。

**PKM 根目录**：`DATA_HOME` 的上级目录（如 `DATA_HOME=/home/user/.pkm/data` 则根目录为 `/home/user/.pkm`）。skill 代码位于 `~/.pkm/skill/`，不在 data 下。

---

## 快速开始

### 最简单的用法

```text
@pkm
```

我会自动判断当前需要执行的操作：

- ✅ 检查知识库结构（Verify）
- 🗄️ 若有已完成任务 → 调用 `@pkm task archive` 执行归档回流（Archive）
- 📦 如果 50_Raw/ 有文件 → 自动组织分类（Organize）
- 💎 如果 20_Areas/knowledge/03notes/ 有新增/变动 → 自动提炼（Distill）

### 查看帮助

```text
@pkm help
```

显示完整的命令列表和使用说明。

---

## 命令列表

### 一键整理知识

```text
@pkm
```

**一键全自动处理**，系统智能整理和提炼知识，无需人工干预。

**自动顺序执行**（不推荐单独使用）：
- `@pkm verify` - 自动检查知识库结构完整性（5 个顶级目录：10_Tasks、20_Areas、30_Resources、40_Archives、50_Raw）
- 主流程中的 Archive - 调用 `@pkm task archive` 自动扫描所有任务工作空间，归档含 completed.md 的已完成任务（知识回流到 20_Areas/knowledge/ 与 20_Areas/Projects/，任务移至 40_Archives/）
- `@pkm organize` - 自动分类整理 `50_Raw/` 中的待处理内容
- `@pkm distill` - 自动提炼 `20_Areas/knowledge/03notes/` 中的知识

**适用场景**：

- ✅ 每天结束前执行一次，自动整理当天积累的知识
- ✅ 任务完成后，自动归档并回流知识
- ✅ 定期维护，保持知识库整洁有序

### 快速捕获

```text
@pkm inbox <内容>                 # 快速捕获，默认不解析链接内容
@pkm inbox --parse <内容>        # 先解析链接内容，再捕获
```

### 智能咨询

```text
@pkm advice <问题>                          # 默认模式（common + local）
@pkm advice --scope <范围> <问题>           # 指定范围模式

scope 值：
  - common          # 仅 AI 通用知识
  - local           # 仅当前知识库
  - task            # 指定任务知识库
  - 默认：common + local（可叠加）
```

### 任务管理

```text
@pkm task add <内容>        # 添加新任务，创建任务区（交互式补全：想法、4象限、计划完成时间、工作量）
@pkm task ls                # 列出所有任务（按计划完成时间排序，含延期风险提示）
@pkm task ls --all          # 列出所有任务（含已归档）
@pkm task use <id>   # 切换到指定任务，加载任务区信息
@pkm task edit <id>         # 编辑任务
@pkm task update <id>       # 更新任务进展
@pkm task done <id>         # 完成任务，总结任务清单
@pkm task delete <id>       # 删除任务
@pkm task archive            # 自动扫描含 completed.md 的任务并归档，回流知识到知识库
```

**任务字段**：状态、ID、标题、工作空间路径、4象限、计划完成时间、工作量

### 长期项目管理

```text
@pkm project add <名称>     # 在 20_Areas/Projects/ 添加新的长期项目
@pkm project delete <project_name>  # 删除项目
@pkm project ls             # 列出所有长期项目
```

### PKM 自管理

```text
@pkm status                 # 查看 PKM 状态（配置、知识库概况、项目/任务列表、版本、上次总结报告简述）
@pkm upgrade                # 更新 PKM（在 ~/.pkm 执行 git pull）
```

### 帮助与信息

```text
@pkm help                  # 显示帮助信息
```

---

## 工作流程

### 1. 前置验证（自动执行）

调用 `_Verifier` 模块：

- ✅ 定位知识库目录：`${DATA_HOME}`
- ✅ 检查 `${DATA_HOME}` 中 **5 个顶级目录**（10_Tasks/、20_Areas/、30_Resources/、40_Archives/、50_Raw/）是否存在且结构完整
- ✅ 确认操作范围白名单（限定在知识库目录内）
- ✅ 生成写权限白名单（manual/ 只读）
- 缺失目录则自动创建，然后继续

### 2. 命令路由

根据命令参数路由到相应模块：

**一键整理知识（无参数）**：
- 执行 `@pkm`：主流程 `Verify → Archive → Organize → Distill`
- 其中 Archive 阶段 = 调用 `@pkm task archive`（由 _TaskManager 执行，归档已完成任务并回流知识）
- 对应可单独调用的子步骤：`@pkm verify`、`@pkm organize`、`@pkm distill`；任务归档通过 `@pkm task archive` 执行（自动扫描含 completed.md 的任务）

**手动命令（带参数）**：

- `inbox <内容>` → `_Verifier` → `_Inbox`（快速捕获）
- `inbox --parse <内容>` → `_Verifier` → `_Inbox`（先解析链接再捕获）
- `advice <问题>` → `_Verifier` → `_Advisor`（默认模式：common + local）
- `advice --scope <范围> <问题>` → `_Verifier` → `_Advisor`（指定范围）
- `task <操作>` → `_Verifier` → `_TaskManager`（任务管理）
- `project <操作>` → `_Verifier` → `_ProjectManager`（长期项目管理）
- `organize` → `_Verifier` → `_Organizer`（组织分类）
- `distill` → `_Verifier` → `_Distiller`（提炼知识）
- `verify` → `_Verifier`（仅验证）
- `status` → `_Verifier` → `_PkmSelfManager`（查看状态）
- `upgrade` → `_PkmSelfManager`（更新版本）
- `help` → `_Help`（显示帮助信息）

### 3. 执行与报告

执行相应操作，生成统一格式的报告。

---

## 内部模块说明

PKM 由 9 个内部模块组成，每个模块负责知识管理的一个环节（与 ARCHITECTURE 5.1 / 5.2 一致）：

| 模块 | 职责 | 对应阶段 | 触发方式 |
|------|------|---------|---------|
| `_Verifier` | 范围守卫，验证结构（5 个顶级目录、操作范围、写权限白名单） | 前置检查 | 自动（每次操作前） |
| `_Inbox` | 快速捕获器 | Capture | `@pkm inbox` |
| `_Advisor` | 智能顾问 | Express | `@pkm advice` |
| `_Organizer` | 智能组织器 | Organize | `@pkm organize` 或主流程 |
| `_Distiller` | 知识提炼器 | Distill | `@pkm distill` 或主流程 |
| `_ProjectManager` | 长期项目管理器 | 支撑 | `@pkm project`（add/delete/ls） |
| `_TaskManager` | 任务管理器 | 支撑 | `@pkm task`（含 archive 归档回流） |
| `_Help` | 帮助信息 | 支撑 | `@pkm help` |
| `_PkmSelfManager` | 自管理器 | 支撑 | `@pkm status` / `@pkm upgrade` |

### 📋 _Verifier（范围守卫）

**职责**：验证知识库结构，缺失目录则自动创建，生成操作白名单

**触发**：每次操作前自动执行

**检查范围**：`${DATA_HOME}` 下 5 个顶级目录（10_Tasks/、20_Areas/、30_Resources/、40_Archives/、50_Raw/）存在且结构完整；不包含 skill（skill 位于 PKM 根目录）。

**详细文档**：`_Verifier.md`

---

### 📥 _Inbox（快速捕获器）

**职责**：快速捕获信息到 Inbox，降低记录门槛

**对应阶段**：CODE 的 **Capture**（捕获）

**触发**：

- 手动调用：`@pkm inbox <内容>`
- 解析链接后捕获：`@pkm inbox --parse <内容>`

**前置要求**：

- ⚠️ 必须先调用 `_Verifier` 验证环境
- 确认 `50_Raw/inbox/` 存在且可写

**核心功能**：

- 快速保存文本、想法、链接到 `50_Raw/inbox/`
- AI 生成文件名（简单总结内容，5-10 字标题）
- 智能处理链接（默认仅引用，`--parse` 模式先解析链接内容再捕获）
- 保存格式：`YYYYMMDD_HHMMSS_标题_inbox.md`

**详细文档**：`_Inbox.md`

---

### 🤔 _Advisor（智能顾问）

**职责**：提供决策支持和知识咨询

**对应阶段**：辅助所有阶段的决策

**触发**：

- 默认模式：`@pkm advice <问题>`（等价于 `--scope common,local`）
- 指定范围：`@pkm advice --scope <范围> <问题>`
  - `--scope common`：仅 AI 通用知识
  - `--scope local`：仅当前知识库
  - `--scope task` 或 `--scope <任务名>`：仅指定任务知识库
  - `--scope common,local`：AI 通用知识 + 当前知识库（默认）
  - `--scope local,任务名`：当前知识库 + 指定任务知识库

**前置要求**：⚠️ 必须先调用 `_Verifier` 验证环境

**核心功能**：根据 scope 检索知识库，结合 AI 通用知识回答问题，提供分类建议（如笔记应放目录）。

**详细文档**：`_Advisor.md`

---

### 📦 _Organizer（智能组织器）

**职责**：处理 `50_Raw/` 中的未分类内容，合并同类内容，分类归位到 PARA 体系

**对应阶段**：CODE 的 **Organize**

**触发**：主流程中有待处理内容时自动执行，或手动调用 `@pkm organize`

**核心功能**：

- 扫描 `50_Raw/`（包含 `inbox/` 和其他待分类素材）
- **可选插件预处理**：若存在 `skill/plugin/SKILL.md`，先按内容类型匹配插件，命中则用对应 `template_<类型>.md` 模版整理，再继续分类
- 按主题/类型合并同类内容到 `50_Raw/merged/`
- 判断类型（项目/知识/资料）和主题，分类归位：
  - 项目 → `20_Areas/Projects/<项目名称>`（仅当有关联项目时）
  - 知识 → `20_Areas/knowledge/03notes/<领域>/`（先放在 notes 层）
  - 资料 → `30_Resources/Library/`
- 整理完清理已分类的文件，清空 `50_Raw/`

**详细文档**：`_Organizer.md`

---

### 💎 _Distiller（知识提炼器）

**职责**：将 `20_Areas/knowledge/03notes/` 中的零散知识按金字塔原理提炼成结构化知识

**对应阶段**：CODE 的 **Distill**

**触发**：主流程中有新增/变动时自动执行，或手动调用 `@pkm distill`

**核心功能**：

- 扫描 `20_Areas/knowledge/03notes/` 各领域目录
- 与已有知识深度整合（去重、交叉引用、结构化）
- 按金字塔原理提炼：零散知识（notes）+ 20_Areas/manual（只读）→ 整理知识 → 应用知识（knowledge/02playbooks/02templates/02cases）→ 原则知识（knowledge/01principles）
- 沉淀到对应目录；系统性检查（一致性、过时性、冗余、逻辑合理性）
- 总结提炼结果，生成报告到 `30_Resources/summary/`，格式 `YYYYMMDD_HHMMSS_标题_Distill.md`
- **整理 Project 区内容**：扫描 `20_Areas/Projects/` 下所有项目，对每个项目内文件检查重复、冗余、一致性等问题，并进行整理（与方案 4.2 一致；规模过大时一次最多处理 20 个文件）

**详细文档**：`_Distiller.md`

---

### 📁 _ProjectManager（项目管理器）

**职责**：管理 `20_Areas/Projects/` 下的长期项目（添加、删除、列表）

**对应阶段**：支撑任务与知识沉淀的长期项目容器

**触发**：`@pkm project add`、`@pkm project delete`、`@pkm project ls`

**核心功能**：

- 在 20_Areas/Projects/ 下添加新长期项目、删除项目、列出所有长期项目
- 项目目录格式可为 `01_xxx` 等（以宪章 2.4 为准）

**详细文档**：`_ProjectManager.md`

---

### 📋 _Help（帮助信息）

**职责**：显示完整帮助信息，包括所有命令列表、使用示例、数据存储路径等

**触发**：`@pkm help`

**详细文档**：`_Help.md`

---

### 📋 _TaskManager（任务管理器）

**职责**：管理任务，支持 4 象限管理；add/ls/use/edit/update/done/delete/archive；任务工作空间 `10_Tasks/TASK_WORKSPACE_YYYYMMDD_HHMMSS_xxx/`，任务数据 `task.md`；archive 时回流知识到 20_Areas/knowledge/ 与 20_Areas/Projects/

**触发**：`@pkm task <子命令>`

**详细文档**：`_TaskManager.md`

---

### 🔧 _PkmSelfManager（自管理器）

**职责**：查看 PKM 运行状态、更新 PKM 项目

**触发**：`@pkm status`、`@pkm upgrade`

**status**：输出配置文件（`~/.pkm/.config`）、数据目录位置、知识库数量概况、长期项目列表（引用 `@pkm project ls`）、任务列表（引用 `@pkm task ls` 与 `@pkm task ls --all`）、PKM 版本、上次 pkm 执行时间、上次 pkm 总结报告简述（不超过 100 字）。

**upgrade**：在 PKM 安装目录（默认 `~/.pkm`）执行 `git pull`，更新 skill 与 command。

**详细文档**：`_PkmSelfManager.md`

---

## 使用示例

### 场景 1：日常工作流（完全自动）

```text
# 每天结束前
@pkm

# 输出示例：
✅ Verifier 验证通过

🗄️ 检测到已完成任务
🔄 执行 @pkm task archive（TaskManager）...
  └─ 知识回流到 20_Areas/knowledge/ 与 20_Areas/Projects/，任务移至 40_Archives/ ✅

📦 检测到 50_Raw/ 有 8 个文件
🔄 执行 Organizer...
  ├─ 合并同类内容到 50_Raw/merged/
  ├─ 知识 → 20_Areas/knowledge/03notes: 5 个
  └─ 50_Raw/ 已清空 ✅

💎 检测到 20_Areas/knowledge/03notes/01_react/ 有新增
🔄 执行 Distiller...
  └─ 报告 → 30_Resources/summary/YYYYMMDD_HHMMSS_知识提炼报告_Distill.md ✅

🎉 完成！主流程执行完毕。
```

### 场景 2：只组织分类 50_Raw/

```text
@pkm organize
```

### 场景 3：只提炼知识

```text
@pkm distill
```

### 场景 4：查看帮助

```text
@pkm help
```

---

## 安全机制

### 双重防火墙

1. **内部防火墙**：受保护区 vs AI 可写区
   - AI 可写：`20_Areas/knowledge/`（03notes、02playbooks、02templates、02cases、01principles）、`10_Tasks/`、`20_Areas/Projects/`、`50_Raw/`、`30_Resources/Library/`、`40_Archives/`
   - AI **只读**：`20_Areas/manual/`，绝不直接修改

2. **外部防火墙**：知识库内 vs 知识库外
   - Verifier 强制检查目录结构，操作仅限 `${DATA_HOME}` 内
   - 禁止操作知识库外路径

### 白名单机制

**可写区域**（AI 可以创建/修改/删除文件）：
`50_Raw/`、`10_Tasks/`（任务工作空间）、`20_Areas/knowledge/`（03notes、02playbooks、02templates、02cases、01principles）、`20_Areas/Projects/`、`30_Resources/Library/`、`40_Archives/`

**只读区域**：`20_Areas/manual/`、`skill/`

**禁止区域**：知识库根目录（DATA_HOME）外的任何路径

---

## 核心原则

1. **自动化优先**：能自动处理的不要人工干预
2. **安全至上**：先验证后操作，永不越界
3. **人类决策**：AI 提建议，人类做决策
4. **渐进式**：从简单到复杂，从手动到自动
5. **可追溯**：所有操作都有日志和报告

---

## 故障排查

### 问题：提示「知识库结构不完整」

**说明**：Verifier 会**自动创建**缺失的 5 个顶级目录，通常不会出现此提示。若仍出现，多为 DATA_HOME 路径不可写或不存在。

**解决**：确认 `~/.pkm/.config` 中 DATA_HOME 指向的目录存在且可写；或手动创建 DATA_HOME 目录后再执行 `@pkm`。

### 问题：文件被标记为「待确认」

**原因**：Organizer 无法判断文件类型。
**解决**：人工判断类型后，将文件移动到正确位置（如 `20_Areas/knowledge/03notes/<领域>/` 或 `30_Resources/Library/`）。

### 问题：草稿质量差

**原因**：原子块质量参差不齐。
**解决**：可手动编写到 `20_Areas/manual/`（受保护区），或重新收集高质量片段到 `50_Raw/inbox/`。

---

## 高级配置

### 手动执行单个步骤

若只想执行部分操作，可单独调用：

```text
@pkm organize              # 只执行组织分类（处理 50_Raw/）
@pkm distill               # 只执行提炼（处理 20_Areas/03notes/）
@pkm task archive          # 归档所有已完成任务（扫描含 completed.md 的，回流知识并搬运到 40_Archives/）
@pkm verify                # 只验证知识库结构
```

---

## 反馈与支持

若使用中遇到问题：

1. 执行 `@pkm help` 查看命令列表
2. 查阅具体模块文档（`_Verifier.md`、`_Inbox.md` 等）
3. 对照架构设计：`docs/ARCHITECTURE.md`

祝你的知识管理之旅愉快！
