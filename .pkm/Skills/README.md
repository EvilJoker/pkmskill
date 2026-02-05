# PKM Skills 使用指南

> **PKM**（Personal Knowledge Management）- 基于 PARA + CODE 的智能知识管理系统

---

## 🚀 快速开始

### 最简单的用法

```text
@pkm
```

系统会自动执行：
- ✅ 验证知识库结构（Verify）
- 🗄️ 归档已完成的项目（Archive）
- 📦 组织分类 `50_Raw/` 中的待处理内容（Organize）
- 💎 提炼 `20_Areas/03notes/` 中的新增知识（Distill）

### 查看帮助

```text
@pkm help
```

---

## 📋 命令列表

### 一键整理知识（推荐）

```text
@pkm
```

**一键全自动处理**，系统智能整理和提炼知识，无需人工干预。

**自动顺序执行**（不推荐单独使用）：
- `@pkm verify` - 自动检查知识库结构完整性
- `@pkm archive` - 自动检测并归档已完成的项目（基于 `COMPLETED.md`，回流知识到 `50_Raw/` 并搬运到 `40_Archives/`）
- `@pkm organize` - 自动分类整理 `50_Raw/` 中的待处理内容
- `@pkm distill` - 自动提炼 `20_Areas/03notes/` 中的知识

**适用场景**：
- ✅ 每天结束前执行一次，自动整理当天积累的知识
- ✅ 项目完成后，自动归档并提取知识
- ✅ 定期维护，保持知识库整洁有序

### 快速捕获

```text
@pkm inbox <内容>                 # 快速捕获（自动识别标题、标签、链接）
@pkm inbox --online <内容>        # 在线模式（抓取并整理链接内容）
```

**示例**：

```text
# 快速捕获想法（自动识别标题和标签）
@pkm inbox React useEffect 的依赖数组如果为空，效果等同于 componentDidMount

# 保存带链接的内容（默认仅引用）
@pkm inbox Python 装饰器详解 https://docs.python.org/zh-cn/3/glossary.html

# 深度学习模式（抓取完整网页内容）
@pkm inbox --online React 18 新特性介绍 https://react.dev/blog/2022/03/29/react-v18
```

### 智能咨询

```text
@pkm advice <问题>                          # 默认模式（common + local）
@pkm advice --scope <范围> <问题>           # 指定范围模式
```

**scope 值说明**：

| scope 值 | 含义 | 检索范围 |
|---------|------|---------|
| `common` | AI 通用知识 | 使用 AI 的通用知识回答，不考虑当前知识库 |
| `local` | 当前知识库 | 检索当前知识库（20_Areas, 30_Resources, 40_Archives） |
| `<项目名>` | 指定项目知识库 | 检索指定项目的知识库（10_Projects/<项目名>/） |
| 默认（无 scope） | common + local | 等价于 `--scope common,local`，AI 通用知识 + 当前知识库 |

**scope 可以叠加**（逗号分隔）：
- `--scope common,local` - AI 通用知识 + 当前知识库
- `--scope local,项目名` - 当前知识库 + 指定项目知识库
- `--scope common,local,项目名` - AI 通用知识 + 当前知识库 + 指定项目知识库

**示例**：

```text
# 默认模式（AI 通用知识 + 你的私域知识）
@pkm advice React 性能优化有哪些最佳实践？
@pkm advice 微服务架构如何设计？

# 仅 AI 通用知识
@pkm advice --scope common React 18 新特性有哪些？

# 仅当前知识库查询
@pkm advice --scope local 上次 Redis 连接池问题怎么解决的？
@pkm advice --scope local 之前做过微服务相关的项目吗？

# 指定项目知识库
@pkm advice --scope 20260113_143000_XXX 这个项目的架构设计是什么？

# 组合模式
@pkm advice --scope common,local React 性能优化有哪些方法？

# 分类建议
@pkm advice 这篇关于 TypeScript 装饰器的笔记应该放到哪个目录？
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
@pkm archive               # 扫描所有项目，基于已存在的 COMPLETED.md 回流知识到 50_Raw 并搬运到 40_Archives/
@pkm archive <项目名>      # 仅为指定项目生成/更新 COMPLETED.md（如：@pkm archive UserAuth），不执行搬运
```

### 帮助与信息

```text
@pkm help                  # 显示帮助信息
```

---

## 🎯 PKM 是什么？

PKM 是一个**统一的知识管理入口**，它整合了 8 个内部模块，实现从知识捕获到归档的完整流程：

```text
主流程：Verify → Archive → Organize → Distill
  ↓        ↓        ↓         ↓
_Verifier _Archiver _Organizer _Distiller

辅助流程：
📥 Capture: _Inbox（快速捕获到 50_Raw/inbox/）
✨ Express: _Advisor（智能咨询）、_Archiver（项目归档）
🔧 支撑: _ProjectCreator（创建项目）、_TodoManager（任务管理）
```

### 基于三大方法论

**PARA**（组织结构）：

- **10_Projects**：短期可完成的项目
- **20_Areas**：长期关注的领域
- **30_Resources**：参考资料和暂存区
- **40_Archives**：已归档的项目
- **50_Raw**：统一素材区（待处理内容）

**CODE**（工作流）：

- **Capture**：捕获信息到 `50_Raw/inbox/`
- **Organize**：分类整理 `50_Raw/` 中的内容
- **Distill**：提炼 `20_Areas/03notes/` 中的知识（金字塔原理）
- **Express**：输出成果（归档项目、知识咨询）

**金字塔原理**（知识组织）：

知识在 `20_Areas/` 中按金字塔结构流动：

- **🏛️ 原则层**（`01principles/`）：顶层智慧、方法论、框架
- **📋 应用层**（`02playbooks/`、`02templates/`、`02cases/`）：标准化流程、模版、案例
- **📝 整理知识层**（`03notes/<领域>/`）：零散知识点，按领域分类

**知识流动方向**：零散知识（notes）→ 应用知识（playbooks/templates/cases）→ 原则知识（principles）

---

## 🏗️ 系统架构

### 目录结构

```text
知识库根目录/
├── 10_Projects/              # 项目（短期目标）
│   └── <时间戳>_<项目名称>/
│       ├── manual/           # 受保护区（AI 只读）
│       └── COMPLETED.md      # 完成标记
├── 20_Areas/                 # 领域（长期关注）
│   ├── manual/               # 受保护区（AI 只读）
│   ├── 01principles/         # 原则层（AI 可写）
│   ├── 02playbooks/          # 应用层：标准化流程（AI 可写）
│   ├── 02templates/          # 应用层：可复用模版（AI 可写）
│   ├── 02cases/              # 应用层：具体案例（AI 可写）
│   └── 03notes/              # 整理知识层（AI 可写）
│       └── <领域>/
├── 30_Resources/             # 资源（参考材料）
│   ├── Library/              # 资料库（AI 可写）
│   ├── summary/              # 报告汇总（AI 可写）
│   ├── todo.md               # 待办任务列表（AI 可写）
│   └── todo_archive.md       # 已完成任务归档（AI 可写）
├── 40_Archives/              # 归档（AI 可写）
│   └── <时间戳>_<项目名称>/
└── 50_Raw/                   # 统一素材区
    ├── inbox/                # 待分类（AI 可写）
    └── merged/               # 合并后的素材（AI 可写）
```

### 内部模块

PKM 由 8 个内部模块组成：

| 模块 | 职责 | 对应阶段 | 文档 |
| ------ | ------ | --------- | ------ |
| **Verifier** | 范围守卫，验证结构 | 前置检查 | `_Verifier.md` |
| **Inbox** | 快速捕获器 | Capture | `_Inbox.md` |
| **Advisor** | 智能顾问 | 辅助决策 | `_Advisor.md` |
| **Organizer** | 智能组织器 | Capture → Organize | `_Organizer.md` |
| **Distiller** | 知识提炼器，金字塔提炼 | Organize → Distill | `_Distiller.md` |
| **Archiver** | 生命周期管理器 | Express | `_Archiver.md` |
| **ProjectCreator** | 项目创建器 | 支撑 | `_ProjectCreator.md` |
| **TodoManager** | 任务管理器 | 支撑 | `_TodoManager.md` |

详细说明请查看 `PKM/Skill.md` 或各模块的文档。

---

## 💡 使用场景

### 场景 1：每日知识整理

```text
# 每天结束前
@pkm

# 系统会：
# 1. ✅ 验证知识库结构
# 2. 🗄️ 归档已完成的项目
# 3. 📦 组织分类 50_Raw/ 中的待处理内容
# 4. 💎 提炼 20_Areas/03notes/ 中的新增知识
```

### 场景 2：快速捕获信息

```bash
# 1. 快速捕获（自动识别标题和标签）
@pkm inbox React useEffect 的依赖数组如果为空，效果等同于 componentDidMount

# 2. 让 AI 自动组织分类
@pkm organize

# 或者一步到位
@pkm inbox React useEffect... && @pkm
```

### 场景 3：深度学习某个主题

```text
# 1. 捕获多个知识片段到 50_Raw/inbox/
# 2. 执行组织分类
@pkm organize

# 3. 当积累足够时，执行提炼
@pkm distill React

# 4. 查看生成的提炼报告
# 位置：30_Resources/summary/YYYYMMDD_HHMMSS_标题_Distill.md
```

### 场景 4：遇到问题寻求建议

```text
# 默认模式（AI + 知识库）
@pkm advice React 性能优化有哪些最佳实践？
# → AI 给出通用方法，并结合你知识库中的实践经验

# 仅 AI 通用知识
@pkm advice --scope common React 18 新特性有哪些？
# → 只使用 AI 通用知识，不检索知识库

# 查询历史经验
@pkm advice --scope local 上次 Redis 连接池问题怎么解决的？
# → 从知识库中找到历史解决方案

# 查询项目知识
@pkm advice --scope 20260113_143000_XXX 这个项目的架构设计是什么？
# → 从指定项目知识库中查找

# 分类咨询
@pkm advice 这篇关于微服务的笔记应该放到哪个目录？
# → AI 分析内容，推荐合适的分类位置
```

### 场景 5：项目完成归档

```bash
# 1. 在项目目录创建完成标记
echo "完成于 2026-01-13" > 10_Projects/UserAuth/COMPLETED.md

# 2. 执行归档
@pkm archive

# 系统会：
# - 移动项目到 40_Archives/
# - 提取可复用知识到 50_Raw/（等待后续 Organize 和 Distill 处理）
# - 生成归档报告
```

---

## 🛡️ 安全机制

### 双重防火墙

1. **内部防火墙**：受保护区 vs AI 可写区

   - ✅ AI 可以自由修改 `20_Areas/03notes/`、`02playbooks/`、`02templates/`、`02cases/`、`01principles/`、`10_Projects/*/`（排除 manual/）
   - ✅ AI **只读** `20_Areas/manual/` 和 `10_Projects/*/manual/`，绝不直接修改

2. **外部防火墙**：知识库内 vs 知识库外

   - ✅ Verifier 强制检查目录结构（6 个必需目录：10_Projects、20_Areas、30_Resources、40_Archives、50_Raw、.pkm）
   - ✅ 生成操作白名单
   - ❌ 禁止操作知识库外的任何路径

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

## 📖 最佳实践

### 1. 先验证后操作

每次操作前，PKM 会自动调用 Verifier 验证环境：

```text
@pkm → 自动验证 → 执行操作
```

### 2. 保持 Inbox 轻量

- 每天清空一次 Inbox
- 不要在 Inbox 中堆积文件
- Inbox 是暂存区，不是长期存储

建议：每天结束前执行 `@pkm`

### 3. 定期蒸馏知识

- 当某主题积累 10+ 条碎片时，立即蒸馏
- 不要等碎片堆积太多，否则蒸馏质量下降

### 4. 人为后置纠偏

- **相信 AI**：将判断和决策交给 AI，保证流程的自动化
- **后置纠偏**：用户负责后期纠偏，发现问题时再修正
- **Manual 区保护**：Manual 区的内容由你完全掌控，AI 只读不写

### 5. 项目完成立即归档

- 项目完成后，立即创建 `COMPLETED.md`
- 不要让完成的项目占用 Projects 空间
- 归档不是"扔掉"，而是"提炼"

---

## 🔧 故障排查

### 问题 1：提示"知识库结构不完整"

**症状**：执行 `@pkm` 时提示缺少目录。

**原因**：知识库未初始化。

**解决**：

```bash
mkdir -p 10_Projects 20_Areas/{manual,01principles,02playbooks,02templates,02cases,03notes} \
         30_Resources/{Library,summary} 40_Archives 50_Raw/{inbox,merged} .pkm/Skills
```

---

### 问题 2：Organizer 无法分类

**症状**：文件被标记为"待确认"。

**原因**：文件类型不明确，AI 无法判断。

**解决**：

1. 查看 `20_Areas/03notes/00_未分类/[待确认]_文件名.md`
2. 人工判断类型，手动移动到正确位置

---

### 问题 3：Distiller 生成的提炼报告质量差

**症状**：提炼报告内容矛盾、逻辑混乱。

**原因**：notes 层知识质量参差不齐。

**解决**：

1. 直接手动编写到 `20_Areas/manual/`（受保护区）
2. 或重新收集高质量的知识片段到 `50_Raw/inbox/`

---

### 问题 4：AI 误操作了 Manual 区

**症状**：Manual 文件被修改。

**原因**：未调用 Verifier，或 AI 工具配置错误。

**解决**：

1. 立即通过 Git 回滚：`git checkout -- 20_Areas/manual/`
2. 检查 `.cursorrules` 配置，确保限制了 AI 的写权限
3. 始终先调用 `@pkm`（会自动执行 Verifier）

---

## 📚 进阶配置

### 手动执行单个步骤

如果只想执行部分操作，可以手动调用：

```text
@pkm organize   # 只执行组织分类（处理 50_Raw/）
@pkm distill    # 只执行提炼（处理 20_Areas/03notes/）
@pkm distill <主题>  # 提炼指定主题（如：@pkm distill React）
@pkm archive    # 只执行归档（模式 B：处理所有已完成项目，知识回流到 50_Raw 并搬运到 40_Archives/）
@pkm verify     # 只验证知识库结构
```

---

## ❓ 常见问题

### Q1：PKM 是代码还是文档？

**A**：PKM 是 **Markdown 文档**，不是代码。它是给 AI 阅读的"工作手册"，AI 理解后会按照指令执行。

---

### Q2：AI 会严格遵守 PKM 吗？

**A**：大多数情况下会，但不是 100%。这就是为什么有 `Verifier` 和白名单机制，提供双重保险。

---

### Q3：可以修改 PKM 吗？

**A**：当然可以！PKM 就是为了让你定制的。根据你的工作习惯调整即可。

修改位置：

- 主入口：`PKM/Skill.md`
- 内部模块：`PKM/_Verifier.md` 等

---

### Q4：如果我想用 MCP 实现怎么办？

**A**：PKM 可以和 MCP 共存：

1. 保留 `PKM/Skill.md` 作为"意图描述"
2. 用 MCP 实现 `Verifier` 作为"硬约束"
3. 其他模块继续用 Markdown

---

### Q5：为什么是 @pkm 而不是 @KnowledgeManager？

**A**：为了简洁！`@pkm` 只有 4 个字符，更容易记忆和输入。

---

## 🎓 学习路径

### 新手（刚开始使用）

1. 初始化知识库结构（见"故障排查"）
2. 执行 `@pkm help` 查看命令
3. 尝试 `@pkm` 体验全自动模式

### 进阶（熟悉基本操作）

1. 查看 `PKM/Skill.md` 了解内部原理
2. 阅读各模块文档（`_Organizer.md`、`_Distiller.md` 等）
3. 根据需求调整配置

### 高级（深度定制）

1. 修改 `PKM/Skill.md` 调整路由逻辑
2. 修改内部模块实现自定义工作流
3. 集成 MCP 实现更强的约束

---

## 📄 相关文档

- **主文档**：`PKM/Skill.md` - PKM 系统完整说明
- **架构文档**：`/docs/ARCHITECTURE.md` - 系统架构和设计理念
- **模块文档**：
  - `PKM/_Verifier.md` - 范围守卫
  - `PKM/_Inbox.md` - 快速捕获器
  - `PKM/_Organizer.md` - 智能组织器
  - `PKM/_Distiller.md` - 知识提炼器
  - `PKM/_Archiver.md` - 生命周期管理器
  - `PKM/_Advisor.md` - 智能顾问
  - `PKM/_ProjectCreator.md` - 项目创建器
  - `PKM/_TodoManager.md` - 任务管理器

---

## 🚀 版本历史

- **v1.0.0** (2026-01-13)：统一入口，从 5 个独立 Skills 重构为单一 `@pkm` 命令

---

## 💬 支持与反馈

如果你在使用过程中遇到问题：

1. 查看本 README 的"故障排查"章节
2. 执行 `@pkm help` 查看命令列表
3. 阅读 `PKM/Skill.md` 了解详细说明
4. 根据你的需求修改配置

---

祝你的知识管理之旅愉快！🚀
