# /pkm.inbox

> 快速捕获碎片化信息到 inbox

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 执行：`@pkm inbox <内容>` 或 `@pkm inbox --parse <内容>`

## 相关命令

- `/pkm` - 主流程
- `/pkm.advice` - 智能咨询
- `/pkm.help` - 帮助
