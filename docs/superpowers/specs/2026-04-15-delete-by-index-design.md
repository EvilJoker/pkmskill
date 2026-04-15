# Design: 支持序号删除 Task 和 Project

## 概述

为 `pkm task delete` 和 `pkm project delete` 增加序号支持，并实现 workspace 物理清理。

## 1. Task Delete

**CLI**: `pkm task delete <序号>`

### 实现步骤

1. 调用 `GET /api/tasks` 获取所有 tasks
2. 根据序号找到对应的 task_id 和 workspace_path
3. 调用 `DELETE /api/tasks/{task_id}` 删除数据
4. 调用 `shutil.rmtree(workspace_path)` 删除 workspace 目录

### 数据流

```
用户输入序号 → API获取task → 获取workspace_path → 删除DB记录 → 删除workspace目录
```

## 2. Project Delete

**CLI**: `pkm project delete <序号>`

### 限制

- `default` 项目不允许删除（序号显示为 `[default]`）

### 实现步骤

1. 调用 `GET /api/projects` 获取所有 projects
2. 检查是否为 default 项目 → 拒绝删除
3. 根据序号找到对应的 project_id 和 workspace_path
4. 获取所有关联的 tasks，将它们的 `project_id` 设为 default 项目
5. 调用 `DELETE /api/projects/{project_id}` 删除数据
6. 调用 `shutil.rmtree(workspace_path)` 删除 workspace 目录

### 数据流

```
用户输入序号 → 检查default → API获取project → 迁移关联tasks到default → 删除DB记录 → 删除workspace目录
```

## 3. Task Create 默认值

**CLI**: `pkm task add <title> [--priority h|m|l]`

- 如果未指定 `--project`，自动关联到 `default` 项目

### 实现步骤

1. 调用 `GET /api/projects` 获取所有 projects
2. 找到 default 项目
3. 创建 task 时设置 `project_id` 为 default 项目的 id

## 4. API 变更

### DELETE /api/projects/{project_id}

**新增 endpoint**

- 获取所有关联的 tasks，将 `project_id` 设为 null（或 default 项目 id）
- 从 projects 表删除记录
- 从文件系统删除 project workspace 目录

**Response**: `{"message": "deleted", "workspace_path": "/path/to/workspace", "migrated_tasks": 3}`

### PATCH /api/tasks/{task_id}

**现有 endpoint 扩展**

- 支持 `project_id` 字段更新

## 5. CLI 代码变更

### pkm/cli.py

#### task delete

```python
@task.command()
@click.argument("task_id")  # 支持 UUID 或 序号
def delete(task_id):
    """Delete a task by ID or index

    Examples:
      pkm task delete 3e3705f1
      pkm task delete 1"""
    if task_id.isdigit():
        idx = int(task_id)
        r = requests.get(f"{API_BASE}/api/tasks")
        tasks = r.json()
        if idx < 1 or idx > len(tasks):
            click.echo(f"Invalid index: {idx}")
            return
        task = tasks[idx - 1]
        task_id = task["id"]
        workspace_path = task.get("workspace_path")

        r = requests.delete(f"{API_BASE}/api/tasks/{task_id}")
        r.raise_for_status()

        if workspace_path and os.path.exists(workspace_path):
            shutil.rmtree(workspace_path)

        click.echo("Task deleted")
    else:
        # 原有的UUID逻辑...
```

#### task add (新增 default project 关联)

```python
@task.command()
@click.argument("title")
@click.option("--priority", "-p", type=click.Choice(["h", "m", "l"]), default="m")
@click.option("--due")
@click.option("--project")
def add(title, priority, due, project):
    """Add a new task

    Examples:
      pkm task add "新任务" --priority h
      pkm task add "新任务" --project my-project"""
    # 获取 default 项目
    if not project:
        r = requests.get(f"{API_BASE}/api/projects")
        projects = r.json()
        for p in projects:
            if p["name"].lower() == "default":
                project = p["id"]
                break

    payload = {"title": title, "priority": priority}
    if project:
        payload["project_id"] = project
    # ...
```

#### project delete (新增)

```python
@project.command()
@click.argument("project_id")  # 支持 UUID 或 序号
def delete(project_id):
    """Delete a project by ID or index

    Examples:
      pkm project delete ccec0f66
      pkm project delete 2"""
    if project_id.isdigit():
        idx = int(project_id)
        r = requests.get(f"{API_BASE}/api/projects")
        projects = r.json()
        if idx < 1 or idx > len(projects):
            click.echo(f"Invalid index: {idx}")
            return
        project = projects[idx - 1]
        project_id = project["id"]

        # 检查是否为 default
        if project["name"].lower() == "default":
            click.echo("Cannot delete default project")
            return
    else:
        # UUID逻辑，检查是否为 default...

    workspace_path = project.get("workspace_path")

    # 调用 API 删除（API 内部迁移 tasks）
    r = requests.delete(f"{API_BASE}/api/projects/{project_id}")
    r.raise_for_status()

    # 删除 workspace
    if workspace_path and os.path.exists(workspace_path):
        shutil.rmtree(workspace_path)

    click.echo("Project deleted")
```

## 6. 测试用例

```python
class TestCLITaskDelete:
    def test_task_delete_by_index(self, runner, wait_for_server):
        """Should delete task by index number"""
        result = runner.invoke(task, ["add", "测试删除序号"], catch_exceptions=False)
        result = runner.invoke(task, ["ls"], catch_exceptions=False)
        result = runner.invoke(task, ["delete", "1"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Task deleted" in result.output

class TestCLIProjectDelete:
    def test_project_delete_by_index(self, runner, wait_for_server):
        """Should delete project and migrate tasks to default"""
        # 创建project和关联task
        runner.invoke(project, ["add", "测试删除项目"], catch_exceptions=False)
        result = runner.invoke(task, ["add", "关联任务", "--project", "测试删除项目"], catch_exceptions=False)
        # 用序号删除project
        result = runner.invoke(project, ["delete", "2"], catch_exceptions=False)
        assert result.exit_code == 0
        # 验证task关联到default
        result = runner.invoke(task, ["get", "<task_id>"], catch_exceptions=False)
        # ...

    def test_project_delete_default_forbidden(self, runner, wait_for_server):
        """Should not allow deleting default project"""
        result = runner.invoke(project, ["delete", "1"], catch_exceptions=False)
        assert result.exit_code != 0

class TestCLITaskCreate:
    def test_task_add_without_project(self, runner, wait_for_server):
        """Should default to default project"""
        result = runner.invoke(task, ["add", "无指定项目"], catch_exceptions=False)
        assert result.exit_code == 0
        # 验证关联到 default 项目
```

## 7. 错误处理

- 序号超出范围 → 提示 "Invalid index: X"
- 删除不存在的 workspace → 跳过，仅删除 DB 记录
- 删除 default 项目 → 拒绝并提示 "Cannot delete default project"
- 无 default 项目时创建 task → 报错提示
