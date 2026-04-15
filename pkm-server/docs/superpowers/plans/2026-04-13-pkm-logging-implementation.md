# PKM 日志系统实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 PKM Server 添加完整日志系统，同时写文件和 stdout

**Architecture:** 配置 Python logging 双写（FileHandler + StreamHandler），在关键流程添加 INFO 日志

**Tech Stack:** Python logging 模块，FastAPI

---

## 文件结构

| 文件 | 改动 |
|------|------|
| `main.py` | 配置 logging（FileHandler + StreamHandler） |
| `knowledge.py` | 添加 INFO 日志 |
| `docker-compose.yml` | 挂载 `~/.pkm/logs` |
| `docker-compose.dev.yml` | 挂载 `~/.pkm_dev/logs` |

---

### Task 1: 配置 main.py 日志系统

**Files:**
- Modify: `main.py:1-60`

- [ ] **Step 1: 修改 main.py 添加日志配置**

在 `import sys` 之后添加日志配置代码：

```python
import logging
import os
from logging.handlers import RotatingFileHandler

# 配置日志目录
LOG_DIR = os.path.expanduser("~/.pkm/logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging():
    """配置双写日志：文件 + stdout"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 文件 Handler
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "pkm.log"),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

    # stdout Handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger.getLogger(__name__)
```

- [ ] **Step 2: 修改 startup 函数添加日志**

在 `startup()` 函数中添加：

```python
logger = logging.getLogger(__name__)

@app.on_event("startup")
def startup():
    setup_logging()
    logger.info("PKM Server starting...")

    database.init_db()
    logger.info("Database initialized")

    # 创建 default 项目工作区
    from pkm.workspace import create_default_project_workspace, get_default_project_workspace
    create_default_project_workspace()
    logger.info("Default project workspace ready")

    # 检查 Claude CLI 环境
    from knowledge import check_claude_environment
    claude_ok, claude_msg = check_claude_environment()
    if not claude_ok:
        logger.warning(f"Claude CLI 检查失败: {claude_msg}")
    else:
        logger.info(f"Claude CLI 环境正常")

    # 启动定时任务调度器
    from knowledge import run_reflow_cycle, run_stage2_cycle

    # Stage1: 每 3 小时整点执行
    scheduler.add_job(run_reflow_cycle, 'cron', minute=0)
    logger.info("Stage1 cron job registered (minute=0, interval=3h)")

    # Stage2: 每 3 小时 +30 分钟执行
    scheduler.add_job(run_stage2_cycle, 'cron', minute=30)
    logger.info("Stage2 cron job registered (minute=30, interval=3h)")

    scheduler.start()
    logger.info("Scheduler started")
    logger.info("PKM Server started on http://0.0.0.0:7890")
```

- [ ] **Step 3: 修改 shutdown 函数添加日志**

```python
@app.on_event("shutdown")
def shutdown():
    logger.info("PKM Server shutting down...")
    scheduler.shutdown()
    logger.info("PKM Server stopped")
```

- [ ] **Step 4: 提交**

```bash
git add main.py
git commit -m "feat: 配置 main.py 双写日志系统"
```

---

### Task 2: 为 knowledge.py 添加日志

**Files:**
- Modify: `knowledge.py`

- [ ] **Step 1: 添加 logger 初始化（在 import 后）**

确认 `knowledge.py` 已有以下代码（之前已添加）：
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

如果没有，添加它。

- [ ] **Step 2: 修改 run_reflow_cycle 函数**

在函数开头添加：
```python
def run_reflow_cycle() -> Dict:
    logger.info("Stage1 triggered: Starting task reflow cycle")
    # ... 原有代码 ...

    logger.info(f"Stage1 completed: processed={result['processed']}, succeeded={result['succeeded']}, failed={result['failed']}")
    return result
```

在处理每个任务时添加：
```python
logger.info(f"Reflowing task: {task['id']} -> {project['name']}")
```

- [ ] **Step 3: 修改 run_stage2_cycle 函数**

在函数开头添加：
```python
def run_stage2_cycle(batch_size: int = 5) -> Dict:
    logger.info("Stage2 triggered: Starting project reflow cycle")
    # ... 原有代码 ...

    logger.info(f"Stage2 completed: processed={result['processed']}, succeeded={result['succeeded']}, failed={result['failed']}")
    return result
```

在处理每个项目时添加：
```python
logger.info(f"Refining project: {project['name']} (id={project['id']})")
```

- [ ] **Step 4: 提交**

```bash
git add knowledge.py
git commit -m "feat: knowledge.py 添加运行时日志"
```

---

### Task 3: 更新 docker-compose 配置

**Files:**
- Modify: `docker-compose.yml`
- Modify: `docker-compose.dev.yml`

- [ ] **Step 1: 修改 docker-compose.yml 添加日志挂载**

在 `volumes` 中添加：
```yaml
volumes:
  - .:/app
  - ~/.pkm:/root/.pkm
  - ~/.pkm/logs:/root/.pkm/logs
```

- [ ] **Step 2: 修改 docker-compose.dev.yml 添加日志挂载**

```yaml
volumes:
  - .:/app
  - ~/.pkm_dev:/root/.pkm
  - ~/.pkm_dev/logs:/root/.pkm/logs
```

- [ ] **Step 3: 提交**

```bash
git add docker-compose.yml docker-compose.dev.yml
git commit -m "feat: docker-compose 添加日志目录挂载"
```

---

### Task 4: 验证日志系统

- [ ] **Step 1: 启动服务**

```bash
make start-dev
```

- [ ] **Step 2: 检查日志文件**

```bash
docker exec pkm-server ls -la /root/.pkm/logs/
docker exec pkm-server cat /root/.pkm/logs/pkm.log
```

- [ ] **Step 3: 检查 docker logs**

```bash
make logs | head -30
```

- [ ] **Step 4: 触发一次 reflow 并检查日志**

```bash
curl -s http://localhost:8890/health
curl -s -X POST http://localhost:8890/api/knowledge/reflow/stage2
make logs | grep -E "(Stage|INFO)"
```

---

## 验证清单

- [ ] `~/.pkm/logs/pkm.log` 文件存在
- [ ] 日志包含启动信息
- [ ] `docker compose logs` 能看到日志
- [ ] Stage1/Stage2 触发时有 INFO 日志

---

**Plan complete. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
