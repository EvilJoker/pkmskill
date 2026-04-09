# make test 命令实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 添加 `make test` 命令，在 Docker 容器内运行测试并生成覆盖率报告

**Architecture:** 修改 Dockerfile 添加 pytest-cov 依赖，修改 Makefile 添加 test 命令，修改 .gitignore 忽略 coverage 目录

**Tech Stack:** Docker, docker-compose, pytest, pytest-cov, coverage

---

## 文件结构

```
pkm-server/
├── Dockerfile         # 修改: 添加 pytest-cov 依赖
├── Makefile          # 修改: 添加 test 命令
├── .gitignore        # 修改: 添加 coverage 忽略
└── requirements.txt   # 无需修改 (pytest-cov 可通过 pip 安装)
```

---

## Task 1: 修改 Dockerfile 添加 pytest-cov

**Files:**
- Modify: `pkm-server/Dockerfile`

- [ ] **Step 1: 修改 Dockerfile**

将：
```dockerfile
RUN pip install --quiet --no-cache-dir fastapi==0.109.2 uvicorn==0.27.1 pydantic==2.6.1 click==8.1.7 requests==2.31.0 pytest==8.0.0 PyYAML==6.0.1
```

改为：
```dockerfile
RUN pip install --quiet --no-cache-dir \
    fastapi==0.109.2 \
    uvicorn==0.27.1 \
    pydantic==2.6.1 \
    click==8.1.7 \
    requests==2.31.0 \
    pytest==8.0.0 \
    pytest-cov==4.1.0 \
    PyYAML==6.0.1
```

- [ ] **Step 2: 验证构建**

```bash
docker-compose build pkm-server
```

- [ ] **Step 3: 提交**

```bash
git add pkm-server/Dockerfile
git commit -m "feat: Dockerfile 添加 pytest-cov 依赖"
```

---

## Task 2: 修改 Makefile 添加 test 命令

**Files:**
- Modify: `pkm-server/Makefile`

- [ ] **Step 1: 修改 Makefile**

在 `.PHONY` 中添加 `test`：

```makefile
.PHONY: install build start stop logs ps clean test
```

在文件末尾添加 `test` 命令：

```makefile
test:
	docker-compose run --rm pkm-server \
		coverage run -m pytest tests/ -v
	coverage report --show-missing
	coverage html -d coverage
```

- [ ] **Step 2: 验证**

```bash
make test
```

预期输出：测试运行并显示覆盖率报告

- [ ] **Step 3: 提交**

```bash
git add pkm-server/Makefile
git commit -m "feat: Makefile 添加 make test 命令"
```

---

## Task 3: 修改 .gitignore 添加 coverage

**Files:**
- Modify: `pkm-server/.gitignore`

- [ ] **Step 1: 修改 .gitignore**

添加：
```
coverage/
.coverage
```

- [ ] **Step 2: 验证 coverage 目录被忽略**

```bash
echo "coverage/" > /tmp/test && mv /tmp/test coverage/
git status  # 应该不显示 coverage/
```

- [ ] **Step 3: 提交**

```bash
git add pkm-server/.gitignore
git commit -m "chore: .gitignore 添加 coverage 目录"
```

---

## Task 4: 运行 make test 验证

- [ ] **Step 1: 清理旧数据库**

```bash
docker exec pkm-server rm -f /root/.pkm/pkm.db
```

- [ ] **Step 2: 运行测试**

```bash
make test
```

预期：
- 所有测试通过
- 分支覆盖率 ≥75%
- 行覆盖率 ≥65%

---

## 实施顺序

1. Task 1: 修改 Dockerfile
2. Task 2: 修改 Makefile
3. Task 3: 修改 .gitignore
4. Task 4: 运行 make test 验证

---

## 自检清单

- [ ] Dockerfile 包含 pytest-cov
- [ ] `make test` 命令存在
- [ ] coverage 目录被 .gitignore 忽略
- [ ] 所有测试通过
- [ ] 分支覆盖率 ≥75%
- [ ] 行覆盖率 ≥65%
