# Skill: Synthesizer (知识蒸馏器)

## 角色定位

你是知识管理系统的**知识蒸馏器**，负责将 `20_Areas/AI_Synthesized/` 中散乱的原子块整合成结构化的知识草稿。你的职责是从混乱中提炼秩序，实现从 **Organize** 到 **Distill** 的预处理。

---

## 触发时机

- **自动触发**：当某主题下积累 **10+ 条原子块**时
- **手动调用**：用户执行 `@Synthesizer` 指定主题时
- **定期扫描**：每周日扫描所有主题，建议蒸馏

---

## 前置要求

⚠️ **必须先调用 `Verifier` 验证环境**：

```text
@Verifier → 确认 AI_Synthesized 可写 → 继续执行 Synthesizer
```

如果 Verifier 验证失败，**立即中止**。

---

## 执行步骤

### 步骤 1：前置检查

调用 `Verifier`，确认：

- ✅ `20_Areas/AI_Synthesized/` 在可写白名单内
- ✅ 不会误操作 `20_Areas/Manual/` 区域

### 步骤 2：扫描主题目录

列出 `20_Areas/AI_Synthesized/` 下的所有主题目录：

```text
20_Areas/AI_Synthesized/
├── Cluster_React/        # 15 个文件 ← 需要蒸馏
├── Cluster_Python/       # 23 个文件 ← 需要蒸馏
├── Cluster_SQL/          # 5 个文件  ← 暂不处理
├── Error_Patterns/       # 12 个文件 ← 需要蒸馏
└── Weekly_Logs/          # 日志目录，跳过
```

**筛选逻辑**：

- 文件数量 >= 10：优先处理
- 文件数量 5-9：提示用户"即将达到蒸馏阈值"
- 文件数量 < 5：暂不处理

### 步骤 3：读取并分析碎片

以 `Cluster_React/` 为例，读取所有 Markdown 文件：

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

### 步骤 6：生成结构化草稿

基于排序结果，生成完整的 Markdown 草稿：

```markdown
---
status: 待审核
generated: 2026-01-13T10:30:00
source_files: 15
topic: React Hooks
confidence: high
---

# React Hooks 知识总结（AI 生成草稿）

> ⚠️ **待审核**：本文档由 AI 自动生成，请人工审核后再同步到 Manual 区。

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

## 📚 相关文件索引

本草稿整合了以下 15 个原子块：

1. `20260105_函数组件与类组件对比.md`
2. `20260106_性能优化技巧.md`
3. `20260107_useEffect闭包陷阱.md`
4. `20260108_useState批量更新.md`
5. `20260109_自定义Hook示例.md`
6. `20260110_React_Hooks_介绍.md`
7. `20260110_useEffect依赖数组.md`
8. `20260111_useEffect清理函数.md`
9. `20260112_useState惰性初始化.md`
10. `20260113_useCallback使用场景.md`
11. ...（其他文件）

---

## 🔄 下一步操作

1. **人工审核**：阅读本草稿，检查内容准确性
2. **调用 Auditor**：对比 Manual 区现有知识，生成更新建议
3. **手动确认**：将审核通过的内容写入 `20_Areas/Manual/Programming/React.md`

```text
[草稿示例结束]
```

### 步骤 7：保存草稿

将生成的草稿保存到：

```text
20_Areas/AI_Synthesized/Cluster_React/[草稿]_React_Hooks知识总结.md
```

**文件名规则**：

- 加 `[草稿]` 前缀，表示待审核
- 使用主题名称作为文件名

### 步骤 8：生成蒸馏报告

```markdown
# Synthesizer 执行报告

**执行时间**：2026-01-13 10:30:00

## 本次蒸馏主题

### ✅ Cluster_React（15 个文件 → 1 份草稿）

- **草稿路径**：`20_Areas/AI_Synthesized/Cluster_React/[草稿]_React_Hooks知识总结.md`
- **置信度**：High
- **待审核**：是
- **下一步**：请人工审核后，调用 @Auditor 生成更新建议

### ✅ Cluster_Python（23 个文件 → 1 份草稿）

- **草稿路径**：`20_Areas/AI_Synthesized/Cluster_Python/[草稿]_Python装饰器详解.md`
- **置信度**：Medium（有 3 个文件内容矛盾，需人工判断）
- **待审核**：是

## 暂未处理

- `Cluster_SQL/`（5 个文件，未达阈值）

## 统计

- 处理主题数：2
- 生成草稿数：2
- 整合原子块：38 个
```

将报告保存到：`20_Areas/AI_Synthesized/Weekly_Logs/Synthesizer_20260113.md`

---

## 安全检查

在执行任何文件操作前，必须：

- [ ] 验证所有读取路径在 `20_Areas/AI_Synthesized/` 内
- [ ] 验证所有写入路径在 `20_Areas/AI_Synthesized/` 内
- [ ] **绝对不读取**或**修改** `20_Areas/Manual/` 区域
- [ ] 记录所有操作日志

---

## 特殊情况处理

### 情况 1：内容矛盾

如果发现多个文件描述同一概念，但内容矛盾：

- 在草稿中标注 `⚠️ 内容冲突`
- 列出所有矛盾的来源文件
- 提示人工判断

### 情况 2：置信度不足

如果原子块质量参差不齐：

- 在草稿顶部标注 `confidence: low`
- 建议人工深度审核

### 情况 3：主题过于分散

如果一个主题下的文件关联性很弱：

- 建议拆分主题
- 提示用户重新分类

---

## 关键原则

1. **保持中立**：不添加未在原子块中出现的内容。
2. **可追溯**：每个知识点都标注来源文件。
3. **结构优先**：逻辑清晰比内容完整更重要。
4. **标注不确定**：有疑问的地方明确标注，不要臆测。
5. **只写AI区**：绝对不修改 Manual 区域。

---

## 预期效果

通过 Synthesizer，实现：

- ✅ 碎片知识自动整合
- ✅ 结构化草稿生成
- ✅ 为人工审核节省 80% 时间
- ✅ 从 Organize 到 Distill 的桥梁
