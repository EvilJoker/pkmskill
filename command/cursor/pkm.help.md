# /pkm.help

> 显示 PKM 帮助信息

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 执行：`@pkm help`

## 命令列表（与 docs/ARCHITECTURE.md 第三、四章一致）

| 命令 | 功能 |
|------|------|
| `/pkm` | 主流程（Verify → Archive → Organize → Distill；Archive = @pkm task archive） |
| `/pkm.inbox` | 快速捕获到 inbox（支持 --parse 先解析链接） |
| `/pkm.advice` | 智能咨询（--scope common/local/task） |
| `/pkm.task` | 任务管理（add/ls/ls --all/use/edit/update/done/delete/archive） |
| `/pkm.project` | 长期项目管理（add/delete/ls） |
| `/pkm.status` | 查看知识库信息 |
| `/pkm.upgrade` | 更新 pkm 版本（git pull） |
| `/pkm.help` | 帮助 |
