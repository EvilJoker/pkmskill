"""Knowledge reflow tests for PKM"""

import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path
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



class TestChangeSetDataclass:
    """Test ChangeSet and FileIndex dataclasses"""

    def test_changeset_empty_init(self):
        """Should create empty changeset"""
        from knowledge import ChangeSet, FileIndex
        cs = ChangeSet()
        assert cs.added == []
        assert cs.modified == []
        assert cs.deleted == []

    def test_file_index_load_save(self, temp_workspace):
        """Should load and save file index"""
        import knowledge
        from knowledge import FileIndex

        original_base = knowledge.KNOWLEDGE_BASE
        knowledge.KNOWLEDGE_BASE = temp_workspace

        fi = FileIndex()
        fi.files["test/file.md"] = knowledge.FileEntry("abc123", "2026-04-22T10:00:00Z")
        fi.save()

        fi2 = FileIndex()
        fi2.load()
        assert "test/file.md" in fi2.files
        assert fi2.files["test/file.md"].md5 == "abc123"

        knowledge.KNOWLEDGE_BASE = original_base


class TestScanProjects:
    """Test two-pass scan_projects function"""

    def test_scan_projects_empty_dir(self):
        """Should handle empty projects directory"""
        import knowledge
        from knowledge import ChangeSet

        original_base = knowledge.PROJECTS_BASE
        knowledge.PROJECTS_BASE = "/tmp/non_existent_projects_xyz"

        cs = knowledge.scan_projects()

        assert isinstance(cs, ChangeSet)
        assert len(cs.added) == 0
        assert len(cs.modified) == 0

        knowledge.PROJECTS_BASE = original_base

    def test_scan_projects_detects_new_file(self, temp_workspace):
        """Should detect newly added files"""
        import knowledge
        from knowledge import ChangeSet

        original_projects = knowledge.PROJECTS_BASE
        original_knowledge = knowledge.KNOWLEDGE_BASE
        knowledge.PROJECTS_BASE = temp_workspace
        knowledge.KNOWLEDGE_BASE = temp_workspace

        project_dir = os.path.join(temp_workspace, "test_project")
        os.makedirs(project_dir, exist_ok=True)
        test_file = os.path.join(project_dir, "notes.md")
        with open(test_file, "w") as f:
            f.write("# Test notes")

        cs = knowledge.scan_projects()

        assert len(cs.added) == 1
        assert str(cs.added[0]).endswith("notes.md")

        knowledge.PROJECTS_BASE = original_projects
        knowledge.KNOWLEDGE_BASE = original_knowledge


class TestAnalyzeAndMerge:
    """Test analyze_and_merge function"""

    @patch("subprocess.run")
    def test_analyze_returns_action(self, mock_run):
        """Should return action result"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "action: skip\n"
        mock_run.return_value = mock_result

        result = knowledge.analyze_and_merge(Path("/tmp/test.md"), "test_project")
        assert "action" in result
        assert result["action"] in ["create", "update", "skip", "discard", "error", "unknown"]

    @patch("subprocess.run")
    def test_empty_file_returns_skip(self, mock_run, temp_workspace):
        """Should skip empty files"""
        test_file = os.path.join(temp_workspace, "empty.md")
        with open(test_file, "w") as f:
            f.write("   \n\t  ")

        result = knowledge.analyze_and_merge(Path(test_file), "test_project")
        assert result["action"] == "skip"


class TestUpdateIndex:
    """Test update_index function"""

    def test_update_index_creates_file(self, temp_workspace):
        """Should create index.md and index.yaml"""
        import knowledge

        original_knowledge = knowledge.KNOWLEDGE_BASE
        original_wiki_dir = knowledge.WIKI_DIR
        original_index_path = knowledge.INDEX_PATH
        original_index_yaml = knowledge.INDEX_YAML_PATH
        knowledge.KNOWLEDGE_BASE = temp_workspace
        wiki_dir = os.path.join(temp_workspace, "_wiki")
        knowledge.WIKI_DIR = wiki_dir
        knowledge.INDEX_PATH = os.path.join(wiki_dir, "index.md")
        knowledge.INDEX_YAML_PATH = os.path.join(wiki_dir, "index.yaml")

        # Create new-style wiki entry with frontmatter
        topic_dir = os.path.join(wiki_dir, "AI")
        os.makedirs(topic_dir, exist_ok=True)
        with open(os.path.join(topic_dir, "AI基础.md"), "w") as f:
            f.write("""---
title: AI基础
type: concept
sources: [test_project/notes.md]
related: [AI工具]
created: 2026-04-27
updated: 2026-04-27
---

# AI基础

## 核心概念
- 机器学习是...

## 相关
- [[AI工具]]
""")

        knowledge.update_index()

        index_path = os.path.join(wiki_dir, "index.md")
        assert os.path.exists(index_path), f"index.md not found at {index_path}"

        with open(index_path, "r") as f:
            content = f.read()
        assert "Knowledge Index" in content
        assert "AI基础" in content

        yaml_path = os.path.join(wiki_dir, "index.yaml")
        assert os.path.exists(yaml_path), f"index.yaml not found at {yaml_path}"

        with open(yaml_path, "r") as f:
            yaml_content = f.read()
        assert "AI基础" in yaml_content

        knowledge.KNOWLEDGE_BASE = original_knowledge
        knowledge.WIKI_DIR = original_wiki_dir
        knowledge.INDEX_PATH = original_index_path
        knowledge.INDEX_YAML_PATH = original_index_yaml


class TestRunReflowCycle:
    """Test run_reflow_cycle function"""

    @patch("knowledge.scan_projects")
    @patch("knowledge.analyze_and_merge")
    @patch("knowledge.update_index")
    def test_reflow_processes_changes(self, mock_update, mock_analyze, mock_scan):
        """Should process changeset"""
        from knowledge import ChangeSet

        mock_scan.return_value = ChangeSet()
        mock_analyze.return_value = {"action": "skip", "file": "/tmp/test.md"}

        result = knowledge.run_reflow_cycle()

        assert "processed" in result
        assert "succeeded" in result
        assert "failed" in result
