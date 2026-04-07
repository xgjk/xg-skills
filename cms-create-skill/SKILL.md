---
name: cms-create-skill
description: 用于"创建新 Skill / 新建 Skill / 写一个 Skill / 按 XGJK 协议生成 Skill 包 / 浏览查看平台已有 Skill / 搜索 Skill"。多轮引导从零生成符合协议的 Skill 目录与 SKILL.md。仅负责发现与创建——发布上架请用 cms-push-skill，问题反馈请用 cms-report-issue
skillcode: cms-create-skill
dependencies:
  - cms-auth-skills
---

# CMS Skill 创建工具

**当前版本**: v1.21.0

> **身份声明**：`cms-create-skill` 现在只负责两件事：发现已有 Skill、按协议创建新 Skill。发布、更新、下架统一转交 `cms-push-skill`；问题反馈统一转交 `cms-report-issue`。

## 两段能力

| # | 核心能力 | 说明 | 需要登录 |
|---|---|---|---|
| 1 | 发现 Skill | 浏览平台已有 Skill、查看详情、搜索筛选 | 否 |
| 2 | 创建 Skill | 按 XGJK 协议模板，多轮对话引导从零构建完整 Skill 包 | 否 |

## 命名区分

- 发现 Skill：先看平台已有的 Skill，避免重复创建。
- 创建 Skill：按协议从零生成内部 Skill 包。

## 协作边界

- 如果用户要发布到我们内部平台、更新、下架、同步 Skill，不在本 Skill 内执行，统一转交 `cms-push-skill`。
- 如果用户要提交问题、查看问题列表、关闭问题，不在本 Skill 内执行，统一转交 `cms-report-issue`。
- 本 Skill 只负责把 Skill 创建好，并明确下一步应该交给哪个依赖 Skill。

## 内部 / 外部定义

### 内部 Skill

- 定义：按照 `docs/` 下编号协议文档生成的 Skill 包。
- 典型动作：创建、结构校对、交付给发布工具。
- 典型表达：
  - "帮我按协议创建一个 Skill"
  - "这个 Skill 按内部规范生成"

### 外部 Skill

- 定义：不是按我方协议原生生成、但已存在于 ClawHub 的 Skill。
- 典型动作：不由本 Skill 创建；如果要同步到平台，转交 `cms-push-skill`。
- 典型表达：
  - "我在 ClawHub 找到一个 Skill，帮我同步到我们平台"
  - "把外部 skill 推到我们的平台"

## 能力宪章

### 核心原则

1. 禁止问用户 token、登录、鉴权细节；鉴权统一依赖 `cms-auth-skills`。
2. 只有声明需要鉴权的动作才获取 `access-token`。
3. 5 步创建流程必须按顺序执行，不跳步。
4. 每一步都要和用户确认，不自作主张。
5. 生成的 Skill 必须严格遵循 `docs/` 下编号协议文档。
6. 目标 Skill 的 `SKILL.md` YAML 头必须声明 `dependencies: - cms-auth-skills`。
7. 目标 Skill 不再生成本地 auth/common，统一依赖 `cms-auth-skills`。
8. 当用户进入发布链路时，只声明下一步转交 `cms-push-skill`，不在本 Skill 中继续维护重复发布实现。
9. 当用户进入问题反馈链路时，只声明下一步转交 `cms-report-issue`，不在本 Skill 中继续维护重复问题实现。
10. 本 Skill 自身只维护 Markdown 说明和创建相关 Python 脚本，不再维护旧接口文档目录。

### 鉴权规则

- 需要鉴权的动作：无
- 不需要鉴权的动作：`get_skills.py`、5 步创建流程、`fetch_api_doc.py`
- 鉴权准备方式：统一通过 `cms-auth-skills` 获取 `access-token`

### 授权依赖

- 创建阶段默认不做写操作，但生成的目标 Skill 仍需依赖 `cms-auth-skills`。
- 当后续进入发布或问题关闭阶段，由对应依赖 Skill 自己处理鉴权动作。

## 能力概览

### 发现 Skill

| 能力 | 模块 | 说明 | 需要登录 |
|---|---|---|---|
| 打开技能管理平台 | 浏览器 | 打开 https://skills.mediportal.com.cn | 否 |
| 浏览 Skill 列表 | `skill-management` | 查看平台所有已发布 Skill | 否 |
| 搜索 Skill | `skill-management` | 按关键词搜索 Skill | 否 |
| 查看 Skill 详情 | `skill-management` | 查看某个 Skill 的完整信息 | 否 |

### 创建 Skill

| 能力 | 模块 | 说明 | 需要登录 |
|---|---|---|---|
| 按协议构建 Skill 包 | 5 步流程 | 从零生成完整 Skill 包 | 否 |
| 获取接口文档 | 工具脚本 | 拉取并解析 Swagger / Markdown 接口定义 | 否 |

### 协作依赖

| 能力 | 模块 | 说明 | 需要登录 |
|---|---|---|---|
| 发布 / 更新 / 下架 | `cms-push-skill` | Skill 创建完成后，统一交给发布 Skill | 由依赖 Skill 决定 |
| 提交 / 查看 / 关闭问题 | `cms-report-issue` | Skill 运行中问题统一交给问题 Skill | 由依赖 Skill 决定 |

## 意图路由表

### 发现 Skill

| 用户说 | 路由到 | 打开文档 | 执行脚本 | 需要登录 |
|---|---|---|---|---|
| "打开技能管理"/"打开玄关 Skill"/"Skill 管理页面" | 浏览器打开 | — | `open https://skills.mediportal.com.cn` 或返回链接 | 否 |
| "有哪些 Skill"/"查看 Skill 列表"/"看看都有什么" | `skill-management` | `references/skill-management/README.md` | `scripts/skill-management/get_skills.py` | 否 |
| "搜索 xxx Skill"/"找一下 xxx 相关的" | `skill-management` | `references/skill-management/README.md` | `scripts/skill-management/get_skills.py --search xxx` | 否 |
| "xxx 这个 Skill 怎么样"/"看看 xxx 的详情" | `skill-management` | `references/skill-management/README.md` | `scripts/skill-management/get_skills.py --detail xxx` | 否 |

### 创建 Skill

| 用户说 | 路由到 | 打开文档 | 执行脚本 | 需要登录 |
|---|---|---|---|---|
| "构建 Skill 包"/"按模板创建 Skill" | 5 步流程 | `docs/007_XGJK_SKILL_CREATION_WORKFLOW.md` | `scripts/fetch_api_doc.py` | 否 |
| "按我们的协议新建一个 Skill"/"从零生成内部 Skill" | 5 步流程 | `docs/007_XGJK_SKILL_CREATION_WORKFLOW.md` | `scripts/fetch_api_doc.py` | 否 |
| "获取接口文档"/"拉取 API 定义" | 工具脚本 | — | `scripts/fetch_api_doc.py` | 否 |

### 发布 / 问题协作

| 用户说 | 路由到 | 打开文档 | 执行脚本 | 需要登录 |
|---|---|---|---|---|
| "打包并发布"/"帮我发布这个 Skill"/"发布到我们内部平台" | `cms-push-skill` | `references/skill-management/README.md` | `python3 cms-push-skill/scripts/skill-management/publish_skill.py ...` | 由依赖 Skill 决定 |
| "把 ClawHub 上这个 Skill 同步到我们平台" | `cms-push-skill` | `references/skill-management/README.md` | `python3 cms-push-skill/scripts/skill-management/publish_skill.py --external ...` | 由依赖 Skill 决定 |
| "帮我提交问题"/"上报这个问题" | `cms-report-issue` | `references/issue-report/README.md` | `python3 cms-report-issue/scripts/issue_report/report_issue.py ...` | 由依赖 Skill 决定 |
| "看看这个 Skill 有哪些问题"/"问题列表" | `cms-report-issue` | `references/issue-report/README.md` | `python3 cms-report-issue/scripts/issue_report/list_issues.py --skill-code xxx` | 由依赖 Skill 决定 |

## 工作流 A：发现 Skill

发现是起点，先看看平台上有什么，再决定是否创建新的。

```bash
# 浏览全部 Skill
python3 cms-create-skill/scripts/skill-management/get_skills.py

# 按关键词搜索
python3 cms-create-skill/scripts/skill-management/get_skills.py --search "机器人"

# 查看详情
python3 cms-create-skill/scripts/skill-management/get_skills.py --detail "im-robot"
```

## 工作流 B：创建 Skill（5 步流程）

> 完整操作手册：`docs/007_XGJK_SKILL_CREATION_WORKFLOW.md`
> 创建规范：`docs/` 下编号协议文档（核心总则见 `001`，详细规则见 `002`-`008`）
> 验证清单：`docs/008_XGJK_SKILL_VALIDATION_CHECKLIST.md`

### 协议文档编号说明

`cms-create-skill/docs/` 下的协议文档统一使用三位编号，编号既是排序规则，也是推荐阅读顺序：

1. `001_XGJK_SKILL_PROTOCOL.md`
2. `002_XGJK_SKILL_NAMING_AND_DESCRIPTION_SPEC.md`
3. `003_XGJK_SKILL_STRUCTURE_SPEC.md`
4. `004_XGJK_SKILL_INDEX_WRITING_SPEC.md`
5. `005_XGJK_SKILL_PYTHON_SCRIPT_SPEC.md`
6. `006_XGJK_SKILL_AUTH_AND_SECURITY_SPEC.md`
7. `007_XGJK_SKILL_CREATION_WORKFLOW.md`
8. `008_XGJK_SKILL_VALIDATION_CHECKLIST.md`

命名规则统一为：`NNN_XGJK_SKILL_<TOPIC>.md`

```text
Step 1  意图理解与需求确认
Step 2  按协议逐步生成
Step 3  三轮反思检查
Step 4  最终确认
Step 5  完成输出总结
```

## 工作流 C：发布协作

这里说的“发布到我们内部平台”，就是把 Skill 注册到当前技能管理平台。

当创建完成后，如果用户明确要发布或同步，不在本 Skill 内继续执行，直接转交 `cms-push-skill`：

```bash
# 先安装发布 Skill
npx clawhub@latest install cms-push-skill --force
```

然后按场景进入对应命令：

```bash
# 内部 Skill：首次发布
python3 cms-push-skill/scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --name "IM 机器人" --internal

# 内部 Skill：更新
python3 cms-push-skill/scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --update --version 1.0.0 --internal

# 外部 Skill：同步到平台
python3 cms-push-skill/scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --name "IM 机器人" --external
```

如果你当前就在 `cms-create-skill` 里，不要继续找本 Skill 自己的发布脚本，下一步直接切到 `cms-push-skill`。

## 工作流 D：问题反馈协作

如果用户要提交问题或处理问题，统一转交 `cms-report-issue`：

```bash
# 先安装问题反馈 Skill
npx clawhub@latest install cms-report-issue --force
```

然后按场景进入对应命令：

```bash
# 提交问题
python3 cms-report-issue/scripts/issue_report/report_issue.py \
  --skill-code im-robot --version 1.0.0 --error "接口超时"

# 查看问题
python3 cms-report-issue/scripts/issue_report/list_issues.py --skill-code im-robot

# 标记为已解决
python3 cms-report-issue/scripts/issue_report/update_issue.py \
  --issue-id abc123 --status resolved --resolution "已修复重试逻辑"

# 关闭问题
python3 cms-report-issue/scripts/issue_report/update_issue.py \
  --issue-id abc123 --status closed
```

如果你当前就在 `cms-create-skill` 里，不要继续找本 Skill 自己的问题脚本，下一步直接切到 `cms-report-issue`。

## 约束

1. 5 步创建流程必须完整执行。
2. 每一步都要多轮确认。
3. 生成结果必须严格遵循协议文档。
4. 所有说明统一写在 Markdown 文档里。
5. 发布和问题反馈只做依赖声明，不在本 Skill 内重复维护实现。

## 能力树

```text
cms-create-skill/
├── SKILL.md
├── docs/
│   ├── 001_XGJK_SKILL_PROTOCOL.md
│   ├── 002_XGJK_SKILL_NAMING_AND_DESCRIPTION_SPEC.md
│   ├── 003_XGJK_SKILL_STRUCTURE_SPEC.md
│   ├── 004_XGJK_SKILL_INDEX_WRITING_SPEC.md
│   ├── 005_XGJK_SKILL_PYTHON_SCRIPT_SPEC.md
│   ├── 006_XGJK_SKILL_AUTH_AND_SECURITY_SPEC.md
│   ├── 007_XGJK_SKILL_CREATION_WORKFLOW.md
│   └── 008_XGJK_SKILL_VALIDATION_CHECKLIST.md
├── references/
│   ├── issue-report/
│   │   └── README.md
│   └── skill-management/
│       └── README.md
└── scripts/
    ├── fetch_api_doc.py
    └── skill-management/
        ├── README.md
        └── get_skills.py
```

## 备注

- 平台“规范协议”页中，“创建 Skills 的规范”分组以 `README.md` 作为索引；`cms-create-skill/docs/` 保留编号协议文档本体。
- 发布能力统一收敛到 `cms-push-skill`，问题反馈能力统一收敛到 `cms-report-issue`。
- 本 Skill 自身的说明目录已经统一为 `docs/` + `references/` + `scripts/`。
