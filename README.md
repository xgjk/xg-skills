# XGJK Skills 仓库（统一管理）

本仓库用于统一管理所有 XGJK Skills（技能包）源码：**每个 skill 作为一个独立文件夹**，在内部遵循同一套 Skill 包协议规范，便于索引、校验与复用。

## 核心约定

1. **每个 Skill = 一个目录**
   仓库根下的一级目录名即为 `skill-name`，例如：`demo-weather/`、`im-robot/`。

2. **Skill 包内部结构固定**
   每个 skill 文件夹内部的目录与文件结构严格遵循《Skill 包协议规范 v1.05》（即 `skill编写规范.md`）要求。

3. **通用内容只做模板/索引，不允许改变协议约束**
   协议中强调的固定文件（如 `common/auth.md`、`scripts/common/toon_encoder.py` 等）在**每个 skill 内都必须“原样复制”**。  
   因此：仓库根可以放“模板/参考”，但最终落地到每个 skill 目录里的固定文件必须与模板完全一致。

## 仓库目录结构（示例）

```text
xg-skills/
├── README.md
├── templates/                    # 可选：固定文件“原样模板/参考源”（只读，不参与运行）
│   ├── common/
│   │   ├── auth.md
│   │   └── conventions.md
│   ├── openapi/common/
│   │   └── appkey.md
│   └── scripts/common/
│       └── toon_encoder.py
├── skills-index.md              # 可选：全局技能索引（按需维护）
└── <skill-name>/
    ├── SKILL.md
    ├── common/
    │   ├── auth.md
    │   └── conventions.md
    ├── openapi/
    │   ├── common/
    │   │   └── appkey.md
    │   └── <module>/
    │       ├── api-index.md
    │       └── <endpoint>.md
    ├── examples/
    │   └── <module>/
    │       └── README.md
    └── scripts/
        ├── common/
        │   └── toon_encoder.py
        └── <module>/
            ├── README.md
            └── <endpoint>.py
```

## Skill 包内部结构（强约束）

每个 `(<skill-name>/)` 内部必须包含以下目录与文件，并保持协议中的强绑定关系：

- `SKILL.md`：主索引（只描述能力与路由入口，不写具体接口参数细节）
- `common/`：基础层固定内容（鉴权规范 + 通用约束）
- `openapi/`：文档层（模块索引 + 每个 endpoint 独立文档）
- `examples/`：引导层（模块的触发场景与标准流程）
- `scripts/`：执行层（模块脚本清单 + 每个 endpoint 一个 Python 脚本）

必须满足 1:1 绑定关系：

- `openapi/<module>/<endpoint>.md` ↔ `scripts/<module>/<endpoint>.py`

并且协议要求：

- 占位符（如 `<module>`、`<endpoint>`、`<skill-name>`）在最终产物中不得残留
- 所有 `scripts/` 下的脚本必须为 Python（`.py`）
- 每个 endpoint 脚本的输入字段与文档中的参数表必须一致
- 所有接口调用必须通过脚本执行，不允许跳过脚本直接调用 API

> 详细的格式模板、生成流水线、自检清单与“禁止项”，以 `skill编写规范.md` 为准。

## 命名规范（建议）

- `<skill-name>`：英文为主，使用短横线分词（如 `demo-weather`、`im-robot`）
- `<module>`：英文小写/短横线风格（如 `forecast`）
- `<endpoint>`：英文短词/短横线风格（如 `get-current`）

## 如何新增/更新一个 Skill（简版流程）

1. 新建 `<skill-name>/` 目录骨架（包含 `common/`、`openapi/`、`examples/`、`scripts/` 等）
2. 将协议要求的固定文件**原样复制**到对应路径（可从 `templates/` 复制，但最终必须落到每个 skill 内）
3. 逐个模块编写：
   - `openapi/<module>/api-index.md`
   - `openapi/<module>/<endpoint>.md`
   - `examples/<module>/README.md`
   - `scripts/<module>/<endpoint>.py`
   - `scripts/<module>/README.md`
4. 更新 `SKILL.md`（能力概览、路由表、能力树）
5. 完成协议自检（结构齐全、1:1 绑定一致、无占位符、脚本语言与输出规则、超时重试策略等）

## 验收标准（必须通过）

- 目录结构齐全且与协议一致
- 固定文件未被修改（逐字一致）
- endpoint 文档与脚本路径严格对应（1:1）
- 脚本满足协议约束：必须为 Python、输出需经过 `toon_encoder.py` 的 TOON 编码、鉴权遵循协议方式、无占位符/无绝对路径

## 维护建议（可选）

- `skills-index.md`：如果你们希望对外快速浏览所有 skill，可以维护一个全局索引文件（列出 skill 名称与一句话能力摘要）
- 可加入“模板一致性校验脚本”（只验证模板与固定文件是否一致，不参与业务逻辑）

## Issue 提报与协作规范（推荐）

为保证问题可追踪、可筛选、可统计，本仓库已启用 GitHub Issue Forms。

### 可用模板

- 🐞 Bug Report
- ✨ Feature Request
- ⚡ Performance Issue
- 🔗 Integration Issue
- ♻️ Regression Report
- 🚨 Incident Report
- 🔒 Security Issue
- 📚 Documentation Issue
- 🛠️ Refactor Proposal
- ❓ Question / Support

### 标签规范（建议最少满足）

每条 Issue 建议至少具备：

1. `type:*`（必选）
   - 例如：`type:bug` / `type:feature` / `type:roadmap`
2. `skill:*`（必选，至少一个）
   - 例如：`skill:cms-auth-skills`、`skill:notex-skills`
3. `priority:*`（建议）
   - `priority:P0` ~ `priority:P3`
4. `severity:*`（Bug/Incident 建议）
   - `severity:critical` / `severity:major` / `severity:minor`
5. `status:*`（流转状态）
   - `status:triage` / `status:in-progress` / `status:blocked` / `status:ready-for-test` / `status:done`

### 标题建议格式

- Bug：`[Bug] <问题一句话描述> — <影响对象/场景>`
- 需求：`[Feature] <需求一句话描述> — <目标对象/场景>`
- 规划：`[Roadmap] <阶段目标> — <里程碑范围>`

### 提报质量基线（DoD）

Issue 中建议至少包含：

- 期望行为（Expected）
- 实际行为（Actual）
- 最小复现步骤（Bug 类）
- 影响范围
- 验收标准（Definition of Done）

---
本 README 作为仓库级入口说明；协议细节以 `skill编写规范.md` 为准。

