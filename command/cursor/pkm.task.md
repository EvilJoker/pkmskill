# /pkm.task

> 任务管理（与 `docs/ARCHITECTURE.md` 4.4 一致）

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 执行：`@pkm task <操作> [参数]`

## 子命令

| 命令 | 功能 |
|------|------|
| `/pkm.task add <内容>` | 添加新任务，创建任务区 |
| `/pkm.task ls` | 列出所有任务 |
| `/pkm.task ls --all` | 列出所有任务（含已归档） |
| `/pkm.task use <id>` | 切换到指定任务 |
| `/pkm.task edit <id>` | 编辑任务 |
| `/pkm.task update <id>` | 更新任务进展 |
| `/pkm.task done <id>` | 完成任务，总结任务清单 |
| `/pkm.task delete <id>` | 删除任务 |
| `/pkm.task archive` | 自动扫描含 completed.md 的任务并归档，回流知识到知识库 |

## 相关命令

- `/pkm` - 主流程
- `/pkm.project` - 长期项目管理
- `/pkm.help` - 帮助
