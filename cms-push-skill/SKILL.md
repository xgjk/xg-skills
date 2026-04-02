---
name: cms-push-skill
description: CMS Skill 推送工具 — 将已创建的 Skill 打包、上传、注册/更新/下架到平台，同步到 ClawHub 和 GitHub；同时包含问题反馈与状态管理
skillCode: cms-push-skill
dependencies:
  - cms-auth-skills
---

**当前版本**: v1.0.2

# cms-push-skill

两大职责：① 将已完成的 Skill 推送到平台；② 问题反馈与状态管理。

## 能力总览

| # | 能力 | 脚本 | 需要 token |
|---|------|------|-----------|
| 1 | 注册新 Skill | `scripts/skill-management/register_skill.py` | 是 |
| 2 | 更新已有 Skill | `scripts/skill-management/update_skill.py` | 是 |
| 3 | 下架 Skill | `scripts/skill-management/delete_skill.py` | 是 |
| 4 | 一站式发布（打包+上传+注册/更新+同步） | `scripts/skill-management/publish_skill.py` | 是 |
| 5 | 打包 Skill 目录为 ZIP | `scripts/skill-management/pack_skill.py` | 否 |
| 6 | 上传文件到七牛 | `scripts/skill-management/upload_to_qiniu.py` | 是 |
| 7 | 问题反馈（上报问题） | `scripts/issue_report/report_issue.py` | 否 |
| 8 | 查看问题列表 | `scripts/issue_report/list_issues.py` | 否 |
| 9 | 更新问题状态 | `scripts/issue_report/update_issue.py` | 是 |

## 路由

### 推送相关

- 首次发布：`python3 publish_skill.py ./my-skill --code my-skill --name "My Skill"`
- 更新发布：`python3 publish_skill.py ./my-skill --code my-skill --update --version 1.1.0`
- 外部发布：`python3 publish_skill.py ./my-skill --code my-skill --name "My Skill" --external`
- 注册：`python3 register_skill.py --code my-skill --name "My Skill"`
- 更新：`python3 update_skill.py --code my-skill --name "New Name"`
- 下架：`python3 delete_skill.py --id <skill-id> --reason "原因"`

### 问题管理

- 上报问题：`python3 report_issue.py --skill-code my-skill --version 1.0.0 --error "ConnectionError" --message "连接超时"`
- 管道上报：`python3 some_script.py 2>&1 | python3 report_issue.py --skill-code my-skill --version 1.0.0 --stdin`
- 查看问题：`python3 list_issues.py --skill-code my-skill`
- 按状态筛选：`python3 list_issues.py --status open --severity error`
- 统计概览：`python3 list_issues.py --stats`
- 更新状态：`python3 update_issue.py --issue-id abc123 --status resolved --resolution "已修复"`

### GitHub Issue 模板应用

`cms-push-skill` 提供了标准化的 GitHub Issue 表单模板集合（位于 `github-issue-templates/` 目录），包含 Bug 报告、功能请求、问题支持等十余种场景的 YAML 模板及配置文件 `config.yml`。

**使用引用方式：**
当我们在发布一个新 Skill，并需要通过 GitHub 管理 Issue 时，可以将这些模板复制到你的仓库目录中（如 `.github/ISSUE_TEMPLATE` 目录）。这样，在 GitHub 页面上新建 Issue 时将自动展现这些表单，规范用户反馈，并通过 Webhook 等机制联动到咱们平台。

### 装饰器自动捕获

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'cms-push-skill', 'scripts'))
from issue_report.report_issue import auto_catch, report_issue

@auto_catch(skill_code="my-skill", version="1.0.0")
def main():
    do_something()  # 异常自动上报到管理平台
```

## 同步选项

`publish_skill.py` 支持同步到 ClawHub 和 GitHub：

- `--sync-clawhub` — 同步到 ClawHub（内部 Skill 默认启用）
- `--sync-github` — 同步到 GitHub（内部 Skill 默认启用）
- `--no-sync-clawhub` — 不同步到 ClawHub
- `--no-sync-github` — 不同步到 GitHub

内部 Skill 默认两者都推，外部 Skill 不支持推送到 ClawHub。

## 问题状态流转

```
open → resolved → closed
```

## 规则

1. 所有接口使用 ClawHub 协议格式
2. 版本号使用 semver 格式（如 1.2.0）
3. 推送前必须通过 cms-auth-skills 获取 access-token
4. 内部 Skill 走七牛上传 + 平台注册
5. 外部 Skill 跳过七牛上传，使用 ClawHub 下载地址
6. 问题反馈零依赖 — 仅使用 Python 标准库
7. 问题上报失败不阻塞业务（装饰器模式下异常重新抛出）

## 环境变量

- `XG_USER_TOKEN` — access-token（推送和问题状态更新必须）

## 能力树

```
cms-push-skill/
├── SKILL.md                                    # 本文件（技能定义）
├── github-issue-templates/                     # GitHub Issue 表单模板仓库
│   ├── config.yml                              # 模板使用说明、链接等全局配置
│   ├── bug_report.yml                          # 缺陷反馈表单模板
│   ├── feature_request.yml                     # 需求/功能请求表单模板
│   └── ...                                     # 性能、集成、安全等更多分类模板
└── scripts/
    ├── skill-management/
    │   ├── register_skill.py                   # 注册新 Skill
    │   ├── update_skill.py                     # 更新已有 Skill
    │   ├── delete_skill.py                     # 下架 Skill
    │   ├── publish_skill.py                    # 一站式发布（打包+上传+注册/更新+同步）
    │   ├── pack_skill.py                       # 打包 Skill 目录为 ZIP
    │   └── upload_to_qiniu.py                  # 上传文件到七牛
    └── issue_report/
        ├── __init__.py
        ├── report_issue.py                     # 问题反馈（上报问题到平台）
        ├── list_issues.py                      # 查看/筛选问题列表 + 统计
        └── update_issue.py                     # 更新问题状态（resolved/closed）
```
