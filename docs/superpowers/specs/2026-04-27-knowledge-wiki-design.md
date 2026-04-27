# Knowledge Wiki 设计方案

> **参考**: Karpathy LLM Wiki 模式

## 1. 背景与目标

### 问题
- `generated/` 扁平存储，内容难以发现
- 缺乏主题入口，文件之间无关联

### 目标
- 参考 LLM Wiki 模式，重构知识库结构
- 支持按主题浏览和发现内容
- 保留现有的增量更新机制（md5 + 两轮扫描）

## 2. 目录结构

```
~/.pkm/
├── 10_Tasks/                      # 任务层
├── 20_Projects/                    # 项目层（Raw Sources）
├── 30_Raw/                        # Raw 层
├── 40_Knowledge/                  # Wiki 层
│   ├── _wiki/                     # LLM 编译的概念页面
│   │   ├── index.md               # 总导航
│   │   ├── index.yaml             # 结构化索引
│   │   ├── AI/
│   │   │   └── *.md              # 概念页面
│   │   ├── 职业发展/
│   │   └── 编程/
│   └── _schema/
│       └── CLAUDE.md              # Wiki 维护规则
└── 80_Archives/                   # 归档层
```

**目录映射**:
| 现状 | 目标 | 说明 |
|------|------|------|
| 90_Knowledge/ | 40_Knowledge/ | Wiki 层 |
| 60_Projects/ | 20_Projects/ | 项目层 |
| 50_Raw/ | 30_Raw/ | Raw 层 |

## 3. Wiki 页面格式

```markdown
---
title: AI基础
type: concept
sources: [P_20260420_职业发展/AI学习笔记.md]
related: [[AI工具]], [[职业规划]]
created: 2026-04-27
updated: 2026-04-27
---

# AI基础

## 核心概念
- 机器学习是...

## 相关
- [[AI工具]]
- [[职业规划]]
```

## 4. 核心机制

### 4.1 源文件层 (20_Projects)
- 只读不修改
- 按项目组织

### 4.2 Wiki 层 (_wiki/)
- 由 LLM 增量维护
- 扁平存储（一个概念一个文件）
- 按主题分组目录

### 4.3 增量更新 (reflow)
- 现有的 md5 + 两轮扫描机制保持不变
- 识别变更后，更新相关概念页面

### 4.4 Schema (_schema/CLAUDE.md)
- 页面格式定义
- 更新策略
- 命名规范

## 5. 索引机制

### 5.1 index.md
```markdown
# Knowledge Index

## AI
- [[AI基础]]
- [[AI工具]]

## 职业发展
- [[职业规划]]
- [[跳槽策略]]

## 最近更新
- 2026-04-27: 更新 [[AI基础]]
```

### 5.2 index.yaml
```yaml
concepts:
  AI基础:
    path: AI/AI基础.md
    sources: [P_20260420_职业发展/AI学习笔记.md]
    related: [AI工具, 职业规划]
  职业规划:
    path: 职业发展/职业规划.md
    sources: [P_20260420_职业发展/职业规划.md]
    related: [AI基础, 跳槽策略]
```

## 6. 迁移策略

1. 删除 `90_Knowledge/generated/`
2. 重命名 `60_Projects/` → `20_Projects/`
3. 重命名 `50_Raw/` → `30_Raw/`
4. 重命名 `90_Knowledge/` → `40_Knowledge/`
5. 创建 `40_Knowledge/_wiki/` 结构
6. 创建 `40_Knowledge/_schema/CLAUDE.md`
7. 重构 reflow 逻辑，按新结构生成 wiki 页面
8. 保留 `20_Projects/` 作为源文件

## 7. 不在本次实现范围

- `30_Raw/` 预留扩展
- 草稿审核流程
- 多维度索引（MOC）
