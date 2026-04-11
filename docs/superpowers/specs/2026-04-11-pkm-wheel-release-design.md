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

## 包结构

```
pkmskill/                          # 仓库根目录
├── pyproject.toml                # 新增：包元数据
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
      - name: Build wheel
        run: pip install build && cd pkm-server && python -m build
      - name: Upload to Release
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

## 安装方式

```bash
# 从 GitHub Release 安装（指定版本）
pip install https://github.com/EvilJoker/pkmskill/releases/download/v0.1.0/pkm-0.1.0-py3-none-any.whl

# 从 CI Artifact 安装（最新 main 构建，不推荐生产使用）
# 通过 GitHub Actions artifacts URL 下载
```

## 验证步骤

1. push to main 后检查 CI 有 wheel artifact
2. push tag v0.1.0 后检查 Releases 有 wheel 文件
3. `pip install` URL 验证安装成功
4. `pkm --version` 或 `pkm task ls` 验证功能正常
