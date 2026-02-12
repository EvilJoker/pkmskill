# /pkm

> 主流程：一键整理知识

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME（数据目录）；PKM 根目录为 DATA_HOME 的上级（若配置不存在则默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`（位于 PKM 根目录下）
3. 执行：`@pkm`

## 工作流

```
Verify → Archive → Organize → Distill
```

## 命令列表

| 命令 | 功能 |
|------|------|
| `/pkm` | 主流程 |
| `/pkm.inbox` | 快速捕获 |
| `/pkm.advice` | 智能咨询 |
| `/pkm.todo` | 任务管理 |
| `/pkm.project` | 项目管理 |
| `/pkm.status` | 查看状态 |
| `/pkm.upgrade` | 更新版本 |
| `/pkm.help` | 帮助 |
