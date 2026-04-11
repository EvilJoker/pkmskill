"""Knowledge reflow tests for PKM"""

import pytest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    init_db,
    create_task,
    get_task,
    update_task,
    create_project,
    get_project,
    create_reflow,
    get_reflow_by_task,
    update_reflow_status,
    list_tasks,
)
import knowledge
import workspace


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
    init_db()
    yield temp_db
    database.DB_PATH = original_path


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


class TestCheckClaudeEnvironment:
    """Test Claude CLI environment check"""

    def test_claude_available(self):
        """Should return True when Claude CLI is available"""
        ok, msg = knowledge.check_claude_environment()
        # Returns tuple, first element is boolean
        assert isinstance(ok, bool)
        assert isinstance(msg, str)

    @patch("subprocess.run")
    def test_claude_not_installed(self, mock_run):
        """Should return False when Claude CLI is not installed"""
        mock_run.side_effect = FileNotFoundError("claude not found")
        ok, msg = knowledge.check_claude_environment()
        assert ok is False
        assert "未安装" in msg or "not found" in msg.lower()

    @patch("subprocess.run")
    def test_claude_timeout(self, mock_run):
        """Should return False when Claude CLI times out"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("claude", 30)
        ok, msg = knowledge.check_claude_environment()
        assert ok is False
        assert "超时" in msg

    @patch("subprocess.run")
    def test_claude_error(self, mock_run):
        """Should return False when Claude CLI returns error"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "some error"
        mock_run.return_value = mock_result
        ok, msg = knowledge.check_claude_environment()
        assert ok is False


class TestShouldExcludeFile:
    """Test file exclusion logic"""

    def test_exclude_by_extension(self):
        """Should exclude files by extension"""
        assert knowledge.should_exclude_file("test.py") is True
        assert knowledge.should_exclude_file("test.js") is True
        assert knowledge.should_exclude_file("test.ts") is True
        assert knowledge.should_exclude_file("test.go") is True
        assert knowledge.should_exclude_file("test.java") is True

    def test_exclude_specific_files(self):
        """Should exclude specific files"""
        assert knowledge.should_exclude_file("task.md") is True
        assert knowledge.should_exclude_file("completed.md") is True
        assert knowledge.should_exclude_file("*.sh") is True

    def test_not_exclude(self):
        """Should not exclude regular files"""
        assert knowledge.should_exclude_file("readme.txt") is False
        assert knowledge.should_exclude_file("notes.md") is False
        # data.json is excluded because *.json is in exclude_patterns
        assert knowledge.should_exclude_file("data.xml") is False
        assert knowledge.should_exclude_file("notes.csv") is False


class TestReadTaskWorkspaceContent:
    """Test reading task workspace content"""

    def test_empty_workspace(self, temp_workspace):
        """Should return empty string for non-existent workspace"""
        result = knowledge.read_task_workspace_content("/non/existent/path")
        assert result == ""

    def test_read_workspace_content(self, temp_workspace):
        """Should read workspace content excluding specified files"""
        # Create test files
        with open(os.path.join(temp_workspace, "task.md"), "w") as f:
            f.write("# Task content")
        with open(os.path.join(temp_workspace, "notes.txt"), "w") as f:
            f.write("Some notes")
        with open(os.path.join(temp_workspace, "solution.md"), "w") as f:
            f.write("Solution content")

        result = knowledge.read_task_workspace_content(temp_workspace)

        # task.md should be excluded
        assert "Task content" not in result
        assert "Some notes" in result
        assert "Solution content" in result

    def test_excludes_py_files(self, temp_workspace):
        """Should exclude Python files"""
        with open(os.path.join(temp_workspace, "test.py"), "w") as f:
            f.write("print('hello')")
        with open(os.path.join(temp_workspace, "notes.txt"), "w") as f:
            f.write("Some notes")

        result = knowledge.read_task_workspace_content(temp_workspace)

        assert "Some notes" in result
        assert "print" not in result  # Python code excluded


class TestExtractKnowledgeWithClaude:
    """Test Claude CLI knowledge extraction"""

    def test_empty_content_returns_empty(self):
        """Should return empty string for empty content"""
        result = knowledge.extract_knowledge_with_claude("")
        assert result == ""

    def test_whitespace_content_returns_empty(self):
        """Should return empty string for whitespace content"""
        result = knowledge.extract_knowledge_with_claude("   \n\t  ")
        assert result == ""

    @patch("subprocess.run")
    def test_extract_success(self, mock_run):
        """Should extract knowledge from content"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "## 经验\n- 经验点1\n## 方案\n- 方案点1"
        mock_run.return_value = mock_result

        content = "Some task content with experiences"
        result = knowledge.extract_knowledge_with_claude(content)

        assert "经验" in result or "experience" in result.lower() or mock_result.stdout in result
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_retry_on_failure(self, mock_run):
        """Should retry on failure"""
        mock_result_fail = MagicMock()
        mock_result_fail.returncode = 1
        mock_result_fail.stderr = "error"

        mock_result_success = MagicMock()
        mock_result_success.returncode = 0
        mock_result_success.stdout = "Knowledge extracted"

        mock_run.side_effect = [mock_result_fail, mock_result_fail, mock_result_success]

        result = knowledge.extract_knowledge_with_claude("content")

        assert "extracted" in result.lower() or "error" in result.lower()
        assert mock_run.call_count == 3  # 2 retries + 1 success


class TestAppendToProjectMemory:
    """Test appending knowledge to project memory"""

    def test_append_to_new_file(self, temp_workspace):
        """Should create project.md and append knowledge"""
        task_info = {"id": "test-123", "title": "测试任务"}
        knowledge_text = "## 经验\n- 经验点1\n\n## 方案\n- 方案点1"

        knowledge.append_to_project_memory(temp_workspace, task_info, knowledge_text)

        project_md_path = os.path.join(temp_workspace, "project.md")
        assert os.path.exists(project_md_path)

        with open(project_md_path, "r") as f:
            content = f.read()

        assert "测试任务" in content
        assert "test-123" in content
        assert "经验点1" in content

    def test_append_to_existing_file(self, temp_workspace):
        """Should append to existing project.md"""
        # Create existing project.md
        existing_content = """# Project: Test

## 项目描述
Test project.

## 经验/方案索引
### 2026-04-01 任务：早先任务
- **任务ID**: old-task-id
- **内容**: Old knowledge
"""
        project_md_path = os.path.join(temp_workspace, "project.md")
        with open(project_md_path, "w") as f:
            f.write(existing_content)

        task_info = {"id": "new-task-id", "title": "新任务"}
        knowledge_text = "## 经验\n- 新经验"

        knowledge.append_to_project_memory(temp_workspace, task_info, knowledge_text)

        with open(project_md_path, "r") as f:
            content = f.read()

        assert "新任务" in content
        assert "new-task-id" in content
        assert "新经验" in content


class TestProcessSingleTaskReflow:
    """Test single task reflow processing"""

    def test_task_not_found(self, override_db_path):
        """Should return error when task not found"""
        success, message = knowledge.process_single_task_reflow("non-existent-id")
        assert success is False
        assert "不存在" in message

    def test_task_not_approved(self, override_db_path):
        """Should return error when task status is not approved"""
        task = create_task(title="测试任务", priority="medium", quadrant=2)
        success, message = knowledge.process_single_task_reflow(task["id"])
        assert success is False
        assert "approved" in message

    def test_task_no_workspace(self, override_db_path):
        """Should return error when task has no workspace"""
        task = create_task(title="测试任务", priority="medium", quadrant=2)
        update_task(task["id"], status="approved")

        success, message = knowledge.process_single_task_reflow(task["id"])
        assert success is False
        assert "工作区" in message

    @patch("knowledge.extract_knowledge_with_claude")
    @patch("knowledge.archive_task_workspace")
    def test_successful_reflow(self, mock_archive, mock_extract, override_db_path, temp_workspace):
        """Should successfully process approved task with workspace"""
        mock_extract.return_value = "## 经验\n- 测试经验"

        # Create project first
        project = create_project(name="测试项目", workspace_path=temp_workspace)

        # Create task with workspace
        task = create_task(
            title="测试任务",
            priority="medium",
            quadrant=2,
            workspace_path=temp_workspace,
            project_id=project["id"]
        )
        update_task(task["id"], status="approved")

        # Create workspace files
        with open(os.path.join(temp_workspace, "notes.md"), "w") as f:
            f.write("Some notes content")

        success, message = knowledge.process_single_task_reflow(task["id"])

        assert success is True
        assert "成功" in message

        # Verify task is archived
        updated_task = get_task(task["id"])
        assert updated_task["status"] == "archived"

        # Verify reflow record created
        reflow = get_reflow_by_task(task["id"])
        assert reflow is not None
        assert reflow["status"] == "completed"


class TestRunReflowCycle:
    """Test reflow cycle execution"""

    def test_no_approved_tasks(self, override_db_path):
        """Should handle no approved tasks"""
        result = knowledge.run_reflow_cycle()

        assert result["processed"] == 0
        assert result["succeeded"] == 0
        assert result["failed"] == 0

    @patch("knowledge.process_single_task_reflow")
    def test_processes_approved_tasks(self, mock_process, override_db_path):
        """Should process approved tasks"""
        mock_process.return_value = (True, "成功")

        task1 = create_task(title="任务1", priority="medium", quadrant=2)
        task2 = create_task(title="任务2", priority="medium", quadrant=2)
        update_task(task1["id"], status="approved")
        update_task(task2["id"], status="approved")

        result = knowledge.run_reflow_cycle()

        assert result["processed"] == 2
        assert result["succeeded"] == 2
        assert result["failed"] == 0

    @patch("knowledge.process_single_task_reflow")
    def test_handles_failures(self, mock_process, override_db_path):
        """Should handle partial failures"""
        mock_process.side_effect = [(True, "成功"), (False, "失败")]

        task1 = create_task(title="任务1", priority="medium", quadrant=2)
        task2 = create_task(title="任务2", priority="medium", quadrant=2)
        update_task(task1["id"], status="approved")
        update_task(task2["id"], status="approved")

        result = knowledge.run_reflow_cycle()

        assert result["processed"] == 2
        assert result["succeeded"] == 1
        assert result["failed"] == 1
        assert len(result["errors"]) == 1


class TestGetReflowStatus:
    """Test reflow status retrieval"""

    def test_status_returns_config(self, override_db_path):
        """Should return reflow status with config"""
        status = knowledge.get_reflow_status()

        assert "pending_approved_tasks" in status
        assert "pending_reflows" in status
        assert "config" in status
        assert "claude_available" in status
        assert "interval" in status["config"]
        assert "exclude_patterns" in status["config"]
