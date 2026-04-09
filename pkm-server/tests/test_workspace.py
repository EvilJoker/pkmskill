import os
import tempfile
import pytest
from workspace import create_task_workspace, create_project_workspace, get_workspace_base_path

def test_get_workspace_base_path():
    """测试获取工作区根目录"""
    base = get_workspace_base_path()
    assert "10_Tasks" in base or base.endswith(".pkm")

def test_create_task_workspace():
    """测试创建任务工作区"""
    with tempfile.TemporaryDirectory() as tmpdir:
        task_id = "TASK_T20260409_01"
        title = "测试任务"
        workspace_path = create_task_workspace(
            task_id=task_id,
            title=title,
            base_dir=tmpdir
        )
        assert os.path.exists(workspace_path)
        assert os.path.exists(os.path.join(workspace_path, "task.md"))
        with open(os.path.join(workspace_path, "task.md")) as f:
            content = f.read()
            assert "测试任务" in content
            assert "TASK_T20260409_01" in content
            assert "AI 使用指南" in content

def test_create_project_workspace():
    """测试创建项目工作区"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_id = "P_20260409_项目A"
        name = "项目A"
        workspace_path = create_project_workspace(
            project_id=project_id,
            name=name,
            base_dir=tmpdir
        )
        assert os.path.exists(workspace_path)
        assert os.path.exists(os.path.join(workspace_path, "project.md"))
        with open(os.path.join(workspace_path, "project.md")) as f:
            content = f.read()
            assert "项目A" in content
            assert "AI 使用指南" in content
