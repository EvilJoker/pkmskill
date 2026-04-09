# PKM 配置文件加载 Implementation Plan

**Goal:** 创建配置加载机制，程序启动时自动从 ~/.pkm/config.yaml 读取配置

**Architecture:**
- 创建 pkm/config.py 配置加载模块，使用 PyYAML
- 程序启动时自动读取 ~/.pkm/config.yaml
- 硬编码默认值作为 fallback
- 创建 .config.example.yaml 模板

**Tech Stack:** PyYAML

---

## Task 1: 创建配置加载模块

**Files:**
- Create: `pkm/config.py`
- Modify: `requirements.txt`
- Create: `.config.example.yaml`

- [ ] **Step 1: 添加 PyYAML 依赖**

```diff
# requirements.txt
+ PyYAML==6.0.1
```

- [ ] **Step 2: 创建配置加载模块**

```python
# pkm/config.py
import os
import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "port": 7890,
    "log_level": "info",
}

CONFIG_PATH = Path("~/.pkm/config.yaml").expanduser()

def load_config() -> dict:
    """Load config from ~/.pkm/config.yaml, fallback to defaults"""
    config = DEFAULT_CONFIG.copy()
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            user_config = yaml.safe_load(f) or {}
            config.update(user_config)
    return config

def get_port() -> int:
    return load_config()["port"]

def get_log_level() -> str:
    return load_config()["log_level"]
```

- [ ] **Step 3: 创建 .config.example.yaml 模板**

```yaml
# .config.example.yaml
port: 7890
log_level: info
```

- [ ] **Step 4: 运行测试验证**

```bash
python -c "from pkm.config import load_config; print(load_config())"
```

Expected: `{'port': 7890, 'log_level': 'info'}`

---

## Task 2: 应用配置到 main.py

**Files:**
- Modify: `main.py`

- [ ] **Step 1: 修改 main.py 使用配置**

```python
# main.py - 添加配置导入，修改 uvicorn 启动

from pkm.config import get_port

# 在 uvicorn 启动时使用配置
if __name__ == "__main__":
    import uvicorn
    port = get_port()
    uvicorn.run("main:app", host="0.0.0.0", port=port)
```

---

## Task 3: 应用配置到 CLI

**Files:**
- Modify: `pkm/cli.py`

- [ ] **Step 1: 修改 CLI 使用配置**

```python
# pkm/cli.py - 修改 API_BASE 默认值

from pkm.config import get_port

API_BASE = os.environ.get("PKM_API_BASE", f"http://localhost:{get_port()}")
```

---

## Task 4: 添加配置测试

**Files:**
- Create: `tests/test_config.py`

- [ ] **Step 1: 创建配置测试**

```python
# tests/test_config.py
import pytest
from pkm.config import load_config, get_port, get_log_level

def test_default_config():
    """Test default config values"""
    config = load_config()
    assert config["port"] == 7890
    assert config["log_level"] == "info"

def test_get_port():
    assert get_port() == 7890

def test_get_log_level():
    assert get_log_level() == "info"
```

- [ ] **Step 2: 运行测试**

```bash
pytest tests/test_config.py -v
```

Expected: PASS

---

## Task 5: 创建 .env.example

**Files:**
- Create: `.env.example`

- [ ] **Step 1: 创建 .env.example 模板（预留）**

```bash
# .env.example
# PKM API Configuration
# API_KEY=your-api-key-here
```

---

## Task 6: 提交

```bash
git add .
git commit -m "feat: add config loading from ~/.pkm/config.yaml"
```
