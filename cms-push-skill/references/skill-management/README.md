# skill-management 模块说明

## 模块职责

`cms-push-skill` 只负责发布链路：

1. 打包 Skill 目录为 ZIP。
2. 上传内部 Skill 到七牛。
3. 注册、更新、下架 Skill。
4. 同步外部 Skill 到平台。

## 脚本清单

| 脚本 | 说明 | 需要鉴权 |
|---|---|---|
| `publish_skill.py` | 一站式发布 / 更新 / 同步 | 是 |
| `pack_skill.py` | 打包 Skill 目录为 ZIP | 否 |
| `upload_to_qiniu.py` | 获取七牛凭证并上传 ZIP | 是 |
| `register_skill.py` | 注册新 Skill | 是 |
| `update_skill.py` | 更新已有 Skill | 是 |
| `delete_skill.py` | 下架 Skill | 是 |

## 常见场景

| 场景 | 脚本 |
|---|---|
| 发布到我们内部平台 | `publish_skill.py --internal` |
| 更新内部 Skill | `publish_skill.py --update --internal` |
| 同步外部 Skill | `publish_skill.py --external` |
| 只打包 ZIP | `pack_skill.py` |
| 只更新注册信息 | `update_skill.py` |
| 下架 Skill | `delete_skill.py` |

## 内部平台发布

这里说的“内部平台”，就是当前技能管理平台。

```bash
# 先准备鉴权
npx clawhub@latest install cms-auth-skills --force

# 发布到内部平台
python3 cms-push-skill/scripts/skill-management/publish_skill.py \
  ./my-skill --code my-skill --name "My Skill" --internal

# 更新内部平台上的 Skill
python3 cms-push-skill/scripts/skill-management/publish_skill.py \
  ./my-skill --code my-skill --update --version 1.1.0 --internal
```

## 问题反馈边界

- 如果用户要提交问题、查看问题列表、解决或关闭问题，统一转交 `cms-report-issue`。
- `cms-push-skill` 不再承担任何问题反馈职责。
- 具体接力方式见 `references/issue-report/README.md`。

## 鉴权边界

- `pack_skill.py` 不需要鉴权。
- 其余写操作统一通过 `cms-auth-skills` 准备 `access-token`。
- 本模块不维护旧接口文档副本，所有说明都放在 Markdown 文档里。
