# pkm config 命令设计

## 概述

新增 `pkm config` 命令作为交互式引导配置工具，在 install.sh 安装后引导用户完成服务配置和启动。

## 用户流程

1. 用户运行 `bash install.sh snapshot`
2. install.sh 下载 wheel、拉取镜像
3. install.sh 调用 `pkm config --default` 启动服务
4. 用户可通过 `pkm config` 重新配置（交互式）

## 命令行接口

```bash
pkm config              # 交互式引导配置
pkm config --default   # 非交互式，使用默认配置+启动
```

## 交互式流程 (`pkm config`)

### 预期交互效果

```
$ pkm config
=== PKM Configuration ===
** only support anthropic like **
Current API_KEY: sk-cp-xxx
Enter API_KEY (press Enter to keep current) :

Current BASE_URL: https://api.minimaxi.com/anthropic
Enter BASE_URL (press Enter to keep current) :

Current MODEL: xxxx
Enter MODEL (press Enter to keep current):


Restarting server...
✓ Configuration complete!
✓ Server is running
  Use 'pkm status' to view status
  Use 'pkm server start/stop/status' to manage
```

### Step 1: 检查环境
- Docker 镜像是否存在
- ~/.pkm 目录是否存在
- 配置文件是否存在（预填充已有值）

### Step 2: 配置各项参数
显示当前值，用户逐项确认或修改：

| 参数 | 环境变量 | 默认值 | 说明 |
|------|----------|--------|------|
| API_KEY | API_KEY | - | Claude API 密钥 |
| BASE_URL | BASE_URL | https://api.anthropic.com | API 地址 |
| MODEL | MODEL | anthropic/claude-3.5-sonnet | 使用模型 |

- 用户输入新值或回车保留当前
- 每项单独 prompt

### Step 3: 创建/更新配置文件
- `~/.pkm/config.yaml` - 端口、日志级别等
- `~/.pkm/.env` - API_KEY、BASE_URL、MODEL 等敏感配置

### Step 4: 启动/重启服务
- 停止旧容器（如存在）
- 使用 `docker compose` 启动新容器，自动映射 `~/.pkm/.env` 中的环境变量
- 等待服务就绪

### Step 5: 确认安装成功
- 检查服务状态
- 提示可用命令: `pkm status` / `pkm server start/stop/status`

## 非交互式流程 (`pkm config --default`)

```python
if 镜像不存在:
    提示错误并退出

创建默认 config.yaml
创建默认 .env (API_KEY 为空)
启动容器
等待就绪
输出成功提示
```

## install.sh 修改

```bash
# 原逻辑: start_container
# 新逻辑: 运行 pkm config --default

echo "Running pkm config --default..."
pkm config --default

echo ""
echo "Installation complete!"
echo "Services: pkm server start/stop/status"
```

## docker-compose.yml 环境变量映射

`~/.pkm/docker-compose.yml` 配置文件：

```yaml
services:
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
```

**注意**：`docker compose` 会自动从 `~/.pkm/.env` 文件读取变量并替换 `${VAR}` 表达式。

### 文件结构

```
~/.pkm/
├── config.yaml    # 端口、日志级别等
├── .env           # API_KEY、ANTHROPIC_BASE_URL、ANTHROPIC_MODEL 等敏感配置
└── pkm.db        # SQLite 数据库（运行时创建）
```

### .env 文件格式

```bash
# PKM Configuration
API_KEY=sk-your-api-key-here
BASE_URL=https://api.anthropic.com
MODEL=anthropic/claude-3.5-sonnet
```

**注意**：`.env` 文件中的变量名（API_KEY、BASE_URL、MODEL）需与 docker-compose.yml 中定义的 `${VAR}` 引用一致。

### config 命令模块

```python
# pkm/commands/config.py
import click
import subprocess
from pathlib import Path

PKM_DIR = Path("~/.pkm").expanduser()
CONFIG_PATH = PKM_DIR / "config.yaml"
ENV_PATH = PKM_DIR / ".env"

# 配置项定义（与 .env 文件中的变量名一致）
CONFIG_ITEMS = [
    {"key": "API_KEY", "prompt": "API_KEY", "default": ""},
    {"key": "BASE_URL", "prompt": "BASE_URL", "default": "https://api.anthropic.com"},
    {"key": "MODEL", "prompt": "MODEL", "default": "anthropic/claude-3.5-sonnet"},
]

def _get_current_value(key):
    """从 .env 读取当前配置值"""
    ...

def _update_value(key, value):
    """更新 .env 中的配置值"""
    ...

def config_interactive():
    """交互式配置"""
    click.echo("=== PKM Configuration ===")
    for item in CONFIG_ITEMS:
        current = _get_current_value(item["key"])
        new_value = click.prompt(
            f"Current {item['prompt']}: {current or '(not set)'}\nEnter {item['prompt']}",
            default=current or item["default"]
        ).strip()
        if new_value:
            _update_value(item["key"], new_value)
    # 重启服务
    ...

@click.command()
@click.option("--default", is_flag=True, help="非交互式默认配置")
def config(default):
    """引导配置 PKM"""
    if default:
        config_default()
    else:
        config_interactive()
```

### server start/stop/status 改造

将 `pkm server` 命令从管理本地进程改为管理 Docker 容器：

```python
# pkm/commands/server_cmd.py
def server_start(api_base=None):
    """启动容器服务"""
    subprocess.run(["docker", "start", "pkm-server"])

def server_stop(api_base=None):
    """停止容器服务"""
    subprocess.run(["docker", "stop", "pkm-server"])

def server_status(api_base=None):
    """检查容器状态"""
    # docker inspect 或 docker ps
```

注意：改用 `docker start/stop` 而非 `docker compose`，因为 install.sh 使用 `docker run` 直接创建容器。

## 错误处理

| 场景 | 处理 |
|------|------|
| 镜像不存在 | 提示先运行 install.sh |
| Docker 未运行 | 提示检查 Docker |
| 容器启动失败 | 显示 docker logs 排查 |
| 服务未就绪 | 等待重试，超时提示 |

## 测试要点

1. `pkm config --default` 完整流程
2. `pkm config` 交互式预填充
3. API Key 更新后服务重启生效
4. 服务就绪检测
