# /pkm.help

> 显示 PKM 帮助信息

## 路由执行

1. 定位 PKM 根目录与数据目录：读取 `~/.pkm/.config` 中的 DATA_HOME；PKM 根目录为 DATA_HOME 的上级（默认 ~/.pkm、~/.pkm/data）
2. 加载 `skill/SKILL.md`
3. 执行：`@pkm help`

## 命令列表（与 ARCHITECTURE 第三章一致）

| 命令 | 功能 |
|------|------|
| `/pkm` | 主流程（Verify → project archive → Organize → Distill） |
| `/pkm.inbox` | 快速捕获（支持 --parse 先解析链接） |
| `/pkm.advice` | 智能咨询（支持 --scope common/local/项目名） |
| `/pkm.todo` | 任务管理（add/ls/ls --done/edit/update/done/delete） |
| `/pkm.project` | 项目管理（add/ls/ls --done/done/update/delete/archive） |
| `/pkm.status` | 查看状态 |
| `/pkm.upgrade` | 更新版本 |
| `/pkm.help` | 帮助 |
