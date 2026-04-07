# POST https://scenario-builder.openclaw.internal/v1/scene/validate-and-gate

## 作用

输出 validationReport（Agent 执行；脚本校验三对象齐全）。

**Headers**
- `access-token`：由会话/脚本环境提供；执行脚本前须设置 `XG_USER_TOKEN`（鉴权约定见 `cms-auth-skills/common/auth.md`）。
- `Content-Type: application/json`

**鉴权类型**
- `access-token`

**Body**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `scenarioPack` | object | 是 |  |
| `apiDraft` | object | 是 |  |
| `validationReport` | object | 是 |  |

## 请求 Schema

```json
{
  "type": "object",
  "required": [
    "scenarioPack",
    "apiDraft",
    "validationReport"
  ],
  "properties": {
    "scenarioPack": {
      "type": "object"
    },
    "apiDraft": {
      "type": "object"
    },
    "validationReport": {
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
    "passed": { "type": "boolean" },
    "evidenceStatus": { "type": "string" },
    "issues": { "type": "array" }
  }
}
```

## 证据状态闭环校验（强制）

1. 脚本会读取 `scenarioPack.productEvidenceStatus`，仅允许：`NOT_PROVIDED` / `PARTIAL` / `READY`。
2. 当 `productEvidenceStatus != READY` 时，必须满足：
   - `apiDraft.needsEvidenceConfirmation=true`
   - `scenarioPack.productEvidenceSource` 非空（至少一个来源标识）
3. 若上述条件不满足，`passed` 必须为 `false`，并在 `issues` 给出缺口原因。

## 脚本映射

- `../../scripts/scene/validate-and-gate.py`

## Agent 可见性（强制）

- `validationReport` 可经表格等形式向用户概括通过/未通过项，**禁止**贴完整 JSON；与 `apiDraft` 同见根目录 `SKILL.md`「用户可见输出规范」第 9 条。
