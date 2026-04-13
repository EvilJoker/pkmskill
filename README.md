# PKM - Personal Knowledge Management CLI

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/EvilJoker/pkmskill)

> 基于 PARA + CODE + 金字塔原理的个人知识管理系统

---

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/EvilJoker/pkmskill/main/install.sh | bash -s snapshot
```

安装脚本会：
1. 检测是否已安装（升级或全新安装）
2. 安装/更新 PKM CLI
3. 拉取 Docker 镜像
4. 启动服务
5. 运行测试验证

## 升级

```bash
# 升级到最新快照版本
curl -fsSL https://raw.githubusercontent.com/EvilJoker/pkmskill/main/install.sh | bash -s snapshot

# 升级（自动备份，无需确认）
curl -fsSL https://raw.githubusercontent.com/EvilJoker/pkmskill/main/install.sh | bash -s snapshot -y
```

> 升级前会提示备份已有数据，使用 `-y` 可跳过确认。

## 快速开始

```bash
pkm --help        # 查看帮助
pkm status        # 查看状态
pkm --version     # 查看版本
```

## 架构

PKM 是一个 FastAPI + SQLite + Docker 的服务架构：

- **CLI**：`pkm` 命令行工具
- **Server**：FastAPI 后端服务
- **Data**：SQLite 数据库存储在 `~/.pkm/`

服务地址：`http://localhost:8890`

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 📮 反馈

遇到问题或有建议？请[提交 Issue](https://github.com/EvilJoker/pkmskill/issues)

---

**让知识管理更简单** 🚀
