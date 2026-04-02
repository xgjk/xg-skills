# skill-management 脚本清单

## 脚本列表

| 脚本 | 接口文档 | 说明 | 需要鉴权 |
|---|---|---|---|
| **`publish_skill.py`** | [publish-skill.md](../../openapi/skill-management/publish-skill.md) | **一站式发布：打包→上传→注册/更新** | **是** |
| `pack_skill.py` | [pack-skill.md](../../openapi/skill-management/pack-skill.md) | 打包 Skill 目录为 ZIP | 否 |
| `upload_to_qiniu.py` | [upload-to-qiniu.md](../../openapi/skill-management/upload-to-qiniu.md) | 获取七牛凭证 + 上传文件 | 是 |
| `register_skill.py` | [register-skill.md](../../openapi/skill-management/register-skill.md) | 注册（发布）新 Skill | 是 |
| `update_skill.py` | [update-skill.md](../../openapi/skill-management/update-skill.md) | 更新已有 Skill | 是 |
| `delete_skill.py` | [delete-skill.md](../../openapi/skill-management/delete-skill.md) | 下架（删除）Skill | 是 |
| `get_skills.py` | [get-skills.md](../../openapi/skill-management/get-skills.md) | 获取 Skill 列表 | 否 |

## 环境变量

| 变量 | 必填 | 说明 |
|---|---|---|
| `XG_USER_TOKEN` | publish/upload/register/update/delete | access-token；建议先通过 `cms-auth-skills` 获取并写入环境变量，pack 和 get-skills 无需鉴权 |

## 内部 / 外部说明

- **内部 Skill**：按我方协议生成的 Skill，发布时走 `打包 → 上传七牛 → 注册/更新`
- **外部 Skill**：通常已存在于 ClawHub，目标是同步到我方平台；发布时跳过七牛上传，直接使用 ClawHub 下载地址
- 当用户说“我在 ClawHub 找到一个 Skill，帮我同步到我们平台”时，应使用外部模式

## 一站式发布（推荐）

先通过 `cms-auth-skills` 准备好 `access-token`，再执行以下命令。

```bash
# 内部 Skill：首次发布（打包 + 上传七牛 + 注册，一条命令搞定）
python3 scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --name "IM 机器人" --internal

# 内部 Skill：更新已有 Skill（打包 + 上传七牛 + 更新）
python3 scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --update --version 2 --internal

# 外部 Skill：发布到平台（跳过七牛上传，下载地址固定为 ClawHub）
python3 scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --name "IM 机器人" --external
```

外部 Skill 发布时，脚本会自动使用：

```text
https://wry-manatee-359.convex.site/api/v1/download?slug=<skillCode>
```

例如 `skillCode=im-robot` 时，对应下载地址为：

```text
https://wry-manatee-359.convex.site/api/v1/download?slug=im-robot
```

## 分步操作

```bash
# 查看当前已发布的 Skill（无需 token）
python3 scripts/skill-management/get_skills.py

# 仅打包（无需 token）
python3 scripts/skill-management/pack_skill.py ./im-robot

# 仅上传（需要 XG_USER_TOKEN）
python3 scripts/skill-management/upload_to_qiniu.py ./im-robot.zip

# 仅注册（需要 XG_USER_TOKEN）
python3 scripts/skill-management/register_skill.py \
  --code im-robot --name "IM 机器人" --download-url "https://..."

# 仅更新（需要 XG_USER_TOKEN）
python3 scripts/skill-management/update_skill.py \
  --code im-robot --download-url "https://..." --version 2

# 下架（需要 XG_USER_TOKEN）
python3 scripts/skill-management/delete_skill.py --id 123 --reason "已废弃"
```
