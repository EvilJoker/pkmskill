# make test 命令设计方案

## 1. 目标

在 `pkm-server` 目录下提供 `make test` 命令，复用容器镜像运行完整测试，包括覆盖率生成，避免本地环境问题。

## 2. 修改文件

### 2.1 Dockerfile

添加 `pytest-cov` 依赖：

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --quiet --no-cache-dir \
    fastapi==0.109.2 \
    uvicorn==0.27.1 \
    pydantic==2.6.1 \
    click==8.1.7 \
    requests==2.31.0 \
    pytest==8.0.0 \
    pytest-cov==4.1.0 \
    PyYAML==6.0.1
COPY . .
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7890", "--loop", "asyncio"]
```

### 2.2 Makefile

添加 `test` 命令：

```makefile
.PHONY: install build start stop logs ps clean test

test:
	docker-compose run --rm pkm-server \
		coverage run -m pytest tests/ -v
	coverage report --show-missing
	coverage html -d coverage
```

### 2.3 .gitignore

添加 coverage 相关：

```
coverage/
.coverage
```

## 3. 工作流程

```bash
make test
```

执行步骤：
1. `docker-compose run --rm pkm-server` - 复用已有镜像或自动构建
2. `coverage run -m pytest tests/ -v` - 运行所有测试并收集覆盖率
3. `coverage report --show-missing` - 终端显示覆盖率报告
4. `coverage html -d coverage` - 生成 HTML 报告到 `pkm-server/coverage/`

## 4. 覆盖率目标

| 指标 | 目标 |
|-----|------|
| 分支覆盖率 | ≥75% |
| 行覆盖率 | ≥65% |

## 5. 注意事项

- 使用 `docker-compose run --rm` 而非 `up` 是为了测试完成后自动清理容器
- coverage 目录输出到宿主机 `pkm-server/coverage/`
- .gitignore 忽略 coverage 目录，避免提交到 git
