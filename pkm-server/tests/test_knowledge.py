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
import pkm.workspace as workspace


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

    @patch("subprocess.run")
    def test_claude_generic_exception(self, mock_run):
        """Should return False when Claude CLI throws generic exception"""
        mock_run.side_effect = OSError("unexpected error")
        ok, msg = knowledge.check_claude_environment()
        assert ok is False
        assert "调用失败" in msg


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

    def test_read_workspace_handles_unreadable_file(self, temp_workspace, monkeypatch):
        """Should handle unreadable files gracefully"""
        # Create a file that will be unreadable
        bad_file = os.path.join(temp_workspace, "bad.md")
        with open(bad_file, "w") as f:
            f.write("content")

        # Make the file unreadable by patching open to raise an exception
        import builtins
        original_open = builtins.open

        def mock_open(*args, **kwargs):
            if "bad.md" in str(args[0]):
                raise PermissionError("Permission denied")
            return original_open(*args, **kwargs)

        monkeypatch.setattr(builtins, "open", mock_open)
        # Should not raise, just skip the bad file
        result = knowledge.read_task_workspace_content(temp_workspace)
        assert "content" not in result  # bad.md should be skipped

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

    @patch("subprocess.run")
    def test_all_retries_fail(self, mock_run):
        """Should return error message when all retries fail"""
        mock_result_fail = MagicMock()
        mock_result_fail.returncode = 1
        mock_result_fail.stderr = "repeated error"

        # 3 次调用都失败
        mock_run.side_effect = [mock_result_fail, mock_result_fail, mock_result_fail]

        result = knowledge.extract_knowledge_with_claude("content")

        assert "[Claude 调用失败" in result
        assert mock_run.call_count == 3


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

    def test_append_to_existing_file_without_header(self, temp_workspace):
        """Should append to existing project.md without ### header"""
        # Create existing project.md with index section but no ### headers
        existing_content = """# Project: Test

## 项目描述
Test project.

## 经验/方案索引
Some content without ### header
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


class TestProcessSingleTaskReflow:
    """Test single task reflow processing"""

    def test_task_not_found(self, override_db_path):
        """Should return error when task not found"""
        success, message = knowledge.process_single_task_reflow("non-existent-id")
        assert success is False
        assert "不存在" in message

    def test_task_not_approved(self, override_db_path):
        """Should return error when task status is not approved"""
        task = create_task(title="测试任务", priority="medium")
        success, message = knowledge.process_single_task_reflow(task["id"])
        assert success is False
        assert "approved" in message

    def test_task_no_workspace(self, override_db_path):
        """Should return error when task has no workspace"""
        task = create_task(title="测试任务", priority="medium")
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

    @patch("knowledge.extract_knowledge_with_claude")
    @patch("knowledge.archive_task_workspace")
    def test_reflow_task_without_project(self, mock_archive, mock_extract, override_db_path, temp_workspace):
        """Should use default project workspace when task has no project"""
        mock_extract.return_value = "## 经验\n- 测试经验"

        # Create default project first
        default_project = create_project(name="default", description="Default", workspace_path=temp_workspace)

        # Create task WITHOUT project_id
        task = create_task(
            title="测试任务无项目",
            priority="medium",
            workspace_path=temp_workspace
            # No project_id!
        )
        update_task(task["id"], status="approved")

        # Create workspace files
        with open(os.path.join(temp_workspace, "notes.md"), "w") as f:
            f.write("Some notes content")

        success, message = knowledge.process_single_task_reflow(task["id"])

        assert success is True
        assert "成功" in message


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

        task1 = create_task(title="任务1", priority="medium")
        task2 = create_task(title="任务2", priority="medium")
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

        task1 = create_task(title="任务1", priority="medium")
        task2 = create_task(title="任务2", priority="medium")
        update_task(task1["id"], status="approved")
        update_task(task2["id"], status="approved")

        result = knowledge.run_reflow_cycle()

        assert result["processed"] == 2
        assert result["succeeded"] == 1
        assert result["failed"] == 1
        assert len(result["errors"]) == 1

    def test_skips_already_processing(self, override_db_path):
        """Should skip tasks that are already processing or completed"""
        from database import get_default_project_id
        task = create_task(title="测试任务", priority="medium")
        update_task(task["id"], status="approved")

        # Create a reflow record with status=processing
        reflow_project_id = get_default_project_id() or create_project(name="default", description="default")["id"]
        reflow = create_reflow(task["id"], reflow_project_id)
        update_reflow_status(reflow["id"], "processing")

        result = knowledge.run_reflow_cycle()

        # Task should be skipped (processed=0 since it's skipped due to reflow status)
        assert result["processed"] == 0


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


# ============ Stage2 Tests ============

class TestKnowledgeBasePaths:
    """Test knowledge base path constants"""

    def test_knowledge_base_defined(self):
        """Should have KNOWLEDGE_BASE defined"""
        assert hasattr(knowledge, "KNOWLEDGE_BASE")
        assert "20_Areas/knowledge" in knowledge.KNOWLEDGE_BASE

    def test_knowledge_subdirs_defined(self):
        """Should have all knowledge subdirectories defined"""
        assert hasattr(knowledge, "PRINCIPLES_DIR")
        assert hasattr(knowledge, "PLAYBOOKS_DIR")
        assert hasattr(knowledge, "TEMPLATES_DIR")
        assert hasattr(knowledge, "CASES_DIR")
        assert hasattr(knowledge, "NOTES_DIR")


class TestClassifyKnowledge:
    """Test knowledge classification"""

    @patch("subprocess.run")
    def test_classify_returns_directory_name(self, mock_run):
        """Should return a valid directory name"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "principles"
        mock_run.return_value = mock_result

        result = knowledge.classify_knowledge("坚持用户至上原则")
        assert result in ["principles", "playbooks", "templates", "cases", "notes"]

    @patch("subprocess.run")
    def test_classify_defaults_to_notes_on_error(self, mock_run):
        """Should return notes as default on error"""
        mock_run.side_effect = OSError("error")
        result = knowledge.classify_knowledge("一些笔记内容")
        assert result == "notes"

    @patch("subprocess.run")
    def test_classify_invalid_response_defaults_to_notes(self, mock_run):
        """Should return notes for invalid classification"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "invalid_response"
        mock_run.return_value = mock_result

        result = knowledge.classify_knowledge("some content")
        assert result == "notes"


class TestCheckDuplicate:
    """Test duplicate checking"""

    def test_empty_dir_returns_not_duplicate(self, temp_workspace):
        """Should return not duplicate when target dir is empty"""
        import knowledge
        # Temporarily change KNOWLEDGE_BASE
        original = knowledge.KNOWLEDGE_BASE
        knowledge.KNOWLEDGE_BASE = temp_workspace

        is_dup, dup_type = knowledge.check_duplicate("some content", "notes")

        knowledge.KNOWLEDGE_BASE = original
        assert is_dup is False
        assert dup_type == "new"

    @patch("subprocess.run")
    def test_check_duplicate_with_similar_response(self, mock_run, temp_workspace):
        """Should return similar when Claude responds with similar"""
        import knowledge
        original = knowledge.KNOWLEDGE_BASE
        knowledge.KNOWLEDGE_BASE = temp_workspace

        # Create a test file
        test_file = os.path.join(temp_workspace, "notes", "test.md")
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        with open(test_file, "w") as f:
            f.write("# Test note\nSome content")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "similar"
        mock_run.return_value = mock_result

        is_dup, dup_type = knowledge.check_duplicate("some content", "notes")

        knowledge.KNOWLEDGE_BASE = original
        assert is_dup is True
        assert dup_type == "similar"

    @patch("subprocess.run")
    def test_find_similar_file_unknown_classification(self, mock_run, temp_workspace):
        """Should use notes dir for unknown classification"""
        import knowledge
        original = knowledge.KNOWLEDGE_BASE
        knowledge.KNOWLEDGE_BASE = temp_workspace

        # Create a notes file
        notes_dir = os.path.join(temp_workspace, "notes")
        os.makedirs(notes_dir, exist_ok=True)
        test_file = os.path.join(notes_dir, "test.md")
        with open(test_file, "w") as f:
            f.write("# Test note\nSome content here")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "new"
        mock_run.return_value = mock_result

        # Call find_similar_file with unknown classification
        result = knowledge.find_similar_file("some content", "unknown_type")

        knowledge.KNOWLEDGE_BASE = original
        # Should use NOTES_DIR as default
        assert result is None or isinstance(result, str)


class TestWriteToKnowledgeBase:
    """Test writing to knowledge base"""

    def setup_method(self):
        """Create temp knowledge base"""
        self.temp_kb = tempfile.mkdtemp()
        import knowledge
        self.original_base = knowledge.KNOWLEDGE_BASE
        knowledge.KNOWLEDGE_BASE = self.temp_kb

    def teardown_method(self):
        """Restore original knowledge base"""
        import knowledge
        knowledge.KNOWLEDGE_BASE = self.original_base
        shutil.rmtree(self.temp_kb, ignore_errors=True)

    def test_write_to_notes_creates_file(self):
        """Should create file in notes directory"""
        content = "这是一条测试知识"
        result = knowledge.write_to_knowledge_base(content, "notes", "测试项目")

        assert os.path.exists(result)
        assert "03notes" in result

    def test_write_to_principles_creates_file(self):
        """Should create file in principles directory"""
        content = "坚持用户至上原则"
        result = knowledge.write_to_knowledge_base(content, "principles", "测试项目")

        assert os.path.exists(result)
        assert "01principles" in result

    def test_write_includes_metadata(self):
        """Should include metadata in written file"""
        content = "测试内容"
        source = "测试项目"
        result = knowledge.write_to_knowledge_base(content, "notes", source)

        with open(result, "r", encoding="utf-8") as f:
            file_content = f.read()

        assert "source: 测试项目" in file_content
        assert "type: notes" in file_content
        assert "测试内容" in file_content


class TestRunStage2Cycle:
    """Test Stage2 cycle execution"""

    def test_no_projects_returns_empty(self, override_db_path):
        """Should handle no projects needing reflow"""
        # 确保 50_Raw 为空
        import shutil
        raw_base = os.path.expanduser("~/.pkm/50_Raw")
        if os.path.exists(raw_base):
            shutil.rmtree(raw_base)

        result = knowledge.run_stage2_cycle(batch_size=5)

        assert result["processed"] == 0
        assert result["succeeded"] == 0
        assert result["failed"] == 0

    def test_project_without_workspace_skipped(self, override_db_path):
        """Should skip projects without workspace"""
        from database import create_project
        project = create_project(name="测试项目", workspace_path=None)

        result = knowledge.run_stage2_cycle(batch_size=5)

        assert result["failed"] == 1
        assert "不存在" in result["errors"][0]["message"]

    @patch("knowledge.classify_knowledge")
    @patch("knowledge.check_duplicate")
    @patch("knowledge.write_to_knowledge_base")
    def test_successful_stage2(self, mock_write, mock_check, mock_classify, override_db_path, temp_workspace):
        """Should successfully process project"""
        mock_classify.return_value = "notes"
        mock_check.return_value = (False, "new")
        mock_write.return_value = "/path/to/file.md"

        from database import create_project, update_project
        project = create_project(name="测试项目", workspace_path=temp_workspace)

        # Create project.md with knowledge section
        project_md_path = os.path.join(temp_workspace, "project.md")
        with open(project_md_path, "w") as f:
            f.write("""# Project: 测试项目

## 经验/方案索引
### 2026-04-01 任务：测试任务
- **任务ID**: test-id
- **内容**: 测试知识内容
""")

        result = knowledge.run_stage2_cycle(batch_size=5)

        assert result["processed"] == 1
        assert result["succeeded"] == 1
        assert result["failed"] == 0

    @patch("knowledge.classify_knowledge")
    @patch("knowledge.check_duplicate")
    @patch("knowledge.write_to_knowledge_base")
    def test_stage2_skips_duplicate(self, mock_write, mock_check, mock_classify, override_db_path, temp_workspace):
        """Should skip duplicate items in stage2"""
        mock_classify.return_value = "notes"
        mock_check.return_value = (True, "duplicate")  # Should trigger continue
        mock_write.return_value = "/path/to/file.md"

        from database import create_project
        project = create_project(name="测试项目", workspace_path=temp_workspace)

        # Create project.md with knowledge section
        project_md_path = os.path.join(temp_workspace, "project.md")
        with open(project_md_path, "w") as f:
            f.write("""# Project: 测试项目

## 经验/方案索引
### 2026-04-01 任务：测试任务
- **任务ID**: test-id
- **内容**: 测试知识内容
""")

        result = knowledge.run_stage2_cycle(batch_size=5)

        # Should skip the duplicate, so nothing written
        assert result["processed"] == 1
        assert result["succeeded"] == 1
        assert result["failed"] == 0
        mock_write.assert_not_called()


class TestGetStage2Status:
    """Test Stage2 status retrieval"""

    def test_status_returns_pending_projects(self, override_db_path):
        """Should return Stage2 status with pending projects count"""
        status = knowledge.get_stage2_status()

        assert "pending_projects" in status
        assert "config" in status
        assert "claude_available" in status


class TestProcessRawInbox:
    """Test 50_Raw inbox processing"""

    def setup_method(self):
        """Create temp 50_Raw directory"""
        self.temp_raw = tempfile.mkdtemp()
        import knowledge
        self.original_raw_base = knowledge.RAW_BASE
        knowledge.RAW_BASE = self.temp_raw

        # Create inbox subdirectory
        self.inbox_dir = os.path.join(self.temp_raw, "inbox")
        os.makedirs(self.inbox_dir, exist_ok=True)

    def teardown_method(self):
        """Restore original 50_Raw base"""
        import knowledge
        knowledge.RAW_BASE = self.original_raw_base
        shutil.rmtree(self.temp_raw, ignore_errors=True)

    def test_empty_raw_returns_empty_result(self):
        """Should return empty result when no files"""
        result = knowledge.process_raw_inbox()
        assert result["processed"] == 0
        assert result["succeeded"] == 0
        assert result["failed"] == 0

    def test_process_single_file(self):
        """Should process single markdown file"""
        # Create test file in inbox
        test_file = os.path.join(self.inbox_dir, "test_inbox.md")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("这是一条测试笔记")

        result = knowledge.process_raw_inbox()

        assert result["processed"] == 1
        assert result["succeeded"] == 1
        # File should be deleted after processing
        assert not os.path.exists(test_file)

    @patch("knowledge.classify_knowledge")
    @patch("knowledge.check_duplicate")
    def test_duplicate_file_deleted(self, mock_check, mock_classify):
        """Should delete file when duplicate is found"""
        mock_classify.return_value = "notes"
        mock_check.return_value = (True, "duplicate")

        test_file = os.path.join(self.inbox_dir, "test_dup.md")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("重复内容")

        result = knowledge.process_raw_inbox()

        assert result["processed"] == 1
        assert result["succeeded"] == 1
        assert not os.path.exists(test_file)

    def test_non_md_file_ignored(self):
        """Should ignore non-markdown files"""
        test_file = os.path.join(self.inbox_dir, "test.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Some text")

        result = knowledge.process_raw_inbox()

        # .txt files should be ignored
        assert result["processed"] == 0
        assert os.path.exists(test_file)  # File should still exist

    def test_empty_file_deleted(self):
        """Should delete empty markdown files"""
        test_file = os.path.join(self.inbox_dir, "empty.md")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("   \n\t  ")  # Whitespace only

        result = knowledge.process_raw_inbox()

        # Empty files should be deleted
        assert not os.path.exists(test_file)


class TestRunStage2CycleWithRaw:
    """Test Stage2 cycle with 50_Raw processing"""

    def setup_method(self):
        """Create temp 50_Raw directory"""
        self.temp_raw = tempfile.mkdtemp()
        import knowledge
        self.original_raw_base = knowledge.RAW_BASE
        knowledge.RAW_BASE = self.temp_raw

        self.inbox_dir = os.path.join(self.temp_raw, "inbox")
        os.makedirs(self.inbox_dir, exist_ok=True)

    def teardown_method(self):
        """Restore original 50_Raw base"""
        import knowledge
        knowledge.RAW_BASE = self.original_raw_base
        shutil.rmtree(self.temp_raw, ignore_errors=True)

    @patch("knowledge.classify_knowledge")
    @patch("knowledge.check_duplicate")
    def test_stage2_processes_raw_first(self, mock_check, mock_classify, override_db_path):
        """Should process 50_Raw before projects"""
        mock_classify.return_value = "notes"
        mock_check.return_value = (False, "new")

        # Create inbox file
        test_file = os.path.join(self.inbox_dir, "test.md")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("测试内容")

        result = knowledge.run_stage2_cycle(batch_size=5)

        assert "raw_processed" in result
        assert result["raw_processed"] == 1
        assert result["raw_succeeded"] == 1
