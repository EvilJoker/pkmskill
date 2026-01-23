#!/bin/bash

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# PKM Skill 仓库地址
REPO_URL="https://github.com/EvilJoker/pkmskill.git"
TEMP_DIR="/tmp/pkmskill"

# PKM Skill 安装脚本
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📦 PKM Skill 安装程序${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 检测是否为更新模式
UPDATE_MODE=false
if [ "$1" == "--update" ]; then
    UPDATE_MODE=true
    echo -e "${YELLOW}🔄 更新模式${NC}"
    echo ""
fi

# 1. 检查当前目录
echo -e "${BLUE}[1/9]${NC} 检查安装环境..."
if [ -f ".git/config" ]; then
    echo -e "      ${GREEN}✓${NC} 检测到 Git 仓库"
else
    echo -e "      ${YELLOW}⚠${NC}  当前目录不是 Git 仓库"
    read -p "      是否继续安装？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}✗${NC} 安装已取消"
        exit 1
    fi
fi
echo ""

# 2. 下载 PKM Skill 仓库
echo -e "${BLUE}[2/9]${NC} 下载 PKM Skill..."

# 清理旧的临时文件
if [ -d "$TEMP_DIR" ]; then
    echo -e "      ${YELLOW}🗑${NC}  清理旧的临时文件..."
    rm -rf "$TEMP_DIR"
fi

# 检查 git 是否安装
if ! command -v git &> /dev/null; then
    echo -e "      ${RED}✗${NC} 未安装 Git，请先安装 Git"
    exit 1
fi

# 克隆仓库
echo -e "      ${BLUE}⬇${NC}  从 GitHub 下载..."
if git clone --depth=1 "$REPO_URL" "$TEMP_DIR" 2>/dev/null; then
    echo -e "      ${GREEN}✓${NC} 下载完成"
else
    echo -e "      ${RED}✗${NC} 下载失败，请检查网络连接"
    exit 1
fi
echo ""

# 3. 清理现有 Skills 文件
echo -e "${BLUE}[3/9]${NC} 清理现有 Skills 文件..."

# 备份现有文件（如果存在且是更新模式）
if [ "$UPDATE_MODE" = true ]; then
    if [ -d ".pkm/Skills" ]; then
    echo -e "      ${YELLOW}🔄${NC} 备份现有 Skills..."
    BACKUP_DIR=".pkm/Skills.backup.$(date +%Y%m%d_%H%M%S)"
    mv .pkm/Skills "$BACKUP_DIR"
    echo -e "      ${GREEN}✓${NC} 已备份到: $BACKUP_DIR"
fi
    if [ -d ".pkm/cursor-commands" ]; then
        echo -e "      ${YELLOW}🔄${NC} 备份现有 Cursor Commands..."
        BACKUP_DIR=".pkm/cursor-commands.backup.$(date +%Y%m%d_%H%M%S)"
        mv .pkm/cursor-commands "$BACKUP_DIR"
        echo -e "      ${GREEN}✓${NC} 已备份到: $BACKUP_DIR"
    fi
fi

# 清理现有文件（无论是否更新模式）
if [ -d ".pkm/Skills" ]; then
    echo -e "      ${YELLOW}🗑${NC}  删除现有 Skills 目录..."
    rm -rf .pkm/Skills
    echo -e "      ${GREEN}✓${NC} 已清理 Skills 目录"
fi

if [ -d ".pkm/cursor-commands" ]; then
    echo -e "      ${YELLOW}🗑${NC}  删除现有 Cursor Commands 目录..."
    rm -rf .pkm/cursor-commands
    echo -e "      ${GREEN}✓${NC} 已清理 Cursor Commands 目录"
fi

if [ ! -d ".pkm/Skills" ] && [ ! -d ".pkm/cursor-commands" ]; then
    echo -e "      ${GREEN}✓${NC} 清理完成（目录不存在或已清理）"
fi
echo ""

# 4. 安装 Skills 文件（Claude Code）
echo -e "${BLUE}[4/9]${NC} 安装 Skills 文件（Claude Code 支持）..."
mkdir -p .pkm/Skills
cp -r "$TEMP_DIR/.pkm/Skills" .pkm/
echo -e "      ${GREEN}✓${NC} Skills 文件已安装"
echo ""

# 5. 安装 Cursor Commands 源文件
echo -e "${BLUE}[5/9]${NC} 安装 Cursor Commands 文件..."
mkdir -p .pkm/cursor-commands
cp -r "$TEMP_DIR/.pkm/cursor-commands/"* .pkm/cursor-commands/
echo -e "      ${GREEN}✓${NC} Cursor Commands 文件已复制"
echo ""

# 6. 配置 Cursor Commands 链接
echo -e "${BLUE}[6/9]${NC} 配置 Cursor Commands..."

if [ -d ".cursor/commands" ]; then
    if [ -f ".cursor/commands/pkm.md" ] || [ -L ".cursor/commands/pkm.md" ]; then
        echo -e "      ${YELLOW}⚠${NC}  检测到现有 .cursor/commands/pkm.md"
        echo ""
        echo "      请选择操作："
        echo "        1) 覆盖（使用 PKM 命令）"
        echo "        2) 跳过（保留现有文件）"
        echo "        3) 备份后覆盖"
        read -p "      请选择 (1/2/3): " choice
        echo ""

        case $choice in
            1)
                rm -f ".cursor/commands/pkm.md"
                ln -s "../../.pkm/cursor-commands/pkm.md" ".cursor/commands/pkm.md"
                echo -e "      ${GREEN}✓${NC} 已创建软链接"
                ;;
            2)
                echo -e "      ${YELLOW}⏭${NC}  跳过，保留现有文件"
                ;;
            3)
                BACKUP_FILE=".cursor/commands/pkm.md.backup.$(date +%Y%m%d_%H%M%S)"
                mv ".cursor/commands/pkm.md" "$BACKUP_FILE"
                ln -s "../../.pkm/cursor-commands/pkm.md" ".cursor/commands/pkm.md"
                echo -e "      ${GREEN}✓${NC} 已备份到: $BACKUP_FILE"
                echo -e "      ${GREEN}✓${NC} 已创建软链接"
                ;;
            *)
                echo -e "      ${RED}✗${NC} 无效选择，跳过配置"
                ;;
        esac
    else
        ln -s "../../.pkm/cursor-commands/pkm.md" ".cursor/commands/pkm.md"
        echo -e "      ${GREEN}✓${NC} 已创建软链接到 .cursor/commands/pkm.md"
    fi
else
    echo -e "      ${YELLOW}?${NC} .cursor/commands/ 目录不存在"
    read -p "      是否创建目录并添加 PKM 命令？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p .cursor/commands
        ln -s "../../.pkm/cursor-commands/pkm.md" ".cursor/commands/pkm.md"
        echo -e "      ${GREEN}✓${NC} 已创建 .cursor/commands/ 并添加 PKM 命令"
    else
        echo -e "      ${YELLOW}⏭${NC}  跳过 Cursor 配置"
        echo -e "      ${BLUE}💡${NC} 稍后可手动创建链接："
        echo -e "         ${YELLOW}mkdir -p .cursor/commands${NC}"
        echo -e "         ${YELLOW}ln -s ../../.pkm/cursor-commands/pkm.md .cursor/commands/pkm.md${NC}"
    fi
fi
echo ""

# 7. 初始化知识库结构
echo -e "${BLUE}[7/9]${NC} 初始化知识库结构..."

DIRS_CREATED=0
for dir in "10_Projects" "20_Areas/manual" "20_Areas/01principles" "20_Areas/02playbooks" "20_Areas/02templates" "20_Areas/02cases" "20_Areas/03notes" "30_Resources/Library" "30_Resources/summary" "40_Archives" "50_Raw/inbox" "50_Raw/merged"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        DIRS_CREATED=$((DIRS_CREATED + 1))
    fi
done

# 创建 todo.md 和 todo_archive.md（如果不存在）
FILES_CREATED=0
if [ ! -f "30_Resources/todo.md" ]; then
    touch "30_Resources/todo.md"
    FILES_CREATED=$((FILES_CREATED + 1))
fi
if [ ! -f "30_Resources/todo_archive.md" ]; then
    touch "30_Resources/todo_archive.md"
    FILES_CREATED=$((FILES_CREATED + 1))
fi

if [ $DIRS_CREATED -gt 0 ] || [ $FILES_CREATED -gt 0 ]; then
    if [ $DIRS_CREATED -gt 0 ]; then
        echo -e "      ${GREEN}✓${NC} 已创建 $DIRS_CREATED 个目录"
    fi
    if [ $FILES_CREATED -gt 0 ]; then
        echo -e "      ${GREEN}✓${NC} 已创建 $FILES_CREATED 个文件"
    fi
else
    echo -e "      ${GREEN}✓${NC} 知识库结构已存在"
fi
echo ""

# 8. 创建示例 README（如果不存在）
echo -e "${BLUE}[8/9]${NC} 创建项目文件..."

if [ ! -f "README.md" ]; then
    cat > README.md << 'EOF'
# 我的知识库

基于 PARA + CODE + 金字塔原理 的个人知识管理系统。

## 快速开始

### 在 Cursor 中

```text
@pkm inbox 学习笔记...     # 快速捕获
@pkm addProject [项目名称]  # 创建新项目（如果未提供名称则询问）
@pkm todo <内容>            # 添加新任务
@pkm todo list              # 列出所有任务
@pkm                        # 一键整理知识
@pkm help                   # 查看帮助
```

### 在 Claude Code 中

```text
@pkm inbox 学习笔记...     # 快速捕获
@pkm addProject [项目名称]  # 创建新项目（如果未提供名称则询问）
@pkm todo <内容>            # 添加新任务
@pkm todo list              # 列出所有任务
@pkm                        # 一键整理知识
@pkm help                   # 查看帮助
```

## 知识库结构

- `10_Projects/` - 短期项目
- `20_Areas/` - 长期领域
  - `manual/` - 受保护区（AI 只读）
  - `01principles/` - 原则层
  - `02playbooks/` - 应用层：标准化流程
  - `02templates/` - 应用层：可复用模版
  - `02cases/` - 应用层：具体案例
  - `03notes/` - 整理知识层
- `30_Resources/` - 参考资料
  - `Library/` - 资料库
  - `summary/` - 报告汇总
  - `todo.md` - 待办任务列表
  - `todo_archive.md` - 已完成任务归档
- `40_Archives/` - 归档
- `50_Raw/` - 统一素材区
  - `inbox/` - 待分类
  - `merged/` - 合并后的素材

## 详细文档

- [架构设计](docs/ARCHITECTURE.md)
- [使用指南](.pkm/Skills/README.md)

---

**PKM Skill** - 让知识管理更简单 🚀
EOF
    echo -e "      ${GREEN}✓${NC} 已创建 README.md"
else
    echo -e "      ${YELLOW}⏭${NC}  README.md 已存在，跳过"
fi
echo ""

# 9. 清理临时文件
echo -e "${BLUE}[9/9]${NC} 清理临时文件..."
if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
    echo -e "      ${GREEN}✓${NC} 已删除临时文件"
else
    echo -e "      ${YELLOW}⏭${NC}  临时文件已清理"
fi
echo ""

# 验证安装
echo -e "${BLUE}验证安装...${NC}"
INSTALL_OK=true
if [ ! -d ".pkm/Skills/PKM" ]; then
    echo -e "      ${RED}✗${NC} Skills 安装失败"
    INSTALL_OK=false
fi

if [ ! -f ".pkm/cursor-commands/pkm.md" ]; then
    echo -e "      ${RED}✗${NC} Cursor Commands 安装失败"
    INSTALL_OK=false
fi
echo ""

if [ "$INSTALL_OK" = true ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ 安装完成！${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BLUE}📚 使用方法：${NC}"
    echo ""
    echo -e "  ${YELLOW}Cursor / Claude Code${NC}:"
    echo -e "    @pkm inbox 学习笔记...    ${GREEN}# 快速捕获${NC}"
    echo -e "    @pkm addProject [项目名称] ${GREEN}# 创建新项目（如果未提供名称则询问）${NC}"
    echo -e "    @pkm todo <内容>          ${GREEN}# 添加新任务${NC}"
    echo -e "    @pkm todo list            ${GREEN}# 列出所有任务${NC}"
    echo -e "    @pkm                      ${GREEN}# 一键整理知识${NC}"
    echo -e "    @pkm help                 ${GREEN}# 查看帮助${NC}"
    echo ""
    echo -e "${BLUE}📖 详细文档：${NC}"
    echo -e "  • .pkm/Skills/README.md"
    echo -e "  • .pkm/Skills/PKM/Skill.md"
    echo -e "  • docs/ARCHITECTURE.md"
    echo ""
    echo -e "🎉 祝你的知识管理之旅愉快！"
    echo ""
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}✗ 安装失败${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "请检查错误信息并重试"
    exit 1
fi

