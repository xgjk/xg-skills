# XGJK Skills 仓库（统一管理）

本仓库用于统一管理所有 XGJK Skills（技能包）源码：**每个 skill 作为一个独立文件夹**，在内部遵循同一套 Skill 包协议规范，便于索引、校验与复用。

## 核心约定

1. **每个 Skill = 一个目录**
   仓库根下的一级目录名即为 `skill-name`，例如：`demo-weather/`、`im-robot/`。

2. **Skill 包内部结构固定**
   每个 skill 文件夹内部的目录与文件结构严格遵循《Skill 包协议规范 v1.05》（即 `skill编写规范.md`）要求。

3. **通用规范以协议文档为准，不强制模板拷贝**
   仓库允许各 skill 按自身实现维护目录与内容；如需复用模板，可按需参考。是否需要固定文件、如何约束，以 `skill编写规范.md` 与具体 skill 实际设计为准。

## Skills 索引（当前仓库）

本仓库以「每个 Skill 一个目录」进行管理。以下为当前已收录的 Skills（以仓库实际目录为准）：

- `cms-auth-skills/`
- `notex-skills/`

> 说明：该索引用于快速查看“当前有哪些 skill”。新增/删除 skill 时，请同步更新此处。

## 仓库结构说明（简版）

```text
xg-skills/
├── README.md
├── .github/ISSUE_TEMPLATE/     # Issue 表单模板（Bug/Feature/Perf/Integration 等）
└── <skill-name>/
    ├── SKILL.md
    ├── common/
    ├── openapi/
    ├── examples/
    └── scripts/
```

## Skill 规范（精简版）

README 只保留最低必要规则，详细协议统一以 `skill编写规范.md` 为准。

### 最小要求（必须）

- 每个 skill 为独立目录，且包含 `SKILL.md`
- `openapi/` 与 `scripts/` 保持 endpoint 1:1 对应
- `scripts/` 统一使用 Python（`.py`）
- 不允许残留占位符（如 `<module>` / `<endpoint>`）

### 命名建议

- `skill-name`：英文短横线风格（如 `cms-auth-skills`）
- `module`：英文小写/短横线风格
- `endpoint`：英文短词/短横线风格

### 新增/更新流程（3 步）

1. 建立/更新 skill 目录（含 `SKILL.md`, `openapi/`, `scripts/` 等）
2. 补齐文档与脚本映射（`openapi/*` ↔ `scripts/*`）
3. 自检并提交（结构完整、命名规范、可执行）

> 详细格式、自检清单与禁止项请查看：`skill编写规范.md`

## Skill 变更操作约束（强制）

为避免误改、错改、跨目录污染，所有对 skill 的新增/更新/删除操作必须遵循以下规则：

### 1) 作用域强约束：必须指定目标 skill 目录

- 所有操作都必须显式指向一个具体目录：`<skill-name>/`
- 禁止“未指定目录”的模糊更新（例如只说“改一下技能”）
- 禁止跨 skill 批量改动但不逐项声明范围

示例：

- ✅ 正确：`更新 cms-auth-skills/openapi/auth/login.md`
- ❌ 错误：`把鉴权逻辑改一下`（未指定 skill 目录）

### 2) 变更类型确认：先确认“新增 / 更新 / 删除”

执行前必须明确并确认本次操作类型：

- 新增（Add Skill）
- 更新（Update Skill）
- 删除（Delete Skill）

若用户描述不清，必须先追问确认，不得自行猜测。

### 3) 删除操作高风险：必须二次确认

任何删除（文件/目录/整 skill）必须满足：

1. 第一次确认：确认删除范围（删除什么、在哪个 skill）
2. 第二次确认：明确用户再次同意后才执行

未完成二次确认，禁止删除。

### 4) 新增与更新：必须基于 Skills 索引定位后执行

- 新增前：先确认是否为“新 skill”还是“现有 skill 扩展更新”
- 更新前：先在 README 的 Skills 索引中定位目标 skill
- 若索引不存在该 skill：
  - 走“新增 skill”流程；或
  - 由用户明确指定后再执行

### 5) 防混乱执行原则（必须）

- 只改用户确认的 skill 目录，不扩散到其他目录
- 涉及多 skill 时，按 skill 分批确认、分批执行
- 不允许因相似名称误操作（如 `cms-*`、`sq-*`）
- 任何“安装/同步/推送”均需对应到指定 skill，不得笼统执行

### 6) 建议执行口令模板（对齐确认）

执行前建议使用如下确认语义：

- `请确认：本次是【新增/更新/删除】`  
- `目标 skill：<skill-name>/`  
- `目标路径：<file-or-folder>`  
- `是否继续执行？`

> 删除类操作再补一次确认：`请二次确认删除以上内容（是/否）`

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


