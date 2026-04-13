# CI 测试 Action 设计

## 概述

为 PKM 项目添加 GitHub Actions CI 测试流程，每次 push 到 main 分支时自动运行测试，确保代码质量和覆盖率达标。

## 目标

- 每次 push 到 main 分支触发 CI 测试
- 执行 `make test` 运行所有测试（单元测试 + API 测试）
- 强制检查覆盖率门槛（行覆盖率 75%，分支覆盖率 65%）
- install.sh 使用 TDD 方式，预期失败，待后续修复

## 触发条件

- Push 到 `main` 分支时触发
- 支持手动触发（workflow_dispatch）

## CI 流程

```
1. Checkout 代码
2. 启动 Docker 服务 (docker-compose up -d)
3. 等待服务就绪
4. 运行 make test（包含覆盖率收集）
5. 检查覆盖率是否达标
   - 行覆盖率 >= 75%
   - 分支覆盖率 >= 65%
6. 执行 install.sh 测试（xfail 标记，允许失败）
7. 输出覆盖率报告
8. 测试失败或覆盖率不达标 → CI 失败
```

## 覆盖率门禁

| 指标 | 门槛 |
|------|------|
| 行覆盖率 | 75% |
| 分支覆盖率 | 65% |

覆盖率不达标时 CI 失败，阻止 Docker 镜像构建和发布。

## install.sh 测试策略

- 创建 `pkm-server/tests/test_install.py`
- 使用 `pytest.xfail` 标记为"预期失败"
- 测试实际执行 install.sh，验证脚本逻辑
- 未来修复 install.sh 后，去掉 xfail 标记即可

## 文件变更

### 新增文件

1. `.github/workflows/ci-test.yml` - CI 测试 Action
2. `pkm-server/tests/test_install.py` - install.sh 测试用例

### 修改文件

1. `.github/workflows/docker-publish.yml` - 添加 needs CI 测试的依赖条件

## Action 文件结构

```yaml
name: CI Test

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: make test
      - name: Check coverage
        run: |
          # Extract coverage from output
          # Fail if below thresholds
```

## 验收标准

1. Push 到 main 分支时 CI 自动触发
2. `make test` 执行所有测试
3. 覆盖率达标时测试通过
4. install.sh 测试为 xfail 状态
5. 测试失败时 CI 状态为失败
6. Docker publish job 依赖 CI test job
