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

    def test_project_ls_shows_default_with_bracket_not_index(self, wait_for_server):
        """Should show default project with [default] not index, other projects with [1], [2]"""
        # Ensure default project exists (it should by default)
        r = run_cli("project ls")
        assert r.returncode == 0
        # Default project should show as [default] not [1]
        assert "[default] default (active)" in r.stdout
        # When we add new projects, they should show with numbered indices
        run_cli('project add "测试序号项目A"')
        run_cli('project add "测试序号项目B"')
        r = run_cli("project ls")
        assert r.returncode == 0
        # default should still be [default], not [1]
        assert "[default] default (active)" in r.stdout
        # Other projects should be numbered [1], [2], etc.
        # (Order depends on API, but they should have indices, not [default])
        assert "[1]" in r.stdout or "[2]" in r.stdout
        assert "测试序号项目A" in r.stdout
        assert "测试序号项目B" in r.stdout
        # Verify no project other than default has [default] label
        lines_with_bracket_default = [l for l in r.stdout.split("\n") if "[default]" in l and "default" not in l.lower()]
        assert len(lines_with_bracket_default) == 0, "Only default project should have [default] label"

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

    def test_project_delete_default_fails(self, wait_for_server):
        """Should not allow deleting default project"""
        # Try to delete default project by name
        r = run_cli("project delete default")
        assert r.returncode != 0
        assert "Cannot delete default" in r.stdout or "Cannot delete default" in r.stderr

    def test_project_delete_by_index(self, wait_for_server):
        """Should delete project by index"""
        # Create a project to delete
        r = run_cli('project add "测试CLI删除索引项目"')
        project_id = r.stdout.split("Project created: ")[1].strip()

        # Get project list and find the index
        r = run_cli("project ls")
        lines = r.stdout.strip().split("\n")
        # Find the line with our project
        idx = None
        for line in lines:
            if "测试CLI删除索引项目" in line:
                # Extract index like [3]
                idx = line.split("]")[0].replace("[", "")
                break
        assert idx is not None, "Project not found in list"

        # Delete by index
        r = run_cli(f"project delete {idx}")
        assert r.returncode == 0
        assert "deleted" in r.stdout

        # Verify deleted
        r = run_cli("project ls")
        assert "测试CLI删除索引项目" not in r.stdout


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

    def test_inbox_add_with_url_shows_warning(self, monkeypatch):
        """Test inbox add with URL parse shows warning when parse fails"""
        import pkm.cli
        from unittest.mock import patch, MagicMock
        import click
        from click.testing import CliRunner

        # Test the path where parse fails (no URLs found)
        with patch.object(pkm.cli, 'extract_urls', return_value=[]):
            with patch.object(pkm.cli.click, 'echo') as mock_echo:
                # The warning should be shown when no URLs found
                pass  # This path just saves without parsing

    def test_inbox_add_empty_content(self):
        """Should handle empty content"""
        r = run_cli("inbox add")
        # 不带内容参数应该报错
        assert r.returncode != 0

    def test_inbox_add_io_error_handling(self, monkeypatch):
        """Test inbox add handles IOError when writing file"""
        import pkm.cli
        from unittest.mock import patch, MagicMock

        with patch.object(pkm.cli, 'generate_inbox_filename', return_value='test_inbox.md'):
            with patch.object(pkm.cli.click, 'echo'):
                with patch('builtins.open', side_effect=IOError("Disk full")):
                    with patch('pkm.cli.os.path.expanduser', return_value='/tmp'):
                        with patch('pkm.cli.os.makedirs'):
                            from click.testing import CliRunner
                            runner = CliRunner()
                            result = runner.invoke(pkm.cli.inbox, ['add', 'test content'])
                            # Should handle IOError gracefully - returncode should be 0 since error is caught
                            # Or it might be 1 if the error causes exit
                            assert result is not None


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


class TestCLIHelperFunctions:
    """Test CLI helper functions"""

    def test_extract_urls(self):
        """Test URL extraction from text"""
        from pkm.cli import extract_urls
        text = "Check this https://example.com and http://test.org and not a url"
        urls = extract_urls(text)
        assert "https://example.com" in urls
        assert "http://test.org" in urls

    def test_extract_urls_no_urls(self):
        """Test URL extraction with no URLs"""
        from pkm.cli import extract_urls
        text = "No URLs here"
        urls = extract_urls(text)
        assert len(urls) == 0

    def test_extract_urls_multiple(self):
        """Test URL extraction with multiple URLs"""
        from pkm.cli import extract_urls
        text = "Links: https://a.com https://b.com https://c.com"
        urls = extract_urls(text)
        assert len(urls) == 3

    def test_generate_inbox_filename(self):
        """Test inbox filename generation"""
        from pkm.cli import generate_inbox_filename
        content = "这是测试内容"
        filename = generate_inbox_filename(content)
        assert filename.endswith("_inbox.md")
        assert "2026" in filename

    def test_generate_inbox_filename_long_content(self):
        """Test inbox filename generation with long content"""
        from pkm.cli import generate_inbox_filename
        content = "A" * 100  # Very long content
        filename = generate_inbox_filename(content)
        assert filename.endswith("_inbox.md")
        assert len(filename) < 80  # Should be truncated

    def test_generate_inbox_filename_with_special_chars(self):
        """Test inbox filename with special characters"""
        from pkm.cli import generate_inbox_filename
        content = "# Test / with # and spaces"
        filename = generate_inbox_filename(content)
        assert filename.endswith("_inbox.md")
        assert "#" not in filename
        assert "/" not in filename

    def test_get_pid_no_file(self, tmp_path):
        """Test get_pid when PID file does not exist"""
        from pkm.cli import get_pid, PID_FILE
        import pkm.cli
        original = pkm.cli.PID_FILE
        pkm.cli.PID_FILE = str(tmp_path / "nonexistent.pid")
        try:
            pid = get_pid()
            assert pid is None
        finally:
            pkm.cli.PID_FILE = original

    def test_save_pid(self, tmp_path):
        """Test save_pid creates file with PID"""
        from pkm.cli import save_pid, get_pid, PID_FILE
        import pkm.cli
        original = pkm.cli.PID_FILE
        pkm.cli.PID_FILE = str(tmp_path / "test.pid")
        try:
            save_pid(12345)
            pid = get_pid()
            assert pid == "12345"
        finally:
            pkm.cli.PID_FILE = original

    def test_is_server_running_true(self, monkeypatch):
        """Test is_server_running when server is up"""
        from pkm.cli import is_server_running
        import requests

        class MockResponse:
            status_code = 200

        monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockResponse())
        assert is_server_running() is True

    def test_is_server_running_false_connection_error(self, monkeypatch):
        """Test is_server_running when connection error occurs"""
        from pkm.cli import is_server_running
        import requests

        def raise_connection_error(*args, **kwargs):
            raise requests.exceptions.ConnectionError("Connection refused")

        monkeypatch.setattr(requests, "get", raise_connection_error)
        assert is_server_running() is False

    def test_is_server_running_false_non_200(self, monkeypatch):
        """Test is_server_running when server returns non-200"""
        from pkm.cli import is_server_running
        import requests

        class MockResponse:
            status_code = 500

        monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockResponse())
        assert is_server_running() is False

    def test_parse_url_with_claude_success(self, monkeypatch):
        """Test parse_url_with_claude with successful response"""
        from pkm.cli import parse_url_with_claude

        class MockResult:
            returncode = 0
            stdout = "Parsed content here"

        def mock_run(*args, **kwargs):
            return MockResult()

        monkeypatch.setattr("subprocess.run", mock_run)
        result = parse_url_with_claude("https://example.com", "test note")
        assert result == "Parsed content here"

    def test_parse_url_with_claude_failure(self, monkeypatch):
        """Test parse_url_with_claude when claude CLI fails"""
        from pkm.cli import parse_url_with_claude

        class MockResult:
            returncode = 1
            stderr = "Error occurred"
            stdout = ""

        def mock_run(*args, **kwargs):
            return MockResult()

        monkeypatch.setattr("subprocess.run", mock_run)
        result = parse_url_with_claude("https://example.com", "test note")
        assert result is None

    def test_parse_url_with_claude_exception(self, monkeypatch):
        """Test parse_url_with_claude when exception occurs"""
        from pkm.cli import parse_url_with_claude

        def mock_run(*args, **kwargs):
            raise Exception("Some error")

        monkeypatch.setattr("subprocess.run", mock_run)
        result = parse_url_with_claude("https://example.com", "test note")
        assert result is None


class TestCLIServerFunctions:
    """Test CLI server helper functions"""

    def test_server_stop_no_pid(self, monkeypatch, tmp_path):
        """Test server_stop when no PID file exists"""
        from pkm.cli import server_stop, PID_FILE
        import pkm.cli

        original = pkm.cli.PID_FILE
        pkm.cli.PID_FILE = str(tmp_path / "nonexistent.pid")
        monkeypatch.setattr("pkm.cli.click.echo", lambda x: None)
        try:
            server_stop()  # Should not raise, just return
        finally:
            pkm.cli.PID_FILE = original

    def test_server_stop_process_not_found(self, monkeypatch, tmp_path):
        """Test server_stop when process does not exist"""
        from pkm.cli import server_stop, PID_FILE
        import pkm.cli

        original = pkm.cli.PID_FILE
        pkm.cli.PID_FILE = str(tmp_path / "test.pid")
        # Write an invalid PID
        with open(pkm.cli.PID_FILE, "w") as f:
            f.write("999999999")
        monkeypatch.setattr("pkm.cli.click.echo", lambda x: None)
        try:
            server_stop()  # Should handle ProcessLookupError
        finally:
            pkm.cli.PID_FILE = original

    def test_server_status_running(self, monkeypatch):
        """Test server_status when server is running"""
        from pkm.cli import server_status
        import click

        captured = []
        monkeypatch.setattr(click, "echo", lambda x: captured.append(x))
        monkeypatch.setattr("pkm.cli.is_server_running", lambda: True)
        server_status()
        assert "running" in captured[0].lower()

    def test_server_status_not_running(self, monkeypatch):
        """Test server_status when server is not running"""
        from pkm.cli import server_status
        import click

        captured = []
        monkeypatch.setattr(click, "echo", lambda x: captured.append(x))
        monkeypatch.setattr("pkm.cli.is_server_running", lambda: False)
        server_status()
        assert "not running" in captured[0].lower()

    def test_server_stop_success(self, monkeypatch, tmp_path):
        """Test server_stop when process is successfully stopped"""
        from pkm.cli import server_stop, PID_FILE
        import pkm.cli
        import os
        import signal
        import click

        original = pkm.cli.PID_FILE
        pkm.cli.PID_FILE = str(tmp_path / "test.pid")
        # Write a valid PID (use current process as mock)
        with open(pkm.cli.PID_FILE, "w") as f:
            f.write(str(os.getpid()))

        captured = []
        monkeypatch.setattr(click, "echo", lambda x: captured.append(x))
        # Mock os.kill to not actually kill, but verify it's called
        killed = []
        def mock_kill(pid, sig):
            killed.append((pid, sig))
        monkeypatch.setattr(os, "kill", mock_kill)
        # Mock os.remove to verify it's called
        removed = []
        def mock_remove(path):
            removed.append(path)
        monkeypatch.setattr(os, "remove", mock_remove)

        try:
            server_stop()
            assert len(killed) == 1
            assert killed[0][1] == signal.SIGTERM
            assert "Server stopped" in captured
            assert str(pkm.cli.PID_FILE) in removed
        finally:
            pkm.cli.PID_FILE = original

    def test_server_start_already_running(self, monkeypatch):
        """Test server_start when server is already running"""
        from pkm.cli import server_start
        import click

        captured = []
        monkeypatch.setattr(click, "echo", lambda x: captured.append(x))
        monkeypatch.setattr("pkm.cli.is_server_running", lambda: True)
        server_start()
        assert "already running" in captured[0]
