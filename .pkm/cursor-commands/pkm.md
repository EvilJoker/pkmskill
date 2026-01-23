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

### 主流程命令

- `/pkm` - 智能整理主流程，自动执行 Verify → Archive → Organize → Distill 四个阶段

### 独立流程命令

#### 捕获流程

- `/pkm inbox <内容>` - 快速捕获碎片化信息到 `50_Raw/inbox/`
- `/pkm inbox --online <内容>` - 抓取网页内容并保存

**示例**：

```text
/pkm inbox React useEffect 的依赖数组如果为空会怎样？
/pkm inbox Python 装饰器详解 https://docs.python.org/...
/pkm inbox --online 这篇文章很有用 https://example.com
```

#### Express 流程

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

### 扩展功能命令

#### 任务管理

- `/pkm todo <内容>` - 添加新任务（交互式补全：想法、4象限、计划、实现思路、关联项目）
- `/pkm todo list` - 列出所有任务（按4象限分组显示，支持筛选）
- `/pkm todo update <id/name>` - 更新任务进展（记录：日期 + 一句话进展）
- `/pkm todo ok <id/name>` - 完成任务（追问总结：内容、收益、价值评分，归档到 todo_archive.md）
- `/pkm todo del <id/name>` - 删除任务

#### 项目创建

- `/pkm addProject` - 创建新项目目录（自动命名为 时间戳_XXX）

#### 手动操作（主流程子命令）

- `/pkm organize` - 组织分类 50_Raw/ 中的内容
- `/pkm distill` - 提炼 20_Areas/03notes/ 中的知识
- `/pkm distill <主题>` - 提炼指定主题（如：/pkm distill React）
- `/pkm archive` - 归档所有包含 COMPLETED.md 的项目
- `/pkm archive <项目>` - 归档指定项目（如：/pkm archive UserAuth）
- `/pkm verify` - 仅验证知识库结构

#### 帮助

- `/pkm help` - 显示此帮助信息

## 执行流程

当你收到 `/pkm` 命令时：

### 1. 前置验证（必须）

参考 `.pkm/Skills/PKM/_Verifier.md`：

- 检查 6 个必需目录是否存在（10_Projects、20_Areas、30_Resources、40_Archives、50_Raw、.pkm）
- 生成操作白名单
- 验证失败则中止

### 2. 命令路由

根据命令参数执行对应操作：

#### `/pkm inbox <内容>`

调用 `.pkm/Skills/PKM/_Inbox.md`：

**默认模式**（不带 --online）：

1. 调用 Verifier 验证 50_Raw/inbox/ 可写
2. AI 总结内容，生成文件名（格式：`YYYYMMDD_HHMMSS_标题_inbox.md`）
3. 写入 `50_Raw/inbox/文件名.md`
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

📄 文件：50_Raw/inbox/20260113_143012_React_useEffect依赖数组_inbox.md
📅 时间：2026-01-13 14:30
```

**在线模式输出**：

```text
✅ 已捕获到 Inbox（在线模式）

📄 文件：50_Raw/inbox/20260113_143100_React18新特性_inbox.md
📅 时间：2026-01-13 14:31
🔗 链接：1 个（已抓取并整理）
📊 内容：用户笔记 + 网页内容（共 2,450 字）
```

#### `/pkm` (无参数)

智能判断并依次执行：

1. ✅ 验证知识库结构（Verifier）
2. 🗄️ 扫描 `10_Projects/` → 有COMPLETED.md → 执行归档（Archiver）
3. 📦 扫描 `50_Raw/` → 有文件 → 执行组织分类（Organizer）
4. 💎 扫描 `20_Areas/03notes/` → 有新增/变动 → 执行提炼（Distiller）

#### `/pkm organize`

调用 `.pkm/Skills/PKM/_Organizer.md`：

- 扫描 `50_Raw/` 中的所有文件（包含 `inbox/` 和其他待分类素材）
- 按主题/类型合并同类内容到 `50_Raw/merged/`
- 判断类型：可执行任务 / 知识片段 / 参考资料
- 分类归位：
  - 任务 → `10_Projects/`（直接放在项目目录下）
  - 知识 → `20_Areas/03notes/<领域>/`（先放在 notes 层）
  - 资料 → `30_Resources/Library/`
- 整理完清空 `50_Raw/`

#### `/pkm distill [主题]`

调用 `.pkm/Skills/PKM/_Distiller.md`：

- 扫描 `20_Areas/03notes/` 各领域目录
- 与已有知识深度整合（去重、交叉引用、结构化）
- 按金字塔原理提炼：
  - 零散知识（notes）+ areas 区的 manual 区（只读）→ 整理知识（notes 内按领域分类）
  - 整理知识 → 应用知识（playbooks/templates/cases）
  - 应用知识 → 原则知识（principles）
- 沉淀到对应目录并生成报告到 `30_Resources/summary/`

#### `/pkm addProject`

调用 `.pkm/Skills/PKM/_ProjectCreator.md`：

- 在 `10_Projects/` 下创建新项目目录
- 目录命名格式：`YYYYMMDD_HHMMSS_XXX`（时间戳在前，固定后缀 XXX）
- 初始化项目模版结构（manual/ 目录）
- 返回创建确认信息

**输出示例**：

```text
✅ 项目已创建

📁 目录：10_Projects/20260113_143000_XXX/
📅 时间：2026-01-13 14:30:00
📂 结构：
   └── manual/
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

- `20_Areas/manual/`
- `10_Projects/*/manual/`
- `.pkm/Skills/`

**可写区域**（AI 可以创建/修改/删除）：

- `50_Raw/` ← inbox 命令写入 `50_Raw/inbox/`
- `10_Projects/*/`（排除 manual/）
- `20_Areas/03notes/`
- `20_Areas/02playbooks/`
- `20_Areas/02templates/`
- `20_Areas/02cases/`
- `20_Areas/01principles/`
- `30_Resources/Library/`
- `40_Archives/`

**禁止区域**（绝对不能操作）：

- 知识库根目录外的任何路径

### ⚠️ 操作约束

1. 每次操作前必须执行 Verifier 验证
2. 不得修改 manual/ 目录（受保护区）
3. 不得删除或修改 .pkm/Skills/ 文件
4. 所有文件操作必须在白名单范围内
5. inbox 命令只能写入 `50_Raw/inbox/`

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
# 自动执行：Verify → Archive → Organize → Distill
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
  - `.pkm/Skills/PKM/_Organizer.md` - 智能组织器
  - `.pkm/Skills/PKM/_Distiller.md` - 知识提炼器
  - `.pkm/Skills/PKM/_Archiver.md` - 生命周期管理

## 知识库结构

```text
<root>/
├── 10_Projects/          # 短期项目
│   └── */
│       └── manual/       # 受保护区（AI 只读）
├── 20_Areas/             # 长期领域
│   ├── manual/           # 受保护区（AI 只读）
│   ├── 01principles/     # 原则层（AI 可写）
│   ├── 02playbooks/      # 应用层：标准化流程（AI 可写）
│   ├── 02templates/      # 应用层：可复用模版（AI 可写）
│   ├── 02cases/          # 应用层：具体案例（AI 可写）
│   └── 03notes/          # 整理知识层（AI 可写）
├── 30_Resources/         # 参考资料
│   ├── Library/          # 资料库（可写）
│   └── summary/          # 报告汇总（可写）
├── 40_Archives/          # 归档（可写）
├── 50_Raw/               # 统一素材区
│   ├── inbox/            # 待分类（可写）← inbox 命令写入这里
│   └── merged/           # 合并后的素材（可写）
└── .pkm/                 # 系统文件
    └── Skills/           # Skill 定义（只读）
```

## 模块映射

| 命令 | 模块文件 | 说明 |
| --- | --- | --- |
| `addProject` | `_ProjectCreator.md` | 项目创建器 |
| `inbox` | `_Inbox.md` | 快速捕获器 |
| `organize` | `_Organizer.md` | 智能组织器 |
| `distill` | `_Distiller.md` | 知识提炼器 |
| `archive` | `_Archiver.md` | 生命周期管理器 |
| `verify` | `_Verifier.md` | 范围守卫 |

---

**版本**：v1.0.0
**方法论**：PARA + CODE
**支持工具**：Cursor, Claude Code
**更新日期**：2026-01-13
