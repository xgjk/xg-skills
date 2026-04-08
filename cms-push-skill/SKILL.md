---
name: cms-push-skill
description: 用于"发布 Skill / 上架 Skill / 推送 Skill / 更新已发布的 Skill / 下架 Skill / 把本地 Skill 上传到平台 / 同步到 ClawHub 或 GitHub"。一键完成 打包 → 七牛上传 → 平台注册/更新/下架。需要先通过 cms-auth-skills 取得 token。问题反馈请用 cms-report-issue
skillcode: cms-push-skill
dependencies:
  - cms-auth-skills
---

**当前版本**: v1.6.2

# cms-push-skill

只负责一件事：把已经准备好的 Skill 推送到平台。

这里说的“平台”，默认就是我们内部技能管理平台。

## 能力总览

| # | 能力 | 脚本 | 需要登录 |
|---|---|---|---|
| 1 | 注册新 Skill | `scripts/skill-management/register_skill.py` | 是 |
| 2 | 更新已有 Skill | `scripts/skill-management/update_skill.py` | 是 |
| 3 | 下架 Skill | `scripts/skill-management/delete_skill.py` | 是 |
| 4 | 一站式发布 | `scripts/skill-management/publish_skill.py` | 是 |
| 5 | 打包 Skill 目录为 ZIP | `scripts/skill-management/pack_skill.py` | 否 |
| 6 | 上传文件到七牛 | `scripts/skill-management/upload_to_qiniu.py` | 是 |

## 路由

- 发布到我们内部平台：`python3 cms-push-skill/scripts/skill-management/publish_skill.py ./my-skill --code my-skill --name "My Skill" --internal`
- 更新我们内部平台上的 Skill：`python3 cms-push-skill/scripts/skill-management/publish_skill.py ./my-skill --code my-skill --update --version 1.1.0 --internal`
- 外部发布：`python3 cms-push-skill/scripts/skill-management/publish_skill.py ./my-skill --code my-skill --name "My Skill" --external`
- 注册：`python3 cms-push-skill/scripts/skill-management/register_skill.py --code my-skill --name "My Skill"`
- 更新：`python3 cms-push-skill/scripts/skill-management/update_skill.py --code my-skill --name "New Name"`
- 下架：`python3 cms-push-skill/scripts/skill-management/delete_skill.py --id <skill-id> --reason "原因"`

如果用户要提交问题、查看问题列表、关闭问题，统一转到 `references/issue-report/README.md` 对应的 `cms-report-issue`；如果用户还没创建 Skill，可先使用 `cms-create-skill`。

## 内部平台发布指引

如果你当前要把 Skill 发布到我们内部平台，最短路径是：

```bash
# 先准备鉴权
npx clawhub@latest install cms-auth-skills --force

# 首次发布到内部平台
python3 cms-push-skill/scripts/skill-management/publish_skill.py \
  ./my-skill --code my-skill --name "My Skill" --internal

# 更新内部平台上的 Skill
python3 cms-push-skill/scripts/skill-management/publish_skill.py \
  ./my-skill --code my-skill --update --version 1.1.0 --internal
```

如果你当前不是在做发布，而是遇到了线上问题、要反馈问题，不在本 Skill 内处理，直接转到 `cms-report-issue`。

## 问题反馈接力

如果你当前正在 `cms-push-skill` 里发布或更新 Skill，后来要反馈问题，最短路径是：

```bash
# 安装问题反馈 Skill
npx clawhub@latest install cms-report-issue --force

# 提交问题
python3 cms-report-issue/scripts/issue_report/report_issue.py \
  --skill-code my-skill --version 1.1.0 --error "..."

# 查看问题列表
python3 cms-report-issue/scripts/issue_report/list_issues.py --skill-code my-skill

# 标记已解决
python3 cms-report-issue/scripts/issue_report/update_issue.py \
  --issue-id abc123 --status resolved --resolution "已修复"
```

## 同步选项

`publish_skill.py` 支持同步到 ClawHub 和 GitHub：

- `--sync-clawhub`：同步到 ClawHub。
- `--sync-github`：同步到 GitHub。
- `--no-sync-clawhub`：不同步到 ClawHub。
- `--no-sync-github`：不同步到 GitHub。

内部 Skill 默认两者都推，外部 Skill 不支持推送到 ClawHub。

## 规则

1. 所有推送动作统一使用 `scripts/skill-management/` 下的脚本。
2. 推送前先通过 `cms-auth-skills` 准备好 `access-token`。
3. 内部 Skill 走七牛上传 + 平台注册。
4. 外部 Skill 跳过七牛上传，直接使用 ClawHub 下载地址。
5. 本 Skill 只维护推送链路；问题闭环统一交给 `cms-report-issue`。
6. 所有说明文档统一使用 Markdown，不维护旧接口文档目录。

## 能力树

```text
cms-push-skill/
├── SKILL.md
├── references/
│   ├── issue-report/
│   │   └── README.md
│   └── skill-management/
│       └── README.md
└── scripts/
    └── skill-management/
        ├── delete_skill.py
        ├── pack_skill.py
        ├── publish_skill.py
        ├── register_skill.py
        ├── update_skill.py
        └── upload_to_qiniu.py
```
