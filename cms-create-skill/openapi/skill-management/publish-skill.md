# 一站式发布 Skill（内部：打包 → 上传七牛 → 注册/更新；外部：直接注册/更新）

## 作用

一键完成 Skill 发布到平台的完整流程。

内部 Skill：
1. 将 Skill 目录打包为 ZIP
2. 获取七牛凭证并上传 ZIP
3. 用下载地址注册（或更新）Skill 到平台

外部 Skill：
1. 跳过七牛上传
2. 直接使用 ClawHub 下载地址注册（或更新）Skill 到平台

支持两种模式：
- **注册模式**（默认）：首次发布新 Skill
- **更新模式**（`--update`）：更新已发布 Skill 的包和信息
- **外部模式**（`--external`）：使用固定 ClawHub 下载地址

## 内部 / 外部说明

- **内部 Skill**：按我方协议生成的 Skill，适用于本地已完成打包内容的发布
- **外部 Skill**：通常是用户已在 ClawHub 找到的 Skill，目标是同步到我方平台，而不是重新按协议创建
- 用户如果说“把 ClawHub 上这个 skill 同步到我们平台”，应直接使用外部模式

## Headers

| Header | 必填 | 说明 |
|---|---|---|
| `access-token` | 是 | 鉴权 token（依赖 `cms-auth-skills/common/auth.md` 获取），用于七牛上传和注册/更新 |

## 参数表

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `skill_dir` | string | 是 | Skill 目录路径 |
| `--code` | string | 是 | Skill 唯一标识 |
| `--name` | string | 注册时必须 | Skill 名称 |
| `--description` | string | 否 | Skill 描述 |
| `--label` | string | 否 | Skill 标签 |
| `--version` | integer | 否 | 版本号（更新时使用） |
| `--update` | flag | 否 | 更新模式（默认注册模式） |
| `--output` | string | 否 | ZIP 输出路径（默认 `<skill-name>.zip`） |
| `--file-key` | string | 否 | 七牛文件 key（默认自动生成） |
| `--internal` | flag | 否 | 标记为内部 Skill |
| `--external` | flag | 否 | 标记为外部 Skill，下载地址固定为 ClawHub |

## 使用示例

```bash
# 内部 Skill：首次发布
python3 cms-create-skill/scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --name "IM 机器人" --description "管理 IM 机器人" --internal

# 内部 Skill：更新已有 Skill
python3 cms-create-skill/scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --update --version 2 --internal

# 外部 Skill：发布到平台（跳过七牛上传）
python3 cms-create-skill/scripts/skill-management/publish_skill.py \
  ./im-robot --code im-robot --name "IM 机器人" --external
```

外部模式的下载地址固定为：

```text
https://wry-manatee-359.convex.site/api/v1/download?slug={skillCode}
```

## 流程

内部 Skill：

```
skill_dir → pack_skill.py → .zip → upload_to_qiniu.py → download_url → register/update_skill.py
```

外部 Skill：

```
skill_dir → https://wry-manatee-359.convex.site/api/v1/download?slug={skillCode} → register/update_skill.py
```

## 脚本映射

- 执行脚本：`../../scripts/skill-management/publish_skill.py`
