# CI Test Action Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 添加 GitHub Actions CI 测试流程，push 到 main 时自动运行测试，覆盖率达标才允许 Docker 发布

**Architecture:** 在现有 docker-publish.yml 基础上新增 ci-test.yml workflow，通过 needs 依赖确保测试通过才发布。测试使用 docker-compose 启动完整环境，执行 make test。

**Tech Stack:** GitHub Actions, Docker Compose, pytest, coverage

---

## 文件变更概览

| 文件 | 操作 |
|------|------|
| `.github/workflows/ci-test.yml` | 新增 |
| `pkm-server/tests/test_install.py` | 新增 |
| `.github/workflows/docker-publish.yml` | 修改 |

---

## Task 1: 创建 CI Test Workflow

**Files:**
- Create: `.github/workflows/ci-test.yml`

- [ ] **Step 1: 编写 ci-test.yml**

```yaml
name: CI Test

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Start services
        run: docker-compose -f pkm-server/docker-compose.yml up -d

      - name: Wait for services
        run: sleep 5

      - name: Run tests with coverage
        run: |
          docker-compose -f pkm-server/docker-compose.yml run --rm \
            -e PKM_API_BASE=http://pkm-server:7890 \
            pkm-server \
            bash -c "coverage run -m pytest tests/ -v --cov=. --cov-branch && coverage report --show-missing"

      - name: Check coverage thresholds
        run: |
          docker-compose -f pkm-server/docker-compose.yml run --rm \
            pkm-server \
            bash -c "coverage report --fail-under=75 --cov-branch --cov-fail-under=65"

      - name: Run install.sh test (xfail expected)
        run: |
          docker-compose -f pkm-server/docker-compose.yml run --rm \
            pkm-server \
            bash -c "pytest tests/test_install.py -v || true"

      - name: Cleanup
        if: always()
        run: docker-compose -f pkm-server/docker-compose.yml down

  install-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Test install.sh (actual execution)
        run: |
          chmod +x pkm-server/install.sh
          timeout 60 pkm-server/install.sh snapshot || echo "install.sh failed as expected (xfail)"

  docker-publish:
    needs: [test, install-test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # ... rest of docker publish steps
```

- [ ] **Step 2: 提交 ci-test.yml**

```bash
git add .github/workflows/ci-test.yml
git commit -m "feat: add ci-test workflow for main branch"
```

---

## Task 2: 创建 install.sh 测试用例

**Files:**
- Create: `pkm-server/tests/test_install.py`

- [ ] **Step 1: 编写 test_install.py**

```python
"""install.sh installation tests - TDD style"""

import pytest
import subprocess
import os
import tempfile
import shutil

# Mark all tests as expected failures (TDD - will pass once install.sh is fixed)
pytestmark = pytest.mark.xfail(reason="install.sh not yet fixed", strict=True)


class TestInstallScript:
    """Test install.sh installation script"""

    def test_install_script_exists(self):
        """install.sh should exist and be executable"""
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "install.sh"
        )
        assert os.path.exists(script_path), f"install.sh not found at {script_path}"
        assert os.access(script_path, os.X_OK), "install.sh should be executable"

    def test_install_script_help(self):
        """install.sh -h should show help without error"""
        result = subprocess.run(
            ["bash", "-c", "../../install.sh -h"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        assert result.returncode == 0, f"help failed: {result.stderr}"
        assert "Usage:" in result.stdout
        assert "snapshot" in result.stdout

    def test_install_script_accepts_snapshot_arg(self):
        """install.sh snapshot should attempt installation"""
        result = subprocess.run(
            ["bash", "-c", "../../install.sh snapshot"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.dirname(__file__)
        )
        # We expect this to fail for now (xfail)
        # Once fixed, it should download and attempt install
        output = result.stdout + result.stderr
        assert "Installing" in output or "Downloading" in output, \
            f"Expected installation output, got: {output}"

    def test_install_script_wheel_url_construction(self):
        """install.sh should construct correct wheel URL"""
        # Test URL construction logic
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "install.sh"
        )
        with open(script_path, "r") as f:
            content = f.read()

        # Should have correct URL pattern for snapshot
        assert "pkm-0.0.0-py3-none-any.whl" in content, \
            "Snapshot wheel URL pattern incorrect"
        assert "releases/download" in content, \
            "Should reference GitHub releases"

    def test_install_script_docker_image_tag(self):
        """install.sh should use correct Docker image tag for snapshot"""
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "install.sh"
        )
        with open(script_path, "r") as f:
            content = f.read()

        # Should reference ghcr.io image
        assert "ghcr.io" in content, \
            "Should use GHCR for Docker image"
        assert ":snapshot" in content or "pkm:snapshot" in content, \
            "Snapshot should use :snapshot tag"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd pkm-server && pytest tests/test_install.py -v
```

预期：所有测试应该 xfail（预期失败）

- [ ] **Step 3: 提交 test_install.py**

```bash
git add pkm-server/tests/test_install.py
git commit -m "feat: add install.sh test with xfail (TDD)"
```

---

## Task 3: 修改 docker-publish.yml 添加 CI 依赖

**Files:**
- Modify: `.github/workflows/docker-publish.yml`

- [ ] **Step 1: 读取现有 docker-publish.yml**

确认当前文件内容（已在探索阶段读取）

- [ ] **Step 2: 修改 snapshot job 添加 needs**

将：
```yaml
snapshot:
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
```

改为：
```yaml
snapshot:
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  needs: [test]
  runs-on: ubuntu-latest
```

- [ ] **Step 3: 修改 release job 添加 needs**

将：
```yaml
release:
  if: startsWith(github.ref, 'refs/tags/v')
  runs-on: ubuntu-latest
```

改为：
```yaml
release:
  if: startsWith(github.ref, 'refs/tags/v')
  needs: [test]
  runs-on: ubuntu-latest
```

- [ ] **Step 4: 提交更改**

```bash
git add .github/workflows/docker-publish.yml
git commit -m "feat: add CI test dependency to docker publish"
```

---

## Task 4: 验证完整流程

- [ ] **Step 1: 本地运行 make test 确认正常**

```bash
cd pkm-server && make test
```

预期：所有测试通过，覆盖率达标

- [ ] **Step 2: 检查 ci-test.yml 语法**

```bash
# 可以用 act 本地测试，或检查 YAML 语法
yamllint .github/workflows/ci-test.yml
```

---

## 验收标准检查清单

- [ ] `.github/workflows/ci-test.yml` 存在且语法正确
- [ ] `pkm-server/tests/test_install.py` 存在，所有测试为 xfail
- [ ] `.github/workflows/docker-publish.yml` 的 snapshot 和 release job 依赖 test job
- [ ] `make test` 在本地运行通过
- [ ] push 到 main 分支时 GitHub Actions 自动触发 CI

---

## 注意事项

1. **覆盖率参数顺序**：`coverage report --fail-under=行覆盖率 --cov-branch --cov-fail-under=分支覆盖率`
2. **docker-compose 路径**：所有 docker-compose 命令需要指定 `-f pkm-server/docker-compose.yml`
3. **install.sh 测试**：在 CI 中允许失败，不影响整体 CI 结果
4. **test job 必须成功**：docker-publish 依赖 test job，所以 test job 必须通过（覆盖率达标）
