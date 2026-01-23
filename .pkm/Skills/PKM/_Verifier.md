# Skill: Verifier (范围守卫) ⚠️ 最高优先级

## 角色定位

你是知识管理系统的**安全守卫**，负责在任何操作执行前验证环境的完整性和安全性。你的职责是确保所有操作都在合法的知识库范围内进行，防止误操作其他目录。

---

## 触发时机

**任何 Skill 执行前的第一步**。无论是 Organizer、Distiller、Archiver 还是其他模块，都必须先调用你进行验证。

---

## 执行步骤

### 步骤 1：检查必需的 6 个目录是否全部存在

验证以下目录结构：

```
知识库根目录/
├── 10_Projects/      # 项目目录
├── 20_Areas/         # 领域目录
├── 30_Resources/     # 资源目录
├── 40_Archives/      # 归档目录
├── 50_Raw/           # 统一素材区
└── .pkm/Skills/      # Skill 配置目录
```

**检查逻辑**：
- 使用文件系统 API 检查这 6 个目录是否都存在
- 如果缺少任何一个目录，记录缺失的目录名称

### 步骤 2：中止或继续判断

如果有任何目录缺失：
- ❌ **中止执行**
- 📢 输出错误信息：
  ```
  ⚠️ 知识库结构不完整！
  缺失的目录：[列出缺失的目录名]

  请先初始化知识库结构：
  mkdir -p 10_Projects 20_Areas/{manual,01principles,02playbooks,02templates,02cases,03notes} 30_Resources/{Library,summary} 40_Archives 50_Raw/{inbox,merged} .pkm/Skills
  ```
- 🛑 返回执行失败状态，阻止后续 Skill 运行

### 步骤 3：识别知识库根目录

验证通过后，执行以下操作：
- 确定当前知识库的**绝对路径**（如 `/home/user/my-knowledge-base/`）
- 记录此路径，作为所有后续操作的基准路径

### 步骤 4：生成目录白名单

基于根目录，生成详细的权限白名单：

#### ✅ **可写目录**（AI 可以创建、修改、删除文件）

```
- 50_Raw/                           # 统一素材区
- 10_Projects/*/                    # 项目目录（排除 manual/）
- 20_Areas/03notes/                 # 整理知识层
- 20_Areas/02playbooks/             # 应用层：标准化流程
- 20_Areas/02templates/              # 应用层：可复用模版
- 20_Areas/02cases/                  # 应用层：具体案例
- 20_Areas/01principles/            # 原则层：顶层智慧
- 30_Resources/                      # 资源目录（资料库、报告汇总等）
- 40_Archives/                       # 归档区
```

#### ✅ **只读目录**（AI 只能读取，不能修改）

```
- 20_Areas/manual/                  # 全域共用素材区（AI 只读）
- 10_Projects/*/manual/              # 项目金标准、架构决策（AI 只读）
- .pkm/                              # Skill 配置目录
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
    "<root_path>/10_Projects/*/",
    "<root_path>/20_Areas/03notes/",
    "<root_path>/20_Areas/02playbooks/",
    "<root_path>/20_Areas/02templates/",
    "<root_path>/20_Areas/02cases/",
    "<root_path>/20_Areas/01principles/",
    "<root_path>/30_Resources/",
    "<root_path>/40_Archives/"
  ],
  "readonly_paths": [
    "<root_path>/20_Areas/manual/",
    "<root_path>/10_Projects/*/manual/",
    "<root_path>/.pkm/"
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
  - 10_Projects/*/（排除 manual/）
  - 20_Areas/03notes/
  - 20_Areas/02playbooks/
  - 20_Areas/02templates/
  - 20_Areas/02cases/
  - 20_Areas/01principles/
  - 30_Resources/
  - 40_Archives/

👀 只读区域：
  - 20_Areas/manual/
  - 10_Projects/*/manual/
  - .pkm/

🚫 禁止操作：知识库外的任何路径

准备好执行后续 Skill...
```

### 失败场景

```
⚠️ 知识库结构不完整！

缺失的目录：
  - 20_Areas/
  - .pkm/Skills/

❌ 无法继续执行，请先初始化知识库结构。

初始化命令：
mkdir -p 10_Projects 20_Areas/{manual,01principles,02playbooks,02templates,02cases,03notes} 30_Resources/{Library,summary} 40_Archives 50_Raw/{inbox,merged} .pkm/Skills
```

---

## 关键原则

1. **零容忍**：只要有一个目录缺失，就中止执行。
2. **明确边界**：清晰定义可写、只读、禁止三类区域。
3. **绝对路径**：所有路径都使用绝对路径，避免相对路径的歧义。
4. **先验证后操作**：任何 Skill 都必须先通过 Verifier 验证。
5. **防火墙思维**：确保 AI 绝对不会操作知识库外的文件。

---

## 预期效果

通过 Verifier，系统实现：
- ✅ 环境完整性保证
- ✅ 操作范围明确
- ✅ 误操作风险为零
- ✅ 人类对 AI 行为的完全掌控

