---
name: cms-report-issue
description: 用于"反馈问题 / 报 bug / 上报错误 / 提交 issue / 查看 Skill 问题列表 / 标记问题已解决 / 关闭问题"。处理 Skill 使用过程中遇到的报错、异常、改进建议；支持 stdin 管道接收错误输出。是 cms-create-skill 与 cms-push-skill 的统一问题反馈入口
skillCode: cms-report-issue
dependencies:
  - cms-auth-skills
---

# CMS Skill 问题上报工具

**当前版本**: v1.0.1

`cms-report-issue` 只负责问题闭环：

1. 提交问题。
2. 查看问题列表和统计。
3. 解决或关闭问题。

`cms-create-skill` 和 `cms-push-skill` 如果遇到问题反馈场景，统一转交到这里处理。

## 能力总览

| # | 能力 | 脚本 | 需要登录 |
|---|---|---|---|
| 1 | 提交问题 | `scripts/issue_report/report_issue.py` | 否 |
| 2 | 查看问题列表 | `scripts/issue_report/list_issues.py` | 否 |
| 3 | 更新问题状态 | `scripts/issue_report/update_issue.py` | 是 |

## 路由

- 上报问题：`python3 cms-report-issue/scripts/issue_report/report_issue.py --skill-code my-skill --version 1.0.0 --error "..."`
- 管道上报：`python3 some_script.py 2>&1 | python3 cms-report-issue/scripts/issue_report/report_issue.py --skill-code my-skill --stdin`
- 查看问题：`python3 cms-report-issue/scripts/issue_report/list_issues.py --skill-code my-skill`
- 查看统计：`python3 cms-report-issue/scripts/issue_report/list_issues.py --stats`
- 解决问题：`python3 cms-report-issue/scripts/issue_report/update_issue.py --issue-id abc123 --status resolved --resolution "已修复"`
- 关闭问题：`python3 cms-report-issue/scripts/issue_report/update_issue.py --issue-id abc123 --status closed`

## 规则

1. 问题提交、查看、关闭统一使用 `scripts/issue_report/` 下的脚本。
2. 需要鉴权的动作只有问题状态更新；鉴权统一通过 `cms-auth-skills` 准备 `access-token`。
3. 问题上报失败不应阻塞原始业务流程；装饰器模式下异常仍需重新抛出。
4. 所有说明文档统一使用 Markdown，不维护旧接口文档目录。

## 能力树

```text
cms-report-issue/
├── SKILL.md
├── references/
│   └── issue-report/
│       └── README.md
├── github-issue-templates/
│   ├── config.yml
│   ├── bug_report.yml
│   ├── feature_request.yml
│   └── ...
└── scripts/
    └── issue_report/
        ├── README.md
        ├── list_issues.py
        ├── report_issue.py
        └── update_issue.py
```
