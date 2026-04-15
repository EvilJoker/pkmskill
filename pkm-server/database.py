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
                completed_at TEXT,
                refined INTEGER DEFAULT 0,
                refined_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'new',
                priority TEXT DEFAULT 'medium',
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_reflow (
                id INTEGER PRIMARY KEY,
                task_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                status TEXT DEFAULT 'new',
                reflowed_at TEXT,
                error TEXT,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_reflow_status ON knowledge_reflow(status)
        """)
        # 添加 refined 和 refined_at 字段（如果不存在）
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN refined INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # 列已存在
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN refined_at TEXT")
        except sqlite3.OperationalError:
            pass  # 列已存在
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
def create_task(title: str, priority: str = "medium",
                project_id: Optional[str] = None, progress: Optional[str] = None,
                due_date: Optional[str] = None, workspace_path: Optional[str] = None) -> dict:
    import uuid
    now = datetime.utcnow().isoformat()
    task = {
        "id": str(uuid.uuid4()),
        "title": title,
        "status": "new",
        "priority": priority,
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
            "INSERT INTO tasks (id, title, status, priority, project_id, progress, due_date, workspace_path, created_at, updated_at, completed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (task["id"], task["title"], task["status"], task["priority"],
             task["project_id"], task["progress"], task["due_date"], task["workspace_path"],
             task["created_at"], task["updated_at"], task["completed_at"])
        )
    return task


def get_task(task_id: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return row_to_task(cursor.fetchone())


def list_tasks(status: Optional[str] = None, project_id: Optional[str] = None) -> List[dict]:
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
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        return [row_to_task(row) for row in cursor.fetchall()]


def update_task(task_id: str, **kwargs) -> Optional[dict]:
    allowed = ["title", "status", "priority", "project_id", "progress", "due_date", "workspace_path"]
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
            "UPDATE tasks SET status = 'done', updated_at = ?, completed_at = ? WHERE id = ?",
            (now, now, task_id)
        )
    return get_task(task_id)


# Knowledge Reflow CRUD
def create_reflow(task_id: str, project_id: str) -> dict:
    now = datetime.utcnow().isoformat()
    reflow = {
        "id": None,
        "task_id": task_id,
        "project_id": project_id,
        "status": "new",
        "reflowed_at": None,
        "error": None,
        "created_at": now
    }
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO knowledge_reflow (task_id, project_id, status, created_at) VALUES (?, ?, ?, ?)",
            (task_id, project_id, "new", now)
        )
        reflow["id"] = cursor.lastrowid
    return reflow


def get_reflow_by_task(task_id: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM knowledge_reflow WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_reflow_status(reflow_id: int, status: str, error: Optional[str] = None) -> None:
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        if status == "completed":
            cursor.execute(
                "UPDATE knowledge_reflow SET status = ?, reflowed_at = ?, error = NULL WHERE id = ?",
                (status, now, reflow_id)
            )
        elif error:
            cursor.execute(
                "UPDATE knowledge_reflow SET status = ?, error = ? WHERE id = ?",
                (status, error, reflow_id)
            )
        else:
            cursor.execute(
                "UPDATE knowledge_reflow SET status = ? WHERE id = ?",
                (status, reflow_id)
            )


def list_pending_reflows() -> List[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM knowledge_reflow WHERE status IN ('new', 'processing') ORDER BY created_at"
        )
        return [dict(row) for row in cursor.fetchall()]


# Stage2: 项目提炼相关
def get_projects_needing_reflow(limit: int = 5) -> List[dict]:
    """获取需要提炼的项目（未提炼或已更新）"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM projects
            WHERE status = 'active'
            AND (refined = 0 OR refined_at IS NULL OR updated_at > refined_at)
            ORDER BY updated_at DESC
            LIMIT ?
        """, (limit,))
        return [row_to_project(row) for row in cursor.fetchall()]


def mark_project_refined(project_id: str) -> None:
    """标记项目已提炼"""
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE projects SET refined = 1, refined_at = ? WHERE id = ?",
            (now, project_id)
        )
