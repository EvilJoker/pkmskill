# /pkm.status

> 查看 PKM 系统状态

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 执行：`@pkm status`

## 输出内容

- 配置文件位置
- 数据目录位置
- 知识库概况
- 项目列表 / 任务列表
- PKM 版本
- 上次执行信息

## 相关命令

- `/pkm.upgrade` - 更新版本
- `/pkm` - 主流程
- `/pkm.help` - 帮助
