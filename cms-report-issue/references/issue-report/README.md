# issue-report 模块说明

## 模块职责

`cms-report-issue` 负责 Skill 问题闭环：

1. 提交问题。
2. 查看问题列表和统计。
3. 解决或关闭问题。

## 脚本清单

| 脚本 | 说明 | 需要鉴权 |
|---|---|---|
| `report_issue.py` | 提交问题，支持命令行和 stdin 管道输入 | 否 |
| `list_issues.py` | 查看问题列表、按条件筛选、查看统计 | 否 |
| `update_issue.py` | 将问题更新为 `resolved` 或 `closed` | 是 |

## 状态流转

```text
open -> resolved -> closed
```

## 常见场景

| 场景 | 脚本 |
|---|---|
| Skill 运行异常，需要快速提交问题 | `report_issue.py` |
| 想看某个 Skill 还有哪些未处理问题 | `list_issues.py --skill-code ...` |
| 问题已修复，需要标记解决 | `update_issue.py --status resolved` |
| 问题确认结案 | `update_issue.py --status closed` |

## GitHub 模板

`github-issue-templates/` 下提供标准化的 GitHub Issue 模板，可按需复制到目标仓库的 `.github/ISSUE_TEMPLATE/` 中使用。

## 鉴权边界

- 问题提交和查看默认可直接调用。
- 问题状态更新前，统一通过 `cms-auth-skills` 准备 `access-token`。
- 本模块不自己处理登录或换取 token。
