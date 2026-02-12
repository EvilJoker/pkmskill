# /pkm.upgrade

> 更新 PKM 版本

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 执行：`@pkm upgrade`

## 功能

在 PKM 安装目录执行 `git pull`，更新 skill 与 command。

## 相关命令

- `/pkm.status` - 查看状态
- `/pkm` - 主流程
- `/pkm.help` - 帮助
