# Skill: WorkspaceManager (工作区管理器)

## 角色定位

你是 PKM 系统的**工作区管理器**，负责 PKM Projects 与 OpenClaw Workspace 之间的同步管理。

---

## 触发时机

- 用户执行 `@pkm workspace` 相关命令时
- 在 OpenClaw 会话中执行 `@pkm` 主流程时
- 在 OpenClaw 中创建项目时

---

## 前置要求

⚠️ **必须先调用 `Verifier` 验证环境**

---

## 概念说明

### OpenClaw Workspace
- 位置：`~/.openclaw/workspace/`
- AI 工作的根目录
- 可以包含软链接指向 PKM 项目

### PKM Projects
- 位置：`~/.pkm/data/10_Projects/`
- 符合命名规范：`YYYYMMDD_HHMMSS_项目名`

### 系统文件（不参与同步）
- AGENTS.md、BOOT.md、BOOTSTRAP.md、HEARTBEAT.md
- IDENTITY.md、SOUL.md、TOOLS.md、USER.md

---

## 操作 1：检测并同步 workspace (`@pkm` 主流程)

### 步骤 1：检测运行环境

检测当前是否在 OpenClaw 会话中：
```bash
# 检查是否有 OpenClaw 相关环境变量或配置文件
if [ -d "$HOME/.openclaw" ]; then
    # 在 OpenClaw 环境中
fi
```

### 步骤 2：扫描 workspace

遍历 workspace 中的所有条目：
```bash
WORKSPACE_DIR="$HOME/.openclaw/workspace"
PROJECTS_DIR="$HOME/.pkm/data/10_Projects"

# 排除系统文件
SYSTEM_FILES="AGENTS.md BOOT.md BOOTSTRAP.md HEARTBEAT.md IDENTITY.md SOUL.md TOOLS.md USER.md"

for item in "$WORKSPACE_DIR"/*; do
    item_name=$(basename "$item")
    
    # 跳过系统文件
    if echo "$SYSTEM_FILES" | grep -q "$item_name"; then
        continue
    fi
    
    # 检查是否为软链接
    if [ -L "$item" ]; then
        target=$(readlink "$item")
        # 检查目标是否在 10_Projects 中
        if [[ "$target" == *"$PROJECTS_DIR"* ]]; then
            # 链接有效，继续
        else
            # 链接目标不在 10_Projects 中
            echo "⚠️ 检测到无效链接: $item_name → $target"
        fi
    else
        # 目录，检查是否在 10_Projects 中
        item_realpath=$(realpath "$item" 2>/dev/null)
        if [[ "$item_realpath" == *"$PROJECTS_DIR"* ]]; then
            # 目录在 10_Projects 中，正常
        else
            # 目录不在 10_Projects 中，需要合并
            UNMERGED_PROJECTS+=("$item_name")
        fi
    fi
done
```

### 步骤 3：询问用户是否合并

如果检测到未纳入 PKM 的项目，询问用户：
```
🔍 检测到 workspace 中有未纳入 PKM 的项目：
- my_project

是否合并到 PKM？[Y/N]
```

### 步骤 4：执行合并

如果用户同意合并：

1. **重命名项目**：
   - 新名称格式：`YYYYMMDD_HHMMSS_原名称`
   ```bash
   timestamp=$(date +%Y%m%d_%H%M%S)
   new_name="${timestamp}_${item_name}"
   ```

2. **移动到 PKM**：
   ```bash
   mv "$WORKSPACE_DIR/$item_name" "$PROJECTS_DIR/$new_name"
   ```

3. **重建软链接**：
   ```bash
   ln -s "$PROJECTS_DIR/$new_name" "$WORKSPACE_DIR/$item_name"
   ```

**合并示例**：
```
# 原始
workspace/my_project/ → /home/user/workspace/my_project/

# 合并后
workspace/my_project → /home/user/.pkm/data/10_Projects/20260214_175000_my_project/
```

---

## 操作 2：创建项目时同步 (`@pkm project add`)

在创建新项目后，询问用户是否同步到 workspace：

```
📦 项目已创建：20260214_175000_my_project

是否同步到 workspace？[Y/N]
  - Y: 创建软链接，链接名可自定义
  - N: 稍后可通过 @pkm workspace add 同步
```

如果选择同步：
```bash
# 询问链接名称（可选，默认使用项目名）
echo "请输入 workspace 中的显示名称（直接回车使用项目名）："
read link_name
link_name=${link_name:-$project_name}

# 创建软链接
ln -s "$PROJECTS_DIR/$project_name" "$WORKSPACE_DIR/$link_name"
```

---

## 操作 3：手动同步命令

### @pkm workspace ls

查看 workspace 同步状态：
```bash
# 输出格式：
🔗 workspace 同步状态：
✅ 已同步：
   - 舆情投资工具 → 10_Projects/20260213_235400_舆情投资建议工具
   - pkm_manager → 10_Projects/20260130_140000_pkm_manager

📁 未同步：
   - my_project (workspace 中存在，PKM 中不存在)
```

### @pkm workspace add <项目>

手动将 PKM 项目同步到 workspace：
```bash
# 用法：@pkm workspace add <项目名>
# 示例：@pkm workspace add my_project

# 检查项目是否存在
if [ -d "$PROJECTS_DIR/$project_name" ]; then
    # 询问链接名称
    echo "请输入 workspace 中的显示名称："
    read link_name
    ln -s "$PROJECTS_DIR/$project_name" "$WORKSPACE_DIR/$link_name"
    echo "✅ 已同步到 workspace"
else
    echo "❌ 项目不存在"
fi
```

### @pkm workspace sync

手动触发全量同步检测（与主流程相同）

---

## 配置文件

### 排除列表

在 `$HOME/.pkm/.config` 中添加：
```bash
# Workspace 同步排除项
WORKSPACE_EXCLUDE="AGENTS.md BOOT.md BOOTSTRAP.md HEARTBEAT.md IDENTITY.md SOUL.md TOOLS.md USER.md"
```

---

## 安全机制

1. **只读扫描**：不修改未确认的项目
2. **备份提醒**：合并前提示用户备份
3. **保留链接名**：workspace 中的显示名称可以不同于 PKM 项目名
4. **系统文件保护**：不修改系统配置文件

---

## 关键原则

1. **用户确认**：合并前必须询问用户
2. **数据完整**：移动项目时确保数据不丢失
3. **灵活链接**：workspace 链接名可自定义
4. **多入口兼容**：支持 PKM 入口和 OpenClaw 入口

---

## 预期效果

通过 WorkspaceManager：
- ✅ workspace 自动同步 PKM 项目
- ✅ 多入口创建的项目可以合并
- ✅ 用户控制同步时机
- ✅ 灵活的链接命名
