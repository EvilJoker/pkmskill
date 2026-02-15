# /pkm.help

> 显示 PKM 帮助信息

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 加载 `skill/_Help.md`
4. 执行：`@pkm help`
