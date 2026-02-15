# /pkm.project

> 长期项目管理（与 `docs/ARCHITECTURE.md` 3 一致）：管理 20_Areas/Projects/

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 执行：`@pkm project <操作>`

## 子命令

| 命令 | 功能 |
|------|------|
| `/pkm.project add <名称>` | 在 20_Areas/Projects/ 添加新的长期项目 |
| `/pkm.project delete <project_name>` | 删除项目 |
| `/pkm.project ls` | 列出所有长期项目 |

## 相关命令

- `/pkm` - 主流程
- `/pkm.task` - 任务管理
- `/pkm.help` - 帮助
