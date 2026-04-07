# issue-report 模块说明

`cms-create-skill` 不再内置问题反馈实现。

如果用户在创建完成后要提交问题、查看问题列表、解决或关闭问题，统一转交 `cms-report-issue`。

## 交接命令

```bash
# 安装问题反馈 Skill
npx clawhub@latest install cms-report-issue --force

# 提交问题
python3 cms-report-issue/scripts/issue_report/report_issue.py \
  --skill-code my-skill --version 1.0.0 --error "..."

# 查看问题
python3 cms-report-issue/scripts/issue_report/list_issues.py --skill-code my-skill

# 标记已解决
python3 cms-report-issue/scripts/issue_report/update_issue.py \
  --issue-id abc123 --status resolved --resolution "已修复"
```

## 说明

- `cms-create-skill` 只保留依赖声明，不再维护 `issue_report` 脚本目录。
- 问题状态更新需要的鉴权规则，由 `cms-report-issue` 自己负责。
- 如果你当前正在 `cms-create-skill` 里，这里就是问题反馈的下一步入口。
