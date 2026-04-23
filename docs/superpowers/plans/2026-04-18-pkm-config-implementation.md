# pkm config 命令实现计划（更新版）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 `pkm config` 交互式配置命令，支持多配置项和 docker-compose 服务管理

**Architecture:** config 命令独立模块，使用 docker-compose 管理容器，.env 文件存储配置

**Tech Stack:** Click CLI, Docker Compose API (subprocess), PyYAML

---

## 文件变更

| 文件 | 操作 | 职责 |
|------|------|------|
| `pkm/commands/config.py` | 修改 | 重构为多配置项 + docker-compose |
| `~/.pkm/docker-compose.yml` | 新建 | 由 config 命令生成 |
| `pkm/commands/server_cmd.py` | 修改 | 使用 docker-compose |
| `tests/test_config.py` | 修改 | 更新测试用例 |

---

## Task 1: 重构 config.py 支持多配置项

**Files:**
- Modify: `pkm/commands/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: 更新 _ensure_config_files 生成完整 .env**

```python
def _ensure_config_files():
    """Ensure config files exist with defaults"""
    _ensure_pkm_dir()

    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f)

    if not ENV_PATH.exists():
        with open(ENV_PATH, "w") as f:
            f.write("# PKM Configuration\n")
            f.write(f"# API_KEY=your-api-key-here\n")
            f.write(f"# BASE_URL=https://api.anthropic.com\n")
            f.write(f"# MODEL=anthropic/claude-3.5-sonnet\n")
```

- [ ] **Step 2: 添加通用 _get_value 和 _update_value 函数**

```python
def _get_value(key):
    """从 .env 读取指定 key 的值"""
    if not ENV_PATH.exists():
        return None
    content = ENV_PATH.read_text()
    for line in content.splitlines():
        if line.startswith(f"{key}="):
            value = line.split("=", 1)[1].strip()
            if value and not value.startswith("#"):
                return value
    return None


def _update_value(key, value):
    """更新 .env 中指定 key 的值"""
    lines = []
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text().splitlines()

    new_lines = []
    found = False
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}")

    ENV_PATH.write_text("\n".join(new_lines) + "\n")
```

- [ ] **Step 3: 添加 _ensure_docker_compose_file 函数**

```python
DOCKER_COMPOSE_CONTENT = """services:
  pkm:
    image: ghcr.io/eviljoker/pkm:snapshot
    container_name: pkm-server
    restart: unless-stopped
    ports:
      - "8890:8890"
    volumes:
      - ~/.pkm:/root/.pkm
    environment:
      - CLAUDECODE=1
      - ANTHROPIC_BASE_URL=${BASE_URL}
      - ANTHROPIC_AUTH_TOKEN=${API_KEY}
      - ANTHROPIC_MODEL=${MODEL}
"""

def _ensure_docker_compose_file():
    """确保 docker-compose.yml 存在"""
    compose_path = PKM_DIR / "docker-compose.yml"
    if not compose_path.exists():
        with open(compose_path, "w") as f:
            f.write(DOCKER_COMPOSE_CONTENT)
    return compose_path
```

- [ ] **Step 4: 修改 _restart_container 使用 docker-compose**

```python
def _restart_container():
    """Stop and start the container using docker compose"""
    compose_path = _ensure_docker_compose_file()

    # Stop and remove old container
    subprocess.run(
        ["docker", "compose", "-f", str(compose_path), "down"],
        capture_output=True
    )

    # Start new container
    subprocess.run(
        ["docker", "compose", "-f", str(compose_path), "up", "-d"],
        check=True
    )
```

- [ ] **Step 5: 更新 config_interactive 支持多配置项**

```python
CONFIG_ITEMS = [
    {"key": "API_KEY", "prompt": "API_KEY", "default": ""},
    {"key": "BASE_URL", "prompt": "BASE_URL", "default": "https://api.anthropic.com"},
    {"key": "MODEL", "prompt": "MODEL", "default": "anthropic/claude-3.5-sonnet"},
]

def config_interactive():
    """Interactive configuration"""
    _ensure_pkm_dir()

    if not _check_image_exists():
        click.echo("Error: Docker image not found. Please run install.sh first.")
        return

    _ensure_config_files()

    click.echo("=== PKM Configuration ===")
    click.echo("** only support anthropic like **")

    for item in CONFIG_ITEMS:
        current = _get_value(item["key"])
        new_value = click.prompt(
            f"Current {item['prompt']}: {current or '(not set)'}\nEnter {item['prompt']} (press Enter to keep current)",
            default=current or item["default"]
        ).strip()
        if new_value:
            _update_value(item["key"], new_value)

    # Restart service
    click.echo("\nRestarting server...")
    _restart_container()

    if _wait_for_service():
        click.echo("✓ Configuration complete!")
        click.echo("✓ Server is running")
        click.echo("  Use 'pkm status' to view status")
        click.echo("  Use 'pkm server start/stop/status' to manage")
    else:
        click.echo("✗ Server failed to start")
```

- [ ] **Step 6: 更新测试用例**

```python
def test_get_value_returns_none_when_no_file():
    """无文件时返回 None"""
    with patch("pathlib.Path.exists", return_value=False):
        from pkm.commands import config as config_module
        result = config_module._get_value("API_KEY")
        assert result is None

def test_get_value_parses_existing():
    """能解析已有值"""
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.read_text", return_value="API_KEY=sk-test123\nBASE_URL=https://api.anthropic.com\n"):
            from pkm.commands import config as config_module
            assert config_module._get_value("API_KEY") == "sk-test123"
            assert config_module._get_value("BASE_URL") == "https://api.anthropic.com"

def test_update_value_adds_new_key():
    """更新不存在的 key 时添加"""
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.read_text", return_value="# comment\n"):
            with patch("pathlib.Path.write_text") as mock_write:
                from pkm.commands import config as config_module
                config_module._update_value("MODEL", "anthropic/claude-3.5-sonnet")
                mock_write.assert_called()
```

- [ ] **Step 7: 运行测试确认通过**

Run: `pytest tests/test_config.py -v`
Expected: PASS

- [ ] **Step 8: 提交**

```bash
git add pkm/commands/config.py tests/test_config.py
git commit -m "refactor: support multiple config items and docker-compose"
```

---

## Task 2: 更新 server_cmd.py 使用 docker-compose

**Files:**
- Modify: `pkm/commands/server_cmd.py`

- [ ] **Step 1: 修改 server_start 使用 docker-compose**

```python
def server_start(api_base=None):
    """Start the container using docker compose"""
    compose_path = PKM_DIR / "docker-compose.yml"
    if not compose_path.exists():
        click.echo("Error: docker-compose.yml not found. Run 'pkm config' first.")
        return

    result = subprocess.run(
        ["docker", "compose", "-f", str(compose_path), "up", "-d"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        click.echo("Server started")
    else:
        click.echo(f"Failed to start server: {result.stderr}")
```

- [ ] **Step 2: 修改 server_stop 使用 docker-compose**

```python
def server_stop(api_base=None):
    """Stop the container using docker compose"""
    compose_path = PKM_DIR / "docker-compose.yml"
    if not compose_path.exists():
        click.echo("Error: docker-compose.yml not found.")
        return

    subprocess.run(
        ["docker", "compose", "-f", str(compose_path), "down"],
        capture_output=True
    )
    click.echo("Server stopped")
```

- [ ] **Step 3: 修改 server_status 使用 docker-compose**

```python
def server_status(api_base=None):
    """Check container status"""
    if api_base is None:
        from pkm.config import get_api_base
        api_base = get_api_base()

    result = subprocess.run(
        ["docker", "compose", "-f", str(PKM_DIR / "docker-compose.yml"), "ps", "--format", "json"],
        capture_output=True, text=True
    )

    if result.returncode == 0 and result.stdout.strip():
        click.echo("Server is running")
        if is_server_running(api_base):
            click.echo("Service is ready")
        else:
            click.echo("Service is not ready")
    else:
        click.echo("Server is not running")
```

- [ ] **Step 4: 运行测试确认通过**

Run: `pytest tests/test_server_cmd.py -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add pkm/commands/server_cmd.py
git commit -m "refactor: server commands use docker-compose"
```

---

## Task 3: 更新 install.sh 移除容器启动逻辑

**Files:**
- Modify: `install.sh`

- [ ] **Step 1: 移除 start_container 函数，改为调用 pkm config --default**

```bash
# 删除 start_container 函数

# 修改 do_snapshot 中调用
do_snapshot() {
    echo "Installing PKM snapshot..."

    mkdir -p "$PKM_HOME"

    local version="snapshot"
    local whl_name="pkm-0.0.0-py3-none-any.whl"
    echo "Version: $version"

    # Download and install wheel
    download_wheel "$version" || echo "Wheel download failed, continuing..."

    # Pull Docker image
    pull_docker_image "$version" || echo "Docker pull failed, continuing..."

    # Run pkm config to setup and start container
    echo "Running pkm config --default..."
    pkm config --default

    echo ""
    echo "Snapshot installation complete!"
    echo "Services: pkm server start/stop/status"
}
```

- [ ] **Step 2: 检查脚本语法**

Run: `bash -n install.sh`

- [ ] **Step 3: 提交**

```bash
git add install.sh
git commit -m "feat: install.sh calls pkm config --default"
```

---

## 验证清单

- [ ] `pkm config --help` 显示帮助
- [ ] `pkm config --default` 启动服务（使用 docker-compose）
- [ ] `pkm config` 交互式配置 API_KEY、BASE_URL、MODEL
- [ ] `pkm server start/stop/status` 管理容器
- [ ] 所有测试通过

---

## 执行选项

**1. Subagent-Driven (recommended)** - 每个 Task 分配给独立 subagent
**2. Inline Execution** - 本 session 顺序执行

选择哪种方式？