# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述
PKM (Personal Knowledge Management) - 任务和项目管理服务，基于 FastAPI + SQLite + Click CLI

## 常用命令
```bash
# 安装依赖
make install

# 构建 Docker 镜像
make build

# 启动服务
make start

# 查看日志
make logs

# 运行测试（带覆盖率）
pytest tests/ --cov=. --cov-report=term-missing --cov-branch

# 删除所有测试数据重新测试
docker exec pkm-server rm -f /root/.pkm/pkm.db
```

## 代码质量要求
- **分支覆盖率**: 75% 以上
- **行覆盖率**: 65% 以上

## 架构
- `main.py` - FastAPI 应用，定义所有 REST API 端点
- `database.py` - SQLite 数据库操作层
- `models.py` - Pydantic 数据模型
- `pkm/cli.py` - Click CLI 命令行接口
- `pkm/config.py` - 配置文件加载模块

## 配置
- 默认配置路径: `~/.pkm/config.yaml`
- 环境变量: `PKM_API_BASE` 可覆盖 API 地址
