# /pkm.advice

> 基于知识库回答问题（与 `docs/ARCHITECTURE.md` 4.3 一致）

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 执行：`@pkm advice <问题>` 或 `@pkm advice --scope <范围> <问题>`

## scope 参数（宪章 4.3）

- `common`：仅 AI 通用知识
- `local`：仅当前知识库（10_Tasks、20_Areas、30_Resources、40_Archives）
- `task` 或 `<任务名>`：指定任务知识库（10_Tasks/<任务工作区>/）
- 默认：common + local（可叠加）

## 相关命令

- `/pkm` - 主流程
- `/pkm.inbox` - 快速捕获
- `/pkm.task` - 任务管理
- `/pkm.help` - 帮助
