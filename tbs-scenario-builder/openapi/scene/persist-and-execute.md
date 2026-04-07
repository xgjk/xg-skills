# POST https://scenario-builder.openclaw.internal/v1/scene/persist-and-execute

## 作用

将草稿写入 `scripts/tbs_assets/scenario_draft.json`（或可覆盖 `draftPath`）并子进程执行 `scripts/scene/tbs_write_executor.py`（真实副作用；legacy 布局仍保留回退）。

## 落库侧行为（TBS HTTP，与 FR-4 / 药品主数据对齐）

子进程 `tbs_write_executor.py` 在创建场景前会解析 `apiDraft.scenes` 中的业务领域、科室、**品种**等标识：

- **药品**：对 `drug_id` 或 `drugName` 调用 `GET /api/v1/admin/basic/drugs` 做名称匹配；列表中不存在同名（模糊匹配）品种时，**自动** `POST /api/v1/admin/basic/drugs` 创建，再使用返回的 `drug_id` 写入场景。与公开 API 文档中的「药品 (Drugs)」一致，见工作区 `TBS/TBS_API_REFERENCE.md` §4.4。
- 业务领域、科室同样采用「先查后建」策略，保证 `POST /api/v1/admin/scenes` 所需外键可用。

对话内步骤只需保证 `scenarioPack.product` / 草稿里品种名称清晰一致；**无需** agent 手工去后台建药品。

**与 `preflight-tbs-master-data` 的关系**：若在落库前已运行 `preflight-tbs-master-data.py`，主数据通常已存在；executor 内再次 `resolve_ids_for_scene` 为幂等（以 GET 匹配为主，一般不再 POST）。

**Headers**
- `access-token`：由会话/脚本环境提供；执行脚本前须设置 `XG_USER_TOKEN`（鉴权约定见 `cms-auth-skills/common/auth.md`）。
- `Content-Type: application/json`

**鉴权类型**
- `access-token`

**Body**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `draftPayload` | object | 否 | 若提供则写入 draftPath |
| `draftPath` | string | 否 | 默认本 skill 包 `scripts/tbs_assets/scenario_draft.json`（若不存在则回退 `runtime/scenario_draft.json`） |
| `userConfirmation` | string | 是 | 用户确认口令，**必须为**：`确认` 或 `取消`。仅当为 `确认` 时才允许继续落库 |
| `validationReport` | object | 是 | 须 passed=true |

## 请求 Schema

```json
{
  "type": "object",
  "required": [
    "userConfirmation",
    "validationReport"
  ],
  "properties": {
    "draftPayload": {
      "type": "object"
    },
    "draftPath": {
      "type": "string"
    },
    "userConfirmation": {
      "type": "string"
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
    "message": { "type": "string" }
  }
}
```

## 脚本映射

- `../../scripts/scene/persist-and-execute.py`
