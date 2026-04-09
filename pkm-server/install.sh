#!/bin/bash
set -e

# 安装到 ~/.pkm
PKM_HOME="${PKM_HOME:-$HOME/.pkm}"
mkdir -p "$PKM_HOME"

# 复制文件
cp -r "$(dirname "$0")"/* "$PKM_HOME/"

# 安装 Python 依赖
pip install -r "$PKM_HOME/requirements.txt"

# 安装 CLI
pip install -e "$PKM_HOME"

echo "PKM installed to $PKM_HOME"