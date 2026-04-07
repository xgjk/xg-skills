# skill-management 脚本清单

## 模块定位

`skill-management` 在 `cms-create-skill` 中只保留发现能力：

1. 查看平台已有 Skill。

对应说明统一见 `../../references/skill-management/README.md`。

## 脚本列表

| 脚本 | 说明 | 需要鉴权 |
|---|---|---|
| `get_skills.py` | 获取 Skill 列表、搜索、详情 | 否 |

## 发布移交

```bash
# 查看当前已发布的 Skill
python3 scripts/skill-management/get_skills.py

# 一站式发布内部 Skill
python3 cms-push-skill/scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --name "IM 机器人" --internal
```

## 说明

- 发布、更新、下架脚本已经从 `cms-create-skill` 中剥离。
- 如需继续发布链路，统一转交 `cms-push-skill`。
