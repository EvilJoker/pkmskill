# Skill: PkmSelfManager (PKM 自管理器)

## 角色定位

你是知识管理系统的**自管理模块**，负责：
- 查看 PKM 系统状态
- 更新 PKM 系统版本

---

## 触发时机

- **查看状态**：用户执行 `@pkm status` 时
- **更新版本**：用户执行 `@pkm upgrade` 时

---

## 前置要求

⚠️ **必须先调用 `Verifier` 验证环境**：

```text
@Verifier → 确认 PKM 配置文件存在 → 继续执行 PkmSelfManager
```

---

## 自动定位 PKM 配置

**AI 自动执行**：每次调用 PKM Skill 时，会自动从配置文件读取配置。

```bash
# 自动检测 PKM 配置
CONFIG_FILE="${HOME}/.pkm/.config"
if [ -f "$CONFIG_FILE" ]; then
    # 读取 DATA_HOME
    DATA_HOME=$(grep "^DATA_HOME=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    # 读取各平台 HOME
    CURSOR_HOME=$(grep "^CURSOR_HOME=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    CLAUDE_HOME=$(grep "^CLAUDE_HOME=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    GEMINI_HOME=$(grep "^GEMINI_HOME=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    OPENCLAW_HOME=$(grep "^OPENCLAW_HOME=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")
fi

# 如果配置不存在，使用默认目录
PKM_HOME="${PKM_HOME:-${HOME}/.pkm}"
DATA_HOME="${DATA_HOME:-${HOME}/.pkm/data}"
```

**配置文件位置**：`~/.pkm/.config`

**配置项**：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| DATA_HOME | 知识数据目录 | ~/.pkm/data |
| CURSOR_HOME | Cursor 配置目录 | ~/.cursor |
| CLAUDE_HOME | Claude Code 配置目录 | ~/.claude |
| GEMINI_HOME | Gemini CLI 配置目录 | ~/.gemini |
| OPENCLAW_HOME | OpenCLAW 配置目录 | ~/.openclaw |

---

## 操作 1：查看状态 (`@pkm status`)

### 步骤 1：读取配置文件

读取 `~/.pkm/.config` 文件，获取配置项。

### 步骤 2：获取知识库位置

根据配置确定知识库根目录（DATA_HOME 的上级目录）。

### 步骤 3：统计知识库概况（与宪章 4.5 一致）

统计各目录下的条目或文件数量：

- `10_Tasks/`：任务（工作空间）数量
- `20_Areas/`：领域数量
- `30_Resources/`：资源数量
- `40_Archives/`：归档数量
- `50_Raw/`：待处理素材数量

### 步骤 4：获取长期项目列表

引用 `@pkm project ls` 获取 20_Areas/Projects/ 下的长期项目列表。

### 步骤 5：获取任务列表

引用 `@pkm task ls` 获取待办任务列表；引用 `@pkm task ls --all` 可展示含已归档任务。

### 步骤 6：获取 PKM 版本

获取当前安装的 PKM 版本（git commit 或 tag）。

### 步骤 7：获取上次执行信息

- 上次 pkm 执行时间：从日志或总结报告文件中提取
- 上次 pkm 总结报告（<100字）：读取最新的 Distill 报告，取前100字核心摘要

### 步骤 8：输出状态报告

```text
╔═══════════════════════════════════════════════════════════╗
║                  PKM 状态报告                              ║
╚═══════════════════════════════════════════════════════════╝

📁 配置文件位置
   ~/.pkm/.config

📂 数据目录位置
   /home/user/.pkm/data

📊 知识库概况
   ┌─────────────────────┬────────┐
   │ 10_Tasks            │ 3 个   │
   │ 20_Areas            │ 5 个   │
   │ 30_Resources        │ 2 个   │
   │ 40_Archives         │ 8 个   │
   │ 50_Raw              │ 4 个   │
   └─────────────────────┴────────┘

📋 活跃项目 (3)
   1. 20260113_143000_用户认证系统
   2. 20260113_150000_电商首页优化
   3. 20260110_090000_性能监控系统

✅ 待办任务 (5)
   1. [第一象限] 修复生产环境登录 Bug
   2. [第二象限] 优化 React 组件性能
   3. [第二象限] 学习 TypeScript 高级特性
   4. [第三象限] 回复客户邮件
   5. [第四象限] 整理项目文档

📦 PKM 版本
   v1.2.3 (commit: abc1234)

⏰ 上次执行
   2026-01-13 18:30:00 (@pkm 主流程)

📝 上次总结报告
   2026-01-13_183000_知识提炼报告_Distill.md
   - 新增知识：5 个，提炼应用层：2 个...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 提示：
  - 使用 @pkm 整理知识库
  - 使用 @pkm project ls 查看长期项目
  - 使用 @pkm task ls 与 @pkm task ls --all 查看任务
  - 使用 @pkm upgrade 更新 PKM 版本
  - 使用 @pkm help 查看帮助
```

---

## 操作 2：更新 PKM (`@pkm upgrade`)

### 步骤 0：检查并初始化 PKM（如需要）

在执行升级前，先检查 PKM 是否为 git 仓库：

```bash
# 检查 PKM_HOME 是否存在
if [ ! -d "$PKM_HOME" ]; then
    echo "PKM 目录不存在，正在创建..."
    mkdir -p "$PKM_HOME"
fi

# 检查是否为 git 仓库
if [ ! -d "$PKM_HOME/.git" ]; then
    echo "检测到 PKM 不是 git 仓库，正在初始化..."
    
    # 备份现有数据（如存在）
    if [ -d "$PKM_HOME/data" ] || [ -f "$PKM_HOME/.config" ]; then
        BACKUP_DIR="${PKM_HOME}_backup_$(date +%Y%m%d_%H%M%S)"
        echo "📦 备份现有数据到 $BACKUP_DIR..."
        mkdir -p "$BACKUP_DIR"
        [ -d "$PKM_HOME/data" ] && cp -r "$PKM_HOME/data" "$BACKUP_DIR/"
        [ -f "$PKM_HOME/.config" ] && cp "$PKM_HOME/.config" "$BACKUP_DIR/"
    fi
    
    # 克隆仓库
    echo "📥 正在克隆 PKM 仓库..."
    git clone https://github.com/EvilJoker/pkmskill.git "$PKM_HOME"
    
    # 恢复用户数据
    if [ -d "$BACKUP_DIR/data" ]; then
        echo "🔄 正在恢复用户数据..."
        rm -rf "$PKM_HOME/data"
        cp -r "$BACKUP_DIR/data" "$PKM_HOME/"
    fi
    if [ -f "$BACKUP_DIR/.config" ]; then
        cp "$BACKUP_DIR/.config" "$PKM_HOME/"
    fi
    
    echo "✅ PKM 初始化完成"
fi
```

### 步骤 1：确认 PKM 安装目录

默认 PKM 安装目录为 `~/.pkm`（或由 PKM_HOME 环境变量指定）。

### 步骤 2：执行 git pull

在 PKM 安装目录执行 `git pull` 命令更新代码。

```bash
cd ~/.pkm && git pull
```

### 步骤 3：处理更新结果

#### 更新成功

```text
✅ PKM 更新成功

📦 PKM 版本
   旧版本：v1.2.2
   新版本：v1.2.3

📝 更新内容
   - 新增功能：项目归档优化
   - Bug 修复：修复任务列表显示问题
   - 文档更新：完善帮助文档

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 提示：
  - Skill 和 Command 已自动更新
  - 如有重大变更，可能需要重启 Cursor/Claude
```

#### 更新失败

```text
❌ PKM 更新失败

📋 可能原因：
   1. 网络连接问题
   2. 本地有未提交的修改
   3. Git 仓库配置问题

💡 解决方案：
   1. 检查网络连接后重试
   2. 先提交或暂存本地修改：cd ~/.pkm && git stash
   3. 手动检查 Git 仓库状态
```

### 步骤 4：验证更新

更新完成后，验证 skill 和 command 文件是否正确更新。

---

## 安全机制

### 1. 路径验证

- ✅ 只读取 `~/.pkm/.config` 配置文件
- ✅ 只在 `~/.pkm/` 目录下执行 git pull
- ❌ 禁止操作知识库数据目录

### 2. 只读操作

- `@pkm status` 只读取信息，不修改任何文件
- `@pkm upgrade` 只执行 git pull，不修改用户数据

---

## 关键原则

1. **状态透明**：用户可以随时查看 PKM 系统状态
2. **一键更新**：用户可以通过简单命令更新 PKM 版本
3. **信息完整**：状态报告包含用户关心的所有信息
4. **安全优先**：更新操作不影响用户数据

---

## 预期效果

通过 PkmSelfManager，用户可以：

- ✅ 查看 PKM 系统配置和数据目录位置
- ✅ 了解知识库的整体概况
- ✅ 查看活跃项目和待办任务
- ✅ 了解 PKM 版本和更新状态
- ✅ 一键更新 PKM 到最新版本
