# POST https://scenario-builder.openclaw.internal/v1/scene/build-prompts

## 作用

生成 promptBundle 四段（Agent 执行；脚本校验 persona 已存在）。

**Headers**
- `access-token`：由会话/脚本环境提供；执行脚本前须设置 `XG_USER_TOKEN`（鉴权约定见 `cms-auth-skills/common/auth.md`）。
- `Content-Type: application/json`

**鉴权类型**
- `access-token`

**Body**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `scenarioPack` | object | 是 | 完整度递增的 scenarioPack |

## 请求 Schema

```json
{
  "type": "object",
  "required": [
    "scenarioPack"
  ],
  "properties": {
    "scenarioPack": {
      "type": "object"
    }
  }
}
```

## 响应 Schema（脚本 TOON 摘要，示意）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "ok": { "type": "boolean" },
    "step": { "type": "string" },
    "evidenceStatus": { "type": "string" },
    "constrainedGeneration": { "type": "boolean" }
  }
}
```

**响应示例**
```json
{
  "ok": true,
  "step": "build-prompts",
  "evidenceStatus": "NOT_PROVIDED",
  "constrainedGeneration": true
}
```

## 脚本映射

- `../../scripts/scene/build-prompts.py`

## 前置条件补充（与 FR-4 对齐）

1. 进入本步骤前应已形成可用 persona（来自 `build-persona` 或等效产物）。
2. `scenarioPack` 中需保留风格约束（如“自然交流、非背书式”）并映射到 prompts。
3. 当 `productEvidenceStatus != READY` 时，提示词可生成沟通框架与追问路径，但不得包含无来源医学结论。
