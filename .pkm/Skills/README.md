# PKM Skills 使用指南

> **PKM**（Personal Knowledge Management）- 基于 PARA + CODE 的智能知识管理系统

---

## 🚀 快速开始

### 最简单的用法

```text
@pkm
```

系统会自动：

- ✅ 验证知识库结构
- 📥 处理 Inbox 中的待分类内容
- 📚 蒸馏积累足够的知识碎片
- 🔍 审计新生成的草稿
- 📦 归档已完成的项目

### 查看帮助

```text
@pkm help
```

---

## 📋 命令列表

### 智能模式（推荐）

```text
@pkm                       # 全自动模式，执行所有需要的操作
```

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

### 手动模式

```text
@pkm addProject            # 创建新项目目录（自动命名为 时间戳_XXX）
@pkm todo <内容>           # 添加新任务
@pkm todo update <id/name> # 更新任务进展
@pkm todo ok <id/name>    # 完成任务
@pkm todo del <id/name>   # 删除任务
@pkm todo list            # 列出所有任务
@pkm classify              # 分类 Inbox 中的内容
@pkm synthesize            # 蒸馏所有达到阈值（10+）的主题
@pkm synthesize <主题>     # 蒸馏指定主题（如：@pkm synthesize React）
@pkm audit                 # 审计所有包含草稿的主题
@pkm audit <主题>          # 审计指定主题（如：@pkm audit Python）
@pkm archive               # 归档所有包含 COMPLETED.md 的项目
@pkm archive <项目名>      # 归档指定项目（如：@pkm archive UserAuth）
@pkm verify                # 仅验证知识库结构
```

### 帮助与信息

```text
@pkm help                  # 显示帮助信息
```

---

## 🎯 PKM 是什么？

PKM 是一个**统一的知识管理入口**，它整合了 7 个内部模块，实现从知识捕获到归档的完整流程：

```text
📥 Capture  ─→  📋 Organize  ─→  🧪 Distill  ─→  ✨ Express
   (捕获)         (组织)          (蒸馏)         (表达)
     ↓              ↓               ↓              ↓
   _Inbox  →  _Classifier → _Synthesizer →  _Archiver
                            → _Auditor
```

### 基于两大方法论

**PARA**（组织结构）：

- **10_Projects**：短期可完成的项目
- **20_Areas**：长期关注的领域
- **30_Resources**：参考资料和暂存区
- **40_Archives**：已归档的项目

**CODE**（工作流）：

- **Capture**：捕获信息到 Inbox
- **Organize**：分类整理
- **Distill**：提炼精华
- **Express**：输出成果

---

## 🏗️ 系统架构

### 目录结构

```text
知识库根目录/
├── 10_Projects/              # 项目（短期目标）
│   ├── ProjectName/
│   │   ├── Manual/           # 人工维护（AI 只读）
│   │   ├── AI_Generated/     # AI 生成（AI 可写）
│   │   └── COMPLETED.md      # 完成标记
│   └── ...
├── 20_Areas/                 # 领域（长期关注）
│   ├── Manual/               # 精选知识（AI 只读）
│   └── AI_Synthesized/       # AI 整合（AI 可写）
│       ├── Cluster_React/
│       ├── Cluster_Python/
│       └── ...
├── 30_Resources/             # 资源（参考材料）
│   ├── 00_Inbox/             # 待处理（AI 可写）
│   └── Library/              # 资料库（AI 可写）
└── 40_Archives/              # 归档（AI 可写）
    └── 2026/
        └── ProjectName/
```

### 内部模块

PKM 由 7 个内部模块组成：

| 模块 | 职责 | 对应阶段 | 文档 |
| ------ | ------ | --------- | ------ |
| **Verifier** | 范围守卫，验证结构 | 前置检查 | `_Verifier.md` |
| **Inbox** | 快速捕获器 | Capture | `_Inbox.md` |
| **Advisor** | 智能顾问 | 辅助决策 | `_Advisor.md` |
| **Classifier** | 智能分流器 | Capture → Organize | `_Classifier.md` |
| **Synthesizer** | 知识蒸馏器 | Organize → Distill | `_Synthesizer.md` |
| **Auditor** | 质量审计员 | Distill（审计） | `_Auditor.md` |
| **Archiver** | 生命周期管理器 | Express | `_Archiver.md` |

详细说明请查看 `PKM/Skill.md` 或各模块的文档。

---

## 💡 使用场景

### 场景 1：每日知识整理

```text
# 每天结束前
@pkm

# 系统会：
# 1. ✅ 验证知识库
# 2. 📥 清空 Inbox（分类到 Projects/Areas/Resources）
# 3. 📚 蒸馏积累足够的知识碎片
# 4. 🔍 生成更新建议清单
# 5. 📦 归档已完成的项目
```

### 场景 2：快速捕获信息

```bash
# 1. 快速捕获（自动识别标题和标签）
@pkm inbox React useEffect 的依赖数组如果为空，效果等同于 componentDidMount

# 2. 让 AI 自动分类
@pkm classify

# 或者一步到位
@pkm inbox React useEffect... && @pkm
```

### 场景 3：深度学习某个主题

```text
# 1. 捕获多个知识片段到 Inbox
# 2. 执行分类
@pkm classify

# 3. 当积累足够时，执行蒸馏
@pkm synthesize React

# 4. 查看生成的草稿和更新建议
# 位置：20_Areas/AI_Synthesized/Cluster_React/[草稿]_*.md
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
# - 提取可复用知识到 AI_Synthesized
# - 生成归档报告
```

---

## 🛡️ 安全机制

### 双重防火墙

1. **内部防火墙**：AI 区 vs Manual 区

   - ✅ AI 可以自由修改 `AI_Synthesized/`, `AI_Generated/`
   - ✅ AI **只读** `Manual/`，绝不直接修改
   - ✅ 所有对 Manual 的更新都通过"建议清单"，由人类决策

2. **外部防火墙**：知识库内 vs 知识库外

   - ✅ Verifier 强制检查目录结构（5 个必需目录）
   - ✅ 生成操作白名单
   - ❌ 禁止操作知识库外的任何路径

### 白名单机制

**可写区域**（AI 可以创建/修改/删除文件）：

- `10_Projects/*/AI_Generated/`
- `20_Areas/AI_Synthesized/`
- `30_Resources/00_Inbox/`
- `30_Resources/Library/`
- `40_Archives/`

**只读区域**（AI 只能读取，不能修改）：

- `20_Areas/Manual/`
- `10_Projects/*/Manual/`
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

### 4. 人工审核是关键

- AI 只能提建议，不能替你做决策
- 必须人工审核 Auditor 生成的清单
- Manual 区的内容由你完全掌控

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
mkdir -p 10_Projects 20_Areas/{Manual,AI_Synthesized} 30_Resources/{00_Inbox,Library} 40_Archives .pkm/Skills
```

---

### 问题 2：Classifier 无法分类

**症状**：文件被标记为"待确认"。

**原因**：文件类型不明确，AI 无法判断。

**解决**：

1. 查看 `20_Areas/AI_Synthesized/Unsorted/[待确认]_文件名.md`
2. 人工判断类型，手动移动到正确位置

---

### 问题 3：Synthesizer 生成的草稿质量差

**症状**：草稿内容矛盾、逻辑混乱。

**原因**：原子块质量参差不齐。

**解决**：

1. 忽略草稿，直接手动编写 Manual
2. 或重新收集高质量的原子块

---

### 问题 4：AI 误操作了 Manual 区

**症状**：Manual 文件被修改。

**原因**：未调用 Verifier，或 AI 工具配置错误。

**解决**：

1. 立即通过 Git 回滚：`git checkout -- 20_Areas/Manual/`
2. 检查 `.cursorrules` 配置，确保限制了 AI 的写权限
3. 始终先调用 `@pkm`（会自动执行 Verifier）

---

## 📚 进阶配置

### 自定义蒸馏阈值

默认：某主题积累 10+ 个文件时触发蒸馏。

调整阈值：

```text
@pkm synthesize React --threshold 20
```

### 跳过某些模块

如果只想执行部分操作：

```text
@pkm --skip-synthesizer --skip-auditor
```

### 查看详细日志

```text
@pkm --verbose
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
2. 阅读各模块文档（`_Classifier.md` 等）
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
  - `PKM/_Classifier.md` - 智能分流器
  - `PKM/_Synthesizer.md` - 知识蒸馏器
  - `PKM/_Auditor.md` - 质量审计员
  - `PKM/_Archiver.md` - 生命周期管理器

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
