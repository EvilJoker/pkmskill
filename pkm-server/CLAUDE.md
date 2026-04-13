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

# 启动服务
make start

# 查看日志
make logs

# 运行测试（CI 使用，包含覆盖率检查）
make test

# 本地测试（包含覆盖率验证和 docker compose down）
make test-local

# 本地部署测试
make test-deploy

# 删除所有测试数据重新测试
docker exec pkm-server rm -f /root/.pkm/pkm.db
```

## 代码质量要求
- **行覆盖率**: 75% 以上
- **分支覆盖率**: 55% 以上（当前可达值）

## CI/CD 流程

### Workflows
- **snapshot.yml**: 构建 + 测试 + 发布制品（push main 时触发）
- **deploy.yml**: 部署验证（push main 时触发，下载安装最新发布版本）

### 流程约束
**每次推送到远端后，必须检查 CI 执行结果，如果失败需要修复：**
- 检查 `Snapshot CI` workflow：构建、测试、发布是否成功
- 检查 `Deploy Test` workflow：部署安装是否成功
- 任一 workflow 失败都需要定位并修复问题后再次推送

## 架构
- `main.py` - FastAPI 应用，定义所有 REST API 端点
- `database.py` - SQLite 数据库操作层
- `models.py` - Pydantic 数据模型
- `pkm/cli.py` - Click CLI 命令行接口
- `pkm/config.py` - 配置文件加载模块

## 配置
- 默认配置路径: `~/.pkm/config.yaml`
- 环境变量: `PKM_API_BASE` 可覆盖 API 地址（容器内测试时设为 `http://localhost:7890`）
