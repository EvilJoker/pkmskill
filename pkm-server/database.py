import sqlite3
import os
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager

DB_PATH = os.path.expanduser("~/.pkm/pkm.db")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                workspace_path TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'medium',
                quadrant INTEGER DEFAULT 2,
                project_id TEXT,
                progress TEXT,
                due_date TEXT,
                workspace_path TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        """)
        conn.commit()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def row_to_task(row) -> dict:
    if not row:
        return None
    return dict(row)


def row_to_project(row) -> dict:
    if not row:
        return None
    return dict(row)


# Project CRUD
def create_project(name: str, description: Optional[str] = None, workspace_path: Optional[str] = None) -> dict:
    import uuid
    now = datetime.utcnow().isoformat()
    project = {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "status": "active",
        "workspace_path": workspace_path,
        "created_at": now,
        "updated_at": now,
        "completed_at": None
    }
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (id, name, description, status, workspace_path, created_at, updated_at, completed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (project["id"], project["name"], project["description"], project["status"],
             project["workspace_path"], project["created_at"], project["updated_at"], project["completed_at"])
        )
    return project


def get_project(project_id: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        return row_to_project(cursor.fetchone())


def list_projects(status: Optional[str] = None) -> List[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute("SELECT * FROM projects WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        return [row_to_project(row) for row in cursor.fetchall()]


def update_project(project_id: str, **kwargs) -> Optional[dict]:
    allowed = ["name", "description", "status", "workspace_path"]
    kwargs = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not kwargs:
        return get_project(project_id)
    kwargs["updated_at"] = datetime.utcnow().isoformat()
    if "status" in kwargs and kwargs["status"] == "completed":
        kwargs["completed_at"] = datetime.utcnow().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values()) + [project_id]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", values)
    return get_project(project_id)


def delete_project(project_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        return cursor.rowcount > 0


# Task CRUD
def create_task(title: str, priority: str = "medium", quadrant: int = 2,
                project_id: Optional[str] = None, progress: Optional[str] = None,
                due_date: Optional[str] = None, workspace_path: Optional[str] = None) -> dict:
    import uuid
    now = datetime.utcnow().isoformat()
    task = {
        "id": str(uuid.uuid4()),
        "title": title,
        "status": "pending",
        "priority": priority,
        "quadrant": quadrant,
        "project_id": project_id,
        "progress": progress,
        "due_date": due_date,
        "workspace_path": workspace_path,
        "created_at": now,
        "updated_at": now,
        "completed_at": None
    }
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (id, title, status, priority, quadrant, project_id, progress, due_date, workspace_path, created_at, updated_at, completed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (task["id"], task["title"], task["status"], task["priority"], task["quadrant"],
             task["project_id"], task["progress"], task["due_date"], task["workspace_path"],
             task["created_at"], task["updated_at"], task["completed_at"])
        )
    return task


def get_task(task_id: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return row_to_task(cursor.fetchone())


def list_tasks(status: Optional[str] = None, project_id: Optional[str] = None,
               quadrant: Optional[int] = None) -> List[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        if quadrant is not None:
            query += " AND quadrant = ?"
            params.append(quadrant)
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        return [row_to_task(row) for row in cursor.fetchall()]


def update_task(task_id: str, **kwargs) -> Optional[dict]:
    allowed = ["title", "status", "priority", "quadrant", "project_id", "progress", "due_date", "workspace_path"]
    kwargs = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not kwargs:
        return get_task(task_id)
    kwargs["updated_at"] = datetime.utcnow().isoformat()
    if "status" in kwargs and kwargs["status"] == "completed":
        kwargs["completed_at"] = datetime.utcnow().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values()) + [task_id]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
    return get_task(task_id)


def delete_task(task_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0


def complete_task(task_id: str) -> Optional[dict]:
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = 'completed', updated_at = ?, completed_at = ? WHERE id = ?",
            (now, now, task_id)
        )
    return get_task(task_id)
