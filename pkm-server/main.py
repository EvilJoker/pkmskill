import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List

from models import Task, TaskCreate, TaskUpdate, Project, ProjectCreate, ProjectUpdate
import database
from pkm.config import get_port

app = FastAPI(title="PKM Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    database.init_db()
    # 创建 default 项目工作区
    from workspace import create_default_project_workspace, get_default_project_workspace
    create_default_project_workspace()
    # 检查 Claude CLI 环境
    from knowledge import check_claude_environment
    claude_ok, claude_msg = check_claude_environment()
    if not claude_ok:
        import logging
        logging.warning(f"Claude CLI 检查失败: {claude_msg}")


@app.get("/health")
def health():
    return {"status": "ok"}


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
    if not database.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "deleted"}


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
        quadrant=task.quadrant,
        project_id=task.project_id,
        progress=task.progress,
        due_date=str(task.due_date) if task.due_date else None,
        workspace_path=task.workspace_path
    )


@app.get("/api/tasks", response_model=List[Task])
def list_tasks(status: Optional[str] = None, project_id: Optional[str] = None,
               quadrant: Optional[int] = None):
    return database.list_tasks(status, project_id, quadrant)


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


# Knowledge Reflow APIs
@app.post("/api/knowledge/reflow")
def trigger_reflow():
    """手动触发知识回流"""
    from knowledge import run_reflow_cycle
    result = run_reflow_cycle()
    return {
        "triggered": True,
        "processed": result["processed"],
        "succeeded": result["succeeded"],
        "failed": result["failed"],
        "message": f"处理了 {result['processed']} 个任务，成功 {result['succeeded']}，失败 {result['failed']}"
    }


@app.get("/api/knowledge/status")
def get_reflow_status():
    """获取回流状态"""
    from knowledge import get_reflow_status as get_status
    return get_status()


@app.patch("/api/knowledge/config")
def update_reflow_config(interval: Optional[int] = None,
                          exclude_patterns: Optional[List[str]] = None,
                          content_types: Optional[List[str]] = None):
    """配置回流参数"""
    from knowledge import REFLOW_CONFIG
    if interval is not None:
        REFLOW_CONFIG["interval"] = interval
    if exclude_patterns is not None:
        REFLOW_CONFIG["exclude_patterns"] = exclude_patterns
    if content_types is not None:
        REFLOW_CONFIG["content_types"] = content_types
    return {"config": REFLOW_CONFIG}


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
