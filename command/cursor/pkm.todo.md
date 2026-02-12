# /pkm.todo

> 管理待办任务

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 执行：`@pkm todo <操作>`

## 子命令

| 命令 | 功能 |
|------|------|
| `/pkm.todo add <内容>` | 添加任务 |
| `/pkm.todo ls` | 列出任务 |
| `/pkm.todo ls --done` | 列出已完成任务 |
| `/pkm.todo edit <id>` | 编辑任务 |
| `/pkm.todo update <id>` | 更新进展 |
| `/pkm.todo done <id>` | 完成任务 |
| `/pkm.todo delete <id>` | 删除任务 |

## 相关命令

- `/pkm` - 主流程
- `/pkm.project` - 项目管理
- `/pkm.help` - 帮助
