"""CLI tests for PKM"""

import pytest
import subprocess
import os
from unittest.mock import patch, MagicMock

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


@pytest.fixture
def mock_api_base(monkeypatch):
    """Mock API_BASE for direct CLI function tests"""
    import pkm.cli
    monkeypatch.setattr(pkm.cli, "API_BASE", "http://localhost:8890")


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

    def test_task_ls_help(self):
        """Task ls help should show examples"""
        r = run_cli("task ls --help")
        assert r.returncode == 0
        assert "Examples:" in r.stdout
        assert "--status" in r.stdout


class TestCLITask:
    """Test CLI task commands"""

    def test_task_ls(self, wait_for_server):
        """Should list tasks"""
        # Create a task first to ensure there's data to list
        run_cli('task add "测试CLI列表任务" --priority high')
        r = run_cli("task ls")
        assert r.returncode == 0
        # Output should contain task format: [id] title (status) [priority]
        assert "]" in r.stdout
        assert "测试CLI列表任务" in r.stdout

    def test_task_add(self, wait_for_server):
        """Should add a new task"""
        r = run_cli('task add "测试CLI添加任务" --priority high')
        assert r.returncode == 0
        assert "Task created:" in r.stdout

        # Verify task was created
        r = run_cli("task ls")
        assert "测试CLI添加任务" in r.stdout

    def test_task_add_with_all_options(self, wait_for_server):
        """Should add task with all options"""
        r = run_cli('task add "测试CLI全选项" --priority medium --due 2026-04-15')
        assert r.returncode == 0
        assert "Task created:" in r.stdout

    def test_task_get(self, wait_for_server):
        """Should get task details"""
        # First create a task
        r = run_cli('task add "测试CLI获取任务" --priority low')
        assert r.returncode == 0
        task_id = r.stdout.split("Task created: ")[1].strip()

        # Get task details
        r = run_cli(f"task get {task_id}")
        assert r.returncode == 0
        assert "测试CLI获取任务" in r.stdout
        assert "low" in r.stdout

    def test_task_update(self, wait_for_server):
        """Should update a task"""
        # Create task
        r = run_cli('task add "测试CLI更新任务" --priority low')
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
        r = run_cli('task add "测试CLI完成任务" --priority medium')
        task_id = r.stdout.split("Task created: ")[1].strip()

        # Mark as done
        r = run_cli(f"task done {task_id}")
        assert r.returncode == 0
        assert "Task completed" in r.stdout

        # Verify
        r = run_cli(f"task get {task_id}")
        assert "done" in r.stdout

    def test_task_delete(self, wait_for_server):
        """Should delete a task"""
        # Create task
        r = run_cli('task add "测试CLI删除任务" --priority low')
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
        r = run_cli('task add "测试CLI状态过滤" --priority medium')
        task_id = r.stdout.split("Task created: ")[1].strip()
        run_cli(f"task done {task_id}")

        # List done
        r = run_cli("task ls --status done")
        assert "测试CLI状态过滤" in r.stdout

        # List new
        r = run_cli("task ls --status new")
        assert "测试CLI状态过滤" not in r.stdout


class TestCLIProject:
    """Test CLI project commands"""

    def test_project_ls(self, wait_for_server):
        """Should list projects"""
        # Create a project first to ensure there's data to list
        run_cli('project add "测试CLI列表项目"')
        r = run_cli("project ls")
        assert r.returncode == 0
        # Output format: [id] name (status)
        assert "]" in r.stdout
        assert "测试CLI列表项目" in r.stdout

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


class TestCLIServer:
    """Test CLI server commands"""

    def test_server_status(self, wait_for_server):
        """Should check server status"""
        r = run_cli("server status")
        assert r.returncode == 0

    def test_server_stop_when_not_running(self):
        """Should handle server stop when not running"""
        # Remove PID file if it exists
        import os
        pid_file = os.path.expanduser("~/.pkm/pkm-server.pid")
        if os.path.exists(pid_file):
            os.remove(pid_file)
        r = run_cli("server stop")
        # Should handle gracefully (not running)
        assert r.returncode == 0


class TestCLIInbox:
    """Test CLI inbox commands"""

    def test_inbox_help(self):
        """Inbox help should show available commands"""
        r = run_cli("inbox --help")
        assert r.returncode == 0
        assert "add" in r.stdout

    def test_inbox_add_help(self):
        """Inbox add help should show examples"""
        r = run_cli("inbox add --help")
        assert r.returncode == 0
        assert "Examples:" in r.stdout
        assert "--parse" in r.stdout

    def test_inbox_add_basic(self, wait_for_server):
        """Should add content to inbox"""
        r = run_cli("inbox add test_content")
        assert r.returncode == 0
        assert "Captured to inbox" in r.stdout
        assert "_inbox.md" in r.stdout

    def test_inbox_add_with_parse_flag(self, wait_for_server):
        """Should add content with parse flag (without actual URL)"""
        r = run_cli("inbox add --parse test_parse")
        assert r.returncode == 0
        # 即使没有有效 URL 也应该能保存
        assert "Captured to inbox" in r.stdout or "Warning" in r.stdout

    def test_inbox_add_empty_content(self):
        """Should handle empty content"""
        r = run_cli("inbox add")
        # 不带内容参数应该报错
        assert r.returncode != 0


class TestCLIProjectPath:
    """Test project list with path option"""

    def test_project_ls_path(self, wait_for_server):
        """Should show project workspace path with -p flag"""
        run_cli('project add "测试项目路径"')
        r = run_cli("project ls -p")
        assert r.returncode == 0
        # Should show a path
        assert "/" in r.stdout or "~" in r.stdout


class TestCLIProjectUpdate:
    """Test project update command"""

    def test_project_update_name_only(self, wait_for_server):
        """Should update project name only"""
        r = run_cli('project add "测试项目更新"')
        project_id = r.stdout.split("Project created: ")[1].strip()
        r = run_cli(f"project update {project_id} --name '新名称'")
        assert r.returncode == 0
        assert "Project updated" in r.stdout

    def test_project_update_description_only(self, wait_for_server):
        """Should update project description only"""
        r = run_cli('project add "测试描述更新"')
        project_id = r.stdout.split("Project created: ")[1].strip()
        r = run_cli(f"project update {project_id} --description '新描述'")
        assert r.returncode == 0
        assert "Project updated" in r.stdout


class TestCLITaskApprove:
    """Test task approve command"""

    def test_task_approve(self, wait_for_server):
        """Should approve a task for reflow"""
        # Create and complete a task
        r = run_cli('task add "测试CLI批准任务" --priority high')
        task_id = r.stdout.split("Task created: ")[1].strip()
        run_cli(f"task done {task_id}")

        # Approve task
        r = run_cli(f"task approve {task_id}")
        assert r.returncode == 0
        assert "approved" in r.stdout.lower()


class TestCLITaskUpdateProgress:
    """Test task update with progress"""

    def test_task_update_progress(self, wait_for_server):
        """Should update task progress"""
        r = run_cli('task add "测试进度更新" --priority medium')
        task_id = r.stdout.split("Task created: ")[1].strip()

        r = run_cli(f"task update {task_id} --progress 50")
        assert r.returncode == 0
        assert "Task updated" in r.stdout

        # Verify
        r = run_cli(f"task get {task_id}")
        assert "50" in r.stdout

    def test_task_update_status(self, wait_for_server):
        """Should update task status"""
        r = run_cli('task add "测试状态更新" --priority medium')
        task_id = r.stdout.split("Task created: ")[1].strip()

        r = run_cli(f"task update {task_id} --status active")
        assert r.returncode == 0
        assert "Task updated" in r.stdout


class TestCLIReflow:
    """Test reflow commands"""

    def test_reflow_run_help(self):
        """Reflow run help should show usage"""
        r = run_cli("reflow run --help")
        assert r.returncode == 0

    def test_reflow_status_help(self):
        """Reflow status help should show usage"""
        r = run_cli("reflow status --help")
        assert r.returncode == 0

    def test_reflow_stage2_help(self):
        """Reflow stage2 help should show usage"""
        r = run_cli("reflow stage2 --help")
        assert r.returncode == 0
        assert "--batch-size" in r.stdout

    def test_reflow_run(self, wait_for_server):
        """Should trigger reflow"""
        r = run_cli("reflow run")
        assert r.returncode == 0
        assert "Starting" in r.stdout or "completed" in r.stdout

    def test_reflow_status(self, wait_for_server):
        """Should get reflow status"""
        r = run_cli("reflow status")
        assert r.returncode == 0
        assert "Pending" in r.stdout or "Claude" in r.stdout

    def test_reflow_stage2(self, wait_for_server):
        """Should trigger stage2"""
        r = run_cli("reflow stage2")
        assert r.returncode == 0
        assert "Starting" in r.stdout or "completed" in r.stdout


class TestCLIErrorHandling:
    """Test CLI error handling"""

    def test_task_get_nonexistent(self, wait_for_server):
        """Should handle getting non-existent task"""
        r = run_cli("task get nonexistent-id-12345")
        assert r.returncode != 0

    def test_task_update_nonexistent(self, wait_for_server):
        """Should handle updating non-existent task"""
        r = run_cli("task update nonexistent-id-12345 --title '新标题'")
        assert r.returncode != 0

    def test_task_delete_nonexistent(self, wait_for_server):
        """Should handle deleting non-existent task"""
        r = run_cli("task delete nonexistent-id-12345")
        assert r.returncode != 0

    def test_project_get_nonexistent(self, wait_for_server):
        """Should handle getting non-existent project"""
        r = run_cli("project get nonexistent-id-12345")
        assert r.returncode != 0

    def test_project_update_nonexistent(self, wait_for_server):
        """Should handle updating non-existent project"""
        r = run_cli("project update nonexistent-id-12345 --name '新名称'")
        assert r.returncode != 0
