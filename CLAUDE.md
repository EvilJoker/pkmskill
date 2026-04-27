# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述
PKM (Personal Knowledge Management) - 任务和项目管理服务，基于 FastAPI + SQLite + Click CLI

## 常用命令
```bash
# 安装依赖
make install

# 构建 wheel 包
make build-client

# 构建 Docker 镜像
make build-server

# 启动服务（生产环境，使用 snapshot 镜像）
make start

# 启动开发环境（本地构建，容器内执行 CLI）
make start-dev

# 查看日志
make logs

# 运行测试
make test

# 运行部署测试（CI 使用， 本地不使用）
make test-deploy
```

## 容器操作规则（重要）
**禁止直接使用 docker compose 命令，必须使用 make 命令！**

| 环境 | 命令 | 用途 |
|------|------|------|
| 生产环境 | `make start` | 部署真实环境，拉取 snapshot 镜像 |
| 开发环境 | `make start-dev` | 日常开发调试，本地构建镜像 |

**禁止的操作：**
- ❌ `docker compose up/down/restart` — 必须用 `make start/start-dev`
- ❌ `docker compose -f docker-compose.yml ...` — 必须用 `make start`
- ❌ `docker compose -f docker-compose.dev.yml ...` — 必须用 `make start-dev`
- ❌ 直接在宿主机执行 pkm CLI — CLI 在容器内执行

## 测试注意事项
**重要：不要删除用户的实际数据！**
- 本地测试使用 `make test`（使用 docker-compose.dev.yml）
- **禁止执行** `docker exec pkm-server rm -f /root/.pkm/pkm.db` — 这会删除用户实际数据
- 测试运行在容器内，使用的是容器内的数据库，不是本地测试数据库
- 代码修改后需要重建镜像再测试：`make build-server && make start-dev`

## 代码质量要求
- **行覆盖率**: 75% 以上
- **分支覆盖率**: 55% 以上（当前可达值）

## CI/CD 流程

### Workflows
- **snapshot.yml**: 构建 + 测试 + 发布制品（push main 时触发）
- **deploy.yml**: 部署验证（push main 时触发，下载安装最新发布版本）
- **base-image.yml**: 构建基础镜像（push base-image 分支时触发）

### 流程约束
**每次推送到远端后，必须检查 CI 执行结果，如果失败需要修复：**
- 检查 `Snapshot CI` workflow：构建、测试、发布是否成功
- 检查 `Deploy Test` workflow：部署安装是否成功
- 任一 workflow 失败都需要定位并修复问题后再次推送

### 基础镜像构建
**重要：基础镜像（ghcr.io/eviljoker/pkm:base-latest）在 GitHub Actions 远端构建，本地不要尝试构建。**

如果修改了 `requirements.txt` 或 `Dockerfile.base`：
1. 推送代码后，远端会自动触发 `base-image.yml` workflow
2. 构建完成后会推送新镜像到 ghcr.io
3. 等待基础镜像构建完成后，再触发业务镜像构建

### 本地开发
**开发环境使用 pkm-server目录下 `make start-dev`（本地构建镜像，CLI在容器内执行）：**
```bash
make start-dev  # 本地构建 + 启动
make status-dev     # 检查服务状态
make logs-dev      # 查看日志
make clean-dev      # 清理容器
```

**生产环境使用 `make start`（拉取 snapshot 镜像）：**
```bash
make start      # 使用 snapshot 镜像启动
```

**本地开发流程：**
1. 修改代码
2. `make start-dev` 重新构建并启动
3. `make status` 验证服务状态
4. 测试完成后 `make clean` 清理

## 架构
- `main.py` - FastAPI 应用，定义所有 REST API 端点
- `database.py` - SQLite 数据库操作层
- `models.py` - Pydantic 数据模型
- `knowledge.py` - 知识回流核心逻辑，支持 Wiki 增量更新
- `pkm/cli.py` - Click CLI 命令行接口
- `pkm/config.py` - 配置文件加载模块

## 目录结构
```
~/.pkm/
├── 10_Tasks/           # 任务层
├── 20_Projects/        # 项目层（Raw Sources）
├── 30_Raw/            # Raw 层
├── 40_Knowledge/      # Wiki 层
│   ├── _wiki/         # LLM 维护的概念页面
│   │   ├── index.md   # 总导航
│   │   ├── index.yaml # 结构化索引
│   │   └── {topic}/   # 按主题分类
│   └── _schema/       # Wiki 维护规则
└── 80_Archives/      # 归档层
```

## 配置
- 默认配置路径: `~/.pkm/config.yaml`
- 环境变量: `PKM_API_BASE` 可覆盖 API 地址（容器内测试时设为 `http://localhost:8890`）
- 知识库路径: `~/.pkm/40_Knowledge`（Wiki 格式）

## 文档
- 文档位置都在 `docs`, 禁止放在 `pkm-server/docs`

## 开发经验总结

**本项目成功的关键因素：**

1. **Demo 优先**：先搭起最小可运行 demo 验证可行性，再完善细节
2. **自动化测试反馈**：make test-local + CI 确保每次改动都被验证
3. **TDD 先写测试**：用测试驱动实现，减少返工
4. **小步快走**：每次迭代控制在较小改动，快速交付价值

**适用场景**：个人工具类项目、快速原型验证
