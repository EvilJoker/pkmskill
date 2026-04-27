import os
import tempfile
import pytest
from pkm.workspace import (
    create_task_workspace,
    create_project_workspace,
    get_workspace_base_path,
    get_default_project_workspace,
    archive_task_workspace,
    create_default_project_workspace,
    generate_task_workspace_name,
    get_raw_base,
    get_inbox_base,
)

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

def test_get_default_project_workspace_creates_if_not_exists():
    """测试获取 default 项目工作区（当不存在时创建）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 设置临时工作区基础目录
        from pkm.workspace import get_project_workspace_base
        original_base = get_project_workspace_base()
        os.environ["PKM_WORKSPACE_BASE"] = tmpdir

        try:
            # 第一次调用应该创建
            workspace1 = get_default_project_workspace()
            assert os.path.exists(workspace1)
            assert "P_default" in workspace1

            # 第二次调用应该返回已存在的
            workspace2 = get_default_project_workspace()
            assert workspace1 == workspace2
        finally:
            if "PKM_WORKSPACE_BASE" in os.environ:
                del os.environ["PKM_WORKSPACE_BASE"]

def test_archive_task_workspace_nonexistent():
    """测试归档不存在的任务工作区"""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = archive_task_workspace(os.path.join(tmpdir, "nonexistent"))
        assert result is None

def test_archive_task_workspace_already_exists():
    """测试归档时目标已存在的分支（添加时间戳）"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建源工作区
        source = os.path.join(tmpdir, "T_task1")
        os.makedirs(source)
        with open(os.path.join(source, "task.md"), "w") as f:
            f.write("# Task")

        # 预创建归档目录和同名文件，模拟已存在的情况
        from pkm.workspace import get_archive_base
        archive_dir = get_archive_base()
        os.makedirs(archive_dir, exist_ok=True)
        # 创建一个文件而非目录来模拟 exists check
        existing = os.path.join(archive_dir, "T_task1")
        with open(existing, "w") as f:
            f.write("# Already exists")

        # 归档
        result = archive_task_workspace(source)
        # 因为目标是文件不是目录，所以会走到创建带时间戳的路径分支
        assert result is not None
        assert "T_task1_" in result


def test_archive_task_workspace_target_not_exists(monkeypatch):
    """测试归档时目标不存在的分支（不添加时间戳）"""
    import tempfile
    import os
    from pkm.workspace import archive_task_workspace, get_archive_base

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建源工作区
        source = os.path.join(tmpdir, "T_task2")
        os.makedirs(source)
        with open(os.path.join(source, "task.md"), "w") as f:
            f.write("# Task")

        # 临时修改归档目录
        archive_dir = os.path.join(tmpdir, "archive")
        os.makedirs(archive_dir, exist_ok=True)
        monkeypatch.setattr("pkm.workspace.get_archive_base", lambda: archive_dir)

        # 归档（目标不存在，不应添加时间戳）
        result = archive_task_workspace(source)
        assert result is not None
        assert not result.endswith("_") or "T_task2_" not in result
        # 目标路径应该直接是 archive_dir/T_task2
        assert result == os.path.join(archive_dir, "T_task2")

def test_create_default_project_workspace_with_existing():
    """测试当默认项目已存在时的分支"""
    with tempfile.TemporaryDirectory() as tmpdir:
        from pkm.workspace import get_project_workspace_base
        original_base = get_project_workspace_base()
        os.environ["PKM_WORKSPACE_BASE"] = tmpdir

        try:
            # 创建默认项目
            ws1 = create_default_project_workspace()
            assert os.path.exists(ws1)

            # 再次创建应该返回已存在的
            ws2 = create_default_project_workspace()
            assert ws1 == ws2
        finally:
            if "PKM_WORKSPACE_BASE" in os.environ:
                del os.environ["PKM_WORKSPACE_BASE"]


def test_generate_task_workspace_name_with_name():
    """测试生成任务工作区名称（带名称）"""
    name = generate_task_workspace_name("测试任务名称较长的情况")
    assert "TASK_T" in name
    assert "测试任务名称较长" in name


def test_generate_task_workspace_name_without_name():
    """测试生成任务工作区名称（不带名称）"""
    name = generate_task_workspace_name("")
    assert "TASK_T" in name
    assert "task" in name


def test_get_raw_base():
    """测试获取 30_Raw 目录"""
    base = get_raw_base()
    assert "30_Raw" in base
    assert os.path.exists(base)


def test_get_inbox_base():
    """测试获取 inbox 目录"""
    base = get_inbox_base()
    assert "inbox" in base.lower() or "Inbox" in base
    assert os.path.exists(base)
