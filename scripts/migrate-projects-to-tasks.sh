#!/bin/bash
#
# 将旧的「项目」格式迁移为新的「任务」格式（与 docs/ARCHITECTURE.md 一致）
#
# 旧格式：
#   - data/10_Projects/YYYYMMDD_HHMMSS_xxx/   （可能有 COMPLETED.md 表示已完成）
#   - data/30_Resources/todo.md, todo_archive.md
#
# 新格式：
#   - data/10_Tasks/tasks.md, tasks_archive.md
#   - data/10_Tasks/TASK_WORKSPACE_YYYYMMDD_HHMMSS_xxx/task.md（及 completed.md 若已完成）
#
# 用法：在 PKM 仓库根目录执行
#   bash scripts/migrate-projects-to-tasks.sh [--dry-run]
# 或指定 DATA_HOME：
#   DATA_HOME=/path/to/data bash scripts/migrate-projects-to-tasks.sh
#
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PKM_HOME="$(cd "${SCRIPT_DIR}/.." && pwd)"
DRY_RUN=false

for arg in "$@"; do
  [ "$arg" = "--dry-run" ] && DRY_RUN=true
done

# 解析 DATA_HOME
if [ -n "$DATA_HOME" ]; then
  DATA_ROOT="$DATA_HOME"
else
  CONFIG_FILE="${PKM_HOME}/.config"
  if [ -f "$CONFIG_FILE" ]; then
    DATA_ROOT=$(grep -E '^DATA_HOME=' "$CONFIG_FILE" | head -1 | sed 's/^DATA_HOME=//' | sed 's/^"//;s/"$//')
  fi
  [ -z "$DATA_ROOT" ] && DATA_ROOT="${PKM_HOME}/data"
fi

OLD_PROJECTS="${DATA_ROOT}/10_Projects"
NEW_TASKS="${DATA_ROOT}/10_Tasks"
OLD_TODO="${DATA_ROOT}/30_Resources/todo.md"
OLD_TODO_ARCHIVE="${DATA_ROOT}/30_Resources/todo_archive.md"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📦 旧项目 → 新任务格式迁移${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  DATA_HOME: ${DATA_ROOT}"
echo -e "  10_Projects: ${OLD_PROJECTS}"
echo -e "  10_Tasks:    ${NEW_TASKS}"
[ "$DRY_RUN" = true ] && echo -e "  ${YELLOW}（仅预览，不写入）${NC}"
echo ""

run() {
  if [ "$DRY_RUN" = true ]; then
    echo -e "  ${YELLOW}[dry-run]${NC} $*"
  else
    "$@"
  fi
}

# 生成任务 ID：从目录名 YYYYMMDD_HHMMSS_xxx 得到 T-YYYYMMDD-HHMMSS-001
task_id_from_dir() {
  local name="$1"
  local seq="$2"
  # 20260113_143000_myproject -> T-20260113-143000-001
  local datepart="${name%%_*}"      # 20260113
  local rest="${name#*_}"          # 143000_myproject
  local timepart="${rest%%_*}"     # 143000
  printf "T-%s-%s-%03d" "$datepart" "$timepart" "$seq"
}

# 从目录名取简短标题（最后一段或整段）
title_from_dir() {
  local name="$1"
  # 20260113_143000_myproject -> myproject；若无下划线则用原名
  if [[ "$name" == *_[0-9][0-9][0-9][0-9][0-9][0-9]_* ]]; then
    echo "${name#*_[0-9][0-9][0-9][0-9][0-9][0-9]_}"
  else
    echo "$name"
  fi
}

# 迁移 10_Projects → 10_Tasks
migrate_projects() {
  [ ! -d "$OLD_PROJECTS" ] && return 0

  echo -e "${BLUE}[1] 迁移 10_Projects → 10_Tasks${NC}"
  run mkdir -p "$NEW_TASKS"
  local seq=1
  local now
  now=$(date '+%Y-%m-%d %H:%M:%S')

  for dir in "$OLD_PROJECTS"/*/; do
    [ -d "$dir" ] || continue
    local name
    name=$(basename "$dir")
    # 跳过明显非项目目录
    case "$name" in
      .*|manual|knowledge) continue ;;
    esac

    local workspace_name="TASK_WORKSPACE_${name}"
    local workspace_path="${NEW_TASKS}/${workspace_name}"
    local task_id
    task_id=$(task_id_from_dir "$name" "$seq")
    local title
    title=$(title_from_dir "$name")

    if [ -f "${dir}COMPLETED.md" ]; then
      # 已完成：生成 task.md + completed.md，并写入 tasks_archive.md
      echo -e "  ${GREEN}✓${NC} [已完成] $name → $workspace_name"
      run mkdir -p "$workspace_path"
      run cp "${dir}COMPLETED.md" "${workspace_path}/completed.md"
      # 生成最小 task.md
      if [ "$DRY_RUN" != true ]; then
        cat > "${workspace_path}/task.md" << EOF
# 任务：$title

**任务 ID**：$task_id
**标题**：$title
**创建时间**：（迁移自旧项目，未记录）
**4 象限**：第二象限（重要但不紧急）
**分类**：（迁移）
**优先级**：中
**标签**：迁移

## 想法/目标

（由 10_Projects/$name 迁移，请按需在 task.md 中补全。）

## 计划

（迁移后请补全。）

## 实现思路

（迁移后请补全。）

## 关联项目

（可选。）

## 进展记录

- （迁移自旧项目，详见 completed.md）

## 其他

原项目目录：10_Projects/$name（迁移后已备份为 10_Projects.bak.*）
EOF
      fi
      # 追加到 tasks_archive.md
      if [ "$DRY_RUN" != true ]; then
        [ ! -f "${NEW_TASKS}/tasks_archive.md" ] && {
          cat > "${NEW_TASKS}/tasks_archive.md" << EOF
# 已完成任务归档

> 最后更新：$now

## 已完成

EOF
        }
        cat >> "${NEW_TASKS}/tasks_archive.md" << EOF
### [已完成] $task_id: $title

**完成时间**：（见 completed.md）  
**完成总结摘要**：（迁移自 COMPLETED.md，详见工作区 completed.md）

---

EOF
      fi
    else
      # 进行中：生成 task.md，并写入 tasks.md
      echo -e "  ${GREEN}✓${NC} [进行中] $name → $workspace_name"
      run mkdir -p "$workspace_path"
      if [ "$DRY_RUN" != true ]; then
        cat > "${workspace_path}/task.md" << EOF
# 任务：$title

**任务 ID**：$task_id
**标题**：$title
**创建时间**：（迁移自旧项目，未记录）
**4 象限**：第二象限（重要但不紧急）
**分类**：（迁移）
**优先级**：中
**标签**：迁移

## 想法/目标

（由 10_Projects/$name 迁移，请按需补全。）

## 计划

（迁移后请补全。）

## 实现思路

（迁移后请补全。）

## 关联项目

（可选。）

## 进展记录

- （迁移自旧项目）

## 其他

原项目目录：10_Projects/$name（迁移后已备份为 10_Projects.bak.*）
EOF
      fi
      # 追加到 tasks.md（先确保文件头存在）
      if [ "$DRY_RUN" != true ]; then
        if [ ! -f "${NEW_TASKS}/tasks.md" ]; then
          cat > "${NEW_TASKS}/tasks.md" << EOF
# 任务清单

> 最后更新：$now

## 进行中

### 第二象限：重要但不紧急

EOF
        fi
        cat >> "${NEW_TASKS}/tasks.md" << EOF
### [进行中] $task_id: $title

**工作空间路径**：$workspace_name/
**4象限**：第二象限（重要但不紧急）

---

EOF
      fi
    fi
    seq=$((seq + 1))
  done

  # 备份并移除 10_Projects
  if [ "$DRY_RUN" != true ] && [ -d "$OLD_PROJECTS" ]; then
    local bak
    bak="${DATA_ROOT}/10_Projects.bak.$(date '+%Y%m%d_%H%M%S')"
    echo -e "  ${YELLOW}备份${NC} 10_Projects → $bak"
    run mv "$OLD_PROJECTS" "$bak"
  fi
  echo ""
}

# 迁移 todo.md / todo_archive.md → tasks.md / tasks_archive.md（内容合并为参考块）
migrate_todo_files() {
  local has_todo=0
  [ -f "$OLD_TODO" ] && has_todo=1
  [ -f "$OLD_TODO_ARCHIVE" ] && has_todo=1
  [ "$has_todo" -eq 0 ] && return 0

  echo -e "${BLUE}[2] 迁移 todo.md / todo_archive.md 为参考内容${NC}"
  run mkdir -p "$NEW_TASKS"
  local now
  now=$(date '+%Y-%m-%d %H:%M:%S')

  if [ -f "$OLD_TODO" ] && [ "$DRY_RUN" != true ]; then
    if [ ! -f "${NEW_TASKS}/tasks.md" ]; then
      cat > "${NEW_TASKS}/tasks.md" << EOF
# 任务清单

> 最后更新：$now

## 进行中

（以下为迁移自 30_Resources/todo.md 的参考内容，请按需整理为上方「进行中」的索引条目。）

<details>
<summary>迁移自 todo.md（仅供参考）</summary>

EOF
      cat "$OLD_TODO" >> "${NEW_TASKS}/tasks.md"
      echo "" >> "${NEW_TASKS}/tasks.md"
      echo "</details>" >> "${NEW_TASKS}/tasks.md"
      echo -e "  ${GREEN}✓${NC} 已把 todo.md 内容并入 tasks.md 作为参考块"
    else
      echo -e "  ${YELLOW}跳过${NC} tasks.md 已存在，未覆盖；旧 todo.md 仍保留于 30_Resources/"
    fi
  fi

  if [ -f "$OLD_TODO_ARCHIVE" ] && [ "$DRY_RUN" != true ]; then
    if [ ! -f "${NEW_TASKS}/tasks_archive.md" ]; then
      cat > "${NEW_TASKS}/tasks_archive.md" << EOF
# 已完成任务归档

> 最后更新：$now

## 已完成

（以下为迁移自 30_Resources/todo_archive.md 的参考内容，请按需整理为正式条目。）

<details>
<summary>迁移自 todo_archive.md（仅供参考）</summary>

EOF
      cat "$OLD_TODO_ARCHIVE" >> "${NEW_TASKS}/tasks_archive.md"
      echo "" >> "${NEW_TASKS}/tasks_archive.md"
      echo "</details>" >> "${NEW_TASKS}/tasks_archive.md"
      echo -e "  ${GREEN}✓${NC} 已把 todo_archive.md 内容并入 tasks_archive.md 作为参考块"
    else
      echo -e "  ${YELLOW}跳过${NC} tasks_archive.md 已存在，未覆盖；旧 todo_archive.md 仍保留于 30_Resources/"
    fi
  fi
  echo ""
}

# 主流程
migrate_projects
migrate_todo_files

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 迁移完成${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}建议：${NC}"
echo "  1. 检查 10_Tasks/tasks.md 与 tasks_archive.md，按需补全索引与 task.md 内容"
echo "  2. 旧 10_Projects 已备份为 10_Projects.bak.<时间戳>，确认无误后可删除"
echo "  3. 若曾使用 30_Resources/todo.md，内容已并入 tasks.md 的参考块，可整理后删除 30_Resources/todo.md / todo_archive.md"
echo ""
