# POST https://scenario-builder.openclaw.internal/v1/scene/publish-ready-compose

## 作用

publish_ready 模式下的策略与槽位（Agent 执行；脚本校验开关）。

**Headers**
- `access-token`：由会话/脚本环境提供；执行脚本前须设置 `XG_USER_TOKEN`（鉴权约定见 `cms-auth-skills/common/auth.md`）。
- `Content-Type: application/json`

**鉴权类型**
- `access-token`

**Body**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `scenarioPack` | object | 是 | 草案 |
| `modeHints` | object | 是 | 须含 `publish_ready: true` 或 `outputMode`: `publish_ready` |

## 请求 Schema

```json
{
  "type": "object",
  "required": [
    "scenarioPack",
    "modeHints"
  ],
  "properties": {
    "scenarioPack": {
      "type": "object"
    },
    "modeHints": {
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
    "message": { "type": "string" }
  }
}
```

## 脚本映射

- `../../scripts/scene/publish-ready-compose.py`
