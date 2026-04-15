# PKM CLI inbox 命令与 Stage2 Raw 处理设计

## 1. inbox CLI 命令

### 1.1 命令格式

```
pkm inbox "<内容>"                    # 直接捕获
pkm inbox --parse "<内容包含链接>"     # AI 解析链接后合并捕获
```

### 1.2 实现位置

`pkm-server/pkm/cli.py` 新增 `inbox` 命令组

### 1.3 处理流程

1. 解析参数，判断 `--parse` 模式
2. 验证 `50_Raw/inbox/` 目录可写（不存在则自动创建）
3. 从用户输入中提取 URL
4. 如果是 `--parse` 模式：
   - 调用 Claude API 解析链接内容
   - 合并用户输入 + 解析结果
5. 生成文件名：`YYYYMMDD_HHMMSS_标题_inbox.md`
6. 写入 `50_Raw/inbox/`

### 1.4 AI 解析提示词（--parse 模式）

```
请访问并解析以下链接的内容，提取：标题、正文要点、代码块（如有）。
以结构化 Markdown 格式输出。

链接：{url}
用户备注：{user_note}

请提取并总结内容。
```

### 1.5 错误处理

- 解析失败时，降级保存用户输入内容
- 内容为空时报错退出

### 1.6 文件命名

统一使用 `_inbox.md` 后缀，无论是否 `--parse` 模式

---

## 2. Stage2 增加 50_Raw 处理

### 2.1 核心理念

50_Raw 是特殊项目，Stage2 扫描并提炼其内容到 20_Areas，然后清理原文件。

### 2.2 处理流程

1. 扫描 `50_Raw/`（包含 inbox/、merged/ 等子目录下的 .md 文件）
2. 读取每个 .md 文件内容
3. 对内容进行分类判断（principles/playbooks/templates/cases/notes）
4. 去重检查：
   - "duplicate"：跳过写入并删除原文件
   - "similar"：合并到已有文件并删除原文件
   - "new"：写入新文件
5. 写入到 `20_Areas/knowledge/{分类}/`
6. 处理完成后删除原文件（清空 50_Raw）

### 2.3 实现位置

`pkm-server/knowledge.py` 的 `run_stage2_cycle` 函数

### 2.4 目录结构

```
50_Raw/                           # Stage2 特殊项目
├── inbox/                        # inbox 命令写入
│   └── ...                       # Stage2 扫描后清理
└── merged/                       # Organize 产出
    └── ...                       # Stage2 扫描后清理

20_Areas/knowledge/               # Stage2 提炼目标
├── 01principles/
├── 02playbooks/
├── 02templates/
├── 02cases/
└── 03notes/
```

---

## 3. 待实现

- [ ] inbox CLI 命令实现
- [ ] Stage2 50_Raw 处理逻辑
- [ ] 单元测试
