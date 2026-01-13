# 知识管理系统架构方案

这套方案的核心目标是构建一个**"自清洁、自进化"**的知识系统。它将你从琐碎的文件搬运中解放出来，让你专注于最核心的"思考"与"验证"。

以下是基于 **Cursor/Claude Code/Gemini CLI + Git + PARA + CODE** 的全套管理方案：

---

## 一、 核心逻辑：PARA 四层 + 双轨制 + Skill 守门

### 1.1 PARA 四层结构（生命周期管理）

方案采用 **PARA** 作为顶层组织逻辑，让知识按时间维度自然流动：

- **10_Projects（项目）**：有明确截止日期的任务。完成后自动归档到 `40_Archives`。
- **20_Areas（领域）**：长期关注的责任领域。这是知识沉淀的核心区域。
- **30_Resources（资源）**：感兴趣但暂未深度加工的素材。`00_Inbox` 是所有信息的捕捉起点。
- **40_Archives（归档）**：已完成的项目和不再活跃的领域。定期清理，保持系统轻量。

### 1.2 双轨制（人机协作的防火墙）

在 **10_Projects** 和 **20_Areas** 内部，实施严格的双轨制：

**在 20_Areas（长期知识）：**

- **📜 Manual（人脑主权区）**：你亲手验证过的"真理"。按 Category 严格分类（如 `Programming/React.md`）。**AI 只读不写**。
- **🤖 AI_Synthesized（AI 自由区）**：AI 自动生成的草稿、聚类、周报。自组织、可删除、零心理负担。**AI 可自由创建/修改/删除**。

**在 10_Projects（活跃项目）：**

- **📜 Manual（项目金标准）**：架构设计文档、技术决策记录（ADR）、核心 API 规范。这些是项目的"宪法"。
- **🤖 AI_Generated（项目流水）**：Bug 记录、测试日志、会议纪要、AI 生成的代码注释。这些可以随时重建。

### 1.3 CODE 流动 + PKM 统一驱动（管理逻辑）

**CODE 是知识在 PARA 四层之间的流动路径，由 `@pkm` 统一驱动**：

```text
@pkm (统一入口)
    ↓
🔍 Verifier (前置检查：确认工作范围)
    ↓
📥 Capture (快速捕获到 Inbox)
    ↓ 【Inbox 模块：智能捕获】
    ↓ 【Classifier 模块：智能分流】
📦 Organize (分流到 10_Projects / 20_Areas / 30_Resources)
    ↓ 【Synthesizer 模块】
💎 Distill (从 AI_Synthesized 晋升到 Manual)
    ↓ 【Auditor 模块】
🚀 Express (反哺开发环境 + 项目归档)
    ↓ 【Archiver 模块】
🗄️ Archives (40_Archives) → 提取知识回流到 20_Areas
    ↑___________________________________________|  (形成闭环)
```

**Skill 文件是驱动 CODE 流程的"引擎程序"**：

```text
🛠️ .pkm/Skills/PKM/
├── Verifier.md         # 【前置守卫】验证目录结构，确认工作范围
├── _Inbox.md           # 【快速捕获】智能捕获内容到 Inbox
├── _Classifier.md      # 驱动 C→O：将 Inbox 分流到 PARA 三层
├── _Synthesizer.md     # 驱动 O→D：整合 AI 区碎片，生成草稿
├── _Auditor.md         # 驱动 D→E：对比 Manual，建议更新
└── _Archiver.md        # 驱动 E→A：归档项目，提取知识回流
```

**关键设计原则**：

- **范围限制（最高优先级）**：所有 Skill 执行前必须先调用 `Verifier` 验证工作范围，禁止修改知识管理工程外的任何目录。
- **知识单向晋升**：只能从 AI 区 → Manual 区，不能反向污染。
- **项目生命周期**：`10_Projects` → `40_Archives` → 知识回流到 `20_Areas`。
- **防火墙机制**：AI 永远不能直接修改 `Manual` 区，只能在 AI 区自由创作。
- **零心理负担**：人类只在 `Manual` 区确认知识，无需整理 AI 区的混乱。

---

## 二、 目录架构 (The Physical Layout)

```text
.
├── 🏗️ 10_Projects/             # 【P】Actionable：活跃项目
│   ├── Project_Alpha/
│   │   ├── 📜 Manual/          # 项目金标准、架构决策
│   │   └── 🤖 AI_Generated/    # 项目流水、Bug 记录、AI 草稿
│
├── 🧠 20_Areas/                # 【A】Responsibility：长期领域
│   ├── 📜 Manual/              # 【人脑主权】严密分类的文件夹 (Category)
│   │   ├── 💻 Programming/     # 存放 React.md, Rust.md
│   │   └── 💰 Finance/         # 存放 Tax.md
│   │
│   └── 🤖 AI_Synthesized/      # 【AI 自由区】自组织，无需同步
│       ├── 🏷️ Cluster_React/   # AI 自动聚类的 React 专题
│       ├── 📅 Weekly_Logs/     # AI 自动按周生成的流水
│       └── 🛠️ Error_Patterns/  # AI 提取的高频错误模式
│
├── 📚 30_Resources/            # 【R】Interests：原材料
│   ├── 📥 00_Inbox/            # 捕捉起点
│   └── 📄 Library/             # 静态 PDF、电子书
│
└── 🗄️ 40_Archives/             # 【A】Completed：归档区
```

---

## 三、 PKM 统一管理系统

你通过在 AI 编码工具（Cursor/Claude Code/Gemini CLI）中调用 **`@pkm`** 来驱动整个知识管理系统。

### 统一入口：`@pkm`

**最简单的用法**：

```text
@pkm
```

系统会自动执行所有需要的操作：

1. ✅ **Verifier**：验证知识库结构
2. 📥 **Classifier**：处理 Inbox 中的待分类内容
3. 📚 **Synthesizer**：蒸馏积累足够的知识碎片
4. 🔍 **Auditor**：审计新生成的草稿
5. 📦 **Archiver**：归档已完成的项目

**手动指定操作**：

```text
@pkm classify              # 仅分类 Inbox
@pkm synthesize React      # 仅蒸馏 React 主题
@pkm audit Python          # 仅审计 Python
@pkm archive               # 仅归档完成项目
@pkm help                  # 显示帮助信息
```

### 内部模块说明

PKM 由 6 个内部模块组成，每个模块负责 CODE 流程的一个环节：

#### 0. **Verifier (范围守卫) ⚠️ 最高优先级**

- **触发时机**：任何操作前自动执行。
- **核心逻辑**：
  1. 检查必需的 5 个目录是否全部存在
  2. 生成操作白名单（可写/只读/禁止）
  3. 验证失败则立即中止
- **效果**：确保只在完整的知识库结构中运行，防止误操作。

#### 1. **Inbox (快速捕获器)**

- **对应阶段**：CODE 的 **Capture**（捕获）
- **触发时机**：手动调用 `@pkm inbox <内容>`
- **核心逻辑**：
  1. 接收用户输入的内容
  2. AI简单总结内容，生成文件名（5-10字标题）
  3. 智能处理链接（默认引用，`--online` 模式抓取内容）
  4. 保存到 `30_Resources/00_Inbox/`
- **效果**：极简操作，一条命令快速捕获，AI自动生成文件名。

#### 2. **Classifier (智能分流器)**

- **对应阶段**：CODE 的 **Capture** → **Organize**
- **触发时机**：Inbox 有文件时自动执行，或手动调用 `@pkm classify`
- **核心逻辑**：
  1. 扫描 `30_Resources/00_Inbox/`
  2. 判断类型（任务/知识/资料）
  3. 自动分流到对应位置
  4. 智能归并：避免主题过度分散
- **效果**：实现从 Capture 到 Organize 的零人工干预。

#### 3. **Synthesizer (知识蒸馏器)**

- **对应阶段**：CODE 的 **Organize** → **Distill**
- **触发时机**：某主题积累 10+ 条原子块时自动执行，或手动调用 `@pkm synthesize <主题>`
- **核心逻辑**：
  1. 扫描同一主题下的所有碎片
  2. 去重、归并相似内容
  3. 按逻辑关系排序
  4. 生成结构化草稿，标注"待审核"
- **效果**：实现从 Organize 到 Distill 的预处理，人类只需最后审核。

#### 4. **Auditor (质量审计员)**

- **对应阶段**：CODE 的 **Distill**（质量审计）
- **触发时机**：Synthesizer 完成草稿后自动触发，或手动调用 `@pkm audit <主题>`
- **核心逻辑**：
  1. 读取 AI 草稿（`[草稿]_*.md`）
  2. 对比 Manual 中的现有知识（只读）
  3. 识别差异（新增/过时/冗余）
  4. 生成"建议更新清单"
- **效果**：驱动人类完成最后的 Distill（人脑确认），保持 Manual 时效性。

#### 5. **Archiver (生命周期管理器)**

- **对应阶段**：CODE 的 **Express**（生命周期管理）
- **触发时机**：发现 `COMPLETED.md` 时自动触发，或手动调用 `@pkm archive`
- **处理对象**：`10_Projects/` 中已完成的项目
- **核心逻辑**：
  1. **前置检查**：调用 `Verifier` 确认操作范围限制在 `10_Projects/`, `20_Areas/AI_Synthesized/`, `40_Archives/`。
  2. 扫描所有项目，识别标记为"完成"的项目（如存在 `COMPLETED.md`）。
  3. 将项目整体移动到 `40_Archives/`，保留完整目录结构。
  4. 从项目的 `Manual/` 和 `AI_Generated/` 中提取"可复用知识"（如架构模式、Bug 解决方案）。
  5. 将提取的知识追加到 `20_Areas/AI_Synthesized/` 对应主题，**禁止直接写入 Manual**。
- **效果**：保持 Projects 区轻量，让知识沉淀回 Areas，形成正反馈循环。

---

## 四、 运行流程：PARA × CODE 联动闭环

### 使用 `@pkm` 驱动整个流程

**最简单的用法**：

```text
@pkm
```

系统会自动依次执行：

### **1. Verify (验证范围)**

Verifier 验证目录结构，生成可操作白名单，确保安全。

### **2. Capture（快速捕获）**

Inbox 模块提供便捷的捕获入口：

```bash
# 快速捕获想法（自动识别标题和标签）
@pkm inbox React useEffect 的依赖数组如果为空，效果等同于 componentDidMount

# 深度学习模式（抓取网页内容）
@pkm inbox --online React 18 新特性 https://react.dev/blog/...
```

### **3. Organize（智能分流）**

Classifier 自动分流 Inbox 中的内容：

- 可执行任务 → `10_Projects/*/AI_Generated/`
- 知识碎片 → `20_Areas/AI_Synthesized/`
- 参考资料 → `30_Resources/Library/`

### **4. Distill（知识蒸馏）**

Synthesizer 蒸馏积累足够的知识碎片：

- 扫描同一主题的碎片，去重归并
- 生成结构化草稿（标记为 `[草稿]_*.md`）

Auditor 对比草稿与 Manual：

- 识别差异（新增/过时/冗余）
- 生成"建议更新清单"
- **人类确认**并手动写入 Manual

### **5. Express（输出归档）**

Archiver 管理项目生命周期：

- 识别已完成的项目（存在 `COMPLETED.md`）
- 移动到 `40_Archives/`
- 提取可复用知识回流到 `20_Areas/AI_Synthesized/`
- 形成知识管理闭环
