# POST https://scenario-builder.openclaw.internal/v1/scene/build-api-draft-dedup

## 作用

组装 apiDraft 与 dedupEvidence（Agent 执行；脚本校验键存在）。

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
| `factGuardPolicy` | object | 是 | 事实结论阻断策略（参数传入，禁止脚本硬编码） |

## 请求 Schema

```json
{
  "type": "object",
  "required": [
    "scenarioPack",
    "apiDraft"
  ],
  "properties": {
    "scenarioPack": {
      "type": "object"
    },
    "apiDraft": {
      "type": "object"
    },
    "factGuardPolicy": {
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

**请求示例（证据未 READY）**
```json
{
  "scenarioPack": {
    "productEvidenceStatus": "PARTIAL",
    "productEvidenceSource": ["api://product/vitco/overview-card"]
  },
  "apiDraft": {
    "needsEvidenceConfirmation": true
  },
  "factGuardPolicy": {
    "blockedFactKeys": ["efficacyConclusion", "safetyConclusion", "numericClaims", "comparativeConclusion"],
    "blockedPhrases": ["显著优于", "疗效更好", "安全性更高"]
  }
}
```

**响应示例**
```json
{
  "ok": true,
  "step": "build-api-draft-dedup",
  "evidenceStatus": "PARTIAL",
  "constrainedGeneration": true
}
```

## 脚本映射

- `../../scripts/scene/build-api-draft-dedup.py`

## Agent 可见性（强制）

- `apiDraft` 与 `dedupEvidence` 为写库契约，**不得**在对话中以代码块或「API Draft」类标题输出（含部分字段）；用户侧仅保留自然语言摘要与确认话术（见根目录 `SKILL.md`「用户可见输出规范」第 9 条）。

## 前置条件补充（与 FR-4 对齐）

1. 进入本步骤前应已具备：发布级骨架、persona、prompts（串行模式）或用户指定的最小独立输入。
2. `apiDraft` 中涉及产品事实的段落必须可追溯到 `productEvidenceSource` 或用户原文证据。
3. 当 `productEvidenceStatus != READY` 时，事实型段落必须标记为“待确认来源”，不得输出确定性比较结论。
4. 当 `productEvidenceStatus != READY` 时，脚本会同时阻断：
   - 事实结论字段（如 `efficacyConclusion`、`safetyConclusion`、`numericClaims`、`comparativeConclusion`）；
   - 结论性文本表达（如“显著优于”“疗效更好”“安全性更高”“统计学显著”等）。
