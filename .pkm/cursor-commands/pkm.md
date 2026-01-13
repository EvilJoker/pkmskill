# PKM - Personal Knowledge Management

智能知识管理系统，基于 PARA+CODE 方法论，自动处理知识捕获、组织、蒸馏和归档。

## 快速使用

```text
/pkm inbox 学习笔记内容...     # 快速捕获
/pkm addProject                # 创建新项目
/pkm todo <内容>               # 添加新任务
/pkm                          # 智能全自动模式
/pkm help                     # 显示帮助
```

## 所有命令

### 🚀 快速捕获（最常用）

- `/pkm inbox <内容>` - 快速保存信息到 Inbox（自动识别任务，推荐使用 todo）
- `/pkm inbox --online <内容>` - 抓取网页内容并保存

**示例**：

```text
/pkm inbox React useEffect 的依赖数组如果为空会怎样？
/pkm inbox Python 装饰器详解 https://docs.python.org/...
/pkm inbox --online 这篇文章很有用 https://example.com
```

### 🤔 智能咨询

- `/pkm advice <问题>` - 默认模式（AI 通用知识 + 私域知识库）
- `/pkm advice --scope <范围> <问题>` - 指定范围模式

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
/pkm advice React 性能优化有哪些最佳实践？
/pkm advice --scope common React 18 新特性有哪些？
/pkm advice --scope local 上次 Redis 连接池问题怎么解决的？
/pkm advice --scope 20260113_143000_XXX 这个项目的架构设计是什么？
/pkm advice --scope common,local React 性能优化有哪些方法？
/pkm advice 这篇 TypeScript 笔记应该放哪个目录？
```

### 🤖 智能模式（推荐）

- `/pkm` - 全自动模式，依次执行所有需要的操作

### 📋 手动操作

- `/pkm addProject` - 创建新项目目录（自动命名为 时间戳_XXX）
- `/pkm todo <内容>` - 添加新任务（交互式补全：想法、4象限、计划、实现思路、关联项目）
- `/pkm todo list` - 列出所有任务（按4象限分组显示，支持筛选）
- `/pkm todo update <id/name>` - 更新任务进展（记录：日期 + 一句话进展）
- `/pkm todo ok <id/name>` - 完成任务（追问总结：内容、收益、价值评分，归档到 todo_archive.md）
- `/pkm todo del <id/name>` - 删除任务
- `/pkm classify` - 分类 Inbox 中的内容
- `/pkm synthesize` - 蒸馏所有达到阈值的主题
- `/pkm synthesize <主题>` - 蒸馏指定主题（如：/pkm synthesize React）
- `/pkm audit` - 审计所有包含草稿的主题
- `/pkm audit <主题>` - 审计指定主题（如：/pkm audit Python）
- `/pkm archive` - 归档所有包含 COMPLETED.md 的项目
- `/pkm archive <项目>` - 归档指定项目（如：/pkm archive UserAuth）
- `/pkm verify` - 仅验证知识库结构

### ℹ️ 帮助与信息

- `/pkm help` - 显示此帮助信息

## 执行流程

当你收到 `/pkm` 命令时：

### 1. 前置验证（必须）

参考 `.pkm/Skills/PKM/_Verifier.md`：

- 检查 5 个必需目录是否存在
- 生成操作白名单
- 验证失败则中止

### 2. 命令路由

根据命令参数执行对应操作：

#### `/pkm inbox <内容>`

调用 `.pkm/Skills/PKM/_Inbox.md`：

**默认模式**（不带 --online）：

1. 调用 Verifier 验证 Inbox 可写
2. AI 总结内容，生成文件名（格式：`简短标题_YYYYMMDD_HHMMSS.md`）
3. 写入 `30_Resources/00_Inbox/文件名.md`
4. 返回确认信息

**在线模式**（带 --online）：

1. 同上验证
2. 检测内容中的链接（http/https）
3. 访问链接，抓取网页内容（标题、正文、代码块）
4. 将 HTML 转换为 Markdown
5. 合并用户笔记 + 网页内容
6. 写入 Inbox
7. 返回确认信息（包含抓取统计）

**输出示例**：

```text
✅ 已捕获到 Inbox

📄 文件：30_Resources/00_Inbox/React_useEffect依赖数组_20260113143012.md
📅 时间：2026-01-13 14:30
```

**在线模式输出**：

```text
✅ 已捕获到 Inbox（在线模式）

📄 文件：30_Resources/00_Inbox/React18新特性_20260113143100.md
📅 时间：2026-01-13 14:31
🔗 链接：1 个（已抓取并整理）
📊 内容：用户笔记 + 网页内容（共 2,450 字）
```

#### `/pkm` (无参数)

智能判断并依次执行：

1. 扫描 `30_Resources/00_Inbox/` → 有文件 → 执行分类
2. 扫描 `20_Areas/AI_Synthesized/` → 有主题≥10文件 → 执行蒸馏
3. 扫描 `20_Areas/AI_Synthesized/` → 有[草稿]文件 → 执行审计
4. 扫描 `10_Projects/` → 有COMPLETED.md → 执行归档

#### `/pkm classify`

调用 `.pkm/Skills/PKM/_Classifier.md`：

- 扫描 Inbox 中的所有文件
- 判断类型：任务 / 知识片段 / 参考资料
- 分流到 Projects/Areas/Resources
- 智能归并主题（避免主题过度分散）

#### `/pkm synthesize [主题]`

调用 `.pkm/Skills/PKM/_Synthesizer.md`：

- 如果指定主题：蒸馏该主题
- 如果不指定：蒸馏所有达到阈值（10+文件）的主题
- 整合碎片知识，生成结构化草稿
- 标记为 `[草稿]_主题名.md`

#### `/pkm audit [主题]`

调用 `.pkm/Skills/PKM/_Auditor.md`：

- 如果指定主题：审计该主题
- 如果不指定：审计所有包含草稿的主题
- 对比 AI 草稿与 Manual 知识
- 生成更新建议清单

#### `/pkm addProject`

调用 `.pkm/Skills/PKM/_ProjectCreator.md`：

- 在 `10_Projects/` 下创建新项目目录
- 目录命名格式：`YYYYMMDD_HHMMSS_XXX`（时间戳在前，固定后缀 XXX）
- 初始化项目模版结构（Manual/ 和 AI_Generated/）
- 返回创建确认信息

**输出示例**：

```text
✅ 项目已创建

📁 目录：10_Projects/20260113_143000_XXX/
📅 时间：2026-01-13 14:30:00
📂 结构：
   ├── Manual/
   └── AI_Generated/
```

#### `/pkm todo [操作] [参数]`

调用 `.pkm/Skills/PKM/_TodoManager.md`：

**添加任务**：`/pkm todo <内容>`
- 识别任务类型
- 确认任务信息（想法、计划、实现思路、关联项目）
- 自动分类和补全
- 写入 `30_Resources/todo.md`

**更新任务**：`/pkm todo update <id/name>`
- 查找任务
- 记录进展（日期 + 一句话进展）
- 更新任务状态

**完成任务**：`/pkm todo ok <id/name>`
- 查找任务
- 追问补全总结（内容、收益、价值评分）
- 移动到 `30_Resources/todo_archive.md`

**删除任务**：`/pkm todo del <id/name>`
- 查找任务
- 确认删除
- 从 todo.md 中移除

**列出任务**：`/pkm todo list`
- 读取 todo.md
- 按状态分组显示
- 支持筛选（可选）

**输出示例**：

```text
✅ 任务已添加

📋 任务 ID：T-20260113-143000-001
📄 文件：30_Resources/todo.md
📅 创建时间：2026-01-13 14:30:00
```

#### `/pkm archive [项目]`

调用 `.pkm/Skills/PKM/_Archiver.md`：

- 如果指定项目：归档该项目
- 如果不指定：归档所有包含 COMPLETED.md 的项目
- 移动项目到 Archives
- 提取可复用知识回流到 Areas

#### `/pkm verify`

调用 `.pkm/Skills/PKM/_Verifier.md`：

- 仅执行验证，不执行其他操作

#### `/pkm help`

显示此帮助文档

### 3. 生成报告

执行完成后，生成结构化报告，包括：

- 执行的操作
- 处理的文件数量
- 结果概览
- 建议的后续操作

## 安全规则（严格执行）

### 🔒 权限控制

**只读区域**（AI 只能读取）：

- `20_Areas/Manual/`
- `10_Projects/*/Manual/`
- `.pkm/Skills/`

**可写区域**（AI 可以创建/修改/删除）：

- `10_Projects/*/AI_Generated/`
- `20_Areas/AI_Synthesized/`
- `30_Resources/00_Inbox/` ← inbox 命令写入这里
- `30_Resources/Library/`
- `40_Archives/`

**禁止区域**（绝对不能操作）：

- 知识库根目录外的任何路径

### ⚠️ 操作约束

1. 每次操作前必须执行 Verifier 验证
2. 不得修改 Manual/ 目录（人工知识区）
3. 不得删除或修改 .pkm/Skills/ 文件
4. 所有文件操作必须在白名单范围内
5. inbox 命令只能写入 `30_Resources/00_Inbox/`

### 🌐 在线模式安全

当使用 `/pkm inbox --online` 时：

- 仅访问用户提供的链接
- 不执行网页中的任何代码或脚本
- 仅提取文本内容（标题、正文、代码块）
- 如果抓取失败，提示用户手动复制或截图

## 日常工作流推荐

### 早上：捕获新想法

```text
/pkm inbox 昨天学到的 React 性能优化技巧...
/pkm inbox --online 这篇文章很有用 https://example.com
```

### 中午：快速记录

```text
/pkm inbox 刚解决的 Bug：邮件发送超时...
```

### 晚上：整理知识

```text
/pkm
# 自动执行：分类 Inbox → 蒸馏知识 → 审计草稿 → 归档项目
```

### 项目完成时

```bash
# 创建完成标记
echo "项目已完成" > 10_Projects/MyProject/COMPLETED.md
```

```text
/pkm archive
```

## 详细文档

- 完整架构：`docs/ARCHITECTURE.md`
- 使用指南：`.pkm/Skills/README.md`
- 主 Skill：`.pkm/Skills/PKM/Skill.md`
- 各模块：
  - `.pkm/Skills/PKM/_ProjectCreator.md` - 项目创建器
  - `.pkm/Skills/PKM/_TodoManager.md` - 待办任务管理器
  - `.pkm/Skills/PKM/_Inbox.md` - 快速捕获器
  - `.pkm/Skills/PKM/_Verifier.md` - 范围验证
  - `.pkm/Skills/PKM/_Classifier.md` - 智能分类
  - `.pkm/Skills/PKM/_Synthesizer.md` - 知识蒸馏
  - `.pkm/Skills/PKM/_Auditor.md` - 质量审计
  - `.pkm/Skills/PKM/_Archiver.md` - 生命周期管理

## 知识库结构

```text
<root>/
├── 10_Projects/          # 短期项目
│   └── */
│       ├── Manual/       # 人工知识（只读）
│       └── AI_Generated/ # AI 生成（可写）
├── 20_Areas/             # 长期领域
│   ├── Manual/           # 人工知识（只读）
│   └── AI_Synthesized/   # AI 蒸馏（可写）
├── 30_Resources/         # 参考资料
│   ├── 00_Inbox/         # 待分类（可写）← inbox 命令写入这里
│   └── Library/          # 已分类（可写）
├── 40_Archives/          # 归档（可写）
└── .pkm/                 # 系统文件
    └── Skills/           # Skill 定义（只读）
```

## 模块映射

| 命令 | 模块文件 | 说明 |
| --- | --- | --- |
| `addProject` | `_ProjectCreator.md` | 项目创建器 |
| `inbox` | `_Inbox.md` | 快速捕获器 |
| `classify` | `_Classifier.md` | 智能分类器 |
| `synthesize` | `_Synthesizer.md` | 知识蒸馏器 |
| `audit` | `_Auditor.md` | 质量审计员 |
| `archive` | `_Archiver.md` | 生命周期管理器 |
| `verify` | `_Verifier.md` | 范围守卫 |

---

**版本**：v1.0.0
**方法论**：PARA + CODE
**支持工具**：Cursor, Claude Code
**更新日期**：2026-01-13
