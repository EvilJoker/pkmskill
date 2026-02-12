# /pkm.advice

> 基于知识库回答问题

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 执行：`@pkm advice <问题>` 或 `@pkm advice --scope <范围> <问题>`

## 相关命令

- `/pkm` - 主流程
- `/pkm.inbox` - 快速捕获
- `/pkm.help` - 帮助
