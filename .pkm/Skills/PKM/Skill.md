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

- ✅ 检查知识库结构（Verifier）
- 📥 如果 Inbox 有文件 → 自动分类（Classifier）
- 📚 如果某主题积累 10+ 碎片 → 自动蒸馏（Synthesizer）
- 🔍 如果有新草稿 → 自动审计（Auditor）
- 📦 如果有项目标记完成 → 自动归档（Archiver）

### 查看帮助

```text
@pkm help
```

显示完整的命令列表和使用说明。

---

## 命令列表

### 智能模式（推荐）

```text
@pkm
```

全自动模式，依次执行所有需要的操作。

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

### 手动指定操作

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

## 工作流程

### 1. 前置验证（自动执行）

调用 `_Verifier` 模块：

- ✅ 检查知识库结构（5 个必需目录）
- ✅ 生成操作白名单
- ❌ 验证失败则立即中止

### 2. 智能路由

根据命令参数或自动检测，路由到相应模块：

**智能模式（无参数）**：

1. 扫描 `30_Resources/00_Inbox/` → 如果有文件 → 调用 `_Classifier`
2. 扫描 `20_Areas/AI_Synthesized/` → 如果有主题 ≥ 10 个文件 → 调用 `_Synthesizer`
3. 扫描 `20_Areas/AI_Synthesized/` → 如果有 `[草稿]` 标记的文件 → 调用 `_Auditor`
4. 扫描 `10_Projects/` → 如果有 `COMPLETED.md` → 调用 `_Archiver`

**手动模式（带参数）**：

- `inbox <内容>` → 先调用 `_Verifier`，再调用 `_Inbox`（快速捕获）
- `inbox --online <内容>` → 先调用 `_Verifier`，再调用 `_Inbox`（在线模式）
- `advice <问题>` → 先调用 `_Verifier`，再调用 `_Advisor`（默认模式：common + local）
- `advice --scope <范围> <问题>` → 先调用 `_Verifier`，再调用 `_Advisor`（指定范围）
- `classify` → 先调用 `_Verifier`，再调用 `_Classifier`
- `synthesize` → 先调用 `_Verifier`，再调用 `_Synthesizer`（蒸馏所有达到阈值的主题）
- `synthesize <主题>` → 先调用 `_Verifier`，再调用 `_Synthesizer`（蒸馏指定主题）
- `audit` → 先调用 `_Verifier`，再调用 `_Auditor`（审计所有草稿）
- `audit <主题>` → 先调用 `_Verifier`，再调用 `_Auditor`（审计指定主题）
- `archive` → 先调用 `_Verifier`，再调用 `_Archiver`（归档所有已完成项目）
- `archive <项目名>` → 先调用 `_Verifier`，再调用 `_Archiver`（归档指定项目）
- `verify` → 仅调用 `_Verifier`
- `help` → 显示帮助信息

### 3. 执行与报告

执行相应操作，生成统一格式的报告。

---

## 内部模块说明

PKM 由 7 个内部模块组成，每个模块负责知识管理的一个环节：

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
- 确认 `30_Resources/00_Inbox/` 存在且可写

**核心功能**：

- 快速保存文本、想法、链接到 `30_Resources/00_Inbox/`
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
  - 优先级排序（Manual > Projects > Archives）
  - 内容摘要提取

- **应用场景**：
  - 分类建议：不知道内容放哪里时咨询
  - 知识查询：快速找到相关笔记
  - 经验参考：查找历史解决方案
  - 决策支持：基于已有经验给建议

**详细文档**：`_Advisor.md`

---

### 📋 _Classifier（智能分流器）

**职责**：处理 Inbox 中的未分类内容，分流到 PARA 体系

**对应阶段**：CODE 的 **Capture** → **Organize**

**触发**：

- 智能模式：Inbox 有文件时
- 手动调用：`@pkm classify`

**核心功能**：

- 扫描 `30_Resources/00_Inbox/`
- 判断类型：可执行任务 / 知识片段 / 参考资料
- 自动分流到 `10_Projects/*/AI_Generated/` 或 `20_Areas/AI_Synthesized/` 或 `30_Resources/Library/`
- 智能归并：避免主题过度分散
- 支持二级分类：如 `Cluster_React/Hooks_useEffect.md`

**详细文档**：`_Classifier.md`

---

### 🧪 _Synthesizer（知识蒸馏器）

**职责**：整合 AI_Synthesized 中的碎片知识，生成结构化草稿

**对应阶段**：CODE 的 **Organize** → **Distill**

**触发**：

- 智能模式：某主题积累 10+ 条原子块时
- 手动调用：`@pkm synthesize` → 蒸馏所有达到阈值（10+）的主题
- 手动调用：`@pkm synthesize <主题>` → 蒸馏指定主题

**核心功能**：

- 扫描主题目录（如 `20_Areas/AI_Synthesized/Cluster_React/`）
- 去重、归并、逻辑排序
- 生成结构化草稿，标记为 `[草稿]_主题名.md`

**详细文档**：`_Synthesizer.md`

---

### 🔍 _Auditor（质量审计员）

**职责**：对比 AI 草稿与 Manual 知识，生成更新建议清单

**对应阶段**：CODE 的 **Distill**（质量审计）

**触发**：

- 智能模式：Synthesizer 生成草稿后自动触发
- 手动调用：`@pkm audit` → 审计所有包含草稿的主题
- 手动调用：`@pkm audit <主题>` → 审计指定主题

**核心功能**：

- 读取 AI 草稿（`[草稿]_*.md`）
- 对比 `20_Areas/Manual/` 中的现有知识
- 识别新增/过时/冗余内容
- 生成更新建议清单（`主题_更新建议_日期.md`）

**详细文档**：`_Auditor.md`

---

### 📦 _Archiver（生命周期管理器）

**职责**：归档完成的项目，提取可复用知识回流到 Areas

**对应阶段**：CODE 的 **Express**（生命周期管理）

**触发**：

- 智能模式：发现 `COMPLETED.md` 时自动归档
- 手动调用：`@pkm archive` → 归档所有包含 COMPLETED.md 的项目
- 手动调用：`@pkm archive <项目名>` → 归档指定项目（即使没有 COMPLETED.md）

**核心功能**：

- 识别已完成的项目（存在 `COMPLETED.md` 或手动指定）
- 移动整个项目到 `40_Archives/`
- 提取可复用知识（架构决策、经验教训）
- 回流到 `20_Areas/AI_Synthesized/`

**详细文档**：`_Archiver.md`

---

## 使用示例

### 场景 1：日常工作流（完全自动）

```text
# 每天结束前
@pkm

# 输出示例：
✅ Verifier 验证通过
📥 检测到 Inbox 有 8 个文件
🔄 执行 Classifier...
  ├─ 任务 → Projects: 3 个
  ├─ 知识 → Areas: 5 个
  └─ Inbox 已清空 ✅

📊 检测到 Cluster_React 有 12 个文件（达到蒸馏阈值）
🔄 执行 Synthesizer...
  └─ 生成草稿：[草稿]_React_Hooks知识总结.md ✅

📋 检测到 1 个新草稿
🔄 执行 Auditor...
  └─ 生成更新建议：React_更新建议_20260113.md ✅

🎉 完成！请查看：
  - AI_Synthesized/Cluster_React/[草稿]_React_Hooks知识总结.md
  - AI_Synthesized/Audit_Reports/React_更新建议_20260113.md
```

---

### 场景 2：只分类 Inbox

```text
@pkm classify

# 输出示例：
✅ Verifier 验证通过
📥 处理 Inbox 中的 8 个文件...

## 分流统计

### 可执行任务 → Projects：3 个
- 实现用户登录功能.md → 10_Projects/UserAuth/AI_Generated/
- 修复支付Bug.md → 10_Projects/Payment/AI_Generated/

### 知识片段 → Areas/AI_Synthesized：5 个
- React_useEffect.md → 20_Areas/AI_Synthesized/Cluster_React/Hooks_useEffect.md
- Python_装饰器.md → 20_Areas/AI_Synthesized/Cluster_Python/高级特性_装饰器.md

✅ Inbox 已清空！
```

---

### 场景 3：蒸馏特定主题

```text
@pkm synthesize React

# 输出示例：
✅ Verifier 验证通过
📚 扫描主题：Cluster_React
  ├─ 找到 15 个原子块
  ├─ 去重后：12 个独特知识点
  └─ 生成草稿：[草稿]_React_Hooks知识总结.md

## 草稿目录

1. 概念：React Hooks 是什么
2. 基本用法
   - useState
   - useEffect
3. 进阶技巧
4. 常见问题
5. 最佳实践

📋 建议：执行 @pkm audit React 查看更新建议
```

---

### 场景 4：查看帮助信息

```text
@pkm help

# 输出示例：
📚 PKM - Personal Knowledge Management v1.0.0

基于 PARA+CODE 的智能知识管理系统

## 📋 命令列表

### 智能模式（推荐）
  @pkm                       全自动模式，依次执行所有需要的操作

### 快速捕获
  @pkm inbox <内容>                 快速捕获（自动识别标题、标签、链接）
  @pkm inbox --online <内容>        在线模式（抓取并整理链接内容）

### 手动模式
  @pkm classify              分类 Inbox 中的内容
  @pkm synthesize            蒸馏所有达到阈值（10+）的主题
  @pkm synthesize <主题>     蒸馏指定主题（如：React）
  @pkm audit                 审计所有包含草稿的主题
  @pkm audit <主题>          审计指定主题（如：Python）
  @pkm archive               归档所有包含 COMPLETED.md 的项目
  @pkm archive <项目名>      归档指定项目（如：UserAuth）
  @pkm verify                仅验证知识库结构

### 帮助
  @pkm help                  显示此帮助信息

## 🚀 快速开始

1. 初始化知识库：
   mkdir -p 10_Projects 20_Areas/{Manual,AI_Synthesized} \
            30_Resources/{00_Inbox,Library} 40_Archives .pkm/Skills

2. 开始使用：
   @pkm                       # 自动处理所有任务

## 📚 详细文档

- 主文档：.pkm/Skills/PKM/Skill.md
- 使用指南：.pkm/Skills/README.md
- 架构说明：docs/ARCHITECTURE.md

## 💡 工作流程

Capture（捕获）→ Organize（组织）→ Distill（蒸馏）→ Express（表达）
   ↓              ↓               ↓              ↓
 _Inbox      _Classifier     _Synthesizer    _Archiver
                           → _Auditor

## 🛡️ 安全机制

✅ 双重防火墙：AI 区 vs Manual 区，知识库内 vs 外
✅ 白名单强制：所有操作限制在白名单内
✅ 只读 Manual：AI 永远不直接修改 Manual 区
```

---

## 安全机制

### 双重防火墙

1. **内部防火墙**：AI 区 vs Manual 区

   - AI 可以自由修改 `AI_Synthesized/`, `AI_Generated/`
   - AI **只读** `Manual/`，绝不直接修改

2. **外部防火墙**：知识库内 vs 知识库外

   - Verifier 强制检查目录结构
   - 禁止操作知识库外的任何路径

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
mkdir -p 10_Projects 20_Areas/{Manual,AI_Synthesized} 30_Resources/{00_Inbox,Library} 40_Archives .pkm/Skills
```

### 问题：文件被标记为"待确认"

**原因**：Classifier 无法判断文件类型。

**解决**：

1. 查看 `20_Areas/AI_Synthesized/Unsorted/[待确认]_文件名.md`
2. 人工判断类型，手动移动到正确位置

### 问题：草稿质量差

**原因**：原子块质量参差不齐。

**解决**：

1. 忽略草稿，直接手动编写 Manual
2. 或重新收集高质量的原子块

---

## 高级配置

### 自定义蒸馏阈值

默认：某主题积累 10+ 个文件时触发蒸馏。

如果你希望调整阈值，可以在调用时指定：

```text
@pkm synthesize React --threshold 20
```

### 跳过某些模块

如果只想执行部分操作：

```text
@pkm --skip-synthesizer --skip-auditor
```

---

## 反馈与支持

如果在使用过程中遇到问题：

1. 执行 `@pkm help` 查看命令列表
2. 查看具体模块文档（`_Verifier.md` 等）
3. 根据你的需求修改内部模块

---

祝你的知识管理之旅愉快！🚀
