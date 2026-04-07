# skill-management 模块说明

## 模块职责

`skill-management` 在 `cms-create-skill` 内只负责发现：

1. 发现平台已有 Skill。

## 脚本清单

| 脚本 | 说明 | 需要鉴权 |
|---|---|---|
| `get_skills.py` | 查看列表、搜索、查看详情 | 否 |

## 常见场景

| 场景 | 触发意图 | 脚本 |
|---|---|---|
| 用户要查看平台上有哪些 Skill | "查看 Skill 列表"、"有哪些 Skill" | `get_skills.py` |
| 用户要搜索某类 Skill | "搜一下 xxx 相关 Skill" | `get_skills.py --search xxx` |
| 用户要把 Skill 发布到我们内部平台 | "发布 Skill"、"注册 Skill"、"发布到内部平台" | 转交 `cms-push-skill` |
| 用户要更新或下架 Skill | "更新 Skill"、"下架 Skill" | 转交 `cms-push-skill` |

## 发布移交

这里说的“内部平台”，就是当前技能管理平台。

```bash
# 安装发布 Skill
npx clawhub@latest install cms-push-skill --force

# 查看列表
python3 cms-create-skill/scripts/skill-management/get_skills.py

# 内部 Skill：一站式发布到内部平台
python3 cms-push-skill/scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --name "IM 机器人" --internal

# 内部 Skill：更新到内部平台
python3 cms-push-skill/scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --update --version 1.0.0 --internal

# 外部 Skill：同步到平台
python3 cms-push-skill/scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --name "IM 机器人" --external
```

## 说明

- 本模块不再维护发布、更新、下架的重复脚本实现。
- 发布链路统一由 `cms-push-skill` 负责。
- 本模块不维护旧接口文档副本，所有说明都放在 Markdown 文档里。
- 如果你当前在 `cms-create-skill` 里，这里就是发布到内部平台的下一步入口。
