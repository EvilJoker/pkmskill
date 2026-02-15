# /pkm.inbox

> 快速捕获碎片化信息到 `50_Raw/inbox/`（与 `docs/ARCHITECTURE.md` 4.1 一致）

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 执行：`@pkm inbox <内容>`（默认不解析链接）或 `@pkm inbox --parse <内容>`（先解析链接内容再捕获）

## 功能要点

- 智能识别任务：若内容像任务，推荐使用 `@pkm task add <内容>`
- 文件名格式：`YYYYMMDD_HHMMSS_标题_inbox.md`
- 保存位置：`50_Raw/inbox/`

## 相关命令

- `/pkm` - 主流程
- `/pkm.task` - 任务管理
- `/pkm.advice` - 智能咨询
- `/pkm.help` - 帮助
