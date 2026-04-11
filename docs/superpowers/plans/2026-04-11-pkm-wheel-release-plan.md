# PKM Wheel 发布实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 pkm CLI 包的 wheel 构建和 GitHub Releases 分发

**Architecture:**
- 在仓库根目录添加 `pyproject.toml`，从 `pkm-server/pkm/` 子目录构建 wheel
- 新增 `release.yml` 工作流：push to main 构建 artifact，push tag 发布 Release
- 提供 `install.sh` 一键安装脚本，自动获取 latest release 并安装

**Tech Stack:** Python build (build, wheel), GitHub Actions, softprops/action-gh-release

---

## 文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `pyproject.toml` | 新增 | 根目录包元数据 |
| `.github/workflows/release.yml` | 新增 | wheel 构建 + Release |
| `.github/workflows/docker-publish.yml` | 无需修改 | 已是规范格式 |
| `install.sh` | 新增 | 一键安装脚本 |

---

## Task 1: 创建 pyproject.toml

**文件:** 创建: `pyproject.toml`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "pkm"
version = "0.1.0"
description = "PKM CLI - Personal Knowledge Management"
readme = "pkm-server/README.md"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1.7",
    "requests>=2.31.0",
]

[project.scripts]
pkm = "pkm.cli:cli"

[tool.setuptools.packages.find]
where = ["pkm-server"]
```

**验证:** 运行 `cd pkm-server && pip install build && python -m build` 确认生成 wheel

---

## Task 2: 创建 release.yml

**文件:** 创建: `.github/workflows/release.yml`

- [ ] **Step 1: 创建工作流文件**

```yaml
name: Build Wheel

on:
  push:
    branches: [main]
  push:
    tags: ['v*']

jobs:
  build-wheel:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install build dependencies
        run: pip install build

      - name: Build wheel
        run: cd pkm-server && python -m build

      - name: Upload wheel artifact
        uses: actions/upload-artifact@v4
        with:
          name: pkm-wheel
          path: pkm-server/dist/*.whl

      - name: Create Release
        if: startsWith(github.ref, 'refs/tags/v')
        uses: softprops/action-gh-release@v2
        with:
          files: pkm-server/dist/*.whl
```

**验证:** push to main 后检查 CI 有 `pkm-wheel` artifact

---

## Task 3: 创建 install.sh

**文件:** 创建: `install.sh`

- [ ] **Step 1: 创建安装脚本**

```bash
#!/bin/bash
set -e

REPO="EvilJoker/pkmskill"
ASSETS_URL="https://api.github.com/repos/${REPO}/releases/latest"

echo "=== Installing PKM CLI ==="

WHEEL_URL=$(curl -sSL "$ASSETS_URL" | grep "browser_download_url" | grep "\.whl" | head -1 | cut -d '"' -f 4)

if [ -z "$WHEEL_URL" ]; then
    echo "Error: No wheel found in latest release"
    exit 1
fi

echo "Downloading: $WHEEL_URL"
pip install "$WHEEL_URL"

echo ""
echo "=== Downloading PKM Docker Image ==="
docker pull ghcr.io/${REPO}:latest

echo ""
echo "=== PKM installed successfully ==="
pkm --version
```

- [ ] **Step 2: 添加执行权限**

```bash
chmod +x install.sh
```

**验证:** `./install.sh` 确认安装成功

---

## Task 4: 提交所有更改

- [ ] **Step 1: 提交所有文件**

```bash
git add pyproject.toml .github/workflows/release.yml install.sh
git commit -m "feat: add wheel build and release workflow"
git push
```

- [ ] **Step 2: 打 tag 触发 Release**

```bash
git tag v0.1.0
git push origin v0.1.0
```

**验证:**
1. CI 完成检查 `pkm-wheel` artifact
2. Release 页面有 wheel 文件
3. 执行 `install.sh` 安装成功

---

## 实施后验证清单

- [ ] `git push` 后 CI 显示 `pkm-wheel` artifact
- [ ] `git push v0.1.0` 后 GitHub Releases 有 wheel 文件
- [ ] `curl -sSL https://raw.githubusercontent.com/EvilJoker/pkmskill/main/install.sh | bash` 安装成功
- [ ] `pkm task ls` 功能正常
- [ ] `docker images | grep pkmskill` 镜像存在
