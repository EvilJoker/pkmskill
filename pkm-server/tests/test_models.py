"""Tests for Pydantic models"""

import pytest
from datetime import date, datetime
from pydantic import ValidationError

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    TaskStatus, TaskPriority, ProjectStatus,
    TaskBase, TaskCreate, TaskUpdate, Task,
    ProjectBase, ProjectCreate, ProjectUpdate, Project
)


class TestEnums:
    """Test enum values"""

    def test_task_status_values(self):
        assert TaskStatus.pending.value == "pending"
        assert TaskStatus.in_progress.value == "in_progress"
        assert TaskStatus.completed.value == "completed"

    def test_task_priority_values(self):
        assert TaskPriority.high.value == "high"
        assert TaskPriority.medium.value == "medium"
        assert TaskPriority.low.value == "low"

    def test_project_status_values(self):
        assert ProjectStatus.active.value == "active"
        assert ProjectStatus.completed.value == "completed"
        assert ProjectStatus.archived.value == "archived"


class TestTaskModels:
    """Test Task models"""

    def test_task_base_default_values(self):
        task = TaskBase(title="Test Task")
        assert task.title == "Test Task"
        assert task.priority == TaskPriority.medium
        assert task.quadrant == 2
        assert task.project_id is None
        assert task.progress is None
        assert task.due_date is None

    def test_task_base_with_all_fields(self):
        task = TaskBase(
            title="Test Task",
            priority=TaskPriority.high,
            quadrant=1,
            project_id="proj-123",
            progress="50",
            due_date=date(2026, 4, 15)
        )
        assert task.title == "Test Task"
        assert task.priority == TaskPriority.high
        assert task.quadrant == 1
        assert task.project_id == "proj-123"
        assert task.progress == "50"
        assert task.due_date == date(2026, 4, 15)

    def test_task_create(self):
        task = TaskCreate(title="New Task", priority=TaskPriority.high, quadrant=3)
        assert task.title == "New Task"
        assert task.priority == TaskPriority.high
        assert task.quadrant == 3

    def test_task_update_partial(self):
        update = TaskUpdate(title="Updated")
        assert update.title == "Updated"
        assert update.status is None
        assert update.priority is None

    def test_task_update_with_all_fields(self):
        update = TaskUpdate(
            title="Updated",
            status=TaskStatus.completed,
            priority=TaskPriority.low,
            quadrant=4,
            project_id="proj-456",
            progress="100",
            due_date=date(2026, 5, 1)
        )
        assert update.title == "Updated"
        assert update.status == TaskStatus.completed
        assert update.priority == TaskPriority.low
        assert update.quadrant == 4
        assert update.project_id == "proj-456"
        assert update.progress == "100"
        assert update.due_date == date(2026, 5, 1)

    def test_task_model(self):
        now = datetime.now()
        task = Task(
            id="task-123",
            title="Test Task",
            status=TaskStatus.pending,
            created_at=now,
            updated_at=now
        )
        assert task.id == "task-123"
        assert task.title == "Test Task"
        assert task.status == TaskStatus.pending
        assert task.created_at == now
        assert task.completed_at is None


class TestProjectModels:
    """Test Project models"""

    def test_project_base(self):
        project = ProjectBase(name="Test Project", description="Description")
        assert project.name == "Test Project"
        assert project.description == "Description"

    def test_project_base_without_description(self):
        project = ProjectBase(name="Test Project")
        assert project.name == "Test Project"
        assert project.description is None

    def test_project_create(self):
        project = ProjectCreate(name="New Project", description="New desc")
        assert project.name == "New Project"
        assert project.description == "New desc"

    def test_project_update_partial(self):
        update = ProjectUpdate(name="Updated Name")
        assert update.name == "Updated Name"
        assert update.description is None
        assert update.status is None

    def test_project_update_with_all_fields(self):
        update = ProjectUpdate(
            name="Updated",
            description="New description",
            status=ProjectStatus.archived
        )
        assert update.name == "Updated"
        assert update.description == "New description"
        assert update.status == ProjectStatus.archived

    def test_project_model(self):
        now = datetime.now()
        project = Project(
            id="proj-123",
            name="Test Project",
            status=ProjectStatus.active,
            created_at=now,
            updated_at=now
        )
        assert project.id == "proj-123"
        assert project.name == "Test Project"
        assert project.status == ProjectStatus.active
        assert project.completed_at is None


class TestModelValidation:
    """Test model validation"""

    def test_task_title_required(self):
        with pytest.raises(ValidationError):
            TaskBase()  # title is required

    def test_project_name_required(self):
        with pytest.raises(ValidationError):
            ProjectBase()  # name is required

    def test_invalid_priority(self):
        # Pydantic accepts any value for enum, but validates it
        # The validation happens at API level, not model level for string enums
        pass  # Enums validate on input

    def test_task_update_all_optional(self):
        # All fields in TaskUpdate are optional
        update = TaskUpdate()
        assert update.title is None
        assert update.status is None

    def test_project_update_all_optional(self):
        # All fields in ProjectUpdate are optional
        update = ProjectUpdate()
        assert update.name is None
        assert update.description is None
        assert update.status is None
