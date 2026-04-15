# PKM 日志系统设计

**日期**：2026-04-13
**状态**：已批准

---

## 目标

为 PKM Server 添加完整的日志系统，记录服务运行流程，便于调试和监控。

## 架构

**日志存储：**
- 日志文件：`~/.pkm/logs/pkm.log`（容器内 `/root/.pkm/logs/pkm.log`）
- 同时输出到 stdout（docker compose logs 可收集）
- 双写：FileHandler + StreamHandler

**日志配置：**
- 级别：INFO
- 格式：`%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- 时间格式：`%Y-%m-%d %H:%M:%S`

## 改动文件

| 文件 | 改动 |
|------|------|
| `main.py` | 配置 logging（FileHandler + StreamHandler） |
| `knowledge.py` | 添加 INFO 日志（定时任务执行、知识提炼步骤） |
| `docker-compose.dev.yml` | 挂载 `~/.pkm_dev/logs` |
| `docker-compose.yml` | 挂载 `~/.pkm/logs` |

## 日志覆盖流程

### 1. 服务启动/关闭
```
[INFO] PKM Server starting...
[INFO] Database initialized
[INFO] Scheduler started
[INFO] Stage1 cron job registered (minute=0)
[INFO] Stage2 cron job registered (minute=30)
[INFO] PKM Server stopped
```

### 2. 定时任务执行
```
[INFO] Stage1 scheduled task triggered
[INFO] Processing X approved tasks...
[INFO] Reflowing task: xxx -> project: xxx
[INFO] Stage1 completed: processed=X, succeeded=Y, failed=Z

[INFO] Stage2 scheduled task triggered
[INFO] Processing X projects needing reflow...
[INFO] Refining project: xxx
[INFO] Knowledge classified as: principles/playbooks/cases/notes
[INFO] Stage2 completed: processed=X, succeeded=Y, failed=Z
```

### 3. API 请求（可选 DEBUG 级别）
```
[DEBUG] POST /api/tasks - Creating task
[DEBUG] POST /api/tasks/{id}/done - Completing task
[DEBUG] POST /api/knowledge/approve/{id} - Approving task
```

## 实施步骤

1. 修改 `main.py`：配置双写日志
2. 修改 `knowledge.py`：在关键步骤添加 logger.info
3. 修改 `docker-compose.yml`：挂载日志目录
4. 修改 `docker-compose.dev.yml`：挂载日志目录
5. 验证：`make start-dev && make logs`

---

**设计完成，等待实施。**
