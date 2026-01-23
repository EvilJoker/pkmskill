#!/bin/bash

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${RED}🗑️  PKM Skill 卸载程序${NC}"
echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 检查是否安装
if [ ! -d ".pkm/Skills" ]; then
    echo -e "${YELLOW}⚠${NC}  未检测到 PKM Skill 安装"
    echo ""
    echo "当前目录可能没有安装 PKM Skill，或者已经被卸载。"
    exit 0
fi

# 确认卸载
echo -e "${YELLOW}⚠  警告：${NC}此操作将删除 PKM Skill 相关文件"
echo ""
echo "将删除："
echo "  • .pkm/Skills/"
echo "  • .pkm/cursor-commands/"
echo "  • .cursor/commands/pkm.md（软链接）"
echo ""
read -p "确定要卸载吗？(y/n) " -n 1 -r
echo ""
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}✓${NC} 取消卸载"
    exit 0
fi

# 备份选项
BACKUP_DIR=""
read -p "是否备份现有数据？(y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    BACKUP_DIR="pkm_backup_$(date +%Y%m%d_%H%M%S)"
    echo -e "${BLUE}📦${NC} 备份到: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    [ -d ".pkm" ] && cp -r .pkm "$BACKUP_DIR/"
    [ -L ".cursor/commands/pkm.md" ] && cp -L ".cursor/commands/pkm.md" "$BACKUP_DIR/" 2>/dev/null || true
    echo -e "   ${GREEN}✓${NC} 备份完成"
fi
echo ""

# 开始卸载
echo -e "${BLUE}[1/4]${NC} 删除 Skills 文件..."
if [ -d ".pkm/Skills" ]; then
    rm -rf .pkm/Skills
    echo -e "      ${GREEN}✓${NC} 已删除 .pkm/Skills/"
else
    echo -e "      ${YELLOW}⏭${NC}  .pkm/Skills/ 不存在"
fi
echo ""

echo -e "${BLUE}[2/4]${NC} 删除 Cursor Commands 文件..."
if [ -d ".pkm/cursor-commands" ]; then
    rm -rf .pkm/cursor-commands
    echo -e "      ${GREEN}✓${NC} 已删除 .pkm/cursor-commands/"
else
    echo -e "      ${YELLOW}⏭${NC}  .pkm/cursor-commands/ 不存在"
fi
echo ""

echo -e "${BLUE}[3/4]${NC} 删除 Cursor Commands 链接..."
if [ -L ".cursor/commands/pkm.md" ]; then
    rm ".cursor/commands/pkm.md"
    echo -e "      ${GREEN}✓${NC} 已删除 .cursor/commands/pkm.md"
elif [ -f ".cursor/commands/pkm.md" ]; then
    # 检查是否为 PKM 文件
    if grep -q "PKM - Personal Knowledge Management" ".cursor/commands/pkm.md" 2>/dev/null; then
        rm ".cursor/commands/pkm.md"
        echo -e "      ${GREEN}✓${NC} 已删除 .cursor/commands/pkm.md"
    else
        echo -e "      ${YELLOW}⚠${NC}  .cursor/commands/pkm.md 可能包含其他内容，保留"
    fi
else
    echo -e "      ${YELLOW}⏭${NC}  .cursor/commands/pkm.md 不存在"
fi
echo ""

echo -e "${BLUE}[4/4]${NC} 清理空目录..."
# 清理 .pkm 目录（如果为空）
if [ -d ".pkm" ] && [ -z "$(ls -A .pkm)" ]; then
    rmdir .pkm
    echo -e "      ${GREEN}✓${NC} 已删除空目录 .pkm/"
fi

# 清理 .cursor/commands 目录（如果为空）
if [ -d ".cursor/commands" ] && [ -z "$(ls -A .cursor/commands)" ]; then
    rmdir .cursor/commands
    echo -e "      ${GREEN}✓${NC} 已删除空目录 .cursor/commands/"
fi
echo ""

# 询问是否删除知识库目录
echo -e "${YELLOW}?${NC} 是否删除知识库目录结构？"
echo ""
echo "知识库目录："
echo "  • 10_Projects/"
echo "  • 20_Areas/"
echo "  • 30_Resources/"
echo "  • 40_Archives/"
echo "  • 50_Raw/"
echo ""
read -p "删除这些目录？(y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${RED}⚠${NC}  删除知识库目录..."
    # 只删除空目录，保护用户数据
    find 10_Projects 20_Areas 30_Resources 40_Archives 50_Raw -type d -empty -delete 2>/dev/null || true
    echo -e "   ${GREEN}✓${NC} 已删除空目录（保留有内容的目录）"
else
    echo ""
    echo -e "${GREEN}✓${NC} 保留知识库目录"
fi
echo ""

# 完成
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 卸载完成${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -n "$BACKUP_DIR" ]; then
    echo -e "${BLUE}📦 备份位置：${NC}$BACKUP_DIR"
    echo ""
fi

echo "感谢使用 PKM Skill！"
echo ""

