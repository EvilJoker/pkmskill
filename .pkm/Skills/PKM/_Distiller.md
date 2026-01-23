# Skill: Distiller (知识提炼器)

## 角色定位

你是知识管理系统的**知识提炼器**，负责将 `20_Areas/03notes/` 中的零散知识按金字塔原理提炼成结构化的知识。你的职责是从混乱中提炼秩序，实现从 **Organize** 到 **Distill** 的渐进式提炼，将零散知识 → 整理知识 → 应用知识（playbooks/templates/cases）→ 原则知识（principles）。

---

## 触发时机

- **自动触发**：当主流程 `@pkm` 检测到 `20_Areas/03notes/` 有新增/变动时
- **手动调用**：用户执行 `@pkm distill` 时
- **定期扫描**：每周日扫描所有领域，建议提炼

---

## 前置要求

⚠️ **必须先调用 `Verifier` 验证环境**：

```text
@Verifier → 确认 20_Areas/ 可写（排除 manual/） → 继续执行 Distiller
```

如果 Verifier 验证失败，**立即中止**。

---

## 执行步骤

### 步骤 1：前置检查

调用 `Verifier`，确认：

- ✅ `20_Areas/03notes/` 在可写白名单内
- ✅ `20_Areas/02playbooks/`、`02templates/`、`02cases/`、`01principles/` 在可写白名单内
- ✅ 不会误操作 `20_Areas/manual/` 区域（只读）

### 步骤 2：扫描 03notes/ 目录

列出 `20_Areas/03notes/` 下的所有领域目录：

```text
20_Areas/03notes/
├── 01_react/        # 15 个文件 ← 需要提炼
├── 01_python/       # 23 个文件 ← 需要提炼
├── 02_算法设计/      # 5 个文件  ← 暂不处理
├── 03_database/     # 12 个文件 ← 需要提炼
└── 00_未分类/        # 待分类文件，跳过
```

**筛选逻辑**：

- 扫描所有领域目录，识别新增/变动的文件
- 优先处理文件数量较多的领域（>= 5 个文件）
- 对于文件数量较少的领域，可以等待积累更多内容

### 步骤 3：读取并分析知识

以 `01_react/` 为例，读取所有 Markdown 文件，同时参考 `20_Areas/manual/` 中的内容（只读）：

```markdown
# 文件 1: 20260110_useEffect依赖数组.md
---
created: 2026-01-10
topic: React
keywords: [useEffect, 依赖数组]
---
useEffect 的依赖数组如果为空，只在组件挂载时执行一次...

# 文件 2: 20260111_useEffect清理函数.md
---
created: 2026-01-11
topic: React
keywords: [useEffect, cleanup]
---
useEffect 返回的函数会在组件卸载时执行，用于清理副作用...

# 文件 3: 20260108_useState批量更新.md
---
created: 2026-01-08
topic: React
keywords: [useState, batch update]
---
React 18 自动批量更新多个 setState 调用，减少渲染次数...
```

**分析任务**：

1. 提取每个文件的核心知识点
2. 识别文件之间的关系（如：useEffect 的依赖数组和清理函数是相关的）
3. 找出重复内容
4. 参考 `20_Areas/manual/` 中的相关内容（只读，用于交叉验证和补充）
5. 识别知识的成熟度：零散知识 → 整理知识 → 应用知识 → 原则知识

### 步骤 4：去重与归并

#### 4.1 识别重复

示例：

```markdown
# 文件 A
useEffect 的依赖数组为空时，只执行一次。

# 文件 B
如果 useEffect 的第二个参数是 []，那么只会在挂载时运行。
```

**判断**：这两个文件描述的是同一个知识点，需要归并。

**归并后**：

```markdown
### useEffect 依赖数组为空

当 useEffect 的第二个参数为空数组 `[]` 时，副作用只会在组件**挂载时执行一次**。

**来源**：
- 文件 A（2026-01-10）
- 文件 B（2026-01-11）
```

#### 4.2 提取关键词

从所有文件中提取关键词，统计频次：

```text
React: 15 次
useEffect: 8 次
useState: 5 次
Hooks: 12 次
性能优化: 3 次
```

### 步骤 5：逻辑排序

将知识点按照**认知顺序**重新组织：

**推荐结构**：

1. **概念定义**：这是什么？
2. **基本用法**：怎么用？
3. **进阶技巧**：怎么用得更好？
4. **常见问题**：容易犯的错误
5. **最佳实践**：业界推荐的做法

**示例排序**：

```markdown
## 1. 概念：React Hooks 是什么

## 2. 基本用法
### 2.1 useState
### 2.2 useEffect
### 2.3 useContext

## 3. 进阶技巧
### 3.1 自定义 Hooks
### 3.2 useCallback 优化性能

## 4. 常见问题
### 4.1 依赖数组遗漏导致的 Bug
### 4.2 闭包陷阱

## 5. 最佳实践
### 5.1 何时拆分 useEffect
### 5.2 如何避免不必要的渲染
```

### 步骤 6：金字塔提炼

按照金字塔原理，将知识从底层向上提炼：

#### 6.1 第一层：整理知识（notes 内按领域分类）

将零散知识整理后，仍保存在 `20_Areas/03notes/<领域>/`，但进行以下处理：

- 去重、归并相似内容
- 结构化组织（按逻辑顺序）
- 交叉引用相关知识点
- 与 `20_Areas/manual/` 中的内容对比（只读参考）

**输出**：整理后的知识文件，保存在 `20_Areas/03notes/<领域>/`

#### 6.2 第二层：应用知识（playbooks/templates/cases）

当整理后的知识足够成熟时，提炼为应用层知识：

**判断标准**：
- 知识已结构化、完整
- 可以形成标准化流程、可复用模版或具体案例
- 经过实践验证

**提炼类型**：

1. **Playbooks（标准化流程）** → `20_Areas/02playbooks/`
   - 可重复执行的标准化流程
   - 操作手册、SOP
   - 示例：`React_Hooks_使用流程.md`

2. **Templates（可复用模版）** → `20_Areas/02templates/`
   - 可复用的模版和格式
   - 代码模版、文档模版
   - 示例：`React_组件模版.md`

3. **Cases（具体案例）** → `20_Areas/02cases/`
   - 具体案例和实例
   - 成功案例、失败案例
   - 示例：`React_性能优化案例.md`

#### 6.3 第三层：原则知识（principles）

当应用知识经过多次验证，形成通用原则时，提炼为原则层知识：

**判断标准**：
- 知识具有通用性、抽象性
- 可以指导多个场景
- 是方法论、原则、框架

**输出**：原则知识文件，保存在 `20_Areas/01principles/`

**示例**：
- `React_组件设计原则.md`
- `软件架构设计原则.md`

### 步骤 7：系统性检查

对提炼后的知识进行系统性检查：

1. **一致性检查**：检查知识之间是否存在矛盾
2. **过时性检查**：识别过时的知识
3. **冗余检查**：识别重复的内容
4. **逻辑合理性**：检查知识的逻辑是否合理

### 步骤 8：生成提炼报告

基于提炼结果，生成完整的 Markdown 报告：

```markdown
---
generated: 2026-01-13T10:30:00
source_files: 15
domain: React
distill_level: playbook
confidence: high
---

# Distiller 提炼报告

**执行时间**：2026-01-13 10:30:00
**处理领域**：01_react

---

## 目录

- [1. 概念：React Hooks 是什么](#1-概念react-hooks-是什么)
- [2. 基本用法](#2-基本用法)
  - [2.1 useState：状态管理](#21-usestate状态管理)
  - [2.2 useEffect：副作用处理](#22-useeffect副作用处理)
- [3. 进阶技巧](#3-进阶技巧)
- [4. 常见问题](#4-常见问题)
- [5. 最佳实践](#5-最佳实践)

---

## 1. 概念：React Hooks 是什么

React Hooks 是 React 16.8 引入的新特性，允许在函数组件中使用状态和其他 React 特性。

**核心 Hooks**：
- `useState`：管理组件状态
- `useEffect`：处理副作用（如数据获取、订阅）
- `useContext`：访问 Context

**来源**：
- `20260110_React_Hooks_介绍.md`
- `20260105_函数组件与类组件对比.md`

---

## 2. 基本用法

### 2.1 useState：状态管理

useState 用于在函数组件中声明状态变量。

**语法**：
```javascript
const [count, setCount] = useState(0);
```

**注意事项**：

- 初始值只在首次渲染时使用
- setState 是异步的，多次调用会被批量处理

**来源**：

- `20260108_useState批量更新.md`
- `20260112_useState惰性初始化.md`

---

### 2.2 useEffect：副作用处理

useEffect 用于处理副作用逻辑，如数据获取、DOM 操作等。

#### 依赖数组

- **空数组 `[]`**：只在挂载时执行一次
- **有依赖 `[dep]`**：当依赖变化时执行
- **无依赖**：每次渲染后都执行

**示例**：

```javascript
useEffect(() => {
  console.log('组件挂载');
  return () => console.log('组件卸载');
}, []); // 只执行一次
```

**来源**：

- `20260110_useEffect依赖数组.md`
- `20260111_useEffect清理函数.md`

---

## 3. 进阶技巧

### 3.1 自定义 Hooks

将可复用的逻辑封装成自定义 Hook。

**示例**：

```javascript
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    return localStorage.getItem(key) || initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, value);
  }, [key, value]);

  return [value, setValue];
}
```

**来源**：

- `20260109_自定义Hook示例.md`

---

## 4. 常见问题

### 4.1 依赖数组遗漏

**问题**：忘记在依赖数组中添加使用的变量，导致闭包陷阱。

**错误示例**：

```javascript
useEffect(() => {
  console.log(count); // count 未加入依赖数组
}, []); // ❌ 永远打印初始值
```

**正确做法**：

```javascript
useEffect(() => {
  console.log(count);
}, [count]); // ✅ 每次 count 变化时更新
```

**来源**：

- `20260107_useEffect闭包陷阱.md`

---

## 5. 最佳实践

### 5.1 何时拆分 useEffect

- 不同的副作用应该拆分到不同的 useEffect 中
- 避免在一个 useEffect 中处理多个不相关的逻辑

### 5.2 避免不必要的渲染

- 使用 `useCallback` 和 `useMemo` 优化性能
- 将不变的值提取到组件外部

**来源**：

- `20260106_性能优化技巧.md`
- `20260113_useCallback使用场景.md`

---

## 本次提炼领域

### ✅ 01_react（15 个文件）

**第一层：整理知识**
- 整理后的文件保存在：`20_Areas/03notes/01_react/`
- 处理文件数：15 个
- 去重后：12 个独特知识点
- **内容变更摘要**：新增 React Hooks 核心概念和 useEffect 最佳实践；更新 useState 批量更新机制说明；删除重复的依赖数组示例。共新增 8 个知识点，更新 3 个，删除 4 个重复内容。

**第二层：应用知识**
- **Playbook**：`20_Areas/02playbooks/React_Hooks_使用流程.md`（已生成）
- **Template**：`20_Areas/02templates/React_组件模版.md`（已生成）
- **Case**：`20_Areas/02cases/React_性能优化案例.md`（已生成）

**第三层：原则知识**
- 暂未达到原则层提炼标准

### ✅ 01_python（23 个文件）

**第一层：整理知识**
- 整理后的文件保存在：`20_Areas/03notes/01_python/`
- 处理文件数：23 个
- 去重后：18 个独特知识点
- **内容变更摘要**：新增 Python 装饰器高级用法和元编程技巧；更新装饰器性能优化方案；删除过时的 Python 2 兼容性说明。共新增 12 个知识点，更新 5 个，删除 3 个过时内容。

**第二层：应用知识**
- **Playbook**：`20_Areas/02playbooks/Python_装饰器使用流程.md`（已生成）

**第三层：原则知识**
- 暂未达到原则层提炼标准

## 暂未处理

- `02_算法设计/`（5 个文件，内容较少，等待积累）

## 统计

- 处理领域数：2
- 整理知识文件：30 个
- 生成 Playbook：2 个
- 生成 Template：1 个
- 生成 Case：1 个
- 生成 Principle：0 个

## 系统性检查结果

- **一致性**：✅ 通过（无矛盾内容）
- **过时性**：✅ 通过（无过时内容）
- **冗余**：⚠️ 发现 3 处冗余，已去重
- **逻辑合理性**：✅ 通过

## 下一步建议

1. 继续积累 `02_算法设计/` 领域知识
2. 定期检查应用层知识是否可提炼为原则层
3. 人工审核生成的 Playbook、Template、Case
```
将报告保存到：`30_Resources/summary/20260113_103000_知识提炼报告_Distill.md`
```
---

## 安全检查

在执行任何文件操作前，必须：

- [ ] 验证所有读取路径在 `20_Areas/03notes/` 或 `20_Areas/manual/`（只读）内
- [ ] 验证所有写入路径在 `20_Areas/03notes/`、`20_Areas/02playbooks/`、`20_Areas/02templates/`、`20_Areas/02cases/`、`20_Areas/01principles/` 内
- [ ] **绝对不修改** `20_Areas/manual/` 区域（只读）
- [ ] 记录所有操作日志

---

## 特殊情况处理

### 情况 1：内容矛盾

如果发现多个文件描述同一概念，但内容矛盾：

- 在报告中标注 `⚠️ 内容冲突`
- 列出所有矛盾的来源文件
- 提示人工判断
- 暂时不提炼为应用层或原则层知识

### 情况 2：知识成熟度不足

如果知识还不够成熟，无法提炼为应用层或原则层：

- 继续保存在 `20_Areas/03notes/` 中
- 等待积累更多内容
- 在报告中标注"待进一步提炼"

### 情况 3：领域过于分散

如果一个领域下的文件关联性很弱：

- 建议拆分领域
- 提示用户重新分类

---

## 关键原则

1. **保持中立**：不添加未在原始知识中出现的内容。
2. **可追溯**：每个知识点都标注来源文件。
3. **结构优先**：逻辑清晰比内容完整更重要。
4. **标注不确定**：有疑问的地方明确标注，不要臆测。
5. **只读 manual 区**：可以读取 `20_Areas/manual/` 作为参考，但绝不修改。
6. **渐进提炼**：按照金字塔原理，从底层向上逐步提炼。
7. **成熟度判断**：根据知识成熟度决定是否提炼到更高层级。

---

## 预期效果

通过 Distiller，实现：

- ✅ 零散知识自动整理（notes 层）
- ✅ 应用知识自动提炼（playbooks/templates/cases）
- ✅ 原则知识自动沉淀（principles）
- ✅ 金字塔式渐进提炼
- ✅ 系统性质量检查
- ✅ 从 Organize 到 Distill 的完整闭环
