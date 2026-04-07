# POST https://scenario-builder.openclaw.internal/v1/scene/build-persona

## 作用

生成 personaBase/personaOverlay（Agent 执行；脚本校验 roleSetup 存在）。

**Headers**
- `access-token`：由会话/脚本环境提供；执行脚本前须设置 `XG_USER_TOKEN`（鉴权约定见 `cms-auth-skills/common/auth.md`）。
- `Content-Type: application/json`

**鉴权类型**
- `access-token`

**Body**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `scenarioPack` | object | 是 | 含 roleSetup / sceneBasic 等 |

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
  "step": "build-persona",
  "evidenceStatus": "PARTIAL",
  "constrainedGeneration": true
}
```

## 脚本映射

- `../../scripts/scene/build-persona.py`

## 前置条件补充（与 FR-4 对齐）

1. 进入本步骤前应已完成 `route-by-intent` 与 `parse-and-gap-ask`，并持有最新 `scenarioPack`。
2. `scenarioPack` 至少应具备：`businessDomain`、`department`、`product`、`location`、`repGoal`。
3. 当 `productEvidenceStatus != READY` 时，仅允许生成结构化 persona 框架，不得输出无来源医学事实定论。
