"""Database layer tests for PKM"""

import pytest
import sys
import os
import tempfile
from unittest.mock import patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    init_db,
    create_task,
    get_task,
    update_task,
    delete_task,
    list_tasks,
    complete_task,
    create_project,
    get_project,
    update_project,
    list_projects,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def override_db_path(temp_db):
    """Override database path for tests"""
    import database
    original_path = database.DB_PATH
    database.DB_PATH = temp_db
    init_db()  # Initialize the temp database
    yield temp_db
    database.DB_PATH = original_path


class TestTaskDatabase:
    """Test task database operations"""

    def test_create_task(self, override_db_path):
        """Should create a task"""
        task = create_task(title="测试任务", priority="high", quadrant=1)
        assert task["title"] == "测试任务"
        assert task["priority"] == "high"
        assert task["quadrant"] == 1
        assert task["status"] == "pending"
        assert "id" in task

    def test_create_task_with_all_fields(self, override_db_path):
        """Should create a task with all fields"""
        task = create_task(
            title="完整任务",
            priority="medium",
            quadrant=2,
            project_id="test-project-id",
            due_date="2026-04-15",
            progress=25
        )
        assert task["project_id"] == "test-project-id"
        assert task["due_date"] == "2026-04-15"
        assert task["progress"] == 25

    def test_get_task(self, override_db_path):
        """Should get a task by ID"""
        created = create_task(title="获取任务", priority="low", quadrant=4)
        task = get_task(created["id"])
        assert task is not None
        assert task["title"] == "获取任务"

    def test_get_task_not_found(self, override_db_path):
        """Should return None for non-existent task"""
        task = get_task("non-existent-id")
        assert task is None

    def test_update_task(self, override_db_path):
        """Should update a task"""
        task = create_task(title="更新任务", priority="low", quadrant=4)
        updated = update_task(task["id"], title="已更新", priority="high", progress=50)
        assert updated is not None  # Returns the updated task object

        task = get_task(task["id"])
        assert task["title"] == "已更新"
        assert task["priority"] == "high"
        assert task["progress"] == "50"  # Stored as string

    def test_delete_task(self, override_db_path):
        """Should delete a task"""
        task = create_task(title="删除任务", priority="low", quadrant=3)
        deleted = delete_task(task["id"])
        assert deleted is True

        task = get_task(task["id"])
        assert task is None

    def test_list_tasks(self, override_db_path):
        """Should list all tasks"""
        create_task(title="任务1", priority="high", quadrant=1)
        create_task(title="任务2", priority="medium", quadrant=2)
        tasks = list_tasks()
        assert len(tasks) == 2

    def test_list_tasks_filter_by_status(self, override_db_path):
        """Should filter tasks by status"""
        task1 = create_task(title="进行中", priority="high", quadrant=1)
        task2 = create_task(title="已完成", priority="medium", quadrant=2)

        complete_task(task2["id"])

        pending = list_tasks(status="pending")
        assert len(pending) == 1
        assert pending[0]["title"] == "进行中"

        # complete_task sets status to 'done' (not 'completed')
        done = list_tasks(status="done")
        assert len(done) == 1
        assert done[0]["title"] == "已完成"

    def test_list_tasks_filter_by_quadrant(self, override_db_path):
        """Should filter tasks by quadrant"""
        create_task(title="Q1任务", priority="high", quadrant=1)
        create_task(title="Q2任务", priority="medium", quadrant=2)
        create_task(title="Q3任务", priority="low", quadrant=3)

        q1_tasks = list_tasks(quadrant=1)
        assert len(q1_tasks) == 1
        assert q1_tasks[0]["title"] == "Q1任务"

    def test_list_tasks_filter_by_project(self, override_db_path):
        """Should filter tasks by project"""
        project = create_project(name="测试项目")
        create_task(title="项目任务1", priority="high", quadrant=1, project_id=project["id"])
        create_task(title="项目任务2", priority="medium", quadrant=2, project_id=project["id"])
        create_task(title="无项目任务", priority="low", quadrant=3)

        project_tasks = list_tasks(project_id=project["id"])
        assert len(project_tasks) == 2
        assert all(t["project_id"] == project["id"] for t in project_tasks)

    def test_complete_task(self, override_db_path):
        """Should mark task as done"""
        task = create_task(title="完成任务", priority="medium", quadrant=2)
        result = complete_task(task["id"])
        assert result is not None  # Returns the updated task object

        task = get_task(task["id"])
        # complete_task sets status to 'done' (new flow: pending -> done -> approved -> archived)
        assert task["status"] == "done"
        assert task["completed_at"] is not None


class TestProjectDatabase:
    """Test project database operations"""

    def test_create_project(self, override_db_path):
        """Should create a project"""
        project = create_project(name="测试项目", description="测试描述")
        assert project["name"] == "测试项目"
        assert project["description"] == "测试描述"
        assert project["status"] == "active"
        assert "id" in project

    def test_get_project(self, override_db_path):
        """Should get a project by ID"""
        created = create_project(name="获取项目", description="详情")
        project = get_project(created["id"])
        assert project is not None
        assert project["name"] == "获取项目"

    def test_get_project_not_found(self, override_db_path):
        """Should return None for non-existent project"""
        project = get_project("non-existent-id")
        assert project is None

    def test_update_project(self, override_db_path):
        """Should update a project"""
        project = create_project(name="更新项目", description="旧描述")
        updated = update_project(project["id"], name="已更新", description="新描述")
        assert updated is not None  # Returns the updated project object

        project = get_project(project["id"])
        assert project["name"] == "已更新"
        assert project["description"] == "新描述"

    def test_list_projects(self, override_db_path):
        """Should list all projects"""
        create_project(name="项目1")
        create_project(name="项目2")
        projects = list_projects()
        assert len(projects) == 2

    def test_list_projects_filter_by_status(self, override_db_path):
        """Should filter projects by status"""
        project1 = create_project(name="进行中项目")
        project2 = create_project(name="已完成项目")

        update_project(project2["id"], status="completed", completed_at="2026-04-08T00:00:00")

        active = list_projects(status="active")
        assert len(active) == 1
        assert active[0]["name"] == "进行中项目"

        completed = list_projects(status="completed")
        assert len(completed) == 1
        assert completed[0]["name"] == "已完成项目"

    def test_archive_project(self, override_db_path):
        """Should archive a project"""
        project = create_project(name="归档项目")
        # Archive is done via update_project with status="archived"
        result = update_project(project["id"], status="archived", completed_at="2026-04-08T00:00:00")
        assert result is not None  # Returns the updated project object

        project = get_project(project["id"])
        assert project["status"] == "archived"


class TestDatabaseEdgeCases:
    """Test edge cases and error handling"""

    def test_create_task_invalid_priority(self, override_db_path):
        """Should handle invalid priority - stores as-is without validation"""
        task = create_task(title="测试", priority="invalid", quadrant=2)
        assert task["priority"] == "invalid"  # Database doesn't validate

    def test_create_task_invalid_quadrant(self, override_db_path):
        """Should handle invalid quadrant"""
        task = create_task(title="测试", quadrant=5)
        assert task["quadrant"] == 5  # Stored as-is

    def test_update_nonexistent_task(self, override_db_path):
        """Should return None when updating non-existent task"""
        result = update_task("non-existent", title="新标题")
        assert result is None

    def test_delete_nonexistent_task(self, override_db_path):
        """Should return False when deleting non-existent task"""
        result = delete_task("non-existent")
        assert result is False

    def test_complete_nonexistent_task(self, override_db_path):
        """Should return None when completing non-existent task"""
        result = complete_task("non-existent")
        assert result is None

    def test_create_task_with_workspace_path(self, override_db_path):
        """测试创建任务时 workspace_path 被记录"""
        task = create_task(
            title="测试任务",
            priority="medium",
            quadrant=2,
            workspace_path="/tmp/test_task_workspace"
        )
        assert task["workspace_path"] == "/tmp/test_task_workspace"
        # 清理
        delete_task(task["id"])

    def test_create_project_with_workspace_path(self, override_db_path):
        """测试创建项目时 workspace_path 被记录"""
        project = create_project(
            name="测试项目",
            description="测试描述",
            workspace_path="/tmp/test_project_workspace"
        )
        assert project["workspace_path"] == "/tmp/test_project_workspace"
        # 清理
        from database import delete_project
        delete_project(project["id"])
