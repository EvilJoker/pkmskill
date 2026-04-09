"""CLI tests for PKM"""

import pytest
import subprocess
import os

PKM_CLI = "pkm"
API_BASE = os.environ.get("PKM_API_BASE", "http://localhost:8890")


def run_cli(args, env=None):
    """Run PKM CLI command and return result"""
    env = env or {}
    env["PKM_API_BASE"] = API_BASE
    result = subprocess.run(
        f"{PKM_CLI} {args}".split(),
        capture_output=True,
        text=True,
        env={**os.environ, **env}
    )
    return result


@pytest.fixture(scope="module")
def wait_for_server():
    """Wait for server to be ready"""
    import requests
    import time

    max_retries = 30
    for _ in range(max_retries):
        try:
            r = requests.get(f"{API_BASE}/health")
            if r.status_code == 200:
                return
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    pytest.fail("Server did not start in time")


class TestCLIHelp:
    """Test CLI help commands"""

    def test_main_help(self):
        """Main help should show available commands"""
        r = run_cli("--help")
        assert r.returncode == 0
        assert "task" in r.stdout
        assert "project" in r.stdout
        assert "server" in r.stdout

    def test_task_help(self):
        """Task help should show task commands"""
        r = run_cli("task --help")
        assert r.returncode == 0
        assert "add" in r.stdout
        assert "ls" in r.stdout
        assert "get" in r.stdout
        assert "update" in r.stdout
        assert "done" in r.stdout
        assert "delete" in r.stdout

    def test_project_help(self):
        """Project help should show project commands"""
        r = run_cli("project --help")
        assert r.returncode == 0
        assert "add" in r.stdout
        assert "ls" in r.stdout
        assert "get" in r.stdout
        assert "update" in r.stdout
        assert "archive" in r.stdout

    def test_task_add_help(self):
        """Task add help should show examples"""
        r = run_cli("task add --help")
        assert r.returncode == 0
        assert "Examples:" in r.stdout
        assert "priority" in r.stdout
        assert "quadrant" in r.stdout

    def test_task_ls_help(self):
        """Task ls help should show examples"""
        r = run_cli("task ls --help")
        assert r.returncode == 0
        assert "Examples:" in r.stdout
        assert "--status" in r.stdout
        assert "--quadrant" in r.stdout


class TestCLITask:
    """Test CLI task commands"""

    def test_task_ls(self, wait_for_server):
        """Should list tasks"""
        r = run_cli("task ls")
        assert r.returncode == 0
        # Output should contain task format: [id] title (status) - Q# [priority]
        assert "]" in r.stdout

    def test_task_add(self, wait_for_server):
        """Should add a new task"""
        r = run_cli('task add "测试CLI添加任务" --priority high --quadrant 1')
        assert r.returncode == 0
        assert "Task created:" in r.stdout

        # Verify task was created
        r = run_cli("task ls")
        assert "测试CLI添加任务" in r.stdout

    def test_task_add_with_all_options(self, wait_for_server):
        """Should add task with all options"""
        r = run_cli('task add "测试CLI全选项" --priority medium --quadrant 2 --due 2026-04-15')
        assert r.returncode == 0
        assert "Task created:" in r.stdout

    def test_task_get(self, wait_for_server):
        """Should get task details"""
        # First create a task
        r = run_cli('task add "测试CLI获取任务" --priority low --quadrant 4')
        assert r.returncode == 0
        task_id = r.stdout.split("Task created: ")[1].strip()

        # Get task details
        r = run_cli(f"task get {task_id}")
        assert r.returncode == 0
        assert "测试CLI获取任务" in r.stdout
        assert "low" in r.stdout
        assert "4" in r.stdout

    def test_task_update(self, wait_for_server):
        """Should update a task"""
        # Create task
        r = run_cli('task add "测试CLI更新任务" --priority low --quadrant 4')
        task_id = r.stdout.split("Task created: ")[1].strip()

        # Update task
        r = run_cli(f"task update {task_id} --title '测试CLI已更新' --priority high")
        assert r.returncode == 0
        assert "Task updated" in r.stdout

        # Verify update
        r = run_cli(f"task get {task_id}")
        assert "测试CLI已更新" in r.stdout
        assert "high" in r.stdout

    def test_task_done(self, wait_for_server):
        """Should mark task as completed"""
        # Create task
        r = run_cli('task add "测试CLI完成任务" --priority medium --quadrant 2')
        task_id = r.stdout.split("Task created: ")[1].strip()

        # Mark as done
        r = run_cli(f"task done {task_id}")
        assert r.returncode == 0
        assert "Task completed" in r.stdout

        # Verify
        r = run_cli(f"task get {task_id}")
        assert "completed" in r.stdout

    def test_task_delete(self, wait_for_server):
        """Should delete a task"""
        # Create task
        r = run_cli('task add "测试CLI删除任务" --priority low --quadrant 3')
        task_id = r.stdout.split("Task created: ")[1].strip()

        # Delete task
        r = run_cli(f"task delete {task_id}")
        assert r.returncode == 0
        assert "Task deleted" in r.stdout

        # Verify deleted
        r = run_cli(f"task get {task_id}")
        assert r.returncode != 0

    def test_task_ls_filter_by_status(self, wait_for_server):
        """Should filter tasks by status"""
        # Create and complete a task
        r = run_cli('task add "测试CLI状态过滤" --priority medium --quadrant 2')
        task_id = r.stdout.split("Task created: ")[1].strip()
        run_cli(f"task done {task_id}")

        # List completed
        r = run_cli("task ls --status completed")
        assert "测试CLI状态过滤" in r.stdout

        # List pending
        r = run_cli("task ls --status pending")
        assert "测试CLI状态过滤" not in r.stdout

    def test_task_ls_filter_by_quadrant(self, wait_for_server):
        """Should filter tasks by quadrant"""
        run_cli('task add "测试CLI象限过滤Q1" --priority high --quadrant 1')
        run_cli('task add "测试CLI象限过滤Q2" --priority medium --quadrant 2')

        r = run_cli("task ls --quadrant 1")
        assert "测试CLI象限过滤Q1" in r.stdout
        assert "测试CLI象限过滤Q2" not in r.stdout


class TestCLIProject:
    """Test CLI project commands"""

    def test_project_ls(self, wait_for_server):
        """Should list projects"""
        r = run_cli("project ls")
        assert r.returncode == 0
        # Output format: [id] name (status)
        assert "]" in r.stdout

    def test_project_add(self, wait_for_server):
        """Should add a new project"""
        r = run_cli('project add "测试CLI项目" --description "测试描述"')
        assert r.returncode == 0
        assert "Project created:" in r.stdout

        # Verify
        r = run_cli("project ls")
        assert "测试CLI项目" in r.stdout

    def test_project_get(self, wait_for_server):
        """Should get project details"""
        # Create project
        r = run_cli('project add "测试CLI获取项目" --description "项目详情"')
        project_id = r.stdout.split("Project created: ")[1].strip()

        # Get details
        r = run_cli(f"project get {project_id}")
        assert r.returncode == 0
        assert "测试CLI获取项目" in r.stdout
        assert "项目详情" in r.stdout

    def test_project_update(self, wait_for_server):
        """Should update a project"""
        # Create project
        r = run_cli('project add "测试CLI更新项目" --description "旧描述"')
        project_id = r.stdout.split("Project created: ")[1].strip()

        # Update
        r = run_cli(f"project update {project_id} --name '测试CLI已更新' --description '新描述'")
        assert r.returncode == 0
        assert "Project updated" in r.stdout

        # Verify
        r = run_cli(f"project get {project_id}")
        assert "测试CLI已更新" in r.stdout
        assert "新描述" in r.stdout

    def test_project_archive(self, wait_for_server):
        """Should archive a project"""
        # Create project
        r = run_cli('project add "测试CLI归档项目"')
        project_id = r.stdout.split("Project created: ")[1].strip()

        # Archive
        r = run_cli(f"project archive {project_id}")
        assert r.returncode == 0

        # Verify status changed to archived
        r = run_cli(f"project get {project_id}")
        assert "archived" in r.stdout

    def test_project_ls_filter_by_status(self, wait_for_server):
        """Should filter projects by status"""
        # Create and archive a project
        r = run_cli('project add "测试CLI项目状态过滤"')
        project_id = r.stdout.split("Project created: ")[1].strip()
        run_cli(f"project archive {project_id}")

        # List active
        r = run_cli("project ls --status active")
        assert "测试CLI项目状态过滤" not in r.stdout

        # List archived (archive sets status to "archived")
        r = run_cli("project ls --status archived")
        assert "测试CLI项目状态过滤" in r.stdout


class TestCLIQuadrantExplanation:
    """Test quadrant explanation in help"""

    def test_quadrant_meaning_in_help(self):
        """Help should explain quadrant meanings"""
        r = run_cli("task --help")
        assert "Q1=urgent+important" in r.stdout
        assert "Q2=important" in r.stdout
        assert "Q3=urgent" in r.stdout
        assert "Q4=other" in r.stdout

    def test_quadrant_option_help(self):
        """Quadrant option should show Q1-Q4 meaning"""
        r = run_cli("task add --help")
        assert "Q1=1" in r.stdout or "Q1" in r.stdout
