---
name: cms-auth-skills
description: CMS 基础鉴权 Skill。任何业务接口 Header 需要 appKey 或 access-token 时都必须先触发本 Skill。支持从上下文、环境变量、sender_id+account_id、appKey换token，并在失败时向用户索要 appKey（工作协同 key / cowork key）。
skillCode: cms-auth-skills
github: https://github.com/xgjk/xg-skills/tree/main/cms-auth-skills
priority: 1
---

# cms-auth-skills

**版本**: v2.3.2

## 定位

- 本 Skill 只负责鉴权值解析，输出 `appKey` 或 `access-token`
- 术语统一：`appKey = 工作协同 key = cowork key`
- 任何业务接口需要鉴权 Header，都必须先触发本 Skill

## AI 执行总规则

1. 先判断目标接口需要 `appKey` 还是 `access-token`
2. 再按固定优先级解析，不要跳步骤
3. 解析失败时，只向用户索要 `appKey`
4. `appKey` 解析与 `access-token` 解析是两个独立步骤：只需要 `appKey` 时，不要主动换 `access-token`
5. 统一通过 `scripts/auth/login.py` 执行，不需要读取或分析 `scripts/auth/*.py` 源码

## 支持能力（5 条）

1. 支持从上下文/显式参数直接获取 `appKey`、`access-token`
2. 支持从环境变量获取（并做判空）：`XG_BIZ_API_KEY`、`XG_USER_TOKEN`
3. 支持通过 `appKey` 获取 `access-token`
4. 支持通过 `sender_id + account_id` 获取 `appKey`
5. 支持在自动解析失败时向用户索要 `appKey`

## 解析优先级（必须按顺序）

### 目标是 `appKey`

1. 上下文/显式 `appKey`
2. 环境变量 `XG_BIZ_API_KEY`
3. `sender_id + account_id`
4. 向用户索要 `appKey`

### 目标是 `access-token`

1. 上下文/显式 `access-token`
2. 上下文/显式 `appKey` -> 换 `access-token`
3. 环境变量 `XG_USER_TOKEN`
4. 环境变量 `XG_BIZ_API_KEY` -> 换 `access-token`
5. `sender_id + account_id` -> `appKey` -> `access-token`
6. 向用户索要 `appKey`

## 上下文字段兼容

- `appKey`：`appKey` / `app_key` / `appkey`
- `access-token`：`access-token` / `access_token` / `token`
- `sender_id`：`sender_id` / `senderId` / `send_id` / `sendId`
- `account_id`：`account_id` / `accountId`

## CLI

推荐参数：

- `--app-key`
- `--access-token`
- `--sender-id`
- `--account-id`
- `--resolve-app-key`
- `--ensure`
- `--update`

兼容旧调用：

- `--context-json`

### 常用示例

```bash
# 直接返回 token
python3 login.py --ensure --access-token "your-token"

# 用 appKey 换 token
python3 login.py --ensure --app-key "your-app-key"

# 只解析 appKey
python3 login.py --resolve-app-key --sender-id "user-001" --account-id "xgjk_prod"

# 兼容旧调用
python3 login.py --ensure --context-json '{"appKey":"your-app-key"}'
```
