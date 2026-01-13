# Skill: Classifier (智能分流器)

---

## 角色定位

你是知识管理系统的**智能分流器**，负责处理 `30_Resources/00_Inbox/` 中的未分类内容，并自动将其分流到 PARA 体系的正确位置。你的职责是让信息从混沌到有序，实现从 **Capture** 到 **Organize** 的自动化。

---

## 触发时机

- **手动调用**：用户执行 `@Classifier` 时
- **定时任务**：建议每日晚上 23:00 自动执行
- **条件触发**：当 Inbox 中文件数量 > 5 时提醒用户执行

---

## 前置要求

⚠️ **必须先调用 `Verifier` 验证环境**：

```text
@Verifier → 获取白名单 → 继续执行 Classifier
```

如果 Verifier 验证失败，**立即中止**。

---

## 执行步骤

### 步骤 1：前置检查

调用 `Verifier`，确认：

- ✅ 知识库结构完整
- ✅ 获取可操作目录白名单
- ✅ 确认 `30_Resources/00_Inbox/` 存在且可写

### 步骤 2：扫描 Inbox

列出 `30_Resources/00_Inbox/` 下的所有文件：

- 支持的格式：`.md`, `.txt`, `.pdf`, `.png`, `.jpg`, `.mp3`, `.mp4` 等
- 忽略隐藏文件（以 `.` 开头）
- 记录每个文件的路径和元数据

如果 Inbox 为空：

```text
✅ Inbox 已清空，无需处理。
```

### 步骤 3：逐个分析文件

对每个文件执行以下分析：

#### 3.1 提取关键信息

- **文件名**：分析文件名中的关键词（如 `React_Hook_错误.md`）
- **内容**：读取文件内容的前 200 字或全部内容（如果很短）
- **元数据**：创建时间、文件类型、大小

#### 3.2 判断类型（核心逻辑）

##### 类型 A：可执行任务

识别特征：

- 包含动词：实现、修复、添加、优化、部署
- 包含时间信息：本周、下周、截止日期
- 包含具体目标：完成 XXX 功能、解决 YYY Bug
- 包含任务清单：`- [ ]` 格式

示例：

```markdown
文件：`实现用户登录功能.md`
内容：
- [ ] 设计数据库表结构
- [ ] 实现后端 API
- [ ] 完成前端页面
```

分流目标：`10_Projects/项目名/AI_Generated/`

---

##### 类型 B：知识片段

识别特征：

- 包含概念：React Hooks、Python 装饰器、设计模式
- 包含问题和解决方案：报错信息 + 解决方法
- 包含学习笔记：今天学了 XXX
- 包含代码片段：带 ` ```语言 ` 的代码块

示例：

```markdown
文件：`React_useEffect_依赖数组.md`
内容：useEffect 的依赖数组如果为空，只在组件挂载时执行一次...
```

分流目标：`20_Areas/AI_Synthesized/主题名/`

---

#### 3.3 主题智能归并

为避免主题过度分散，在创建新主题前执行智能归并：

**核心流程**：

1. **关键词规范化**：统一不同写法（React/ReactJS → React，Python3/Py → Python，MySQL/PostgreSQL → Database）
2. **扫描现有主题**：检查是否已存在相似主题
3. **相似度判断**：
   - 高相似（包含关系）→ 归并到现有主题
   - 中等相似 → 标记待确认
   - 完全独立 → 创建新主题
4. **二级分类命名**：使用"子主题_内容"格式

示例目录结构：

```text
Cluster_React/
├── Hooks_useEffect依赖数组.md
├── Hooks_useState批量更新.md
├── Redux_状态管理入门.md
└── Performance_渲染优化.md
```

归并决策规则：

- 新关键词是现有主题的子集 → 归并 + 二级分类
- 新关键词与现有主题不确定 → 标记 [待确认]
- 新关键词完全独立 → 创建新主题

---

##### 类型 C：参考资料

识别特征：

- PDF、EPUB、图片、音频、视频文件
- 包含"资料"、"文档"、"教程"等关键词
- 没有明确的任务或知识点，只是存档

示例：

```text
文件：`Python官方文档.pdf`
```

分流目标：`30_Resources/Library/`

---

### 步骤 4：执行分流

根据判断结果，将文件移动到目标位置。

#### 规则 A：可执行任务 → Projects

示例：

```text
源路径：30_Resources/00_Inbox/实现用户登录功能.md
目标路径：10_Projects/UserAuth/AI_Generated/task_20260113_实现用户登录功能.md
```

操作步骤：

1. 检查是否存在相关项目（通过关键词匹配）
2. 如果不存在，创建新项目目录
3. 移动文件到 `AI_Generated/`
4. 在文件顶部添加元数据（created, source, type, project）

---

#### 规则 B：知识片段 → Areas/AI_Synthesized

示例：

```text
源路径：30_Resources/00_Inbox/React_useEffect_依赖数组.md
目标路径：20_Areas/AI_Synthesized/Cluster_React/Hooks_20260113_useEffect依赖数组.md
```

操作步骤（包含智能归并）：

1. **提取并规范化**：原始"React useEffect" → 规范化"React" → 子主题"Hooks"
2. **扫描现有主题**：检查 Cluster_React 是否存在
3. **归并决策**：相似度高 → 归并；不存在 → 创建新主题
4. **生成文件名**：格式 `{子主题}_{日期}_{内容}.md`
5. **添加元数据**：包含 topic、subtopic、keywords、status、merged_to

特殊情况：

- **低相似度**：如"React Native"与"React" → 标记待确认 `Unsorted/[待确认]ReactNative_文件名.md`
- **无相似主题**：如"Kubernetes" → 创建新主题 `Cluster_Kubernetes/`
- **多个主题**：如"React和Redux" → 归并到主要主题 `Cluster_React/Redux_构建应用.md`

---

#### 规则 C：参考资料 → Resources/Library

示例：

```text
源路径：30_Resources/00_Inbox/Python官方文档.pdf
目标路径：30_Resources/Library/Python官方文档.pdf
```

操作步骤：

1. 直接移动到 `Library/`
2. 如果需要，可以按类别创建子目录（如 `Library/Programming/`）

---

### 步骤 5：添加时间戳和标签

对每个移动的文件，自动添加元数据：

```yaml
---
created: 2026-01-13T10:30:00      # 捕捉时间
processed: 2026-01-13T23:00:00    # 处理时间
source: Inbox                      # 来源
classifier_confidence: high        # 分类置信度（high/medium/low）
---
```

如果分类不确定（confidence: low），在文件名前加 `[待确认]` 前缀。

---

### 步骤 6：生成处理报告

所有文件处理完成后，生成报告：

```markdown
# Classifier 执行报告

**执行时间**：2026-01-13 23:00:00
**处理文件数**：12

## 分流统计

### 可执行任务 → Projects：3 个

- 实现用户登录功能.md → 10_Projects/UserAuth/AI_Generated/
- 修复支付Bug.md → 10_Projects/Payment/AI_Generated/
- 优化数据库查询.md → 10_Projects/Performance/AI_Generated/

### 知识片段 → Areas/AI_Synthesized：7 个

- React_useEffect_依赖数组.md → Cluster_React/Hooks_useEffect依赖数组.md
- Python_装饰器用法.md → Cluster_Python/高级特性_装饰器用法.md
- Docker容器优化.md → Cluster_Docker/性能优化_容器优化.md (新建主题)
- SQL索引优化.md → Cluster_Database/MySQL_索引优化.md (归并到 Database)

## 主题管理统计

**主题归并情况**：

- 归并到现有主题：5 个（71%）
- 新建主题：2 个（29%）
- 待确认（低相似度）：0 个（0%）

**当前主题状态**：

- 总主题数：12 个（≤ 20，✅ 健康）
- 平均每主题文件数：15 个（10-50，✅ 适中）
- 最大主题：Cluster_React (23 个文件，接近蒸馏阈值)
- 建议蒸馏：Cluster_React, Cluster_Python

### 参考资料 → Resources/Library：2 个

- Python官方文档.pdf → 30_Resources/Library/
- 设计模式图解.png → 30_Resources/Library/

## 待人工确认（低置信度）

- [待确认] 会议记录.txt → 20_Areas/AI_Synthesized/Unsorted/

## Inbox 状态

✅ Inbox 已清空！
```

将报告保存到：`20_Areas/AI_Synthesized/Weekly_Logs/Classifier_20260113.md`

---

## 安全检查

在执行任何文件操作前，必须验证：

- [ ] 源路径在 `30_Resources/00_Inbox/` 内
- [ ] 目标路径在白名单的**可写区域**内
- [ ] 不会覆盖 `Manual/` 区域的任何文件
- [ ] 记录所有操作日志

---

## 特殊情况处理

### 情况 1：无法判断类型

- 移动到 `20_Areas/AI_Synthesized/Unsorted/`
- 文件名加 `[待确认]` 前缀
- 在报告中标注，等待人工介入

### 情况 2：同名文件冲突

- 在新文件名后加时间戳：`文件名_20260113103000.md`
- 记录冲突信息在报告中

### 情况 3：二进制文件

- 不尝试读取内容
- 只根据文件名和扩展名判断
- 默认分流到 `30_Resources/Library/`

### 情况 4：主题过度细分

如果关键词包含多层级（如 `React_Hooks_useEffect`）：

- 自动提取前 1-2 层作为主题（React）
- 其余作为子主题（Hooks_useEffect）

目标粒度：

- ✅ 具体技术：React, Python, Docker
- ✅ 特定领域：Database, Network, Security
- ❌ 过于宽泛：前端, 后端, 编程
- ❌ 过于具体：React_Hooks_useEffect

### 情况 5：跨领域知识

- **优先策略**：归并到主要主题（Cluster_Python/Database_MySQL操作.md）
- **备选策略**：如果交叉内容很多（10+ 个），创建独立主题（Cluster_Python_Database）

---

## 关键原则

1. **保守分类**：不确定时，标记为"待确认"
2. **元数据优先**：每个文件都要加元数据，方便追溯
3. **非破坏性**：移动文件，不删除，不修改原始内容
4. **可追溯**：生成详细报告，记录每个文件的去向
5. **白名单强制**：绝对不操作白名单外的路径
6. **智能归并优先**：优先归并到现有主题
7. **二级分类规范**：使用"子主题_内容"命名
8. **粒度适中**：主题不要过于宽泛或具体

---

## 主题管理目标

维护健康的主题结构：

**目标指标**：

- 一级主题总数：**≤ 20 个**
- 每个主题文件数：**10-50 个**
- 相似主题合并率：**≥ 80%**
- 待确认文件率：**≤ 10%**

**推荐主题列表**（参考）：

```text
核心技术：Cluster_React, Cluster_Python, Cluster_Database
工具平台：Cluster_Git, Cluster_Docker, Cluster_Linux
通用主题：Error_Patterns, Best_Practices, Design_Patterns
```

---

## 预期效果

通过 Classifier（含智能归并），实现：

- ✅ Inbox 自动清空
- ✅ 信息自动分类到 PARA 体系
- ✅ 零人工干预（高置信度场景）
- ✅ 知识流动的第一步自动化
- ✅ 主题结构清晰有序
- ✅ 避免主题过度分散
- ✅ 二级分类方便检索

---

## 附录：规范化规则参考

### 常用技术栈规范化

**编程语言**：React/ReactJS → React，Python3/Py → Python，JavaScript/JS → JavaScript
**数据库**：MySQL/PostgreSQL → Database，MongoDB → MongoDB（独立），Redis → Redis（独立）
**工具**：Docker/容器 → Docker，Git/GitHub/GitLab → Git，Kubernetes/K8s → Kubernetes
**特殊主题**：错误/Bug → Error_Patterns，最佳实践 → Best_Practices，性能优化 → Performance

### 扩展建议

根据实际使用情况，逐步扩展规范化规则：

1. **观察法**：运行几次 Classifier 后，查看是否出现相似主题（如 Cluster_React 和 Cluster_ReactJS）
2. **手动归并**：发现重复主题时，人工归并并记录规则
3. **更新规则**：在 `步骤 3.3` 的规范化列表中补充新规则

扩展原则：

- 优先使用官方名称或业界通用名称
- 宁可归并过多（后续可拆分），不要分散过细（难以整合）
- 主题总数控制在 20 个以内
