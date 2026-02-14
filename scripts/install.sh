#!/bin/bash

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 安装目录 = 脚本所在仓库根目录（不可交互修改，可通过安装后的 .config 调整）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PKM_HOME="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ============ 帮助信息 ============
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h     显示此帮助信息"
    echo ""
    echo "说明:"
    echo "  安装目录为脚本所在仓库根目录，安装后可通过编辑 .config 更改路径。"
    echo ""
    echo "  支持的平台: Cursor, Claude Code, Gemini CLI, OpenCLAW"
}

# ============ 平台检测函数 ============
# 各平台检测路径（用于输出说明）
CURSOR_PATHS=("${HOME}/.cursor" "${HOME}/Library/Application Support/Cursor")
CLAUDE_PATHS=("${HOME}/.claude/skills" "${HOME}/Library/Application Support/Claude/skills")
GEMINI_PATHS=("${HOME}/.gemini/skills" "${HOME}/.gemini/agents")
OPENCLAW_PATHS=("${HOME}/.openclaw/skills" "${HOME}/.openclaw/agents")

print_paths() {
    local name="$1"
    shift
    local arr=("$@")
    echo -e "      检测路径: ${arr[*]}"
}

detect_cursor() {
    local cursor_dirs=("${CURSOR_PATHS[@]}")
    for dir in "${cursor_dirs[@]}"; do
        [ -d "$dir" ] && echo "$dir" && return 0
    done
    return 1
}

detect_claude() {
    local claude_dirs=("${CLAUDE_PATHS[@]}")
    for dir in "${claude_dirs[@]}"; do
        [ -d "$dir" ] && echo "$dir" && return 0
    done
    return 1
}

detect_gemini() {
    local gemini_dirs=("${GEMINI_PATHS[@]}")
    for dir in "${gemini_dirs[@]}"; do
        [ -d "$dir" ] && echo "$dir" && return 0
    done
    return 1
}

detect_openclaw() {
    local openclaw_dirs=("${OPENCLAW_PATHS[@]}")
    for dir in "${openclaw_dirs[@]}"; do
        [ -d "$dir" ] && echo "$dir" && return 0
    done
    return 1
}

# ============ 安装函数 ============

install_cursor() {
    local pkm_home="$1"
    local cursor_dir

    print_paths "Cursor" "${CURSOR_PATHS[@]}"
    cursor_dir=$(detect_cursor) || {
        echo -e "      ${YELLOW}⚠ 未检测到 Cursor${NC}（上述路径均不存在），跳过"
        return 1
    }

    echo -e "      ${GREEN}✓ 检测到 Cursor: ${cursor_dir}${NC}"

    # 安全检查：确保目标不在 PKM_HOME 内
    local normalized_pkm_home
    normalized_pkm_home=$(cd "$pkm_home" 2>/dev/null && pwd)
    if [[ "$cursor_dir" == *"$normalized_pkm_home"* ]] || [[ "$normalized_pkm_home" == *"$cursor_dir"* ]]; then
        echo -e "      ${RED}✗ 错误：安装路径与 PKM 路径冲突，无法安装${NC}"
        return 1
    fi

    # 安装 Commands
    local cmd_dir="${cursor_dir}/commands"
    mkdir -p "$cmd_dir"
    for cmd in "${pkm_home}"/command/cursor/*.md; do
        [ -f "$cmd" ] || continue
        cmd_name=$(basename "$cmd" .md)
        ln -sf "$cmd" "${cmd_dir}/${cmd_name}.md"
        echo -e "      ${GREEN}✓${NC} 已安装 /${cmd_name}"
    done

    # 安全检查：确保目标路径不会创建在 PKM_HOME 内（防止递归）
    if [[ "${skill_dir}" == *"${pkm_home}"* ]] || [[ "${pkm_home}/skill" == *"${skill_dir}"* ]]; then
        echo -e "      ${RED}✗ 错误：安装路径冲突，无法安装${NC}"
        return 1
    fi
    
    # 安装 Skills
    local skill_dir="${cursor_dir}/skills"
    mkdir -p "$skill_dir"
    ln -sf "${pkm_home}/skill" "${skill_dir}/PKM"
    echo -e "      ${GREEN}✓${NC} 已安装 @pkm"

    return 0
}

install_claude() {
    local pkm_home="$1"
    local claude_dir

    print_paths "Claude" "${CLAUDE_PATHS[@]}"
    claude_dir=$(detect_claude) || {
        echo -e "      ${YELLOW}⚠ 未检测到 Claude Code${NC}（上述路径均不存在），跳过"
        return 1
    }

    echo -e "      ${GREEN}✓ 检测到 Claude Code: ${claude_dir}${NC}"

    # 安全检查：确保目标不在 PKM_HOME 内
    local normalized_pkm_home
    normalized_pkm_home=$(cd "$pkm_home" 2>/dev/null && pwd)
    if [[ "$claude_dir" == *"$normalized_pkm_home"* ]] || [[ "$normalized_pkm_home" == *"$claude_dir"* ]]; then
        echo -e "      ${RED}✗ 错误：安装路径与 PKM 路径冲突，无法安装${NC}"
        return 1
    fi
    
    # 安全检查：确保目标路径不会创建在 PKM_HOME 内（防止递归）
    if [[ "${claude_dir}" == *"${pkm_home}"* ]] || [[ "${pkm_home}/skill" == *"${claude_dir}"* ]]; then
        echo -e "      ${RED}✗ 错误：安装路径冲突，无法安装${NC}"
        return 1
    fi
    
    mkdir -p "$claude_dir"
    ln -sf "${pkm_home}/skill" "${claude_dir}/pkm"
    echo -e "      ${GREEN}✓${NC} 已安装 @pkm"

    return 0
}

install_gemini() {
    local pkm_home="$1"
    local gemini_dir

    print_paths "Gemini" "${GEMINI_PATHS[@]}"
    gemini_dir=$(detect_gemini) || {
        echo -e "      ${YELLOW}⚠ 未检测到 Gemini CLI${NC}（上述路径均不存在），跳过"
        return 1
    }

    echo -e "      ${GREEN}✓ 检测到 Gemini CLI: ${gemini_dir}${NC}"

    # 安全检查：确保目标不在 PKM_HOME 内
    local normalized_pkm_home
    normalized_pkm_home=$(cd "$pkm_home" 2>/dev/null && pwd)
    if [[ "$gemini_dir" == *"$normalized_pkm_home"* ]] || [[ "$normalized_pkm_home" == *"$gemini_dir"* ]]; then
        echo -e "      ${RED}✗ 错误：安装路径与 PKM 路径冲突，无法安装${NC}"
        return 1
    fi
    
    # 安全检查：确保目标路径不会创建在 PKM_HOME 内（防止递归）
    if [[ "${gemini_dir}" == *"${pkm_home}"* ]] || [[ "${pkm_home}/skill" == *"${gemini_dir}"* ]]; then
        echo -e "      ${RED}✗ 错误：安装路径冲突，无法安装${NC}"
        return 1
    fi
    
    mkdir -p "$gemini_dir"
    ln -sf "${pkm_home}/skill" "${gemini_dir}/pkm"
    echo -e "      ${GREEN}✓${NC} 已安装 /pkm"

    return 0
}

install_openclaw() {
    local pkm_home="$1"
    local openclaw_dir

    print_paths "OpenCLAW" "${OPENCLAW_PATHS[@]}"
    openclaw_dir=$(detect_openclaw) || {
        echo -e "      ${YELLOW}⚠ 未检测到 OpenCLAW${NC}（上述路径均不存在），跳过"
        return 1
    }

    echo -e "      ${GREEN}✓ 检测到 OpenCLAW: ${openclaw_dir}${NC}"

    # 安全检查：确保目标不在 PKM_HOME 内，防止嵌套创建
    local normalized_pkm_home
    normalized_pkm_home=$(cd "$pkm_home" 2>/dev/null && pwd)
    if [[ "$openclaw_dir" == *"$normalized_pkm_home"* ]] || [[ "$normalized_pkm_home" == *"$openclaw_dir"* ]]; then
        echo -e "      ${RED}✗ 错误：安装路径与 PKM 路径冲突，无法安装${NC}"
        return 1
    fi

    mkdir -p "$openclaw_dir"

    # 检查主目录是否已存在
    local link_path="${openclaw_dir}/pkm"
    
    # 检查运行时目录是否存在副本（Skill 市场可能已安装，不区分大小写）
    local local_link_path
    local_link_path=$(find "${HOME}/.local/openclaw/skills" -maxdepth 1 -type d -iname "pkm" 2>/dev/null | head -1)

    # 检查是否已存在软链接或目录
    if [ -L "$link_path" ]; then
        echo -e "      ${GREEN}✓${NC} @pkm 已存在（${link_path}），跳过"
    elif [ -d "$link_path" ]; then
        echo -e "      ${YELLOW}⚠${NC} @pkm 目录已存在（${link_path}），请先删除后再安装"
    elif [ -n "$local_link_path" ] && [ -d "$local_link_path" ]; then
        # 检查运行时目录是否存在副本（Skill 市场可能已安装）
        echo -e "      ${YELLOW}⚠${NC} 检测到 @pkm 副本（${local_link_path}），请先通过 Skill 市场卸载后再安装"
    else
        ln -sf "${pkm_home}/skill" "${link_path}"
        echo -e "      ${GREEN}✓${NC} 已安装 @pkm"
    fi

    return 0
}

# ============ 主流程 ============

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}错误：未知参数: $1${NC}"
            show_help
            exit 1
            ;;
    esac
    shift
done

# 标题
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📦 PKM Skill 安装程序${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📁 安装目录: ${PKM_HOME}${NC}"
echo ""

# [1/3] 创建 .config 并填充正确路径
echo -e "${BLUE}[1/3]${NC} 创建 .config..."

CONFIG_TEMPLATE="${PKM_HOME}/.config.template"
CONFIG_FILE="${PKM_HOME}/.config"

if [ -f "$CONFIG_TEMPLATE" ]; then
    sed "s|/home/user|${HOME}|g" "$CONFIG_TEMPLATE" | sed "s|${HOME}/\.pkm/data|${PKM_HOME}/data|g" > "$CONFIG_FILE"
    echo -e "      ${GREEN}✓${NC} 已生成 ${CONFIG_FILE}（DATA_HOME=${PKM_HOME}/data）"
else
    echo -e "      ${YELLOW}⚠${NC} 未找到 .config.template，写入默认 .config"
    cat > "$CONFIG_FILE" << EOF
# 安装脚本生成，可按需修改（见 docs/ARCHITECTURE.md 2.3、6.3）
DATA_HOME="${PKM_HOME}/data"
CURSOR_HOME="${HOME}/.cursor/"
CLAUDE_HOME="${HOME}/.claude/"
GEMINI_HOME="${HOME}/.gemini/"
OPENCLAW_HOME="${HOME}/.openclaw/"
EOF
    echo -e "      ${GREEN}✓${NC} 已生成 ${CONFIG_FILE}"
fi
echo ""

# [2/3] 创建 data 目录结构
echo -e "${BLUE}[2/3]${NC} 创建目录结构..."

mkdir -p "${PKM_HOME}/data"
cd "${PKM_HOME}/data"

DIRS=(
    "10_Projects"
    "20_Areas/manual"
    "20_Areas/01principles"
    "20_Areas/02playbooks"
    "20_Areas/02templates"
    "20_Areas/02cases"
    "20_Areas/03notes"
    "30_Resources/Library"
    "30_Resources/summary"
    "40_Archives"
    "50_Raw/inbox"
    "50_Raw/merged"
)

for dir in "${DIRS[@]}"; do
    mkdir -p "$dir"
done

touch 30_Resources/todo.md
touch 30_Resources/todo_archive.md

echo -e "      ${GREEN}✓${NC} 目录结构已创建"
echo ""

# [3/3] 安装到各平台（使用当前仓库的 skill/command，无需复制）
echo -e "${BLUE}[3/3]${NC} 安装到各平台..."
echo ""

INSTALLED=0

# Cursor
echo -e "  ${CYAN}🔍 检测 Cursor...${NC}"
if install_cursor "$PKM_HOME"; then
    INSTALLED=$((INSTALLED + 1))
fi
echo ""

# Claude Code
echo -e "  ${CYAN}🔍 检测 Claude Code...${NC}"
if install_claude "$PKM_HOME"; then
    INSTALLED=$((INSTALLED + 1))
fi
echo ""

# Gemini CLI
echo -e "  ${CYAN}🔍 检测 Gemini CLI...${NC}"
if install_gemini "$PKM_HOME"; then
    INSTALLED=$((INSTALLED + 1))
fi
echo ""

# OpenCLAW
echo -e "  ${CYAN}🔍 检测 OpenCLAW...${NC}"
if install_openclaw "$PKM_HOME"; then
    INSTALLED=$((INSTALLED + 1))
fi
echo ""

# 完成
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 安装完成！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📁 安装目录: ${PKM_HOME}${NC}"
echo -e "${BLUE}🔗 已安装到: ${INSTALLED} 个平台${NC}"
echo ""
echo -e "${YELLOW}下一步：${NC}"
echo "  在 AI 工具中输入 @pkm help 查看命令"
echo ""
echo -e "${YELLOW}提示：${NC} 可通过编辑 ${CONFIG_FILE} 修改安装位置（如 DATA_HOME、各平台路径等）。"
echo ""
