# /pkm

> 主流程：一键整理知识

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME（数据目录）；PKM 根目录为 DATA_HOME 的上级（若配置不存在则默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`（位于 PKM 根目录下）
3. 执行：`@pkm`

## 工作流

主流程执行顺序（与 `docs/ARCHITECTURE.md` 4.2 一致）：

```
Verify → Archive → Organize → Distill
```

- **Verify**：前置安全检查（5 个顶级目录、操作范围、写权限白名单）
- **Archive**：调用 `@pkm task archive` 执行任务归档与知识回流
- **Organize**：合并、分类、归位，清空 50_Raw/
- **Distill**：深度整合、金字塔提炼、系统性检查，生成报告

## 命令列表

| 命令 | 功能 |
|------|------|
| `/pkm` | 主流程（Verify → Archive → Organize → Distill） |
| `/pkm.inbox` | 快速捕获到 inbox |
| `/pkm.advice` | 智能咨询 |
| `/pkm.help` | 帮助信息 |
| `/pkm.task` | 任务管理 |
| `/pkm.status` | 查看知识库信息 |
| `/pkm.upgrade` | 更新 pkm 版本 |
| `/pkm.project` | 长期项目管理（add/delete/ls） |
