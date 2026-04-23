import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from apscheduler.schedulers.background import BackgroundScheduler

from models import Task, TaskCreate, TaskUpdate, Project, ProjectCreate, ProjectUpdate
import database
from pkm.config import get_port
from logging_config import setup_logging, get_logger

# 初始化日志
setup_logging()
logger = get_logger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()

# Status cache
status_cache = {
    "tasks": {"total": 0, "by_status": {}},
    "projects": {"total": 0, "by_status": {}},
    "knowledge": {"pending_approved_tasks": 0, "pending_reflows": 0, "claude_available": False},
    "server": {"status": "unknown"},
    "last_updated": None
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan - startup and shutdown handler"""
    logger.info("PKM Server starting...")

    database.init_db()
    logger.info("Database initialized")

    # 创建 default 项目工作区
    from pkm.workspace import create_default_project_workspace, get_default_project_workspace
    create_default_project_workspace()
    logger.info("Default project workspace ready")

    # 确保 default 项目存在于数据库
    from pkm.workspace import get_project_workspace_base
    default_project_id = database.get_default_project_id()
    if not default_project_id:
        default_ws = get_default_project_workspace()
        database.create_project("default", "Default project", workspace_path=default_ws)
        logger.info("Default project created in database")
    else:
        logger.info("Default project exists in database")

    # 检查 Claude CLI 环境
    from knowledge import check_claude_environment
    claude_ok, claude_msg = check_claude_environment()
    if not claude_ok:
        logger.warning(f"Claude CLI 检查失败: {claude_msg}")
    else:
        logger.info("Claude CLI 环境正常")

    # 启动定时任务调度器
    from knowledge import run_reflow_cycle

    # reflow: 每天 00:00 执行 Project → Knowledge 回流
    scheduler.add_job(run_reflow_cycle, 'cron', hour=0, minute=0)
    logger.info("reflow cron job registered (daily at 00:00)")

    # Status cache: 每 60 秒更新
    scheduler.add_job(update_status_cache, 'interval', seconds=60)
    logger.info("Status cache job registered (interval=60s)")

    # 立即更新一次缓存
    update_status_cache()
    status_cache["server"]["status"] = "running"

    scheduler.start()
    logger.info("Scheduler started")
    logger.info("PKM Server started on http://0.0.0.0:8890")

    yield  # ====== 服务器运行中 ======

    # Shutdown
    logger.info("PKM Server shutting down...")
    scheduler.shutdown()
    logger.info("PKM Server stopped")


app = FastAPI(title="PKM Server", lifespan=lifespan)


def update_status_cache():
    """更新状态缓存"""
    from knowledge import get_reflow_status
    global status_cache
    try:
        # Update tasks stats
        tasks = database.list_tasks()
        status_cache["tasks"]["total"] = len(tasks)
        by_status = {}
        for t in tasks:
            s = t.get("status", "unknown")
            by_status[s] = by_status.get(s, 0) + 1
        status_cache["tasks"]["by_status"] = by_status

        # Update projects stats
        projects = database.list_projects()
        status_cache["projects"]["total"] = len(projects)
        by_status = {}
        for p in projects:
            s = p.get("status", "unknown")
            by_status[s] = by_status.get(s, 0) + 1
        status_cache["projects"]["by_status"] = by_status

        # Update knowledge stats
        reflow_status = get_reflow_status()
        status_cache["knowledge"] = {
            "pending_approved_tasks": reflow_status.get("pending_approved_tasks", 0),
            "pending_reflows": reflow_status.get("pending_reflows", 0),
            "claude_available": reflow_status.get("claude_available", False)
        }

        from datetime import datetime
        status_cache["last_updated"] = datetime.now().isoformat()
        logger.debug("Status cache updated")
    except Exception as e:
        logger.error(f"Failed to update status cache: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/status")
def get_status():
    """获取缓存的状态信息"""
    return status_cache


# Projects
@app.post("/api/projects", response_model=Project)
def create_project(project: ProjectCreate):
    return database.create_project(project.name, project.description)


@app.get("/api/projects", response_model=List[Project])
def list_projects(status: Optional[str] = None):
    return database.list_projects(status)


@app.get("/api/projects/{project_id}", response_model=Project)
def get_project(project_id: str):
    project = database.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.patch("/api/projects/{project_id}", response_model=Project)
def update_project(project_id: str, update: ProjectUpdate):
    project = database.update_project(project_id, **update.model_dump(exclude_unset=True))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str):
    project = database.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 检查是否为 default 项目
    if project["name"].lower() == "default":
        raise HTTPException(status_code=400, detail="Cannot delete default project")

    # 迁移关联任务到 default
    migrated = database.migrate_tasks_to_default(project_id)

    # 删除项目
    workspace_path = project.get("workspace_path")
    database.delete_project(project_id)

    return {
        "message": "deleted",
        "workspace_path": workspace_path,
        "migrated_tasks": migrated
    }


@app.post("/api/projects/{project_id}/archive", response_model=Project)
def archive_project(project_id: str):
    project = database.update_project(project_id, status="archived")
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# Tasks
@app.post("/api/tasks", response_model=Task)
def create_task(task: TaskCreate):
    return database.create_task(
        title=task.title,
        priority=task.priority.value,
        project_id=task.project_id,
        progress=task.progress,
        due_date=str(task.due_date) if task.due_date else None,
        workspace_path=task.workspace_path
    )


@app.get("/api/tasks", response_model=List[Task])
def list_tasks(status: Optional[str] = None, project_id: Optional[str] = None):
    return database.list_tasks(status, project_id)


@app.get("/api/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    task = database.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, update: TaskUpdate):
    data = update.model_dump(exclude_unset=True)
    if "priority" in data and data["priority"]:
        data["priority"] = data["priority"].value
    if "due_date" in data and data["due_date"]:
        data["due_date"] = str(data["due_date"])
    task = database.update_task(task_id, **data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str):
    if not database.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "deleted"}


@app.post("/api/tasks/{task_id}/done", response_model=Task)
def done_task(task_id: str):
    task = database.complete_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=get_port())


@app.get("/api/knowledge/status")
def get_reflow_status():
    """获取回流状态"""
    from knowledge import get_reflow_status as get_status
    return get_status()



@app.post("/api/knowledge/approve/{task_id}")
def approve_task_reflow(task_id: str):
    """批准任务回流（将状态从 done 改为 approved）"""
    from database import get_task, update_task
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] != "done":
        raise HTTPException(status_code=400, detail=f"Task status is {task['status']}, expected done")
    updated = update_task(task_id, status="approved")
    return updated


# reflow API (每天 00:00 自动执行)
@app.post("/api/knowledge/reflow")
def trigger_reflow():
    """手动触发 reflow 回流（每天 00:00 自动执行）"""
    from knowledge import run_reflow_cycle
    result = run_reflow_cycle()
    return {
        "triggered": True,
        "processed": result["processed"],
        "succeeded": result["succeeded"],
        "failed": result["failed"],
        "deleted": result.get("deleted", 0),
        "message": f"处理了 {result['processed']} 个文件，成功 {result['succeeded']}，失败 {result['failed']}"
    }
