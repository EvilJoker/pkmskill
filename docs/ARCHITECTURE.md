# 知识管理系统架构方案

这套方案的核心目标是构建一个**"自清洁、自进化"**的知识系统。它将你从琐碎的文件搬运中解放出来，让你专注于最核心的"思考"与"验证"。

以下是基于 **Cursor/Claude Code/Gemini CLI + Git + PARA + CODE** 的全套管理方案：

---

## 一、 设计

### 1.0 设计原则

- 简单至上：不追求繁琐的流程，保证核心的机制简单易用。
- 相信AI: 相信AI的能力，将判断和决策交给AI，用户负责后期纠偏，保证流程的自动化。
- 渐进提炼: 从碎片到知识，从知识到经验，是渐进式提炼的过程。
- 任务驱动： 任务是工作的最小单元，任务结束需要知识回流，保证任务和知识库不割裂。

### 1.1 CODE 信息管理法则

**CODE 是解决知识的捕获、组织、蒸馏、表达的闭环流程**：

- **Capture（捕获）**：快速捕获碎片化信息到 `50_Raw/inbox/`，降低捕获门槛。
- **Organize（组织）**：对素材进行合并、分类、归位，实现智能分流。
- **Distill（提炼）**：深度整合、去重、结构化，沉淀为可复用知识。
- **Express（表达）**：通过智能咨询、任务归档等方式输出应用知识。

### 1.2 PARA 结构

**PARA 是解决顶层组织逻辑，让知识按时间维度自然流动**：

- **10_Tasks（任务）**：有明确截止日期的任务。聚焦任务的执行。
- **20_Areas（领域）**：长期关注的责任领域。聚焦知识的沉淀。
- **30_Resources（资源）**：感兴趣但暂未深度加工的素材。聚焦第三方的资料与文档。
- **40_Archives（归档）**：已完成的任务和不再活跃的领域。定期清理，保持系统轻量。
- **50_Raw（素材区）**：自定义的新鲜素材区, 统一的新鲜素材捕捉起点，包含 inbox 和待分类的碎片。整理后应清空。

### 1.3 金字塔流动

**流动聚焦 20_Areas的组织逻辑， 实现从零散到凝练的渐进式提炼**：

人类的知识第一界别是凝练的 "经验"，其次才是零散的 "知识"。类似DIKW模型，从知识到经验，是渐进式提炼的过程。

- **顶层（原则层）**：Principles（方法论、原则、框架），最凝练的经验总结。
- **上层（应用层）**：Playbooks（标准化流程）、Templates（可复用模版）、Cases（具体案例）。
- **中层（整理知识）**：聚焦各个领域的知识，是整理过后的知识，是知识的集合。
- **底层（零散知识）**：粗糙的、新鲜的、碎片化的、未被整理的知识。

知识流动方向：零散知识 → 整理知识（knowledge/03notes/） → 应用知识（knowledge/playbooks/templates/cases） → 原则知识（knowledge/principles），通过 Distill 过程实现自下而上的提炼和自组织。

### 1.4 任务是短期的工作单元、项目是长期维护的领域

**任务驱动知识回流，确保任务执行过程中产生的知识能够沉淀到知识库**：

- **Task（任务）**：短期工作单元，有时间约束的目标，每个 Task 有独立的 `task.md` 和任务工作空间
- **四象限管理**：通过重要/紧急四象限法管理任务优先级
- **任务容器**：每个 Task 对应一个任务工作空间，承载任务执行过程中的所有内容
- **Project（项目）**：长期维护的领域，存放在 `20_Areas/Projects/`
- **知识回流**：Task 完成后，知识回流到 `20_Areas/knowledge/`，Task 相关内容回流到 `20_Areas/Projects/<项目名>`
- **闭环保障**：保证任务和知识库不割裂，形成完整的知识循环



## 二、 目录架构 (The Physical Layout)


### 2.1 PKM 整体目录结构

```
~/.pkm/                          # PKM 主目录（安装位置，配置见 .config）
├── .config                      # 安装与运行配置（见 2.3）
├── data/                        # 知识数据（10_50 目录）
│   ├── 10_Tasks/
│   ├── 20_Areas/
│   ├── 30_Resources/
│   ├── 40_Archives/
│   └── 50_Raw/
├── skill/                       # Skills 代码
│   ├── SKILL.md
│   ├── _Verifier.md
│   ├── _Inbox.md
│   ├── _PkmSelfManager.md       # 自管理：status / upgrade
│   └── ...
└── command/                    # Commands（仅 Cursor 支持）
    └── cursor/
        ├── pkm.md              # /pkm 主流程
        ├── pkm.inbox.md        # /pkm.inbox 捕获
        ├── pkm.advice.md       # /pkm.advice 智能咨询
        ├── pkm.help.md         # /pkm.help 帮助
        ├── pkm.task.md         # /pkm.task 任务
        ├── pkm.status.md        # /pkm.status 查看当前状态
        └── pkm.upgrade.md      # /pkm.upgrade 更新 PKM（git pull）
```

### 2.2 目录说明

| 目录 | 说明 | 是否可写 |
|------|------|---------|
| `data/` | 知识数据，包含 10_50 目录 | 是 |
| `skill/` | Skills 代码，驱动流程的引擎 | 否（只读） |
| `command/` | Cursor 斜杠命令入口（仅 Cursor 支持 Command） | 否（只读） |

### 2.3 配置文件

**配置文件位置**：`~/.pkm/.config`

```bash
DATA_HOME="/home/user/.pkm/data"
CURSOR_HOME="/home/user/.cursor/"
CLAUDE_HOME="/home/user/.claude/"
GEMINI_HOME="/home/user/.gemini/"
OPENCLAW_HOME="/home/user/.openclaw/"
```

安装后由 `.config.template` 复制为 `.config` 并按需修改；Skill/Command 运行时从此文件解析 `DATA_HOME` 及各平台路径。

### 2.4 data 文件夹详细说明

```text
.
├── 🏗️ 10_Tasks/               # 【P】Actionable：活跃任务（聚焦任务执行）
│   ├── tasks.md                 # 任务清单，四象限管理任务
│   ├── tasks_archive.md         # 已完成任务清单
│   ├── TASK_WORKSPACE_YYYYMMDD_HHMMSS_XXX/     # 任务工作区目录（时间戳_XXX 格式）
│   │   └── task.md              # 任务数据, 承载任务记忆
│   └── ...
│
├── 🧠 20_Areas/                  # 【A】Responsibility：长期领域（聚焦知识沉淀，按金字塔流动）
│   ├── Projects/                 # 长期维护的项目
│   │   └── 01_xxx/               # 项目目录（01_xxx 格式）
│   ├── manual/                   # 受保护区：（AI 只读，人工按需删除/更新）
│   └── knowledge/                # 知识区：全域共用知识区（AI 只读，人工按需删除/更新）
│       ├── 01principles/            # 顶层原则层：被提炼的顶层智慧（方法论、原则、框架）
│       ├── 02playbooks/             # 上层应用层：被提炼的标准化流程（SOP、操作手册）
│       ├── 02templates/             # 上层应用层：可复用的模版和格式
│       ├── 02cases/                 # 上层应用层：具体案例和实例
│       └── 03notes/                 # 中层整理知识：被整理后的零散知识，按领域分类
│           ├── 01_python/           # Python 领域知识
│           ├── 02_算法设计/          # 算法设计领域知识
│           └── ...                  # 其他领域知识
│
├── 📚 30_Resources/              # 【R】Interests：原材料（聚焦第三方资料与文档）
│   └── Library/                 # 静态资料库（PDF、电子书、参考文档）
│
├── 🗄️ 40_Archives/               # 【A】Completed：归档区
│   ├── TASK_WORKSPACE_YYYYMMDD_HHMMSS_XXX/     # 归档任务工作区目录（时间戳_XXX 格式，保留完整结构）
│   └── ...
│
└── 📥 50_Raw/                    # 【Raw】统一素材区：新鲜素材捕捉起点（整理后应清空）
    ├── inbox/                   # 捕获的原子笔记（@pkm inbox 产出）
    ├── merged/                  # 合并后的素材（Organize 产出，待分类）
    └── ...                      # 其他待分类素材（Archive 回流、临时文件等）
```

### 2.5 skill 文件夹详细说明
```text
skill/
├── SKILL.md              # 主入口：统一路由，解析命令并调用对应模块
│
├── 【捕获流程】
│   └── _Inbox.md         # @pkm inbox：快速捕获碎片化信息到 50_Raw/inbox/
│
├── 【提炼流程（主流程）】
│   ├── _Verifier.md      # Verify：前置安全检查（目录结构、操作范围、写权限白名单）
│   ├── _Organizer.md    # Organize：合并同类内容到 50_Raw/merged/，分类归位，清空 50_Raw/（含可选插件预处理）
│   └── _Distiller.md    # Distill：深度整合、金字塔提炼、系统性检查，生成报告
│
├── 【智能咨询】
│   └── _Advisor.md       # @pkm advice：基于知识库回答问题，支持 scope 参数
│
├── 【任务管理】
│   └── _TaskManager.md   # @pkm task：管理待办任务，支持4象限管理
│
├── 【自管理】
│   └── _PkmSelfManager.md  # @pkm status / @pkm upgrade：查看当前状态、更新项目（git pull）
│
└── plugin/                 # Organizer 插件：按内容类型用模版预处理 50_Raw 条目（可选）
    ├── SKILL.md             # 插件注册表：插件名、匹配条件、模版文件
    ├── template_summary_problem.md   # 故障/问题总结模版
    └── template_meeting_minutes.md   # 会议纪要模版
```
### 2.6 command 文件夹详细说明

仅 **Cursor** 支持斜杠 Command；其他平台通过 Skill（`@pkm`）使用相同能力。

```text
command/
└── cursor/
    ├── pkm.md          # /pkm：主流程（Verify → Archive → Organize → Distill）
    ├── pkm.inbox.md    # /pkm.inbox：快速捕获到 inbox
    ├── pkm.advice.md   # /pkm.advice：智能咨询
    ├── pkm.help.md     # /pkm.help：帮助信息
    ├── pkm.task.md     # /pkm.task：任务管理
    ├── pkm.status.md   # /pkm.status：查看知识库信息
    └── pkm.upgrade.md  # /pkm.upgrade：更新 pkm 版本
```

---


## 三、 命令设计


**C.O.D.E 命令**：

| 命令 | 功能 | 说明 |
|------|------|------|
| `@pkm inbox <内容>` | 捕获流程 | 快速捕获碎片化信息到 inbox，默认不解析链接内容 |
| `@pkm inbox --parse <内容>` | 捕获流程 | 快速捕获碎片化信息到 inbox，：先解析链接内容，再捕获 |
| `@pkm advice <问题>` | 智能咨询 | 基于知识库回答问题 |
| `@pkm advice --scope <范围> <问题>` | 智能咨询 | scope 有三种：common、local、task，基于知识库回答问题，指定范围。common 表示使用 AI 通用知识，local 表示使用当前知识库，task 表示使用指定任务知识库 |
| `@pkm` | 主流程 | 智能整理：Verify → Archive → Organize → Distill |
| `@pkm help` | 帮助 | 显示帮助信息 |

**PKM 自管理**（由 `_PkmSelfManager.md` 实现）：

| 命令 | 功能 | 说明 |
|------|------|------|
| `@pkm status` | 查看状态 | 输出：配置文件内容、数据目录位置、知识库数量概况、项目列表（含已完成）、任务列表（含已完成）、PKM 版本、上次 pkm 执行时间、上次 pkm 总结报告简述 |
| `@pkm upgrade` | 更新pkm项目 | 在 PKM 安装目录（~/.pkm）执行 `git pull`，更新 skill 与 command |

**task 命令**：

| 命令 | 功能 | 说明 |
|------|------|------|
| `@pkm task add <内容>` | 添加 | 添加新任务，创建任务区 |
| `@pkm task ls` | 列表 | 列出所有任务 |
| `@pkm task ls --all` | 列表 | 列出所有任务,包含已经归档的任务 |
| `@pkm task use <id>` | 使用 | 切换到指定任务，并加载任务区信息 |
| `@pkm task edit <id>` | 编辑 | 编辑任务 |
| `@pkm task update <id>` | 更新 | 更新任务进展 |
| `@pkm task done <id>` | 完成 | 完成任务，追问总结（内容、收益、价值评分）并生成 `completed.md`（含需回流资料与知识清单） |
| `@pkm task delete <id>` | 删除 | 删除任务 |
| `@pkm task archive` | 归档 | 自动扫描所有任务工作空间，找出存在 `completed.md` 的（表示已完成），对其进行归档并回流知识到知识库 |

**project 命令**：

| 命令 | 功能 | 说明 |
|------|------|------|
| `@pkm project add <名称>` | 添加 | 在 areas 添加新的长期项目 |
| `@pkm project delete <project_name>` | 删除 | 删除项目 |
| `@pkm project ls` | 列表 | 列出所有长期项目 |

## 四、 工作流设计
### 4.1 捕获流程（Capture）

**命令**：`@pkm inbox <内容>`

| 参数 | 说明 |
|------|------|
| `<内容>` | 要捕获的内容 |
| `--parse` | 先解析链接内容，再捕获 |

**功能**：快速捕获碎片化信息到 inbox

**详细步骤**：
1. 接收用户输入的内容（文本、链接等）
2. 智能识别任务（包含动词、时间信息、具体目标等）
3. 如果是任务，推荐使用 `@pkm task` 命令
4. 如果不是任务，AI 简单总结内容，生成文件名（5-10字标题）
5. 智能处理链接（默认引用，`--parse` 模式抓取内容）
6. 保存到 `50_Raw/inbox/`，文件格式：`YYYYMMDD_HHMMSS_标题_inbox.md`

### 4.2 提炼流程（主流程）

**命令**：`@pkm`

**功能**：智能整理主流程，执行 Verify → Archive → Organize → Distill 四个阶段

**流程图**：
```text
@pkm
  ↓
🔍 Verify    # Verifier：前置安全检查
  ↓
🗄️ Archive   # 调用 @pkm task archive
  ↓
📦 Organize  # Organizer：合并、分类、归位
  ↓
💎 Distill   # Distiller：深度整合、金字塔提炼、系统性检查
  ↑______________________________________________|  闭环：后续再 Organize/Distill 可迭代优化
```

**详细步骤**：

#### Verify（前置安全检查）
- 定位知识库目录位置：`${DATA_HOME}`
- 检查 5 个顶级目录是否存在，缺失则自动创建
- 确认操作范围白名单（限定在知识库目录内）
- 生成写权限白名单（manual/ 只读）

#### Archive（归档回流）
- 调用 `@pkm task archive`：自动扫描所有任务工作空间，找出存在 `completed.md` 的（表示已完成），逐项执行归档与回流，详细步骤见任务管理章节

#### Organize（组织分类）
- 扫描 `50_Raw/`（包含 `inbox/` 和其他待分类素材）
- **可选插件预处理**：若存在 `skill/plugin/SKILL.md`，先按内容类型匹配插件（如故障总结、会议纪要），命中则用对应 `template_<类型>.md` 模版整理内容，再继续后续步骤
- 为了准确性，每次分类最多10个文件
- 按主题/类型合并同类内容到 `50_Raw/merged/`
- 判断类型（项目/知识/资料）和主题
- 分类归位：
  - 项目 → `20_Areas/Projects/<项目名称>` 将任务归档的对应的项目，如果没有对应项目 就忽略。
  - 知识 → `20_Areas/knowledge/03notes/<领域>/`（先放在 notes 层）
  - 资料 → `30_Resources/Library/`
- 整理完清理 已经分类的文件

#### Distill（提炼沉淀）
- 扫描各层新增/变动素材（只关注 `20_Areas/knowledge/03notes/`），
- 与已有知识深度整合（去重、交叉引用、结构化）
- 按金字塔原理提炼：
  - 零散知识（notes）+ areas 区的 manual 区(只读，不被自动改写) → 整理知识（notes 内按领域分类）
  - 整理知识 → 应用知识（knowledge/playbooks/templates/cases）
  - 应用知识 → 原则知识（knowledge/principles）
- 沉淀到对应目录：
  - `20_Areas/knowledge/03notes/<领域>/` → 整理后的知识
  - `20_Areas/knowledge/02playbooks/`、`02templates/`、`02cases/` → 应用层知识
  - `20_Areas/knowledge/01principles/` → 原则层知识
- 系统性检查：一致性、过时性、冗余、逻辑合理性
- 总结提炼结果，生成报告，保存到 `30_Resources/summary/`， 格式为 `YYYYMMDD_HHMMSS_标题_Distill.md`

- 整理 Project 区内容：
  - 扫描 `20_Areas/Projects/` 下的所有项目,对每个项目文件检查是否存在重复、冗余、一致性等问题，并进行整理。

- 扫描和整理时，为了精确，请控制规模，当改动的文件过多时，一次最多处理20个文件，下次再处理其他文件。

### 4.3 智能咨询（Advice）

**命令**：`@pkm advice <问题>`

| 参数 | 说明 |
|------|------|
| `<问题>` | 要咨询的问题 |
| `--scope <范围>` | 检索范围：common、local、task |

**功能**：基于知识库回答问题

**详细步骤**：
1. 根据 scope 参数确定检索范围（common/local/task）
2. 检索对应的知识库内容
3. 结合 AI 通用知识回答问题
4. 提供分类建议（如：笔记应该放到哪个目录）

**scope 参数**：
- `common`：仅使用 AI 通用知识
- `local`：仅检索当前知识库（10_Tasks、20_Areas、30_Resources、40_Archives）
- `<任务名>`：检索指定任务知识库（10_Tasks/<任务名>/）
- 默认：`common + local`（可叠加）

### 4.4 任务管理（Task）

**命令**：`@pkm task <操作> [参数]`

**功能**：管理任务，支持 4 象限管理方法，任务完成后自动创建知识回流

**详细步骤**：

#### 添加任务
- `@pkm task add <内容>`：添加新任务，**自动创建任务空间**
  - 交互式补全信息：想法、4象限、计划完成时间、**工作量**（人小时/人天/人月）、计划、实现思路
  - 自动在任务清单里 `tasks.md` 里添加任务元数据
- 自动创建任务目录：`10_Tasks/TASK_WORKSPACE_YYYYMMDD_HHMMSS_xxx/`
  - `task.md`：任务详细数据（承载任务记忆）

#### 列表查看
- `@pkm task ls`：列出所有任务（**按计划完成时间排序**，按 4 象限分组显示，支持筛选）
- `@pkm task ls --all`：列出所有任务，包含已归档
- 显示**计划完成时间**、**工作量**、进展核查与延期风险提示（超期任务高亮）

#### 切换任务
- `@pkm task use <id>`：切换到指定任务，加载任务区信息
- 切换后，后续操作默认在该任务上下文执行

#### 编辑任务
- `@pkm task edit <id>`：编辑任务内容
- `@pkm task update <id>`：更新任务进展（记录日期 + 一句话进展）

#### 完成/归档
- `@pkm task done <id>`：完成任务，追问总结：内容、收益、价值评分，并生成完成总结文件 `completed.md`，里面还包含需要回流的资料和知识清单。
- `@pkm task archive`：**自动扫描所有任务工作空间**，找出存在 `completed.md` 的（表示已完成），对其进行归档并**回流知识到知识库**。对每个已完成的任务：
  - 扫描该任务目录中的内容，主要是资料和知识，先了解该任务。
  - 根据 `completed.md` 中的内容，提取可复用知识 → `20_Areas/knowledge/`，项目相关的就提取到 `20_Areas/Projects/<项目名称>/`。
  - 任务目录移至 `40_Archives/`
- `@pkm task delete <id>`：删除任务

**4 象限管理**：
- 🔴 第一象限：重要且紧急
- 🟡 第二象限：重要但不紧急
- 🟠 第三象限：不重要但紧急
- 🟢 第四象限：不重要且不紧急

#### tasks.md 的结构设计

**位置**：`10_Tasks/tasks.md`
**用途**：任务清单索引，按 4 象限组织进行中任务，供 `@pkm task ls` 等使用。**详细数据仅存于各任务工作空间下的 `task.md`**，此处仅保留最小索引以减少重复。

**结构**：

- **文档头**：标题「任务清单」、最后更新时间。
- **按 4 象限分组**：
  - 第一象限：重要且紧急
  - 第二象限：重要但不紧急
  - 第三象限：不重要但紧急
  - 第四象限：不重要且不紧急
- **每条任务**（仅索引字段，详情见对应 `task.md`）：
  - 状态：`[进行中]`
  - 任务 ID：`T-YYYYMMDD-HHMMSS-序号`
  - 标题（简短）
  - **工作空间路径**：`TASK_WORKSPACE_YYYYMMDD_HHMMSS_xxx/`（该目录下的 `task.md` 为任务完整数据）
  - 4 象限（用于分组展示）
  - 计划完成时间（用于排序和提醒）
  - 工作量（人小时/人天/人月）

**已完成任务**：从 `tasks.md` 移除后，写入 `10_Tasks/tasks_archive.md`，每条仅保留：状态 `[已完成]`、任务 ID、标题、完成时间、完成总结摘要（可选 4 象限）；详情见归档目录中的 `task.md` / `completed.md`。

#### task.md 的结构设计

**位置**：`10_Tasks/TASK_WORKSPACE_YYYYMMDD_HHMMSS_xxx/task.md`
**用途**：单任务的详细数据，承载任务记忆，与该任务工作空间一一对应。

**结构**：

- **元数据**（权威数据源，tasks.md 仅存索引）：任务 ID、标题、创建时间、**计划完成时间**、**工作量**（人小时/人天/人月）、4 象限、分类、优先级、标签。
- **想法/目标**：任务的核心想法或目标（完整内容）。
- **计划**：实现计划或步骤（完整内容）。
- **实现思路**：技术实现思路或方法（完整内容）。
- **关联项目**：`20_Areas/Projects/<项目名称>/`（可选）。
- **进展记录**：按时间顺序的完整记录，每条为「日期 + 时间 - 一句话进展」。
- **其他关联**：关联的代码库(含位置信息，可选)
- **其他**：任务执行过程中产生的子文档、链接等可放在同工作空间目录下，在 task.md 中可引用。

**完成任务时**：在同一工作空间下生成 `completed.md`，包含：完成时间、内容摘要、收益、价值评分（1–10）、需回流的资料与知识清单（供 `@pkm task archive` 使用）。`@pkm task archive` 会扫描所有任务工作空间，发现存在 `completed.md` 的即对该任务执行归档：整目录移至 `40_Archives/`，并依 completed.md 回流知识到 `20_Areas/knowledge/` 与 `20_Areas/Projects/`。

### 4.5 自管理（Status / Upgrade）

由 `_PkmSelfManager.md` 实现，用于查看当前运行状态与更新 PKM 项目。

**命令**：`@pkm status`、`@pkm upgrade`

#### status（查看状态）
- 输出**配置文件**：`~/.pkm/.config` 中的配置项（如 DATA_HOME、各平台 HOME）
- 输出**数据目录位置**：当前知识库根路径（由 DATA_HOME 决定）
- 输出**知识库数量概况**：10_Tasks / 20_Areas / 30_Resources / 40_Archives / 50_Raw 下的条目或文件数量概况
- 输出**任务列表**：待办与已完成任务 引用 `@pkm task ls 和 @pkm task ls --all`
- 输出**长期项目列表**：20_Areas/Projects/ 下的长期项目 引用 `@pkm project ls`
- 输出**PKM 版本**：当前安装的 PKM 版本（如 git 的 commit 或 tag）
- 输出**上次 pkm 执行时间**：最近一次执行主流程（或主要命令）的时间
- 输出**上次 pkm 总结报告简述**：最近一次主流程（如 Distill）产生的总结报告的简要概括

#### upgrade（更新项目）
- 在 PKM 安装目录（默认 `~/.pkm`）执行 `git pull`
- 更新 skill 与 command，无需重新安装


## 五、 skill 结构设计

Skill 文件是驱动 CODE 流程的"引擎程序"，位于 `skill/` 目录下。

### 5.1 Skill 文件组织

Skill 文件按照工作流设计组织，每个文件对应一个明确的职责：

```text
skill/
├── SKILL.md              # 主入口：统一路由，解析命令并调用对应模块
│
├── 【捕获流程】
│   └── _Inbox.md         # @pkm inbox：快速捕获碎片化信息到 50_Raw/inbox/
│
├── 【提炼流程（主流程）】
│   ├── _Verifier.md      # Verify：前置安全检查（目录结构、操作范围、写权限白名单）
│   ├── _Organizer.md    # Organize：合并同类内容到 50_Raw/merged/，分类归位，清空 50_Raw/（含可选插件预处理）
│   └── _Distiller.md    # Distill：深度整合、金字塔提炼、系统性检查，生成报告
│
├── 【智能咨询】
│   └── _Advisor.md       # @pkm advice：基于知识库回答问题，支持 scope 参数
│
├── 【任务管理】
│   └── _TaskManager.md   # @pkm task：管理任务，支持4象限管理，自动创建任务空间
│
├── 【长期项目管理】
│   └── _ProjectManager.md # @pkm project：管理 20_Areas/Projects/ 下的长期项目
│
├── 【帮助信息】
│   └── _Help.md           # @pkm help：显示帮助信息
│
├── 【自管理】
│   └── _PkmSelfManager.md  # @pkm status / @pkm upgrade：查看当前状态、更新项目（git pull）
│
└── plugin/                 # Organizer 插件：按内容类型用模版预处理 50_Raw 条目（可选）
     ├── SKILL.md             # 插件注册表：插件名、匹配条件、模版文件
     ├── template_summary_problem.md   # 故障/问题总结模版
     └── template_meeting_minutes.md   # 会议纪要模版
```

### 5.2 Skill 文件职责

| Skill 文件 | 对应工作流 | 触发方式 | 核心功能 |
|-----------|----------|---------|---------|
| `SKILL.md` | 统一入口 | `@pkm` | 解析命令，路由到对应模块 |
| `_Inbox.md` | 捕获流程 | `@pkm inbox` | 快速捕获碎片化信息，生成原子笔记到 `50_Raw/inbox/`（格式：`YYYYMMDD_HHMMSS_标题_inbox.md`） |
| `_Verifier.md` | 提炼流程-Verify | 自动（任何操作前） | 检查 5 个顶级目录是否存在，缺失则自动创建；确认操作范围白名单；生成写权限白名单（manual/ 只读） |
| `_Organizer.md` | 提炼流程-Organize | `@pkm` 主流程 | 扫描 `50_Raw/`（包含 `inbox/` 和其他待分类素材）；**可选插件预处理**：若存在 `plugin/SKILL.md`，先按内容类型匹配插件（如故障、会议纪要），命中则用对应 `template_<类型>.md` 模版整理内容；按主题/类型合并同类内容到 `50_Raw/merged/`；为了准确性，每次分类最多10个文件；判断类型（项目/知识/资料）和主题；分类归位：项目→`20_Areas/Projects/<项目名称>`（如有关联项目），知识→`20_Areas/knowledge/03notes/<领域>/`，资料→`30_Resources/Library/`；整理完清理已经分类的文件 |
| `_Distiller.md` | 提炼流程-Distill | `@pkm` 主流程 | 扫描各层新增/变动素材（只关注 `20_Areas/knowledge/03notes/`）；与已有知识深度整合（去重、交叉引用、结构化）；按金字塔原理提炼：零散知识（notes）+ areas 区的 manual 区 → 整理知识 → 应用知识（knowledge/playbooks/templates/cases）→ 原则知识（knowledge/principles）；沉淀到对应目录；系统性检查（一致性、过时性、冗余、逻辑合理性）；生成报告到 `30_Resources/summary/`（格式：`YYYYMMDD_HHMMSS_标题_Distill.md`）；整理 Project 区内容：扫描 `20_Areas/Projects/` 下的所有项目,对每个项目文件检查是否存在重复、冗余、一致性等问题，并进行整理。 |
| `_Advisor.md` | 智能咨询 | `@pkm advice` | 根据 scope 参数确定检索范围（common/local/task）；检索对应的知识库内容；结合 AI 通用知识回答问题；提供分类建议 |
| `_TaskManager.md` | 任务管理 | `@pkm task` | 管理任务，支持 4 象限管理；add（自动创建任务空间）/ls/use/edit/update/done/delete/archive；任务空间：`10_Tasks/TASK_WORKSPACE_YYYYMMDD_HHMMSS_xxx/` + `task.md`；archive 时回流知识到 `20_Areas/knowledge/` 和 `20_Areas/Projects/` |
| `_ProjectManager.md` | 长期项目管理 | `@pkm project` | 管理 `20_Areas/Projects/` 下的长期项目；add/delete/ls |
| `_Help.md` | 帮助信息 | `@pkm help` | 显示完整帮助信息，包括所有命令列表、使用示例、数据存储路径等 |
| `_PkmSelfManager.md` | 自管理 | `@pkm status` / `@pkm upgrade` | **status**：输出配置文件、数据目录、知识库概况、任务列表、长期项目列表、PKM 版本、上次 pkm 执行时间、上次 pkm 总结报告简述；**upgrade**：在 ~/.pkm 执行 `git pull` 更新项目 |

### 5.3 Skill 文件设计原则

- **单一职责**：每个 Skill 文件只负责一个特定功能，职责边界清晰，避免功能重叠
- **统一入口**：所有命令通过 `SKILL.md` 统一路由，简化用户接口，降低使用门槛
- **安全前置**：所有操作前必须调用 `_Verifier.md` 验证，确保操作范围和安全，防止越界写入
- **模块化**：各模块独立，便于维护、测试和扩展，符合设计原则中的"简化优先"
- **可组合**：主流程（提炼流程）通过组合 Verify → Archive → Organize → Distill 实现完整功能
- **流程对应**：Skill 文件组织与工作流设计一一对应（捕获流程、提炼流程、智能咨询、任务管理、长期项目管理），便于理解和维护
- **渐进提炼**：`_Distiller.md` 模块体现金字塔原理，实现从零散知识（notes）→ 整理知识 → 应用知识（knowledge/playbooks/templates/cases）→ 原则知识（knowledge/principles）的渐进式提炼
- **信任 AI**：默认允许 AI 自动落地，符合设计原则中的"信任为主"，人工负责后期纠偏

### 5.4 Organizer 插件（plugin，可选）

在 Organize 阶段，若存在 `skill/plugin/` 目录，则在对 50_Raw 中每个文件做类型判断之前，先按**内容类型**用**自定义模版**做一次结构化整理。

- **plugin/SKILL.md**：插件注册表，列出插件名、匹配条件（内容特征）、模版文件名
- **模版文件**：命名格式 `template_<内容类型>.md`，定义该类型的字段与格式，供 AI 从原文抽取并填充
- **内置模版**：`template_summary_problem.md`（故障/问题总结）、`template_meeting_minutes.md`（会议纪要）
- **执行顺序**：扫描 50_Raw → 插件预处理（匹配则按模版整理）→ 合并同类 → 分类归位


## 六、 部署设计

### 6.1 部署原则

- **全局安装**：Skills、Commands、知识数据统一放在一处（默认 `~/.pkm/`）
- **安装方式**：用户将项目 clone 到 `~/.pkm`，配置写在 `~/.pkm/.config`
- **平台链接**：各 AI 平台通过软链接指向 `~/.pkm` 下的 skill/command，避免重复拷贝

### 6.2 知识库的初始化

采用 **git clone 到目标目录** 的方式安装，目标目录即 PKM 根目录（默认 `~/.pkm`）。

```bash
# 将项目克隆到 ~/.pkm（若已存在请先备份或换用其他目录）
git clone https://github.com/EvilJoker/pkmskill.git ~/.pkm
```

克隆完成后，仓库根目录即作为 `~/.pkm` 使用，其中应包含 `data/`、`skill/`、`command/`、`.config` 等（可由安装脚本初始化或由仓库自带）。

### 6.3 项目更新

```bash
git pull
```

### 6.3 配置文件

**配置文件位置**：`~/.pkm/.config`

```bash
# 知识数据目录（PARA 10_50 所在目录）
DATA_HOME="/home/user/.pkm/data"

# 各平台安装目录（用于软链接目标，可选）
CURSOR_HOME="/home/user/.cursor/"
CLAUDE_HOME="/home/user/.claude/"
GEMINI_HOME="/home/user/.gemini/"
OPENCLAW_HOME="/home/user/.openclaw/"
```

**读取逻辑**：
- Skill/Command 执行时读取 `~/.pkm/.config` 中的 `DATA_HOME` 等
- PKM 根目录可由 `DATA_HOME` 的上级目录推导（如 `DATA_HOME=/home/user/.pkm/data` 则根目录为 `/home/user/.pkm`）
- 若配置文件不存在，默认使用 `~/.pkm` 为根目录、`~/.pkm/data` 为数据目录
- 安装时可由 `.config.template` 复制为 `.config` 后按需修改

### 6.4 安装到各平台（软链接到全局）

通过**软链接**将 `~/.pkm` 下的 skill/command 链到各平台**官方约定的全局目录**，无需拷贝，便于 `git pull` 统一更新。以下按各平台当前能力编写，仅支持 Skill 的只链 Skill，同时支持 Command 的再链 Command。

| 平台 | 支持 Command | 支持 Skill | 全局路径（默认） |
|------|---------------|------------|------------------|
| Cursor | ✅ `~/.cursor/commands/` | ✅ `~/.cursor/skills/` | `~/.cursor` |
| Claude Code | ❌（斜杠命令由 Skill 提供） | ✅ `~/.claude/skills/` | `~/.claude` |
| Gemini CLI | ❌ | ✅ `~/.gemini/skills/` | `~/.gemini` |
| OpenCLAW | ❌ | ✅ `~/.openclaw/skills/` | `~/.openclaw` |

一键式安装脚本：
```bash
./install.sh
```

安装的具体流程如下

#### Cursor

**平台特性**（[Cursor 文档](https://cursor.com/docs/context/skills)）：
- **Skills**：用户级全局目录为 `~/.cursor/skills/`，每个 Skill 为子目录且内含 `SKILL.md`，启动时自动发现，可用 `@` 或 `/` 唤起。
- **Commands**：用户级全局目录为 `~/.cursor/commands/`，单文件（如 `pkm.md`）即一条斜杠命令。
→ 同时支持 **Command** 与 **Skill**，需分别软链接。

**链接关系**：
- Commands：`~/.pkm/command/cursor/*.md` → `~/.cursor/commands/` 下同名文件（含 `pkm.md`、`pkm.inbox.md`、`pkm.advice.md`、`pkm.help.md`、`pkm.task.md`、`pkm.project.md`、`pkm.status.md`、`pkm.upgrade.md`）
- Skill：`~/.pkm/skill` → `~/.cursor/skills/PKM`（PKM 为技能目录名，内含 `SKILL.md`）

**命令**（路径可按 `.config` 中的 `CURSOR_HOME` 调整，默认 `~/.cursor`）：
```bash
mkdir -p ~/.cursor/commands ~/.cursor/skills
ln -sf ~/.pkm/command/cursor/pkm.md ~/.cursor/commands/pkm.md
ln -sf ~/.pkm/command/cursor/pkm.inbox.md ~/.cursor/commands/pkm.inbox.md
ln -sf ~/.pkm/command/cursor/pkm.advice.md ~/.cursor/commands/pkm.advice.md
ln -sf ~/.pkm/command/cursor/pkm.help.md ~/.cursor/commands/pkm.help.md
ln -sf ~/.pkm/command/cursor/pkm.task.md ~/.cursor/commands/pkm.task.md
ln -sf ~/.pkm/command/cursor/pkm.project.md ~/.cursor/commands/pkm.project.md
ln -sf ~/.pkm/command/cursor/pkm.status.md ~/.cursor/commands/pkm.status.md
ln -sf ~/.pkm/command/cursor/pkm.upgrade.md ~/.cursor/commands/pkm.upgrade.md
ln -sf ~/.pkm/skill ~/.cursor/skills/PKM
```

**使用**：在 Cursor 中可用 `@pkm`（Skill）或斜杠命令：`/pkm`、`/pkm.inbox`、`/pkm.advice`、`/pkm.help`、`/pkm.task`、`/pkm.project`、`/pkm.status`、`/pkm.upgrade`。

#### Claude Code

**平台特性**（[Claude Code 文档](https://code.claude.com/docs/en/skills)）：
- **Skills**：个人全局目录为 `~/.claude/skills/<技能名>/`，每技能一目录且内含 `SKILL.md`；支持 `/技能名` 斜杠命令，由 Skill 提供（Custom slash commands 已合并进 Skills）。
- 无独立的「Commands」目录，斜杠命令即 Skill 的显式唤起。
→ 仅需安装 **Skill**，无需单独 Command 链接。

**链接关系**：
- Skill：`~/.pkm/skill` → `~/.claude/skills/pkm`（即 `~/.claude/skills/pkm/SKILL.md` 由该链接指向）

**命令**（路径按 `.config` 中的 `CLAUDE_HOME` 调整，默认 `~/.claude`）：
```bash
mkdir -p ~/.claude/skills
ln -sf ~/.pkm/skill ~/.claude/skills/pkm
```

**使用**：在 Claude Code 中 `/pkm` 或由 Claude 在对话中按需调用 PKM Skill。

#### Gemini CLI

**平台特性**（[Gemini CLI 文档](https://geminicli.com/docs/cli/skills)）：
- **Skills**：用户级目录为 `~/.gemini/skills/`，每个 Skill 为子目录（含 `SKILL.md`）；无独立 Commands，能力均通过 Skills 扩展。
→ 仅支持 **Skill**，软链接到用户 Skills 目录即可。也可用 `gemini skills link ~/.pkm` 等官方方式挂载。

**链接关系**：
- Skill：`~/.pkm/skill` → `~/.gemini/skills/pkm`

**命令**（路径按 `.config` 中的 `GEMINI_HOME` 调整，默认 `~/.gemini`）：
```bash
mkdir -p ~/.gemini/skills
ln -sf ~/.pkm/skill ~/.gemini/skills/pkm
```

**使用**：在 Gemini CLI 交互中由模型按描述匹配并激活 PKM Skill，或通过 `/skills` 相关命令管理。

#### OpenCLAW

**平台特性**（[OpenCLAW 文档](https://docs.openclaw.ai/clawdhub)等）：
- **Skills**：本地/用户级目录为 `~/.openclaw/skills/`，每个 Skill 为子目录（含 `SKILL.md`）；可通过 ClawHub 安装，也支持本地目录。
→ 仅支持 **Skill**，无独立 Commands。

**链接关系**：
- Skill：`~/.pkm/skill` → `~/.openclaw/skills/pkm`

**命令**（路径按 `.config` 中的 `OPENCLAW_HOME` 调整，默认 `~/.openclaw`）：
```bash
mkdir -p ~/.openclaw/skills
ln -sf ~/.pkm/skill ~/.openclaw/skills/pkm
```

**使用**：在 OpenCLAW 中按平台约定发现并调用 PKM Skill。

---

**更新**：在 `~/.pkm` 目录下执行 `git pull` 即可更新。