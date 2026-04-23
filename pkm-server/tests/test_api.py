"""API integration tests for PKM Server"""

import pytest
import requests
import time
import os

BASE_URL = os.environ.get("PKM_API_BASE", "http://localhost:8890")


@pytest.fixture(scope="module")
def api_client():
    """API client fixture"""
    class APIClient:
        def __init__(self, base_url):
            self.base_url = base_url
            self.session = requests.Session()

        def health(self):
            return self.session.get(f"{self.base_url}/health")

        def list_tasks(self, **params):
            return self.session.get(f"{self.base_url}/api/tasks", params=params)

        def create_task(self, **data):
            return self.session.post(f"{self.base_url}/api/tasks", json=data)

        def get_task(self, task_id):
            return self.session.get(f"{self.base_url}/api/tasks/{task_id}")

        def update_task(self, task_id, **data):
            return self.session.patch(f"{self.base_url}/api/tasks/{task_id}", json=data)

        def delete_task(self, task_id):
            return self.session.delete(f"{self.base_url}/api/tasks/{task_id}")

        def done_task(self, task_id):
            return self.session.post(f"{self.base_url}/api/tasks/{task_id}/done")

        def list_projects(self, **params):
            return self.session.get(f"{self.base_url}/api/projects", params=params)

        def create_project(self, **data):
            return self.session.post(f"{self.base_url}/api/projects", json=data)

        def get_project(self, project_id):
            return self.session.get(f"{self.base_url}/api/projects/{project_id}")

        def update_project(self, project_id, **data):
            return self.session.patch(f"{self.base_url}/api/projects/{project_id}", json=data)

        def archive_project(self, project_id):
            return self.session.post(f"{self.base_url}/api/projects/{project_id}/archive")

    return APIClient(BASE_URL)


@pytest.fixture(scope="module", autouse=True)
def wait_for_server(api_client):
    """Wait for server to be ready"""
    # Wait up to 10 minutes for server to be ready
    # (pytest runs all tests including test_cli.py first which takes ~4 min)
    max_retries = 600
    for i in range(max_retries):
        try:
            r = api_client.session.get(f"{api_client.base_url}/api/status")
            if r.status_code == 200:
                print(f"\nServer ready after {i} seconds")
                return
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    pytest.fail(f"Server not ready after {max_retries} seconds")


@pytest.fixture(autouse=True)
def cleanup_tasks(api_client):
    """Clean up test tasks after each test"""
    yield
    # Cleanup: delete all tasks created by tests
    r = api_client.list_tasks()
    if r.status_code == 200:
        for task in r.json():
            if task.get("title", "").startswith("测试_"):
                api_client.delete_task(task["id"])


@pytest.fixture(autouse=True)
def cleanup_projects(api_client):
    """Clean up test projects after each test"""
    yield
    # Cleanup: delete all projects created by tests
    r = api_client.list_projects()
    if r.status_code == 200:
        for project in r.json():
            if project.get("name", "").startswith("测试_"):
                api_client.archive_project(project["id"])


class TestHealthEndpoint:
    """Test health endpoint"""

    def test_health_returns_ok(self, api_client, wait_for_server):
        """Health endpoint should return 200 and ok status"""
        r = api_client.health()
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestTaskAPI:
    """Test Task API endpoints"""

    def test_create_task(self, api_client, wait_for_server):
        """Should create a new task"""
        r = api_client.create_task(
            title="测试_task_create",
            priority="high"
        )
        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "测试_task_create"
        assert data["priority"] == "high"
        assert data["status"] == "new"
        assert "id" in data

    def test_create_task_with_all_fields(self, api_client, wait_for_server):
        """Should create a task with all optional fields"""
        r = api_client.create_task(
            title="测试_task_full",
            priority="medium",
            due_date="2026-04-15",  # as string, API converts to date
            progress="0"  # as string per model
        )
        assert r.status_code == 200
        data = r.json()
        assert "2026-04-15" in data["due_date"]
        assert data["progress"] == "0"

    def test_list_tasks(self, api_client, wait_for_server):
        """Should list all tasks"""
        # Create a task first
        api_client.create_task(title="测试_task_list", priority="low")

        r = api_client.list_tasks()
        assert r.status_code == 200
        tasks = r.json()
        assert isinstance(tasks, list)
        assert any(t["title"] == "测试_task_list" for t in tasks)

    def test_list_tasks_filter_by_status(self, api_client, wait_for_server):
        """Should filter tasks by status"""
        # Create tasks with different statuses
        r1 = api_client.create_task(title="测试_task_pending", priority="medium")
        task_id = r1.json()["id"]

        # Mark as completed
        api_client.done_task(task_id)

        # Filter by new
        r = api_client.list_tasks(status="new")
        assert r.status_code == 200
        tasks = r.json()
        assert not any(t["id"] == task_id for t in tasks)

        # Filter by done
        r = api_client.list_tasks(status="done")
        assert r.status_code == 200
        tasks = r.json()
        assert any(t["id"] == task_id for t in tasks)

    def test_get_task(self, api_client, wait_for_server):
        """Should get a single task by ID"""
        r = api_client.create_task(title="测试_task_get", priority="high")
        task_id = r.json()["id"]

        r = api_client.get_task(task_id)
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == task_id
        assert data["title"] == "测试_task_get"

    def test_get_task_not_found(self, api_client, wait_for_server):
        """Should return 404 for non-existent task"""
        r = api_client.get_task("non-existent-id")
        assert r.status_code == 404

    def test_update_task(self, api_client, wait_for_server):
        """Should update a task"""
        r = api_client.create_task(title="测试_task_update", priority="medium")
        task_id = r.json()["id"]

        r = api_client.update_task(task_id, title="测试_task_updated", priority="high", progress="50")
        assert r.status_code == 200

        r = api_client.get_task(task_id)
        data = r.json()
        assert data["title"] == "测试_task_updated"
        assert data["priority"] == "high"
        assert data["progress"] == "50"

    def test_update_task_workspace_path(self, api_client, wait_for_server):
        """Should update task workspace_path via PATCH"""
        r = api_client.create_task(title="测试_task_workspace", priority="medium")
        task_id = r.json()["id"]

        r = api_client.update_task(task_id, workspace_path="/tmp/test_task_ws")
        assert r.status_code == 200

        r = api_client.get_task(task_id)
        data = r.json()
        assert data["workspace_path"] == "/tmp/test_task_ws"

    def test_done_task(self, api_client, wait_for_server):
        """Should mark a task as done"""
        r = api_client.create_task(title="测试_task_done", priority="medium")
        task_id = r.json()["id"]

        r = api_client.done_task(task_id)
        assert r.status_code == 200

        r = api_client.get_task(task_id)
        data = r.json()
        assert data["status"] == "done"
        assert data["completed_at"] is not None

    def test_delete_task(self, api_client, wait_for_server):
        """Should delete a task"""
        r = api_client.create_task(title="测试_task_delete", priority="low")
        task_id = r.json()["id"]

        r = api_client.delete_task(task_id)
        assert r.status_code == 200

        r = api_client.get_task(task_id)
        assert r.status_code == 404


class TestProjectAPI:
    """Test Project API endpoints"""

    def test_create_project(self, api_client, wait_for_server):
        """Should create a new project"""
        r = api_client.create_project(name="测试_project_create", description="测试描述")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "测试_project_create"
        assert data["description"] == "测试描述"
        assert data["status"] == "active"
        assert "id" in data

    def test_list_projects(self, api_client, wait_for_server):
        """Should list all projects"""
        r = api_client.create_project(name="测试_project_list")
        project_id = r.json()["id"]

        r = api_client.list_projects()
        assert r.status_code == 200
        projects = r.json()
        assert isinstance(projects, list)
        assert any(p["id"] == project_id for p in projects)

    def test_list_projects_filter_by_status(self, api_client, wait_for_server):
        """Should filter projects by status"""
        r = api_client.create_project(name="测试_project_active")
        project_id = r.json()["id"]

        # Archive the project (sets status to "archived")
        api_client.archive_project(project_id)

        # Filter by active
        r = api_client.list_projects(status="active")
        assert r.status_code == 200
        projects = r.json()
        assert not any(p["id"] == project_id for p in projects)

        # Filter by archived
        r = api_client.list_projects(status="archived")
        assert r.status_code == 200
        projects = r.json()
        assert any(p["id"] == project_id for p in projects)

    def test_get_project(self, api_client, wait_for_server):
        """Should get a single project by ID"""
        r = api_client.create_project(name="测试_project_get", description="详情描述")
        project_id = r.json()["id"]

        r = api_client.get_project(project_id)
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == project_id
        assert data["name"] == "测试_project_get"
        assert data["description"] == "详情描述"

    def test_get_project_not_found(self, api_client, wait_for_server):
        """Should return 404 for non-existent project"""
        r = api_client.get_project("non-existent-id")
        assert r.status_code == 404

    def test_update_project(self, api_client, wait_for_server):
        """Should update a project"""
        r = api_client.create_project(name="测试_project_update")
        project_id = r.json()["id"]

        r = api_client.update_project(project_id, name="测试_project_updated", description="新描述")
        assert r.status_code == 200

        r = api_client.get_project(project_id)
        data = r.json()
        assert data["name"] == "测试_project_updated"
        assert data["description"] == "新描述"

    def test_update_project_workspace_path(self, api_client, wait_for_server):
        """Should update project workspace_path via PATCH"""
        r = api_client.create_project(name="测试_project_workspace")
        project_id = r.json()["id"]

        r = api_client.update_project(project_id, workspace_path="/tmp/test_project_ws")
        assert r.status_code == 200

        r = api_client.get_project(project_id)
        data = r.json()
        assert data["workspace_path"] == "/tmp/test_project_ws"

    def test_archive_project(self, api_client, wait_for_server):
        """Should archive a project"""
        r = api_client.create_project(name="测试_project_archive")
        project_id = r.json()["id"]

        r = api_client.archive_project(project_id)
        assert r.status_code == 200

        r = api_client.get_project(project_id)
        data = r.json()
        assert data["status"] == "archived"
        # Note: completed_at is only set when status is "completed", not "archived"

    def test_delete_project_not_found(self, api_client, wait_for_server):
        """Should return 404 when deleting non-existent project"""
        r = api_client.session.delete(f"{api_client.base_url}/api/projects/non-existent-id")
        assert r.status_code == 404

    def test_delete_default_project_fails(self, api_client, wait_for_server):
        """Should not allow deleting default project"""
        # Get the default project
        r = api_client.list_projects()
        projects = r.json()
        default_project = next((p for p in projects if p["name"].lower() == "default"), None)
        assert default_project is not None, "Default project should exist"

        # Try to delete default project
        r = api_client.session.delete(f"{api_client.base_url}/api/projects/{default_project['id']}")
        assert r.status_code == 400
        assert "default" in r.json()["detail"].lower()

    def test_approve_task_reflow_not_found(self, api_client, wait_for_server):
        """Should return 404 when approving non-existent task"""
        r = api_client.session.post(f"{api_client.base_url}/api/knowledge/approve/non-existent-task-id")
        assert r.status_code == 404


class TestTaskProjectRelation:
    """Test relationship between tasks and projects"""

    def test_task_with_project(self, api_client, wait_for_server):
        """Should create a task associated with a project"""
        # Create project
        r = api_client.create_project(name="测试_relation_project")
        project_id = r.json()["id"]

        # Create task with project
        r = api_client.create_task(
            title="测试_relation_task",
            priority="high",
            project_id=project_id
        )
        task_id = r.json()["id"]

        # Verify task has project_id
        r = api_client.get_task(task_id)
        data = r.json()
        assert data["project_id"] == project_id

        # List tasks for project
        r = api_client.list_tasks(project=project_id)
        tasks = r.json()
        assert any(t["id"] == task_id for t in tasks)


class TestStatusAPI:
    """Test Status API endpoint"""

    def test_get_status(self, api_client, wait_for_server):
        """Should return cached status info"""
        r = api_client.session.get(f"{api_client.base_url}/api/status")
        assert r.status_code == 200
        data = r.json()
        assert "tasks" in data
        assert "projects" in data
        assert "knowledge" in data
        assert "server" in data
        assert "last_updated" in data

    def test_status_includes_tasks_stats(self, api_client, wait_for_server):
        """Should include task counts by status"""
        r = api_client.session.get(f"{api_client.base_url}/api/status")
        data = r.json()
        assert "total" in data["tasks"]
        assert "by_status" in data["tasks"]

    def test_status_includes_projects_stats(self, api_client, wait_for_server):
        """Should include project counts by status"""
        r = api_client.session.get(f"{api_client.base_url}/api/status")
        data = r.json()
        assert "total" in data["projects"]
        assert "by_status" in data["projects"]

    def test_status_includes_knowledge_stats(self, api_client, wait_for_server):
        """Should include knowledge reflow stats"""
        r = api_client.session.get(f"{api_client.base_url}/api/status")
        data = r.json()
        assert "claude_available" in data["knowledge"]


class TestKnowledgeAPI:
    """Test Knowledge Reflow API endpoints"""

    def test_get_reflow_status(self, api_client, wait_for_server):
        """Should return reflow status"""
        r = api_client.session.get(f"{api_client.base_url}/api/knowledge/status")
        assert r.status_code == 200
        data = r.json()
        assert "claude_available" in data

    def test_trigger_reflow(self, api_client, wait_for_server):
        """Should trigger reflow cycle"""
        r = api_client.session.post(f"{api_client.base_url}/api/knowledge/reflow")
        assert r.status_code == 200
        data = r.json()
        assert data["triggered"] is True
        assert "processed" in data
        assert "succeeded" in data
        assert "failed" in data

    def test_approve_task_reflow(self, api_client, wait_for_server):
        """Should approve task reflow (change status from done to approved)"""
        # Create a task and mark it as done
        task = api_client.create_task(
            title="测试_approve",
            priority="medium",
            project_id="default"
        )
        assert task.status_code == 200
        task_id = task.json()["id"]

        # Complete the task (sets status to done)
        done = api_client.done_task(task_id)
        assert done.status_code == 200

        # Approve the task
        r = api_client.session.post(f"{api_client.base_url}/api/knowledge/approve/{task_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "approved"

        # Cleanup
        api_client.delete_task(task_id)

    def test_approve_task_reflow_wrong_status(self, api_client, wait_for_server):
        """Should fail to approve task that is not in done status"""
        # Create a new task (status = new, not done)
        task = api_client.create_task(
            title="测试_approve_wrong_status",
            priority="medium"
        )
        assert task.status_code == 200
        task_id = task.json()["id"]

        # Try to approve - should fail because task status is 'new' not 'done'
        r = api_client.session.post(f"{api_client.base_url}/api/knowledge/approve/{task_id}")
        assert r.status_code == 400

        # Cleanup
        api_client.delete_task(task_id)

