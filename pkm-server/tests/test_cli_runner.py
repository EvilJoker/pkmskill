"""CLI tests using CliRunner for coverage tracking"""

import pytest
import os
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

# 设置 API_BASE 环境变量
os.environ["PKM_API_BASE"] = os.environ.get("PKM_API_BASE", "http://localhost:8890")


@pytest.fixture(scope="module")
def runner():
    """Create a CliRunner instance"""
    return CliRunner()


@pytest.fixture(scope="module")
def wait_for_server():
    """Wait for server to be ready"""
    import requests
    import time

    max_retries = 30
    for _ in range(max_retries):
        try:
            r = requests.get(f"{os.environ['PKM_API_BASE']}/health")
            if r.status_code == 200:
                return
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    pytest.fail("Server did not start in time")


def run_cli(runner, cli_func, args, env=None):
    """Run CLI command using CliRunner with proper env setup"""
    from pkm.cli import API_BASE
    # 临时设置 API_BASE
    original_api_base = API_BASE
    if env and "PKM_API_BASE" in env:
        import pkm.cli
        pkm.cli.API_BASE = env["PKM_API_BASE"]

    result = runner.invoke(cli_func, args, catch_exceptions=False)

    # 恢复 API_BASE
    if env and "PKM_API_BASE" in env:
        import pkm.cli
        pkm.cli.API_BASE = original_api_base

    return result


# Import CLI commands
from pkm.cli import cli, task, project, inbox, reflow, server


class TestCLIHelp:
    """Test CLI help commands"""

    def test_main_help(self, runner):
        """Main help should show available commands"""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "task" in result.output
        assert "project" in result.output
        assert "server" in result.output

    def test_task_help(self, runner):
        """Task help should show task commands"""
        result = runner.invoke(task, ["--help"])
        assert result.exit_code == 0
        assert "add" in result.output
        assert "ls" in result.output
        assert "get" in result.output
        assert "update" in result.output
        assert "done" in result.output
        assert "delete" in result.output

    def test_project_help(self, runner):
        """Project help should show project commands"""
        result = runner.invoke(project, ["--help"])
        assert result.exit_code == 0
        assert "add" in result.output
        assert "ls" in result.output
        assert "get" in result.output
        assert "update" in result.output
        assert "archive" in result.output

    def test_task_add_help(self, runner):
        """Task add help should show examples"""
        result = runner.invoke(task, ["add", "--help"])
        assert result.exit_code == 0
        assert "eg:" in result.output
        assert "priority" in result.output

    def test_task_ls_help(self, runner):
        """Task ls help should show examples"""
        result = runner.invoke(task, ["ls", "--help"])
        assert result.exit_code == 0
        assert "eg:" in result.output
        assert "--status" in result.output


class TestCLITask:
    """Test CLI task commands"""

    def test_task_ls(self, runner, wait_for_server):
        """Should list tasks"""
        # Create a task first
        result = runner.invoke(task, ["add", "测试CLI列表任务", "--priority", "high"], catch_exceptions=False)
        result = runner.invoke(task, ["ls"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "]" in result.output
        assert "测试CLI列表任务" in result.output

    def test_task_add(self, runner, wait_for_server):
        """Should add a new task"""
        result = runner.invoke(task, ["add", "测试CLI添加任务", "--priority", "high"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Task created:" in result.output

        # Verify task was created
        result = runner.invoke(task, ["ls"], catch_exceptions=False)
        assert "测试CLI添加任务" in result.output

    def test_task_add_with_all_options(self, runner, wait_for_server):
        """Should add task with all options"""
        result = runner.invoke(task, ["add", "测试CLI全选项", "--priority", "medium", "--due", "2026-04-15"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Task created:" in result.output

    def test_task_add_with_project(self, runner, wait_for_server):
        """Should add task with project association"""
        # Create a project first
        result = runner.invoke(project, ["add", "测试项目关联"], catch_exceptions=False)
        project_id = result.output.split("Project created: ")[1].strip()

        # Add task with project
        result = runner.invoke(task, ["add", "测试任务关联项目", "--priority", "high", "--project", project_id], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Task created:" in result.output

    def test_task_get(self, runner, wait_for_server):
        """Should get task details"""
        # First create a task
        result = runner.invoke(task, ["add", "测试CLI获取任务", "--priority", "low"], catch_exceptions=False)
        assert result.exit_code == 0
        task_id = result.output.split("Task created: ")[1].strip()

        # Get task details
        result = runner.invoke(task, ["get", task_id], catch_exceptions=False)
        assert result.exit_code == 0
        assert "测试CLI获取任务" in result.output
        assert "low" in result.output

    def test_task_update(self, runner, wait_for_server):
        """Should update a task"""
        # Create task
        result = runner.invoke(task, ["add", "测试CLI更新任务", "--priority", "low"], catch_exceptions=False)
        task_id = result.output.split("Task created: ")[1].strip()

        # Update task
        result = runner.invoke(task, ["update", task_id, "--title", "测试CLI已更新", "--priority", "high"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Task updated" in result.output

        # Verify update
        result = runner.invoke(task, ["get", task_id], catch_exceptions=False)
        assert "测试CLI已更新" in result.output
        assert "high" in result.output

    def test_task_update_multiple_fields(self, runner, wait_for_server):
        """Should update multiple fields at once"""
        # Create task
        result = runner.invoke(task, ["add", "测试多字段更新", "--priority", "low"], catch_exceptions=False)
        task_id = result.output.split("Task created: ")[1].strip()

        # Update multiple fields
        result = runner.invoke(task, ["update", task_id, "--title", "新标题", "--priority", "high", "--progress", "75"], catch_exceptions=False)
        assert result.exit_code == 0

        # Verify
        result = runner.invoke(task, ["get", task_id], catch_exceptions=False)
        assert "新标题" in result.output
        assert "high" in result.output
        assert "75" in result.output

    def test_task_done(self, runner, wait_for_server):
        """Should mark task as completed"""
        # Create task
        result = runner.invoke(task, ["add", "测试CLI完成任务", "--priority", "medium"], catch_exceptions=False)
        task_id = result.output.split("Task created: ")[1].strip()

        # Mark as done
        result = runner.invoke(task, ["done", task_id], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Task completed" in result.output

        # Verify
        result = runner.invoke(task, ["get", task_id], catch_exceptions=False)
        assert "done" in result.output

    def test_task_delete(self, runner, wait_for_server):
        """Should delete a task"""
        # Create task
        result = runner.invoke(task, ["add", "测试CLI删除任务", "--priority", "low"], catch_exceptions=False)
        task_id = result.output.split("Task created: ")[1].strip()

        # Delete task
        result = runner.invoke(task, ["delete", task_id], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Task deleted" in result.output

        # Verify deleted
        result = runner.invoke(task, ["get", task_id], catch_exceptions=True)
        assert result.exit_code != 0

    def test_task_ls_filter_by_status(self, runner, wait_for_server):
        """Should filter tasks by status"""
        # Create and complete a task
        result = runner.invoke(task, ["add", "测试CLI状态过滤", "--priority", "medium"], catch_exceptions=False)
        task_id = result.output.split("Task created: ")[1].strip()
        runner.invoke(task, ["done", task_id], catch_exceptions=False)

        # List done
        result = runner.invoke(task, ["ls", "--status", "done"], catch_exceptions=False)
        assert "测试CLI状态过滤" in result.output

        # List new
        result = runner.invoke(task, ["ls", "--status", "new"], catch_exceptions=False)
        assert "测试CLI状态过滤" not in result.output


class TestCLIProject:
    """Test CLI project commands"""

    def test_project_ls(self, runner, wait_for_server):
        """Should list projects"""
        # Create a project first
        result = runner.invoke(project, ["add", "测试CLI列表项目"], catch_exceptions=False)
        result = runner.invoke(project, ["ls"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "]" in result.output
        assert "测试CLI列表项目" in result.output

    def test_project_add(self, runner, wait_for_server):
        """Should add a new project"""
        result = runner.invoke(project, ["add", "测试CLI项目", "--description", "测试描述"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Project created:" in result.output

        # Verify
        result = runner.invoke(project, ["ls"], catch_exceptions=False)
        assert "测试CLI项目" in result.output

    def test_project_get(self, runner, wait_for_server):
        """Should get project details"""
        # Create project
        result = runner.invoke(project, ["add", "测试CLI获取项目", "--description", "项目详情"], catch_exceptions=False)
        project_id = result.output.split("Project created: ")[1].strip()

        # Get details
        result = runner.invoke(project, ["get", project_id], catch_exceptions=False)
        assert result.exit_code == 0
        assert "测试CLI获取项目" in result.output
        assert "项目详情" in result.output

    def test_project_update(self, runner, wait_for_server):
        """Should update a project"""
        # Create project
        result = runner.invoke(project, ["add", "测试CLI更新项目", "--description", "旧描述"], catch_exceptions=False)
        project_id = result.output.split("Project created: ")[1].strip()

        # Update
        result = runner.invoke(project, ["update", project_id, "--name", "测试CLI已更新", "--description", "新描述"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Project updated" in result.output

        # Verify
        result = runner.invoke(project, ["get", project_id], catch_exceptions=False)
        assert "测试CLI已更新" in result.output
        assert "新描述" in result.output

    def test_project_archive(self, runner, wait_for_server):
        """Should archive a project"""
        # Create project
        result = runner.invoke(project, ["add", "测试CLI归档项目"], catch_exceptions=False)
        project_id = result.output.split("Project created: ")[1].strip()

        # Archive
        result = runner.invoke(project, ["archive", project_id], catch_exceptions=False)
        assert result.exit_code == 0

        # Verify status changed to archived
        result = runner.invoke(project, ["get", project_id], catch_exceptions=False)
        assert "archived" in result.output

    def test_project_ls_filter_by_status(self, runner, wait_for_server):
        """Should filter projects by status"""
        # Create and archive a project
        result = runner.invoke(project, ["add", "测试CLI项目状态过滤"], catch_exceptions=False)
        project_id = result.output.split("Project created: ")[1].strip()
        runner.invoke(project, ["archive", project_id], catch_exceptions=False)

        # List active
        result = runner.invoke(project, ["ls", "--status", "active"], catch_exceptions=False)
        assert "测试CLI项目状态过滤" not in result.output

        # List archived
        result = runner.invoke(project, ["ls", "--status", "archived"], catch_exceptions=False)
        assert "测试CLI项目状态过滤" in result.output


class TestCLIServer:
    """Test CLI server commands"""

    def test_server_status(self, runner, wait_for_server):
        """Should check server status"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            result = runner.invoke(server, ["status"], catch_exceptions=False)
            assert result.exit_code == 0

    def test_server_stop_when_not_running(self, runner):
        """Should handle server stop when not running"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = runner.invoke(server, ["stop"], catch_exceptions=False)
            # Should handle gracefully (not running)
            assert result.exit_code == 0


class TestCLIInbox:
    """Test CLI inbox commands"""

    def test_inbox_help(self, runner):
        """Inbox help should show available commands"""
        result = runner.invoke(inbox, ["--help"])
        assert result.exit_code == 0
        assert "add" in result.output

    def test_inbox_add_help(self, runner):
        """Inbox add help should show examples"""
        result = runner.invoke(inbox, ["add", "--help"])
        assert result.exit_code == 0
        assert "Examples:" in result.output
        assert "--parse" in result.output

    def test_inbox_add_basic(self, runner, wait_for_server):
        """Should add content to inbox"""
        result = runner.invoke(inbox, ["add", "test_content"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Captured to inbox" in result.output
        assert "_inbox.md" in result.output

    def test_inbox_add_with_parse_flag(self, runner, wait_for_server):
        """Should add content with parse flag"""
        result = runner.invoke(inbox, ["add", "--parse", "test_parse"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Captured to inbox" in result.output or "Warning" in result.output

    def test_inbox_add_empty_content(self, runner):
        """Should handle empty content"""
        result = runner.invoke(inbox, ["add"], catch_exceptions=False)
        assert result.exit_code != 0


class TestCLIProjectLsDisplay:
    """Test project ls display format - should use index numbers like task ls"""

    def test_project_ls_with_single_project(self, runner, wait_for_server):
        """Should show project with index number, not UUID"""
        # Create a project
        runner.invoke(project, ["add", "测试项目显示"], catch_exceptions=False)
        result = runner.invoke(project, ["ls"], catch_exceptions=False)
        assert result.exit_code == 0
        # Should show [序号] 名称 (状态)，不显示完整UUID
        assert "]" in result.output
        assert "测试项目显示" in result.output
        # 不应该显示UUID格式 [xxxxxxxx-xxxx-xxxx...]
        import re
        uuid_pattern = r'\[[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\]'
        assert not re.search(uuid_pattern, result.output), "不应显示UUID"

    def test_project_ls_with_path_flag(self, runner, wait_for_server):
        """Should show project name with path when -a flag is used"""
        # Create a project
        runner.invoke(project, ["add", "测试路径显示"], catch_exceptions=False)
        result = runner.invoke(project, ["ls", "-a"], catch_exceptions=False)
        assert result.exit_code == 0
        # 应该显示 [序号] 名称 [状态] uuid - 路径 格式
        assert "-" in result.output
        assert "测试路径显示" in result.output
        assert "/" in result.output

    def test_project_ls_multiple_projects(self, runner, wait_for_server):
        """Should show multiple projects with sequential index numbers"""
        # Create multiple projects
        runner.invoke(project, ["add", "项目A"], catch_exceptions=False)
        runner.invoke(project, ["add", "项目B"], catch_exceptions=False)
        runner.invoke(project, ["add", "项目C"], catch_exceptions=False)
        result = runner.invoke(project, ["ls"], catch_exceptions=False)
        assert result.exit_code == 0
        # 应该显示 [1], [2], [3] 等序号
        assert "[1]" in result.output
        assert "[2]" in result.output
        assert "[3]" in result.output
        # 不应该显示UUID
        import re
        uuid_pattern = r'\[[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\]'
        assert not re.search(uuid_pattern, result.output), "不应显示UUID"

    def test_project_ls_no_uuid_in_output(self, runner, wait_for_server):
        """Should never show UUID in project ls output"""
        runner.invoke(project, ["add", "无UUID测试"], catch_exceptions=False)
        result = runner.invoke(project, ["ls"], catch_exceptions=False)
        assert result.exit_code == 0
        # 确保输出中没有8-4-4-4-12格式的UUID
        lines = result.output.split("\n")
        for line in lines:
            if line.strip():
                # 检查是否包含UUID模式
                parts = line.split("]")
                if len(parts) > 0:
                    first_part = parts[0].strip().lstrip("[")
                    # 如果第一个部分包含-，说明是UUID格式，应该报错
                    assert "-" not in first_part or first_part.replace("-", "").isalnum() is False, \
                        f"不应显示UUID: {line}"


class TestCLIProjectUpdate:
    """Test project update command"""

    def test_project_update_name_only(self, runner, wait_for_server):
        """Should update project name only"""
        result = runner.invoke(project, ["add", "测试项目更新"], catch_exceptions=False)
        project_id = result.output.split("Project created: ")[1].strip()
        result = runner.invoke(project, ["update", project_id, "--name", "新名称"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Project updated" in result.output

    def test_project_update_description_only(self, runner, wait_for_server):
        """Should update project description only"""
        result = runner.invoke(project, ["add", "测试描述更新"], catch_exceptions=False)
        project_id = result.output.split("Project created: ")[1].strip()
        result = runner.invoke(project, ["update", project_id, "--description", "新描述"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Project updated" in result.output


class TestCLITaskApprove:
    """Test task approve command"""

    def test_task_approve(self, runner, wait_for_server):
        """Should approve a task for reflow"""
        # Create and complete a task
        result = runner.invoke(task, ["add", "测试CLI批准任务", "--priority", "high"], catch_exceptions=False)
        task_id = result.output.split("Task created: ")[1].strip()
        runner.invoke(task, ["done", task_id], catch_exceptions=False)

        # Approve task
        result = runner.invoke(task, ["approve", task_id], catch_exceptions=False)
        assert result.exit_code == 0
        assert "approved" in result.output.lower()


class TestCLITaskUpdateProgress:
    """Test task update with progress"""

    def test_task_update_progress(self, runner, wait_for_server):
        """Should update task progress"""
        result = runner.invoke(task, ["add", "测试进度更新", "--priority", "medium"], catch_exceptions=False)
        task_id = result.output.split("Task created: ")[1].strip()

        result = runner.invoke(task, ["update", task_id, "--progress", "50"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Task updated" in result.output

        # Verify
        result = runner.invoke(task, ["get", task_id], catch_exceptions=False)
        assert "50" in result.output


class TestCLIInteractiveTask:
    """Test interactive task commands"""

    def test_task_add_interactive(self, runner, wait_for_server):
        """Should add task interactively"""
        # Create a project first for selection
        result = runner.invoke(project, ["add", "交互测试项目"], catch_exceptions=False)
        project_id = result.output.split("Project created: ")[1].strip()

        # Simulate interactive input: title, priority (3=low), due (empty), project (1)
        inputs = "测试交互添加\n3\n\n1\n"
        result = runner.invoke(task, ["add"], input=inputs, catch_exceptions=False)
        assert result.exit_code == 0
        assert "Task created:" in result.output

    def test_task_update_interactive(self, runner, wait_for_server):
        """Should update task interactively"""
        # Create a task first
        result = runner.invoke(task, ["add", "待更新任务", "--priority", "low"], catch_exceptions=False)
        task_id = result.output.split("Task created: ")[1].strip()

        # Simulate interactive input: task index (1), new title (empty=skip), priority (empty=skip), progress (empty=skip)
        inputs = "1\n\n\n\n"
        result = runner.invoke(task, ["update"], input=inputs, catch_exceptions=False)
        # Should complete without error (interactive mode entered and exited)
        assert result.exit_code == 0


class TestCLIReflow:
    """Test reflow commands"""

    def test_reflow_run_help(self, runner):
        """Reflow run help should show usage"""
        result = runner.invoke(reflow, ["run", "--help"])
        assert result.exit_code == 0

    def test_reflow_status_help(self, runner):
        """Reflow status help should show usage"""
        result = runner.invoke(reflow, ["status", "--help"])
        assert result.exit_code == 0

    def test_reflow_run(self, runner, wait_for_server):
        """Should trigger reflow"""
        result = runner.invoke(reflow, ["run"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Starting" in result.output or "completed" in result.output

    def test_reflow_status(self, runner, wait_for_server):
        """Should get reflow status"""
        result = runner.invoke(reflow, ["status"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Pending" in result.output or "Claude" in result.output



class TestCLIErrorHandling:
    """Test CLI error handling"""

    def test_task_get_nonexistent(self, runner, wait_for_server):
        """Should handle getting non-existent task"""
        result = runner.invoke(task, ["get", "nonexistent-id-12345"], catch_exceptions=True)
        assert result.exit_code != 0

    def test_task_update_nonexistent(self, runner, wait_for_server):
        """Should handle updating non-existent task"""
        result = runner.invoke(task, ["update", "nonexistent-id-12345", "--title", "新标题"], catch_exceptions=True)
        assert result.exit_code != 0

    def test_task_delete_nonexistent(self, runner, wait_for_server):
        """Should handle deleting non-existent task"""
        result = runner.invoke(task, ["delete", "nonexistent-id-12345"], catch_exceptions=True)
        assert result.exit_code != 0

    def test_project_get_nonexistent(self, runner, wait_for_server):
        """Should handle getting non-existent project"""
        result = runner.invoke(project, ["get", "nonexistent-id-12345"], catch_exceptions=True)
        assert result.exit_code != 0

    def test_project_update_nonexistent(self, runner, wait_for_server):
        """Should handle updating non-existent project"""
        result = runner.invoke(project, ["update", "nonexistent-id-12345", "--name", "新名称"], catch_exceptions=True)
        assert result.exit_code != 0
