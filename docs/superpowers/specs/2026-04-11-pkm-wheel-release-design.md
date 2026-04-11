# PKM Wheel 发布设计

## 目标

将 `pkm` Python CLI 包构建为 `.whl` 文件，通过 GitHub Releases 分发，支持 `pip install` 远程安装。

## 构建产物

| 产物 | 触发条件 | 位置 |
|------|---------|------|
| Wheel (.whl) | push to main | CI Artifacts |
| Wheel (.whl) | push tag (v*) | GitHub Release |
| Docker 镜像 | push to main | ghcr.io (latest) |
| Docker 镜像 | push tag (v*) | ghcr.io (tag) + GitHub Release |

## 文件改动

1. **新增** `.github/workflows/release.yml` — 构建 wheel + 发布 Release
2. **修改** `.github/workflows/docker-publish.yml` — 改为 push to main 触发
3. **新增** `pyproject.toml` — 根目录，包元数据定义
4. **新增** `install.sh` — 一键安装脚本（wheel + Docker 镜像）

## 包结构

```
pkmskill/                          # 仓库根目录
├── pyproject.toml                # 新增：包元数据
├── install.sh                    # 新增：一键安装脚本
├── pkm-server/
│   └── pkm/                      # CLI 包所在目录
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       └── config.py
```

## 工作流设计

### release.yml（新增）

```yaml
name: Build and Release

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
        uses: actions/setup-python@v4
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
        uses: softprops/action-gh-release@v1
        with:
          files: pkm-server/dist/*.whl
```

### docker-publish.yml（修改触发条件）

```yaml
on:
  push:
    branches: [main]
  push:
    tags: ['v*']
```

## 一键安装脚本

`install.sh` 放在仓库根目录，用户执行：

```bash
curl -sSL https://raw.githubusercontent.com/EvilJoker/pkmskill/main/install.sh | bash
```

### 脚本功能

1. 获取 GitHub latest release 的 wheel 下载地址
2. 执行 `pip install <wheel-url>` 安装 pkm CLI
3. 执行 `docker pull ghcr.io/EvilJoker/pkmskill:latest` 下载最新镜像

### install.sh 源码

```bash
#!/bin/bash
set -e

REPO="EvilJoker/pkmskill"
ASSETS_URL="https://api.github.com/repos/${REPO}/releases/latest"

echo "=== Installing PKM CLI ==="

# 获取 latest release 的 wheel 下载地址
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

## 安装方式

```bash
# 一键安装（推荐）
curl -sSL https://raw.githubusercontent.com/EvilJoker/pkmskill/main/install.sh | bash

# 手动安装指定版本
pip install https://github.com/EvilJoker/pkmskill/releases/download/v0.1.0/pkm-0.1.0-py3-none-any.whl
```

## 验证步骤

1. push to main 后检查 CI 有 wheel artifact
2. push tag v0.1.0 后检查 Releases 有 wheel 文件
3. 执行 install.sh 验证安装成功
4. `pkm task ls` 验证功能正常
5. `docker images | grep pkmskill` 验证镜像下载成功
