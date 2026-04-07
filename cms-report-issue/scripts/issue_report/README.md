# issue_report 脚本清单

## 模块定位

`issue_report` 负责问题提交、查看和关闭，对应说明统一见 `../../references/issue-report/README.md`。

## 脚本列表

| 脚本 | 说明 | 需要鉴权 |
|---|---|---|
| `report_issue.py` | 提交问题 | 否 |
| `list_issues.py` | 查看问题列表、筛选、统计 | 否 |
| `update_issue.py` | 更新问题状态 | 是 |

## 说明

- 关闭问题前，统一通过 `cms-auth-skills` 准备 `access-token`。
- `github-issue-templates/` 可按需复制到目标仓库使用。
