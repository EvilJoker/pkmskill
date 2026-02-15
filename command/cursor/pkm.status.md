# /pkm.status

> 查看知识库信息（与 `docs/ARCHITECTURE.md` 4.5 一致）

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 执行：`@pkm status`

## 输出内容

- 配置文件内容、数据目录位置
- 知识库数量概况（10_Tasks、20_Areas、30_Resources、40_Archives、50_Raw）
- 任务列表（引用 @pkm task ls / @pkm task ls --all）
- 长期项目列表（引用 @pkm project ls）
- PKM 版本、上次 pkm 执行时间、上次 pkm 总结报告简述

## 相关命令

- `/pkm.upgrade` - 更新 pkm 版本
- `/pkm` - 主流程
- `/pkm.help` - 帮助
