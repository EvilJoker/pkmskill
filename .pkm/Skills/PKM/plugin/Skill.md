---
name: Organizer Plugin Registry
description: Organizer 阶段插件注册表，在分类前按内容类型用模版预处理 50_Raw 中的条目
---

# Organizer 插件注册表

本目录下的插件在 **Organizer 处理 50_Raw/** 时生效：在「逐个分析文件」之前，先根据内容类型匹配插件，命中则按对应模版整理内容，再继续类型判断与分类归位。

## 约定

- **Skill.md**（本文件）：插件注册表，列出插件名称、匹配条件、模版文件。
- **模版文件**：命名格式 `template_<内容类型>.md`，例如 `template_summary_problem.md`。定义该类型的字段与格式，供 AI 从原文抽取并填充。

## 插件列表

| 插件名 | 匹配条件（内容特征） | 模版文件 |
|--------|----------------------|----------|
| summary_problem | 故障/问题类：含 故障、报错、异常、提出人、工单、现象、根因 等关键词，或明显为问题/事故描述 | `template_summary_problem.md` |
| meeting_minutes | 会议纪要类：含 会议、纪要、参会人、议题、决议、待办 等关键词，或明显为会议记录/会议摘要格式 | `template_meeting_minutes.md` |

## 使用方式

Organizer 执行时：

1. 若存在 `.pkm/Skills/PKM/plugin/Skill.md`，则读取本注册表。
2. 对 50_Raw 中每个文件（含 inbox、merged）：用「匹配条件」判断是否命中某插件。
3. 若命中：读取对应 `template_*.md`，按模版从原文抽取字段并重写/补充内容，再继续后续分析、合并、分类。
4. 若未命中：跳过插件，按原流程处理。

## 扩展

新增插件时：

1. 在 `plugin/` 下新增模版文件，命名：`template_<内容类型>.md`。
2. 在本表「插件列表」中增加一行：插件名、匹配条件、模版文件名。
