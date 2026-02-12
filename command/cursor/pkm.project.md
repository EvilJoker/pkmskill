# /pkm.project

> 管理项目目录

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 执行：`@pkm project <操作>`

## 子命令

| 命令 | 功能 |
|------|------|
| `/pkm.project add <名称>` | 创建项目 |
| `/pkm.project ls` | 列出项目 |
| `/pkm.project ls --done` | 列出已完成项目 |
| `/pkm.project done <项目名>` | 标记完成 |
| `/pkm.project update <项目名>` | 更新进展 |
| `/pkm.project delete <项目名>` | 删除项目 |
| `/pkm.project archive` | 归档项目 |

## 相关命令

- `/pkm` - 主流程
- `/pkm.todo` - 任务管理
- `/pkm.help` - 帮助
