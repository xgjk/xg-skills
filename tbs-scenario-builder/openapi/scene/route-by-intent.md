# POST https://scenario-builder.openclaw.internal/v1/scene/route-by-intent

## 作用

根据用户消息与会话状态给出主意图与下一跳步骤（由 Agent 推理；脚本做最小契约校验）。

**Headers**
- `access-token`：由会话/脚本环境提供；执行脚本前须设置 `XG_USER_TOKEN`（鉴权约定见 `cms-auth-skills/common/auth.md`）。
- `Content-Type: application/json`

**鉴权类型**
- `access-token`

**Body**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `userText` | string | 是 | 用户原话 |
| `routeDecision` | object | 是 | 上游路由决策结果（参数驱动） |
| `modeHints` | object | 否 | 如 publish_ready |
| `sessionState` | object | 否 | 已有 scenarioPack 等 |

## 请求 Schema

```json
{
  "type": "object",
  "required": [
    "userText",
    "routeDecision"
  ],
  "properties": {
    "userText": {
      "type": "string"
    },
    "modeHints": {
      "type": "object"
    },
    "routeDecision": {
      "type": "object"
    },
    "sessionState": {
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
    "intent": { "type": "string" },
    "nextStep": { "type": "string" },
    "reason": { "type": "string" },
    "needClarification": { "type": "boolean" },
    "clarifyQuestion": { "type": "string" },
    "preconditions": { "type": "array" }
  }
}
```

## 路由规则补充（强制）

1. 本脚本只做参数校验，不做文本关键词推断；路由意图必须由上游通过 `routeDecision` 传入。
2. `PERSIST_CONFIRM` 必须校验上下文前置条件（如 `sessionState.validationReport.passed=true`）；不满足时不得直接路由落库。
3. 返回 `preconditions` 列出下一步缺失条件，便于调用方补齐（例如“缺少 validationReport.passed=true”）。

## 脚本映射

- `../../scripts/scene/route-by-intent.py`
