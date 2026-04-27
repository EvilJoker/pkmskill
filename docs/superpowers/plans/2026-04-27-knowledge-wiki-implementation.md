# Knowledge Wiki 实现计划

> **参考**: `docs/superpowers/specs/2026-04-27-knowledge-wiki-design.md`

## 目标
重构知识库结构，支持按主题浏览和发现内容

## 目录结构（目标）
```
~/.pkm/
├── 10_Tasks/                      # 任务层
├── 20_Projects/                   # 项目层（原 60_Projects）
├── 30_Raw/                        # Raw 层（原 50_Raw）
├── 40_Knowledge/                  # Wiki 层（原 90_Knowledge）
│   ├── _wiki/
│   │   ├── index.md
│   │   ├── index.yaml
│   │   ├── AI/
│   │   ├── 职业发展/
│   │   └── 编程/
│   └── _schema/
│       └── CLAUDE.md
└── 80_Archives/                   # 归档层
```

**目录映射**:
| 现状 | 目标 | 说明 |
|------|------|------|
| 90_Knowledge/ | 40_Knowledge/ | Wiki 层重命名 |
| 60_Projects/ | 20_Projects/ | 项目层重命名 |
| 50_Raw/ | 30_Raw/ | Raw 层重命名 |
| 10_Tasks/ | 10_Tasks/ | 不变 |
| 80_Archives/ | 80_Archives/ | 不变 |

---

## ⚠️ 重要约束

**测试红线**：
- 必须使用 `make test` 运行测试
- 禁止修改 `~/.pkm/` 下的任何数据
- 测试在 Docker 容器内执行，使用独立数据库

**重构风险**：
- 涉及目录重命名（`90_Knowledge` → `40_Knowledge`）
- 涉及目录重命名（`60_Projects` → `20_Projects`）
- 涉及目录重命名（`50_Raw` → `30_Raw`）
- 涉及文件名模式变更（UUID → 主题命名）
- 需要确保 `pkm reflow` 命令向后兼容

---

## Task 1: 创建目录结构和基础文件

**文件**:
- 创建: `pkm/knowledge_wiki.py` (新模块)

**步骤**:
- [ ] 创建 `40_Knowledge/_wiki/` 目录结构
- [ ] 创建 `40_Knowledge/_schema/CLAUDE.md`
- [ ] 定义 `WikiPage` 数据结构
- [ ] 定义 frontmatter 格式
- [ ] 定义 wiki 页面模板

**验证**:
- [ ] `pkm reflow` 能识别新目录结构

---

## Task 2: 重构 reflow 逻辑

**文件**:
- 修改: `pkm/commands/reflow.py`

**步骤**:
- [ ] 分析现有 reflow 逻辑（两轮扫描 + md5）
- [ ] 保留增量更新机制（md5 + 两轮扫描）
- [ ] 修改输出目标：从 `generated/*.md` 改为 `_wiki/{topic}/*.md`
- [ ] 修改文件命名：从 UUID 改为 `{topic}-{title}.md`

**验证**:
- [ ] `make test` 通过
- [ ] `pkm reflow` 能在新路径生成文件

---

## Task 3: 实现 Wiki 索引生成

**文件**:
- 修改: `pkm/knowledge_wiki.py`

**步骤**:
- [ ] 实现 `generate_index_md()` 生成总导航
- [ ] 实现 `generate_index_yaml()` 生成结构化索引
- [ ] 在 reflow 完成后调用索引生成

**验证**:
- [ ] `40_Knowledge/_wiki/index.md` 存在且格式正确
- [ ] `40_Knowledge/_wiki/index.yaml` 存在且格式正确

---

## Task 4: 更新 CLI 命令

**文件**:
- 修改: `pkm/cli.py`

**步骤**:
- [ ] 检查 `pkm reflow` 命令注册是否正常
- [ ] 检查 `pkm inbox` 命令是否正常（可能依赖 knowledge 路径）
- [ ] 更新命令帮助文档

**验证**:
- [ ] `pkm --help` 正常
- [ ] `pkm reflow --help` 正常
- [ ] `pkm inbox --help` 正常

---

## Task 5: 更新配置常量

**文件**:
- 修改: `pkm/config.py`
- 修改: `pkm/knowledge.py`

**步骤**:
- [ ] 更新 `KNOWLEDGE_DIR` 从 `90_Knowledge` 改为 `40_Knowledge`
- [ ] 添加 `WIKI_DIR`, `SCHEMA_DIR` 等常量
- [ ] 更新相关引用

**验证**:
- [ ] `make test` 通过
- [ ] 配置加载正常

---

## Task 6: 迁移现有数据

**⚠️ 高风险操作**（最后执行）

**步骤**:
- [ ] 备份 `~/.pkm/90_Knowledge/`（可选）
- [ ] 删除 `~/.pkm/90_Knowledge/generated/`
- [ ] 验证 `pkm reflow` 能在 `40_Knowledge/_wiki/` 生成新文件

**验证**:
- [ ] 旧 `generated/` 已删除
- [ ] 新 `_wiki/` 结构正确
- [ ] `pkm reflow` 正常工作

---

## Task 7: 完整功能验证

**验证清单**:

| 功能 | 验证命令 | 预期结果 |
|------|----------|----------|
| CLI 基础 | `pkm --help` | 显示帮助 |
| Reflow | `pkm reflow` | 生成 wiki 页面 |
| Inbox | `pkm inbox ls` | 显示任务列表 |
| Project | `pkm project ls` | 显示项目列表 |
| Task | `pkm task ls` | 显示任务列表 |
| Server | `make test` | 全部测试通过 |

---

## Task 8: 更新文档

**文件**:
- 修改: `CLAUDE.md`

**步骤**:
- [ ] 更新目录结构说明
- [ ] 更新 reflow 相关说明

---

## 执行顺序

```
1. Task 1: 创建目录结构和基础文件
2. Task 2: 重构 reflow 逻辑
3. Task 3: 实现 Wiki 索引生成
4. Task 4: 更新 CLI 命令
5. Task 5: 更新配置常量
6. Task 6: 迁移现有数据（⚠️ 高风险，最后执行）
7. Task 7: 完整功能验证
8. Task 8: 更新文档
```

---

## 风险缓解

| 风险 | 缓解措施 |
|------|----------|
| 测试污染用户数据 | 使用 `make test` 在 Docker 容器内测试 |
| reflow 路径变更 | 保留旧路径兼容，或分阶段切换 |
| CLI 命令失效 | 先验证 `pkm --help` 正常再继续 |
