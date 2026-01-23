# 知识管理系统架构方案

这套方案的核心目标是构建一个**"自清洁、自进化"**的知识系统。它将你从琐碎的文件搬运中解放出来，让你专注于最核心的"思考"与"验证"。

以下是基于 **Cursor/Claude Code/Gemini CLI + Git + PARA + CODE** 的全套管理方案：

---

## 一、 设计

### 1.0 设计原则

- 简单至上：不追求繁琐的流程，保证核心的机制简单易用。
- 相信AI: 相信AI的能力，将判断和决策交给AI，用户负责后期纠偏，保证流程的自动化。
- 渐进提炼: 从碎片到知识，从知识到经验，是渐进式提炼的过程。

### 1.1 CODE 信息管理法则

**CODE 是解决知识的捕获、组织、蒸馏、表达的闭环流程**：

- **Capture（捕获）**：快速捕获碎片化信息到 `50_Raw/inbox/`，降低捕获门槛。
- **Organize（组织）**：对素材进行合并、分类、归位，实现智能分流。
- **Distill（提炼）**：深度整合、去重、结构化，沉淀为可复用知识。
- **Express（表达）**：通过智能咨询、项目归档等方式输出应用知识。

### 1.2 PARA 结构

**PARA 是解决顶层组织逻辑，让知识按时间维度自然流动**：

- **10_Projects（项目）**：有明确截止日期的任务。聚焦任务的执行。
- **20_Areas（领域）**：长期关注的责任领域。聚焦知识的沉淀。
- **30_Resources（资源）**：感兴趣但暂未深度加工的素材。聚焦第三方的资料与文档。
- **40_Archives（归档）**：已完成的项目和不再活跃的领域。定期清理，保持系统轻量。
- **50_Raw（素材区）**：自定义的新鲜素材区, 统一的新鲜素材捕捉起点，包含 inbox 和待分类的碎片。整理后应清空。

### 1.3 金字塔流动

**流动聚焦 20_Areas的组织逻辑， 实现从零散到凝练的渐进式提炼**：

人类的知识第一界别是凝练的 "经验"，其次才是零散的 "知识"。类似DIKW模型，从知识到经验，是渐进式提炼的过程。

- **顶层（原则层）**：Principles（方法论、原则、框架），最凝练的经验总结。
- **上层（应用层）**：Playbooks（标准化流程）、Templates（可复用模版）、Cases（具体案例）。
- **中层（整理知识）**：聚焦各个领域的知识，是整理过后的知识，是知识的集合。
- **底层（零散知识）**：粗糙的、新鲜的、碎片化的、未被整理的知识。

知识流动方向：零散知识 → 整理知识 → 应用知识 → 原则知识，通过 Distill 过程实现自下而上的提炼和自组织。


## 二、 目录架构 (The Physical Layout)

```text
.
├── 🏗️ 10_Projects/               # 【P】Actionable：活跃项目（聚焦任务执行）
│   ├── YYYYMMDD_HHMMSS_XXX/     # 项目目录（时间戳_XXX 格式）
│   │   └── manual/              # 受保护区：项目金标准、架构决策（AI 只读，人工维护）
│   └── ...
│
├── 🧠 20_Areas/                  # 【A】Responsibility：长期领域（聚焦知识沉淀，按金字塔流动）
│   ├── manual/                  # 受保护区：全域共用素材区（AI 只读，人工按需删除/更新）
│   ├── 01principles/            # 顶层原则层：被提炼的顶层智慧（方法论、原则、框架）
│   ├── 02playbooks/             # 上层应用层：被提炼的标准化流程（SOP、操作手册）
│   ├── 02templates/             # 上层应用层：可复用的模版和格式
│   ├── 02cases/                 # 上层应用层：具体案例和实例
│   └── 03notes/                 # 中层整理知识：被整理后的零散知识，按领域分类
│       ├── 01_python/           # Python 领域知识
│       ├── 02_算法设计/          # 算法设计领域知识
│       └── ...                  # 其他领域知识
│
├── 📚 30_Resources/              # 【R】Interests：原材料（聚焦第三方资料与文档）
│   ├── Library/                 # 静态资料库（PDF、电子书、参考文档）
│   ├── todo.md                  # 待办任务列表
│   └── todo_archive.md          # 已完成任务归档
│
├── 🗄️ 40_Archives/               # 【A】Completed：归档区
│   ├── YYYYMMDD_HHMMSS_XXX/     # 归档项目目录（时间戳_XXX 格式，保留完整结构）
│   └── ...
│
└── 📥 50_Raw/                    # 【Raw】统一素材区：新鲜素材捕捉起点（整理后应清空）
    ├── inbox/                   # 捕获的原子笔记（@pkm inbox 产出）
    ├── merged/                  # 合并后的素材（Organize 产出，待分类）
    └── ...                      # 其他待分类素材（Archive 回流、临时文件等）
```

## 三、 工作流设计

### 3.1 捕获流程（Capture）

**命令**：`@pkm inbox <内容>`

**功能**：快速捕获碎片化信息，生成原子笔记

**流程**：
1. 接收用户输入的内容（文本、链接等）
2. 智能识别任务（包含动词、时间信息、具体目标等）
3. 如果是任务，推荐使用 `@pkm todo` 命令
4. 如果不是任务，AI 简单总结内容，生成文件名（5-10字标题）
5. 智能处理链接（默认引用，`--online` 模式抓取内容）
6. 保存到 `50_Raw/inbox/`，文件格式：`YYYYMMDD_HHMMSS_标题_inbox.md`

**效果**：极简操作，一条命令快速捕获，AI 自动生成文件名，智能识别任务。

### 3.2 提炼流程（主流程）

**命令**：`@pkm`

**功能**：智能整理主流程，执行 Verify → Archive → Organize → Distill 四个阶段

**流程图**：
```text
@pkm
  ↓
🔍 Verify    # Verifier：前置安全检查
  ↓
🗄️ Archive   # Archiver：归档已完成项目，提取可复用知识
  ↓
📦 Organize  # Organizer：合并、分类、归位
  ↓
💎 Distill   # Distiller：深度整合、金字塔提炼、系统性检查
  ↑______________________________________________|  闭环：后续再 Organize/Distill 可迭代优化
```

**详细步骤**：

#### Verify（前置安全检查）
- 检查 6 个顶级目录（10_Projects/、20_Areas/、30_Resources/、40_Archives/、50_Raw/、.pkm/）是否存在且结构完整
- 确认操作范围白名单（限定在知识库目录内）
- 生成写权限白名单（manual/ 只读）
- 验证失败则立即中止后续流程

#### Archive（归档回流）
- 扫描 `10_Projects/` 识别已完成项目（存在 `COMPLETED.md` 标记）
- 将项目整体移至 `40_Archives/<YYYY>/` 保留完整目录结构
- 从项目 提取可复用知识（架构模式、解决方案、经验总结、资料等）包括manual区，放置到 `50_Raw/`

#### Organize（组织分类）
- 扫描 `50_Raw/`（包含 `inbox/` 和其他待分类素材）
- 按主题/类型合并同类内容到 `50_Raw/merged/`
- 判断类型（任务/知识/资料）和主题
- 分类归位：
  - 任务 → `10_Projects/`
  - 知识 → `20_Areas/03notes/<领域>/`（先放在 notes 层）
  - 资料 → `30_Resources/Library/`
- 整理完清空 `50_Raw/`

#### Distill（提炼沉淀）
- 扫描各层新增/变动素材（只关注 `20_Areas/03notes/`）
- 与已有知识深度整合（去重、交叉引用、结构化）
- 按金字塔原理提炼：
  - 零散知识（notes）+ areas 区的 manual 区(只读，不被自动改写) → 整理知识（notes 内按领域分类）
  - 整理知识 → 应用知识（playbooks/templates/cases）
  - 应用知识 → 原则知识（principles）
- 沉淀到对应目录：
  - `20_Areas/03notes/<领域>/` → 整理后的知识
  - `20_Areas/02playbooks/`、`02templates/`、`02cases/` → 应用层知识
  - `20_Areas/01principles/` → 原则层知识
- 系统性检查：一致性、过时性、冗余、逻辑合理性
- 总结提炼结果，生成报告，保存到 `30_Resources/summary/`， 格式为 `YYYYMMDD_HHMMSS_标题_Distill.md`

### 3.3 Express 暴露流程

**命令**：`@pkm advice <问题> [--scope <范围>]`

**功能**：智能咨询/输出，基于知识库回答问题

**流程**：
1. 根据 scope 参数确定检索范围（common/local/项目名）
2. 检索对应的知识库内容
3. 结合 AI 通用知识回答问题
4. 提供分类建议（如：笔记应该放到哪个目录）

**scope 参数**：
- `common`：仅使用 AI 通用知识
- `local`：仅检索当前知识库（10_Projects、20_Areas、30_Resources、40_Archives）
- `<项目名>`：检索指定项目知识库（10_Projects/<项目名>/）
- 默认：`common + local`（可叠加）

**效果**：充分利用知识库，提供精准的咨询和建议。

### 3.4 Todo 扩展流程（任务管理）

**命令**：`@pkm todo [操作] [参数]`

**功能**：管理待办任务，支持 4 象限管理方法

**操作**：
- `@pkm todo add <内容>`：添加新任务（可选[add]，交互式补全信息：想法、4象限、计划、实现思路、关联项目）
- `@pkm todo list`：列出所有任务（按 4 象限分组显示，支持筛选）
- `@pkm todo update <id/name>`：更新任务进展（记录日期 + 一句话进展）
- `@pkm todo ok <id/name>`：完成任务（追问总结：内容、收益、价值评分，归档到 todo_archive.md）
- `@pkm todo del <id/name>`：删除任务

**4 象限管理**：
- 🔴 第一象限：重要且紧急
- 🟡 第二象限：重要但不紧急
- 🟠 第三象限：不重要但紧急
- 🟢 第四象限：不重要且不紧急

**效果**：统一管理待办任务，支持优先级分类，便于追踪和回顾。

## 四、 具体实现：Skill 文件结构

Skill 文件是驱动 CODE 流程的"引擎程序"，位于 `.pkm/Skills/PKM/` 目录下。

### 4.1 Skill 文件组织

Skill 文件按照工作流设计组织，每个文件对应一个明确的职责：

```text
.pkm/Skills/PKM/
├── Skill.md              # 主入口：统一路由，解析命令并调用对应模块
│
├── 【捕获流程】
│   └── _Inbox.md         # 快速捕获碎片化信息到 50_Raw/inbox/
│
├── 【提炼流程（主流程）】
│   ├── _Verifier.md      # Verify：前置安全检查（目录结构、操作范围、写权限白名单）
│   ├── _Archiver.md      # Archive：归档已完成项目，提取可复用知识到 50_Raw/
│   ├── _Organizer.md     # Organize：合并同类内容到 50_Raw/merged/，分类归位，清空 50_Raw/
│   └── _Distiller.md     # Distill：深度整合、金字塔提炼、系统性检查，生成报告
│
├── 【Express 流程】
│   └── _Advisor.md       # 基于知识库回答问题，支持 scope 参数
│
└── 【扩展功能】
    ├── _ProjectCreator.md  # 创建新项目目录（时间戳_XXX）
    └── _TodoManager.md     # 管理待办任务，支持4象限管理
```

### 4.2 Skill 文件职责

| Skill 文件 | 对应工作流 | 触发方式 | 核心功能 |
|-----------|----------|---------|---------|
| `Skill.md` | 统一入口 | `@pkm` | 解析命令，路由到对应模块 |
| `_Inbox.md` | 捕获流程 | `@pkm inbox` | 快速捕获碎片化信息，生成原子笔记到 `50_Raw/inbox/`（格式：`YYYYMMDD_HHMMSS_标题_inbox.md`） |
| `_Verifier.md` | 提炼流程-Verify | 自动（任何操作前） | 检查 6 个顶级目录（10_Projects/、20_Areas/、30_Resources/、40_Archives/、50_Raw/、.pkm/）是否存在且结构完整；确认操作范围白名单；生成写权限白名单（manual/ 只读）；验证失败则立即中止 |
| `_Archiver.md` | 提炼流程-Archive | `@pkm` 主流程 | 扫描 `10_Projects/` 识别已完成项目（存在 `COMPLETED.md` 标记）；将项目整体移至 `40_Archives/<YYYY>/` 保留完整目录结构；从项目提取可复用知识（架构模式、解决方案、经验总结、资料等）包括 manual 区，放置到 `50_Raw/` |
| `_Organizer.md` | 提炼流程-Organize | `@pkm` 主流程 | 扫描 `50_Raw/`（包含 `inbox/` 和其他待分类素材）；按主题/类型合并同类内容到 `50_Raw/merged/`；判断类型（任务/知识/资料）和主题；分类归位：任务→`10_Projects/`，知识→`20_Areas/03notes/<领域>/`，资料→`30_Resources/Library/`；整理完清空 `50_Raw/` |
| `_Distiller.md` | 提炼流程-Distill | `@pkm` 主流程 | 扫描各层新增/变动素材（只关注 `20_Areas/03notes/`）；与已有知识深度整合（去重、交叉引用、结构化）；按金字塔原理提炼：零散知识（notes）+ areas 区的 manual 区 → 整理知识 → 应用知识（playbooks/templates/cases）→ 原则知识（principles）；沉淀到对应目录；系统性检查（一致性、过时性、冗余、逻辑合理性）；生成报告到 `30_Resources/summary/`（格式：`YYYYMMDD_HHMMSS_标题_Distill.md`） |
| `_Advisor.md` | Express 流程 | `@pkm advice` | 根据 scope 参数确定检索范围（common/local/项目名）；检索对应的知识库内容；结合 AI 通用知识回答问题；提供分类建议 |
| `_ProjectCreator.md` | 扩展功能 | `@pkm addProject` | 自动生成项目目录名：`YYYYMMDD_HHMMSS_XXX`（时间戳在前，固定后缀 XXX）；在 `10_Projects/` 下创建目录；初始化项目模版结构（manual/） |
| `_TodoManager.md` | Todo 扩展流程 | `@pkm todo` | 管理待办任务，支持4象限管理；添加任务（可选 [add]）、列出任务、更新任务、完成任务、删除任务；写入 `30_Resources/todo.md`，归档到 `todo_archive.md` |

### 4.3 Skill 文件设计原则

- **单一职责**：每个 Skill 文件只负责一个特定功能，职责边界清晰，避免功能重叠
- **统一入口**：所有命令通过 `Skill.md` 统一路由，简化用户接口，降低使用门槛
- **安全前置**：所有操作前必须调用 `_Verifier.md` 验证，确保操作范围和安全，防止越界写入
- **模块化**：各模块独立，便于维护、测试和扩展，符合设计原则中的"简化优先"
- **可组合**：主流程（提炼流程）通过组合 Verify → Archive → Organize → Distill 实现完整功能，体现 CODE 流程
- **流程对应**：Skill 文件组织与工作流设计一一对应（捕获流程、提炼流程、Express 流程、扩展功能），便于理解和维护
- **渐进提炼**：`_Distiller.md` 模块体现金字塔原理，实现从零散知识（notes）→ 整理知识 → 应用知识（playbooks/templates/cases）→ 原则知识（principles）的渐进式提炼
- **信任 AI**：默认允许 AI 自动落地，符合设计原则中的"信任为主"，人工负责后期纠偏


## 六、 COMMAND 设计

`@pkm` 是知识管理系统的统一命令入口，通过简单的命令驱动整个 CODE 流程。

### 6.1 命令分类

**主流程命令**：
- `@pkm`：智能整理主流程，自动执行 Verify → Archive → Organize → Distill 四个阶段

**独立流程命令**：
- `@pkm inbox <内容>`：捕获流程，快速捕获碎片化信息到 `50_Raw/inbox/`
- `@pkm advice <问题> [--scope <范围>]`：Express 流程，基于知识库回答问题

**扩展功能命令**：
- `@pkm todo [操作] [参数]`：任务管理，支持4象限管理方法
- `@pkm addProject`：创建新项目目录（时间戳_XXX 格式）
- `@pkm help`：显示帮助信息

### 6.2 命令设计原则

- **极简接口**：最少命令，最多功能，降低使用门槛
- **智能默认**：`@pkm` 主流程自动检测并执行需要的操作，无需手动指定
- **流程对应**：命令与工作流设计一一对应，便于理解和使用
- **参数可选**：支持可选参数和默认值，简化常用场景