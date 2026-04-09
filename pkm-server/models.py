from datetime import datetime, date
from enum import Enum
from typing import Optional
from pydantic import BaseModel
import uuid


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskPriority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class ProjectStatus(str, Enum):
    active = "active"
    completed = "completed"
    archived = "archived"


class TaskBase(BaseModel):
    title: str
    priority: TaskPriority = TaskPriority.medium
    quadrant: int = 2
    project_id: Optional[str] = None
    progress: Optional[str] = None
    due_date: Optional[date] = None
    workspace_path: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    quadrant: Optional[int] = None
    project_id: Optional[str] = None
    progress: Optional[str] = None
    due_date: Optional[date] = None
    workspace_path: Optional[str] = None


class Task(TaskBase):
    id: str
    status: TaskStatus = TaskStatus.pending
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    workspace_path: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    workspace_path: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    workspace_path: Optional[str] = None


class Project(ProjectBase):
    id: str
    status: ProjectStatus = ProjectStatus.active
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    workspace_path: Optional[str] = None

    class Config:
        from_attributes = True
