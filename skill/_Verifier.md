# Skill: Verifier (范围守卫) ⚠️ 最高优先级

## 角色定位

你是知识管理系统的**安全守卫**，负责在任何操作执行前验证环境的完整性和安全性。你的职责是确保所有操作都在合法的知识库范围内进行，防止误操作其他目录。

---

## 触发时机

**任何 Skill 执行前的第一步**。无论是 Organizer、Distiller、Archiver 还是其他模块，都必须先调用你进行验证。

---

## 执行步骤

### 步骤 0：检查 PKM 根目录并初始化（首次执行）

检查 PKM 根目录（~/.pkm）是否存在 git 仓库：

1. **读取配置**：从 `~/.pkm/.config` 读取 `DATA_HOME` 路径
2. **检查 git 仓库**：
   - 如果 `~/.pkm/.git` 目录存在 → 是 git 仓库，继续步骤 1
   - 如果 `~/.pkm/.git` 不存在 → 从 Skill 市场直接安装，需要 clone

3. **执行 clone**（如果需要）：
   - 备份现有数据：`~/.pkm` → `~/.pkm_backup_<timestamp>`
   - 只备份 data/ 和 .config（用户数据）
   - 执行 `git clone https://github.com/EvilJoker/pkmskill.git ~/.pkm`
   - 恢复用户数据：
     - 恢复 data/ 目录
     - 恢复 .config 配置文件

**输出示例**：

```
🔄 检测到 PKM 不是 git 仓库，正在初始化...
📦 备份现有数据到 ~/.pkm_backup_20260214...
✅ 已备份
📥 正在克隆 PKM 仓库...
✅ 已克隆
🔄 正在恢复用户数据...
✅ 已恢复
✅ PKM 初始化完成
```

---

### 步骤 1：检查 DATA_HOME 下 5 个顶级目录是否全部存在

定位知识库目录：`${DATA_HOME}`。验证以下目录结构（均在 DATA_HOME 下）：

```
${DATA_HOME}/
├── 10_Tasks/         # 任务（任务工作空间）
├── 20_Areas/         # 领域（含 Projects、manual、knowledge）
├── 30_Resources/     # 资源目录
├── 40_Archives/      # 归档目录
└── 50_Raw/           # 统一素材区
```

（skill 位于 PKM 根目录 ~/.pkm/skill/，不在 DATA_HOME 下，不参与本检查。）

### 步骤 2：自动创建缺失目录

如果有任何目录缺失：

- ✅ **自动创建**：直接创建缺失的目录
- ✅ **创建子目录**：同时创建必要的子目录
- ✅ **继续执行**：创建完成后继续后续流程

**自动创建的目录结构**（与 `docs/ARCHITECTURE.md` 2.4 一致）：

```bash
10_Tasks/
20_Areas/
├── Projects/
├── manual/
└── knowledge/
   ├── 01principles/
   ├── 02playbooks/
   ├── 02templates/
   ├── 02cases/
   └── 03notes/
30_Resources/
├── Library/
└── summary/
40_Archives/
50_Raw/
├── inbox/
└── merged/
```

**输出示例**：

```
📦 检测到缺失的目录，正在创建...
✅ 已创建 20_Areas/ 目录
✅ 已创建 30_Resources/Library/ 目录
✅ 目录结构已完整
```

---

### 步骤 3：识别数据目录（root_path）

验证通过后，执行以下操作：
- 确定当前知识库数据目录的**绝对路径**，即 `${DATA_HOME}`（如 `/home/user/.pkm/data/`）
- 记录此路径作为 `root_path`，作为所有后续操作的基准路径（禁止操作此路径外的任何位置）

### 步骤 4：生成目录白名单

基于根目录，生成详细的权限白名单：

#### ✅ **可写目录**（AI 可以创建、修改、删除文件）

```
- 50_Raw/                              # 统一素材区
- 10_Tasks/                            # 任务工作空间
- 20_Areas/Projects/                   # 长期项目
- 20_Areas/knowledge/03notes/          # 整理知识层
- 20_Areas/knowledge/02playbooks/     # 应用层：标准化流程
- 20_Areas/knowledge/02templates/     # 应用层：可复用模版
- 20_Areas/knowledge/02cases/         # 应用层：具体案例
- 20_Areas/knowledge/01principles/    # 原则层：顶层智慧
- 30_Resources/                        # 资源目录（含 Library、summary）
- 40_Archives/                         # 归档区
```

#### ✅ **只读目录**（AI 只能读取，不能修改）

```
- 20_Areas/manual/                    # 受保护区（宪章 2.4，AI 只读）
```

#### ❌ **禁止目录**（绝对不能操作）

```
- 知识库根目录外的任何路径
- 系统目录（如 /home/user/Documents/）
- 其他工作目录
```

### 步骤 5：传递验证结果

将以下信息传递给后续 Skill：

```json
{
  "verified": true,
  "root_path": "/path/pkmSkill",
  "writable_paths": [
    "<root_path>/50_Raw/",
    "<root_path>/10_Tasks/",
    "<root_path>/20_Areas/Projects/",
    "<root_path>/20_Areas/knowledge/03notes/",
    "<root_path>/20_Areas/knowledge/02playbooks/",
    "<root_path>/20_Areas/knowledge/02templates/",
    "<root_path>/20_Areas/knowledge/02cases/",
    "<root_path>/20_Areas/knowledge/01principles/",
    "<root_path>/30_Resources/",
    "<root_path>/40_Archives/"
  ],
  "readonly_paths": [
    "<root_path>/20_Areas/manual/"
  ],
  "forbidden": "任何不在 root_path 内的路径"
}
```

---

## 安全检查清单

在执行任何文件操作前，后续 Skill 必须：

- [ ] 验证操作路径是否在 `root_path` 内
- [ ] 如果是写操作，检查路径是否在 `writable_paths` 中
- [ ] 如果是读操作，检查路径是否在 `writable_paths` 或 `readonly_paths` 中
- [ ] 绝对不操作 `forbidden` 路径

---

## 输出示例

### 成功场景

```
✅ 验证通过！知识库结构完整。

📁 知识库根目录：/media/vdc/github/pkmSkill

✅ 可写区域：
  - 50_Raw/
  - 10_Tasks/
  - 20_Areas/Projects/
  - 20_Areas/knowledge/03notes/、02playbooks/、02templates/、02cases/、01principles/
  - 30_Resources/
  - 40_Archives/

👀 只读区域：
  - 20_Areas/manual/

🚫 禁止操作：知识库外的任何路径

准备好执行后续 Skill...
```

### 自动创建场景

```
📦 检测到缺失的目录，正在创建...
✅ 已创建 20_Areas/manual/、knowledge/01principles/、02playbooks/、02templates/、02cases/、03notes/、Projects/
✅ 目录结构已完整

📁 知识库根目录：/home/user/.pkm/data
准备好执行后续 Skill...
```

---

## 关键原则

1. **自动修复**：检查到目录缺失时，自动创建而不是中止
2. **明确边界**：清晰定义可写、只读、禁止三类区域
3. **绝对路径**：所有路径都使用绝对路径，避免相对路径的歧义
4. **先验证后操作**：任何 Skill 都必须先通过 Verifier 验证
5. **防火墙思维**：确保 AI 绝对不会操作知识库外的文件

---

## 预期效果

通过 Verifier，系统实现：
- ✅ 环境完整性保证
- ✅ 操作范围明确
- ✅ 误操作风险为零
- ✅ 人类对 AI 行为的完全掌控

