---
name: PKM
description: 基于 PARA+CODE 的智能知识管理系统，自动处理知识捕获、组织、蒸馏和归档
---

# Skill: PKM (Personal Knowledge Management)

> 统一的知识管理入口，基于 **PARA**（Projects/Areas/Resources/Archives）和 **CODE**（Capture/Organize/Distill/Express）方法论。

---

## 快速开始

### 最简单的用法

```text
@pkm
```

我会自动判断当前需要执行的操作：

- ✅ 检查知识库结构（Verify）
- 🗄️ 如果有项目标记完成 → 自动归档（Archive）
- 📦 如果 50_Raw/ 有文件 → 自动组织分类（Organize）
- 💎 如果 20_Areas/03notes/ 有新增/变动 → 自动提炼（Distill）

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
- `@pkm verify` - 自动检查知识库结构完整性
- `@pkm archive` - 自动以“模式 B”（无参数 `@pkm archive`）检测并归档已完成的项目（基于 `COMPLETED.md`，回流知识到 `50_Raw/` 并搬运到 `40_Archives/`）
- `@pkm organize` - 自动分类整理 `50_Raw/` 中的待处理内容
- `@pkm distill` - 自动提炼 `20_Areas/03notes/` 中的知识

**适用场景**：

- ✅ 每天结束前执行一次，自动整理当天积累的知识
- ✅ 项目完成后，自动归档并提取知识
- ✅ 定期维护，保持知识库整洁有序

### 快速捕获

```text
@pkm inbox <内容>                 # 快速捕获，自动识别标题和标签
@pkm inbox --online <内容>        # 在线模式，抓取链接内容
```

### 智能咨询

```text
@pkm advice <问题>                          # 默认模式（common + local）
@pkm advice --scope <范围> <问题>           # 指定范围模式

scope 值：
  - common          # AI 通用知识
  - local           # 当前知识库
  - 项目名          # 指定项目知识库
  - 可叠加：common,local 或 local,项目名
```

### 任务管理

```text
@pkm todo <内容>           # 添加新任务
@pkm todo update <id/name> # 更新任务进展
@pkm todo ok <id/name>    # 完成任务
@pkm todo del <id/name>   # 删除任务
@pkm todo list            # 列出所有任务
```
### 项目

```text
@pkm addProject [项目名称]  # 创建新项目目录（格式：YYYYMMDD_HHMMSS_<项目名称>，如果未提供名称则询问）
@pkm archive               # 扫描所有项目，基于已存在的 COMPLETED.md 进行知识回流并搬运到 40_Archives/
@pkm archive <项目名>      # 仅为指定项目生成/更新 COMPLETED.md 清单，不执行搬运
```

### 帮助与信息

```text
@pkm help                  # 显示帮助信息
```

---

## 工作流程

### 1. 前置验证（自动执行）

调用 `_Verifier` 模块：

- ✅ 检查知识库结构（6 个必需目录：10_Projects、20_Areas、30_Resources、40_Archives、50_Raw、.pkm）
- ✅ 生成操作白名单
- ❌ 验证失败则立即中止

### 2. 命令路由

根据命令参数路由到相应模块：

**一键整理知识（无参数）**：
- 执行 `@pkm` 命令：执行主流程 `Verify → Archive → Organize → Distill`
对应子命令：`@pkm verify`、`@pkm archive`、`@pkm organize`、`@pkm distill`

**手动命令（带参数）**：

- `inbox <内容>` → `_Verifier` → `_Inbox`（快速捕获）
- `inbox --online <内容>` → `_Verifier` → `_Inbox`（在线模式）
- `advice <问题>` → `_Verifier` → `_Advisor`（默认模式：common + local）
- `advice --scope <范围> <问题>` → `_Verifier` → `_Advisor`（指定范围）
- `todo <操作>` → `_Verifier` → `_TodoManager`（任务管理）
- `addProject [项目名称]` → `_Verifier` → `_ProjectCreator`（创建项目）
- `organize` → `_Verifier` → `_Organizer`（组织分类）
- `distill` → `_Verifier` → `_Distiller`（提炼知识）
- `archive [项目名]` → `_Verifier` → `_Archiver`（归档项目）
- `verify` → `_Verifier`（仅验证）
- `help` → 显示帮助信息

### 3. 执行与报告

执行相应操作，生成统一格式的报告。

---

## 内部模块说明

PKM 由 8 个内部模块组成，每个模块负责知识管理的一个环节：

| 模块 | 职责 | 对应阶段 | 触发方式 |
|------|------|---------|---------|
| `_Verifier` | 范围守卫，验证结构 | 前置检查 | 自动（每次操作前） |
| `_Inbox` | 快速捕获器 | Capture | `@pkm inbox` |
| `_Advisor` | 智能顾问 | Express | `@pkm advice` |
| `_Organizer` | 智能组织器 | Organize | `@pkm organize` 或自动 |
| `_Distiller` | 知识提炼器 | Distill | `@pkm distill` 或自动 |
| `_Archiver` | 生命周期管理器 | Express | `@pkm archive` 或自动 |
| `_ProjectCreator` | 项目创建器 | 支撑 | `@pkm addProject` |
| `_TodoManager` | 任务管理器 | 支撑 | `@pkm todo` |

### 📋 _Verifier（范围守卫）

**职责**：验证知识库结构，生成操作白名单

**触发**：每次操作前自动执行

**详细文档**：`_Verifier.md`

---

### 📥 _Inbox（快速捕获器）

**职责**：快速捕获信息到 Inbox，降低记录门槛

**对应阶段**：CODE 的 **Capture**（捕获）

**触发**：

- 手动调用：`@pkm inbox <内容>`
- 在线模式：`@pkm inbox --online <内容>`

**前置要求**：

- ⚠️ 必须先调用 `_Verifier` 验证环境
- 确认 `50_Raw/inbox/` 存在且可写

**核心功能**：

- 快速保存文本、想法、链接到 `50_Raw/inbox/`
- AI生成文件名（简单总结内容，5-10字标题）
- 智能处理链接（默认仅引用，`--online` 模式抓取内容）
- 保持内容原生（最小化处理，保留原始格式）

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
  - `--scope 项目名`：仅指定项目知识库
  - `--scope common,local`：AI 通用知识 + 当前知识库（默认）
  - `--scope local,项目名`：当前知识库 + 项目知识库

**前置要求**：

- ⚠️ 必须先调用 `_Verifier` 验证环境

**核心功能**：

- **通用咨询模式**：AI 通用知识 + 私域知识库增强
  - 基于 AI 能力回答任何问题
  - 检索知识库相关内容作为补充
  - 结合通用知识和个人经验给建议

- **私域模式**：仅查询知识库
  - 检索历史笔记和经验
  - 找到相关项目案例
  - 提取个人最佳实践

- **智能检索**：
  - 关键词匹配（文件名、路径）
  - 优先级排序（manual/ > principles > playbooks/templates/cases > notes > Projects > Archives）
  - 内容摘要提取

- **应用场景**：
  - 分类建议：不知道内容放哪里时咨询
  - 知识查询：快速找到相关笔记
  - 经验参考：查找历史解决方案
  - 决策支持：基于已有经验给建议

**详细文档**：`_Advisor.md`

---

### 📦 _Organizer（智能组织器）

**职责**：处理 `50_Raw/` 中的未分类内容，合并同类内容，分类归位到 PARA 体系

**对应阶段**：CODE 的 **Organize**

**触发**：

- 智能模式：`50_Raw/` 有文件时
- 手动调用：`@pkm organize`

**核心功能**：

- 扫描 `50_Raw/`（包含 `inbox/` 和其他待分类素材）
- **可选插件预处理**：若存在 `.pkm/Skills/PKM/plugin/Skill.md`，先按内容类型匹配插件，命中则用对应 `template_<类型>.md` 模版整理（如故障总结模版），再继续分类
- 按主题/类型合并同类内容到 `50_Raw/merged/`
- 判断类型：可执行任务 / 知识片段 / 参考资料
- 分类归位：
  - 任务 → `10_Projects/`（直接放在项目目录下）
  - 知识 → `20_Areas/03notes/<领域>/`（先放在 notes 层）
  - 资料 → `30_Resources/Library/`
- 整理完清空 `50_Raw/`

**详细文档**：`_Organizer.md`

---

### 💎 _Distiller（知识提炼器）

**职责**：将 `20_Areas/03notes/` 中的零散知识按金字塔原理提炼成结构化知识

**对应阶段**：CODE 的 **Distill**

**触发**：

- 智能模式：`20_Areas/03notes/` 有新增/变动时
- 手动调用：`@pkm distill`

**核心功能**：

- 扫描 `20_Areas/03notes/` 各领域目录
- 与已有知识深度整合（去重、交叉引用、结构化）
- 按金字塔原理提炼：
  - 零散知识（notes）+ areas 区的 manual 区（只读）→ 整理知识（notes 内按领域分类）
  - 整理知识 → 应用知识（playbooks/templates/cases）
  - 应用知识 → 原则知识（principles）
- 沉淀到对应目录：
  - `20_Areas/03notes/<领域>/` → 整理后的知识
  - `20_Areas/02playbooks/`、`02templates/`、`02cases/` → 应用层知识
  - `20_Areas/01principles/` → 原则层知识
- 系统性检查：一致性、过时性、冗余、逻辑合理性
- 生成报告到 `30_Resources/summary/`

**详细文档**：`_Distiller.md`

---

### 📦 _Archiver（生命周期管理器）

**职责**：基于 `COMPLETED.md` 归档完成的项目，并将项目中的经验与资料统一回流到 `50_Raw/`

**对应阶段**：CODE 的 **Express**（生命周期管理）

**触发**：

- 智能模式：`@pkm` 主流程中自动调用（等价于执行 `@pkm archive`，走模式 B）
- 手动模式 A：`@pkm archive <项目名>` → 仅为指定项目生成/更新 `COMPLETED.md` 清单，不执行搬运
- 手动模式 B：`@pkm archive` → 扫描所有项目，基于已有 `COMPLETED.md` 进行知识回流并搬运到 `40_Archives/`

> **重要说明**：无论是 `@pkm` 一键主流程，还是手动执行 `@pkm archive`（模式 B），**都只会处理已经存在 `COMPLETED.md` 的项目**，不会自动为所有项目批量生成 `COMPLETED.md`；生成或更新单个项目的 `COMPLETED.md` 只能通过模式 A：`@pkm archive <项目名>`。

**核心功能**：

- 识别已完成的项目（存在 `COMPLETED.md`）
- 移动整个项目到 `40_Archives/`，保留完整结构
- 提取可复用知识和资料（架构决策、经验教训、学习笔记、设计文档、测试文档等）
- 将上述内容统一回流到 `50_Raw/`，等待后续 `Organizer` 和 `Distiller` 处理

**详细文档**：`_Archiver.md`

---

## 使用示例

### 场景 1：日常工作流（完全自动）

```text
# 每天结束前
@pkm

# 输出示例：
✅ Verifier 验证通过

🗄️ 检测到 1 个项目已完成
🔄 执行 Archiver...
  └─ 归档到 40_Archives/，知识回流到 50_Raw/ ✅

📦 检测到 50_Raw/ 有 8 个文件
🔄 执行 Organizer...
  ├─ 合并同类内容到 50_Raw/merged/
  ├─ 任务 → Projects: 3 个
  ├─ 知识 → Areas/03notes: 5 个
  └─ 50_Raw/ 已清空 ✅

💎 检测到 20_Areas/03notes/01_react/ 有新增
🔄 执行 Distiller...
  ├─ 整理知识 → 20_Areas/03notes/01_react/
  ├─ 应用知识 → 20_Areas/02playbooks/React_Hooks_使用流程.md
  └─ 报告 → 30_Resources/summary/20260113_103000_知识提炼报告_Distill.md ✅

🎉 完成！主流程执行完毕。
```

---

### 场景 2：只组织分类 50_Raw/

```text
@pkm organize

# 输出示例：
✅ Verifier 验证通过
📥 处理 Inbox 中的 8 个文件...

## 分流统计

### 可执行任务 → Projects：3 个
- 实现用户登录功能.md → 10_Projects/UserAuth/
- 修复支付Bug.md → 10_Projects/Payment/

### 知识片段 → Areas/03notes：5 个
- React_useEffect.md → 20_Areas/03notes/01_react/
- Python_装饰器.md → 20_Areas/03notes/01_python/

✅ 50_Raw/ 已清空！
```

---

### 场景 3：提炼特定主题

```text
@pkm distill React

# 输出示例：
✅ Verifier 验证通过
💎 扫描主题：React
  ├─ 找到 15 个知识片段（20_Areas/03notes/01_react/）
  ├─ 去重后：12 个独特知识点
  ├─ 整合 manual/ 区内容（只读参考）
  └─ 生成提炼报告：30_Resources/summary/20260113_103000_React知识提炼_Distill.md

## 提炼结果

1. 概念：React Hooks 是什么 → 已整理到 20_Areas/03notes/01_react/
2. 基本用法 → 已提炼到 20_Areas/02playbooks/React_Hooks_使用流程.md
   - useState
   - useEffect
3. 进阶技巧 → 已提炼到 20_Areas/02templates/React_Hooks_高级模式.md
4. 常见问题 → 已提炼到 20_Areas/02cases/React_Hooks_常见问题案例.md
5. 最佳实践 → 已提炼到 20_Areas/01principles/React_Hooks_最佳实践.md

✅ 提炼完成！知识已按金字塔原理沉淀到对应层级。
```

---

### 场景 4：查看帮助信息

```text
@pkm help

# 输出示例：
📚 PKM - Personal Knowledge Management v1.0.0

基于 PARA+CODE 的智能知识管理系统

## 📋 命令列表

### 一键整理知识（推荐）
  @pkm                       全自动模式，依次执行所有需要的操作

### 快速捕获
  @pkm inbox <内容>                 快速捕获（自动识别标题、标签、链接）
  @pkm inbox --online <内容>        在线模式（抓取并整理链接内容）

### 手动模式
  @pkm organize              组织分类 50_Raw/ 中的内容
  @pkm distill              提炼 20_Areas/03notes/ 中的知识
  @pkm distill <主题>       提炼指定主题（如：React）
  @pkm archive               扫描所有项目，基于已存在的 COMPLETED.md 回流知识到 50_Raw 并搬运到 40_Archives/
  @pkm archive <项目名>      仅为指定项目生成/更新 COMPLETED.md（如：UserAuth），不执行搬运
  @pkm verify                仅验证知识库结构

### 帮助
  @pkm help                  显示此帮助信息

## 🚀 快速开始

1. 初始化知识库：
   mkdir -p 10_Projects 20_Areas/{manual,01principles,02playbooks,02templates,02cases,03notes} \
            30_Resources/{Library,summary} 40_Archives 50_Raw/{inbox,merged} .pkm/Skills

2. 开始使用：
   @pkm                       # 自动处理所有任务

## 📚 详细文档

- 主文档：.pkm/Skills/PKM/Skill.md
- 使用指南：.pkm/Skills/README.md
- 架构说明：docs/ARCHITECTURE.md

## 💡 工作流程

Capture（捕获）→ Organize（组织）→ Distill（提炼）→ Express（表达）
   ↓              ↓               ↓              ↓
 _Inbox      _Organizer      _Distiller      _Archiver

主流程：Verify → Archive → Organize → Distill

## 🛡️ 安全机制

✅ 双重防火墙：受保护区 vs AI 可写区，知识库内 vs 外
✅ 白名单强制：所有操作限制在白名单内
✅ 只读 manual/：AI 永远不直接修改 manual/ 区（受保护区）
```

---

## 安全机制

### 双重防火墙

1. **内部防火墙**：受保护区 vs AI 可写区

   - AI 可以自由修改 `20_Areas/03notes/`、`02playbooks/`、`02templates/`、`02cases/`、`01principles/`、`10_Projects/*/`（排除 manual/）
   - AI **只读** `20_Areas/manual/` 和 `10_Projects/*/manual/`，绝不直接修改

2. **外部防火墙**：知识库内 vs 知识库外

   - Verifier 强制检查目录结构
   - 禁止操作知识库外的任何路径

### 白名单机制

**可写区域**（AI 可以创建/修改/删除文件）：

- `50_Raw/`
- `10_Projects/*/`（排除 manual/）
- `20_Areas/03notes/`
- `20_Areas/02playbooks/`
- `20_Areas/02templates/`
- `20_Areas/02cases/`
- `20_Areas/01principles/`
- `30_Resources/Library/`
- `40_Archives/`

**只读区域**（AI 只能读取，不能修改）：

- `20_Areas/manual/`
- `10_Projects/*/manual/`
- `.pkm/`

**禁止区域**（绝对不能操作）：

- 知识库根目录外的任何路径

---

## 核心原则

1. **自动化优先**：能自动处理的不要人工干预
2. **安全至上**：先验证后操作，永不越界
3. **人类决策**：AI 提建议，人类做决策
4. **渐进式**：从简单到复杂，从手动到自动
5. **可追溯**：所有操作都有日志和报告

---

## 故障排查

### 问题：提示"知识库结构不完整"

**原因**：缺少必需的目录。

**解决**：

```bash
mkdir -p 10_Projects 20_Areas/{manual,01principles,02playbooks,02templates,02cases,03notes} \
         30_Resources/{Library,summary} 40_Archives 50_Raw/{inbox,merged} .pkm/Skills
```

### 问题：文件被标记为"待确认"

**原因**：Organizer 无法判断文件类型。

**解决**：

1. 查看 `20_Areas/03notes/00_未分类/[待确认]_文件名.md`
2. 人工判断类型，手动移动到正确位置

### 问题：草稿质量差

**原因**：原子块质量参差不齐。

**解决**：

1. 直接手动编写到 `20_Areas/manual/`（受保护区）
2. 或重新收集高质量的知识片段到 `50_Raw/inbox/`

---

## 高级配置

### 手动执行单个步骤

如果只想执行部分操作，可以手动调用：

```text
@pkm organize   # 只执行组织分类（处理 50_Raw/）
@pkm distill    # 只执行提炼（处理 20_Areas/03notes/）
@pkm archive    # 只执行归档（模式 B：处理所有已完成项目，知识回流到 50_Raw 并搬运到 40_Archives/）
@pkm verify     # 只验证知识库结构
```

---

## 反馈与支持

如果在使用过程中遇到问题：

1. 执行 `@pkm help` 查看命令列表
2. 查看具体模块文档（`_Verifier.md` 等）
3. 根据你的需求修改内部模块

---

祝你的知识管理之旅愉快！🚀
