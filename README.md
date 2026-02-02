# PKM Skill - 智能知识管理工具包

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/EvilJoker/pkmskill)

> 基于 **PARA + CODE + 金字塔原理** 的 AI 驱动知识管理系统，让 AI 成为你的知识管家

---

## 📖 什么是 PKM Skill？

PKM Skill 是一个智能知识管理工具包，通过 AI 自动化处理知识的捕获、组织、蒸馏和表达。你只需专注于思考和验证，繁琐的知识整理工作交给 AI。

### 核心理念：PARA + CODE + 金字塔原理

#### 🗂️ PARA（知识组织结构）

五层生命周期管理，让知识自然流动：

- **10_Projects（项目）**：短期目标，有明确截止日期
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
- 📋 **任务管理**：`@pkm todo` 管理待办任务，支持4象限管理方法
- 🏗️ **项目创建**：`@pkm addProject` 快速创建项目目录
- 🤖 **智能自动化**：自动分类、蒸馏落地、归档
- 🔌 **Organizer 插件**：可选按内容类型用模版预处理（如故障总结、会议纪要），再分类归位
- 🔒 **安全防护**：严格的范围守卫，保护人工知识区域
- 🔄 **CODE 闭环**：完整的 Capture → Organize → Distill → Express 流程
- 📦 **即装即用**：一行命令安装到任何项目

## 🚀 快速安装

### 方式 1：一键安装（推荐）

```bash
# 在你的知识库项目根目录下执行
cd /path/to/your/knowledge-base

# 自动从 GitHub 下载并安装
curl -fsSL https://raw.githubusercontent.com/EvilJoker/pkmskill/main/scripts/install.sh | bash
```

安装脚本会自动：

- ✅ 从 GitHub 下载最新版本
- ✅ 安装 Skills 文件（Claude Code 支持）
- ✅ 配置 Cursor Commands（创建软链接）
- ✅ 初始化知识库结构
- ✅ 清理临时文件

### 方式 2：本地安装

```bash
# 1. 克隆本仓库
git clone https://github.com/EvilJoker/pkmskill.git
cd pkmskill

# 2. 进入你的知识库项目目录
cd /path/to/your/knowledge-base

# 3. 运行安装脚本
bash /path/to/pkmskill/scripts/install.sh
```

## 📖 使用方法

### 在 Cursor 中使用

安装后，在 Cursor 聊天窗口中输入：

```text
@pkm inbox 学习笔记...
@pkm help
```

### 在 Claude Code 中使用

1. 确保 Skills 目录已正确安装到 `.pkm/Skills/`
2. 在 Claude Code 中输入：

```text
@pkm inbox 学习笔记...
@pkm help
```

### 常用命令

| 命令 | 功能 | 使用场景 |
| ---- | ---- | -------- |
| `@pkm inbox <内容>` | 快速捕获 | 随时记录想法、笔记 |
| `@pkm inbox --online <内容>` | 抓取网页内容 | 保存网页文章 |
| `@pkm addProject [项目名称]` | 创建新项目 | 快速创建项目目录（格式：YYYYMMDD_HHMMSS_<项目名称>，如果未提供名称则询问） |
| `@pkm todo <内容>` | 添加新任务 | **任务管理**：添加待办任务，交互式补全信息（想法、4象限、计划等） |
| `@pkm todo list` | 列出所有任务 | **任务管理**：查看所有任务，按4象限分组，支持筛选 |
| `@pkm todo update <id/name>` | 更新任务进展 | **任务管理**：记录任务进展（日期 + 一句话描述） |
| `@pkm todo ok <id/name>` | 完成任务 | **任务管理**：完成任务，追问总结（内容、收益、价值评分），归档 |
| `@pkm todo del <id/name>` | 删除任务 | **任务管理**：删除不需要的任务 |
| `@pkm advice <问题>` | 智能咨询 | 默认模式（AI + 知识库） |
| `@pkm advice --scope <范围> <问题>` | 指定范围咨询 | 精确控制知识来源 |
| `@pkm` | **一键整理知识**（最常用） | 每天结束时执行，自动完成所有整理工作 |

#### `@pkm` 一键整理知识详解

`@pkm` 是最常用的命令，它会自动检测并执行所有需要的操作：

```text
执行流程：
1. ✅ 验证知识库结构（Verify）
2. 🗄️ 如果有项目标记完成 → 自动归档（Archive）
3. 📦 如果 50_Raw/ 有文件 → 自动组织分类（Organize，含可选插件预处理：故障总结、会议纪要等模版）
4. 💎 如果 20_Areas/03notes/ 有新增/变动 → 自动提炼（Distill）
```

**推荐使用**：每天结束前执行一次 `@pkm`，系统会自动处理所有待办事项。

#### 手动子流程（通常不需要单独执行）

以下命令是 `@pkm` 一键整理知识的子流程，通常由 `@pkm` 自动调用。如需手动执行：

| 命令 | 功能 | 说明 |
| ---- | ---- | ---- |
| `@pkm organize` | 组织分类 50_Raw/ 中的内容 | `@pkm` 会自动执行，无需单独调用 |
| `@pkm distill` | 提炼 20_Areas/03notes/ 中的知识 | `@pkm` 会自动执行，如需手动调用可执行此命令 |
| `@pkm archive` | 归档项目 | `@pkm` 会自动执行，无需单独调用 |

#### 任务管理功能

新增的待办任务管理功能，支持4象限管理方法：

| 命令 | 功能 | 说明 |
| ---- | ---- | ---- |
| `@pkm todo <内容>` | 添加新任务 | 交互式询问，补全任务信息（想法、4象限、计划等） |
| `@pkm todo list` | 列出所有任务 | 按4象限分组显示，支持筛选 |
| `@pkm todo update <id/name>` | 更新任务进展 | 记录进展（日期 + 一句话描述） |
| `@pkm todo ok <id/name>` | 完成任务 | 追问总结（内容、收益、价值评分），归档到 todo_archive.md |
| `@pkm todo del <id/name>` | 删除任务 | 删除指定任务 |

**4象限管理**：
- 🔴 第一象限：重要且紧急
- 🟡 第二象限：重要但不紧急
- 🟠 第三象限：不重要但紧急
- 🟢 第四象限：不重要且不紧急

完整文档：[架构文档](docs/ARCHITECTURE.md)

## 📂 知识库结构

安装后，你的项目会有以下结构：

```text
your-knowledge-base/
├── .pkm/
│   ├── Skills/                  # PKM 工具包（Claude Code）
│   │   └── PKM/
│   │       ├── Skill.md         # 主入口
│   │       ├── _ProjectCreator.md # 项目创建器
│   │       ├── _TodoManager.md  # 待办任务管理器
│   │       ├── _Inbox.md        # 快速捕获器
│   │       ├── _Advisor.md      # 智能顾问
│   │       ├── _Verifier.md     # 范围守卫
│   │       ├── _Organizer.md     # 智能组织器
│   │       ├── _Distiller.md     # 知识提炼器
│   │       ├── _Archiver.md      # 生命周期管理
│   │       └── plugin/           # Organizer 插件（可选）：按内容类型用模版预处理
│   │           ├── Skill.md      # 插件注册表
│   │           ├── template_summary_problem.md   # 故障/问题总结模版
│   │           └── template_meeting_minutes.md    # 会议纪要模版
│   └── cursor-commands/
│       └── pkm.md               # Cursor Commands 定义
├── .cursor/
│   └── commands/
│       └── pkm.md → ../../.pkm/cursor-commands/pkm.md  # 软链接
├── 10_Projects/                 # 短期项目
│   └── <时间戳>_<项目名称>/     # 项目目录（格式：YYYYMMDD_HHMMSS_<项目名称>）
│       └── manual/              # 受保护区：项目金标准、架构决策（AI 只读）
├── 20_Areas/                    # 长期领域
│   ├── manual/                  # 受保护区：全域共用素材区（AI 只读）
│   ├── 01principles/            # 原则层：被提炼的顶层智慧
│   ├── 02playbooks/             # 应用层：标准化流程
│   ├── 02templates/             # 应用层：可复用模版
│   ├── 02cases/                 # 应用层：具体案例
│   └── 03notes/                 # 整理知识层：按领域分类
├── 30_Resources/                # 参考资料
│   ├── Library/                 # 资料库
│   ├── summary/                 # 报告汇总
│   ├── todo.md                  # 待办任务列表
│   └── todo_archive.md          # 已完成任务归档
├── 40_Archives/                 # 归档
└── 50_Raw/                      # 统一素材区
    ├── inbox/                   # 待分类（inbox 命令写入这里）
    └── merged/                  # 合并后的素材
```

## 🔄 更新工具包

```bash
# 从远程更新（推荐）
curl -fsSL https://raw.githubusercontent.com/EvilJoker/pkmskill/main/scripts/install.sh | bash -s -- --update

# 或本地安装
bash /path/to/pkmskill/scripts/install.sh --update
```

## 🗑️ 卸载

```bash
# 使用卸载脚本
bash /path/to/pkmSkill/scripts/uninstall.sh

# 或从远程卸载
curl -fsSL https://raw.githubusercontent.com/EvilJoker/pkmskill/main/scripts/uninstall.sh | bash
```

## 🤝 支持的 AI 工具

- ✅ **Cursor** - 通过 `.cursor/commands/pkm.md` 配置（使用 `@pkm` 命令）
- ✅ **Claude Code** - 通过 Skills 目录自动识别（使用 `@pkm` 命令）
- 🚧 **Gemini CLI** - 即将支持

## 💡 日常工作流

### 早上：快速捕获

```text
@pkm inbox 昨晚想到的新点子...
@pkm inbox --online 这篇文章很有用 https://example.com
```

### 工作中：实时记录

```text
@pkm inbox Bug修复：邮件发送超时问题
@pkm inbox React性能优化技巧...
```

### 任务管理：规划与追踪

```text
# 添加新任务（交互式补全信息）
@pkm todo 实现用户认证功能
@pkm todo 优化数据库查询性能
@pkm todo 学习 TypeScript 高级特性

# 查看任务列表（按4象限分组）
@pkm todo list
@pkm todo list --quadrant 1        # 只看第一象限（重要且紧急）

# 更新任务进展
@pkm todo update T-20260113-143000-001
# 或
@pkm todo update 优化用户登录

# 完成任务
@pkm todo ok T-20260113-143000-001
# 系统会追问：内容、收益、价值评分

# 删除任务
@pkm todo del T-20260113-143000-001

@pkm addProject [项目名称]
```

**💡 任务管理是日常工作的重要组成部分**，通过4象限管理方法，帮助你：
- 🔴 优先处理重要且紧急的任务
- 🟡 规划重要但不紧急的任务
- 🟠 快速处理不重要但紧急的任务
- 🟢 延后或删除不重要且不紧急的任务


### 开始任务：创建和归档项目

项目是临时性的任务，可以将项目资料集中放在一个目录下，方便完成任务。
当项目完成后，可以将项目资料归档到 Areas 中，方便后续查阅。

```text
@pkm addProject [项目名称]  # 创建新项目（如果未提供名称则询问）
@pkm archive 归档项目，提取可复用知识回流到 Areas
```

### 遇到问题：智能咨询

```text
@pkm advice React 性能优化有哪些最佳实践？
@pkm advice --scope common React 18 新特性有哪些？
@pkm advice --scope local 上次 Redis 连接池问题怎么解决的？
@pkm advice --scope 20260113_143000_用户认证系统 这个项目的架构设计是什么？
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

### 迁移旧笔记：逐步导入

如果你有旧的笔记需要迁移到新系统，建议采用**逐步迁移**的方式：

**❌ 不推荐**：一次性将所有旧笔记放入 `50_Raw/`
- 日志量太大，AI 可能会忽略部分内容
- 难以审核和验证归纳结果
- 容易造成信息过载

**✅ 推荐**：逐步迁移，分批处理

```text
# 1. 选择一小批相关笔记（建议每次 5-10 个文件）
# 2. 复制到 50_Raw/ 或 50_Raw/inbox/
cp /path/to/old/notes/*.md 50_Raw/

# 3. 执行一键整理
@pkm
# 4. 重复步骤 1-3，逐步迁移下一批笔记
```

**迁移建议**：
- 📦 **按主题分批**：每次迁移一个主题的笔记（如：React、Python、架构设计等）
- 🔍 **审核归纳结果**：每次迁移后都要审核 AI 的分类和归纳结果
- ⏱️ **控制节奏**：不要急于一次性迁移所有内容，保持节奏，确保质量
- 📝 **保留原文件**：迁移过程中保留原始文件，确认无误后再删除



## 📚 文档

- [架构设计](docs/ARCHITECTURE.md) - 完整架构说明
- [Skills 使用指南](.pkm/Skills/README.md) - 详细使用文档

## 🛠️ 开发

```bash
# 克隆仓库
git clone https://github.com/EvilJoker/pkmskill.git
cd pkmSkill

# 在测试项目中安装
cd /path/to/test-project
bash /path/to/pkmSkill/scripts/install.sh
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
