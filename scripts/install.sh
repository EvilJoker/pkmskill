#!/bin/bash

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 默认安装目录
DEFAULT_PKM_HOME="${HOME}/.pkm"

# ============ 帮助信息 ============
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h     显示此帮助信息"
    echo ""
    echo "说明:"
    echo "  默认安装目录: ${DEFAULT_PKM_HOME}"
    echo ""
    echo "  支持的平台: Cursor, Claude Code, Gemini CLI, OpenCLAW"
}

# ============ 平台检测函数 ============

detect_cursor() {
    local cursor_dirs=("${HOME}/.cursor" "${HOME}/Library/Application Support/Cursor")
    for dir in "${cursor_dirs[@]}"; do
        [ -d "$dir" ] && echo "$dir" && return 0
    done
    return 1
}

detect_claude() {
    local claude_dirs=("${HOME}/.claude/skills" "${HOME}/Library/Application Support/Claude/skills")
    for dir in "${claude_dirs[@]}"; do
        [ -d "$dir" ] && echo "$dir" && return 0
    done
    return 1
}

detect_gemini() {
    local gemini_dirs=("${HOME}/.gemini/skills" "${HOME}/.gemini/agents")
    for dir in "${gemini_dirs[@]}"; do
        [ -d "$dir" ] && echo "$dir" && return 0
    done
    return 1
}

detect_openclaw() {
    local openclaw_dirs=("${HOME}/.openclaw/skills" "${HOME}/.openclaw/agents")
    for dir in "${openclaw_dirs[@]}"; do
        [ -d "$dir" ] && echo "$dir" && return 0
    done
    return 1
}

# ============ 安装函数 ============

install_cursor() {
    local pkm_home="$1"
    local cursor_dir
    
    cursor_dir=$(detect_cursor) || {
        echo -e "      ${YELLOW}⚠${NC} 未检测到 Cursor，跳过"
        return 1
    }

    echo -e "      ${GREEN}✓${NC} 检测到 Cursor: $cursor_dir"

    # 安装 Commands
    local cmd_dir="${cursor_dir}/commands"
    mkdir -p "$cmd_dir"
    for cmd in "${pkm_home}"/command/cursor/*.md; do
        [ -f "$cmd" ] || continue
        cmd_name=$(basename "$cmd" .md)
        ln -sf "$cmd" "${cmd_dir}/${cmd_name}.md"
        echo -e "      ${GREEN}✓${NC} 已安装 /${cmd_name}"
    done

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
    
    claude_dir=$(detect_claude) || {
        echo -e "      ${YELLOW}⚠${NC} 未检测到 Claude Code，跳过"
        return 1
    }

    echo -e "      ${GREEN}✓${NC} 检测到 Claude Code: $claude_dir"
    
    mkdir -p "$claude_dir"
    ln -sf "${pkm_home}/skill" "${claude_dir}/pkm"
    echo -e "      ${GREEN}✓${NC} 已安装 @pkm"

    return 0
}

install_gemini() {
    local pkm_home="$1"
    local gemini_dir
    
    gemini_dir=$(detect_gemini) || {
        echo -e "      ${YELLOW}⚠${NC} 未检测到 Gemini CLI，跳过"
        return 1
    }

    echo -e "      ${GREEN}✓${NC} 检测到 Gemini CLI: $gemini_dir"
    
    mkdir -p "$gemini_dir"
    ln -sf "${pkm_home}/skill" "${gemini_dir}/pkm"
    echo -e "      ${GREEN}✓${NC} 已安装 /pkm"

    return 0
}

install_openclaw() {
    local pkm_home="$1"
    local openclaw_dir
    
    openclaw_dir=$(detect_openclaw) || {
        echo -e "      ${YELLOW}⚠${NC} 未检测到 OpenCLAW，跳过"
        return 1
    }

    echo -e "      ${GREEN}✓${NC} 检测到 OpenCLAW: $openclaw_dir"
    
    mkdir -p "$openclaw_dir"
    ln -sf "${pkm_home}/skill" "${openclaw_dir}/pkm"
    echo -e "      ${GREEN}✓${NC} 已安装 @pkm"

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

# 选择安装目录
read -p "安装目录 [默认: ~/.pkm]: " PKM_HOME
PKM_HOME="${PKM_HOME:-$DEFAULT_PKM_HOME}"
PKM_HOME="${PKM_HOME/#\~/$HOME}"  # 展开 ~

echo ""
echo -e "${BLUE}📁 安装目录: ${PKM_HOME}${NC}"
echo ""

# 创建目录结构
echo -e "${BLUE}[1/3]${NC} 创建目录结构..."

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

# 创建必要文件
touch 30_Resources/todo.md
touch 30_Resources/todo_archive.md

echo -e "      ${GREEN}✓${NC} 目录结构已创建"

# 复制 Skill 和 Command
echo ""
echo -e "${BLUE}[2/3]${NC} 复制 Skill 和 Command..."

mkdir -p "${PKM_HOME}/skill"
cp -r "$(dirname "$0")/../skill/"* "${PKM_HOME}/skill/"

mkdir -p "${PKM_HOME}/command"
cp -r "$(dirname "$0")/../command/"* "${PKM_HOME}/command/"

echo -e "      ${GREEN}✓${NC} Skill 和 Command 已安装"

# 安装到各平台
echo ""
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
