# POST https://scenario-builder.openclaw.internal/v1/scene/parse-and-gap-ask

## 作用

从自然语言抽取场景字段并标记缺口（Agent 执行；脚本对**核心五元组**做硬性校验，其余字段按发布级在后续步骤与闸门补齐）。

**Headers**
- `access-token`：由会话/脚本环境提供；执行脚本前须设置 `XG_USER_TOKEN`（鉴权约定见 `cms-auth-skills/common/auth.md`）。
- `Content-Type: application/json`

**鉴权类型**
- `access-token`

**Body**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `userText` | string | 是 | 用户描述 |
| `parsedFields` | object | 是 | 上游结构化解析结果（参数驱动） |
| `scenarioPack` | object | 否 | 解析出的草案 |
| `missingFields` | array | 否 | 缺口列表 |
| `productCandidates` | array | 否 | 产品候选（参数驱动，建议由上游 API 返回后传入） |
| `knowledgeSearchResult` | object | 否 | 知识库预检结果（可由上游注入，未提供则由当前步骤执行预检） |

## 请求 Schema

```json
{
  "type": "object",
  "required": [
    "userText",
    "parsedFields"
  ],
  "properties": {
    "userText": {
      "type": "string"
    },
    "scenarioPack": {
      "type": "object"
    },
    "parsedFields": {
      "type": "object"
    },
    "missingFields": {
      "type": "array"
    },
    "productCandidates": {
      "type": "array"
    },
    "knowledgeSearchResult": {
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

## 解析输出契约（Agent 语义层，强制）

`scenarioPack` 在本阶段至少维护以下字段（缺失可不填值但需进入 `missingFields`）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `department` | string | 部门/科室（如“神经内科门诊”） |
| `product` | string | 品种/产品（如“维图可”） |
| `location` | string | 地点（机构 + 场景） |
| `doctorConcerns` | string[] | 医生隐含顾虑（2-4 条，去重） |
| `repGoal` | string | 医药代表目标（单句、可执行） |
| `productKnowledgeNeeds` | string[] | 产品知识需求主题（2-6 条） |
| `productEvidenceStatus` | enum | `NOT_PROVIDED` / `PARTIAL` / `READY` |
| `productEvidenceSource` | array | 已命中的资料来源标识（契约层：文件名/URL/系统检索回写的来源 token）；**对用户话术不得**要求用户自行提供此类标识 |

**`product` 与 TBS 药品表（落库时）**：本阶段只需给出**准确、可匹配的产品名**（与业务口径一致）。用户确认落库后，`tbs_write_executor.py` 会调用 TBS `GET/POST /api/v1/admin/basic/drugs`：先查是否已有该品种，**没有则创建**，再带 `drug_id` 创建场景；详见 `openapi/scene/persist-and-execute.md` 与 `TBS/TBS_API_REFERENCE.md` §4.4 药品接口。

**最小结构示意**

```json
{
  "scenarioPack": {
    "department": "神经内科门诊",
    "product": "维图可",
    "location": "三级医院-神经内科门诊",
    "doctorConcerns": [
      "药品未进院导致院内可及性不足",
      "对产品认知不足",
      "缺乏院前癫痫急救处方经验"
    ],
    "repGoal": "争取主任沟通时间并自然传递维图可产品特点",
    "productKnowledgeNeeds": [
      "维图可基础认知与临床定位",
      "院前癫痫急救相关使用场景要点",
      "首次处方决策中的风险边界与注意事项",
      "未进院条件下的可及性与沟通策略"
    ],
    "productEvidenceStatus": "PARTIAL",
    "productEvidenceSource": [
      "kb://product/vitco/overview-card"
    ]
  }
}
```

## 脚本映射

- `../../scripts/scene/parse-and-gap-ask.py`

## 用户可见话术（parse-and-gap-ask，强制）

本节约束 **Agent 对用户的自然语言回复**；契约字段名仍可出现在 `scenarioPack` / 脚本入参中，但 **不得照抄到用户消息里**。

1. **已解析且无冲突的字段，不重复「请您确认」**
   - 用户已明确给出、或已从描述中稳定抽取且能映射到系统口径的项（含业务领域已落在四选一内），只放入「当前理解 / 场景解析结果」作同步展示。
   - 仅当 **缺失**、**与用户原文矛盾**、或 **置信度不足需二选一** 时，才列入「需要您补充或确认」；不得把已成立的「临床推广」等再包装成待确认项。

2. **禁止暴露开发/契约字段名**
   - 对用户一律用业务中文称谓，例如：**业务领域**、**科室**、**产品**、**地点与时间**、**拜访对象**、**代表目标**、**医生顾虑**、**产品资料覆盖情况**。
   - **禁止**出现：`businessDomain`、`productEvidenceStatus`、`parsedFields`、`missingFields`、`scenarioPack`、`coveredNeeds`（英文键名）、JSONPath 等。

3. **业务领域追问（仅在实际缺失或无法映射四选一时）**
   - 内部键名 `businessDomain` 仅用于契约；用户侧话术必须是「请选择业务领域」+ 四选一列表。
   - 若已从用户描述判定为四选一之一且无冲突，**不要**再发起「业务领域是哪一个」类追问。

4. **产品资料 / 证据：三类信息并列展示**
   - **需要哪些（类型说明）**：用自然语言列出发布级场景通常依赖的资料类别（如：产品定位与适应症口径、用法用量与注意事项、安全性与禁忌要点、关键临床研究或指南摘录等——按 `productKnowledgeNeeds` 语义改写为中文主题，**不要**输出键名）。
   - **已具备**：根据知识库预检结果，用「已从企业资料库关联到 / 已覆盖的主题：…」表述；可概括主题名称，**不要**罗列系统 ID。
   - **仍需您补充**：仅列仍未覆盖的主题；引导用户 **上传文件、粘贴可引用摘要、或提供可公开访问的文献/说明书链接**。
   - **禁止**向用户索要：`知识卡 ID`、内部知识库条目链接、任何需用户从后台复制的技术标识。此类由检索/API 或落库链路写入，用户只需提供内容素材。

## 缺口追问规范（强制）

1. 对缺失字段做用户可见追问时，优先使用简短、可直接回答的问法。
2. `businessDomain` 缺失时，必须使用固定四选一，不得开放式追问。
3. 固定选项来源：`scripts/tbs_assets/system_business_domains.json`。

**业务领域追问模板（推荐，仅在实际缺失时使用）**

```text
请选择业务领域（四选一）：
1) 临床推广
2) 院外零售
3) 学术合作
4) 通用能力
```

## 产品知识需求识别与预检分流（强制）

1. 本脚本不做文本解析与兜底，`parsedFields` 必须由上游解析后传入。
2. 产品识别采用参数驱动：优先从 `productCandidates` 或 `knowledgeSearchResult.hits[].productName` 获取；不做文本兜底识别。
3. 在追问用户补充资料前，必须先执行“知识库预检”：
   - 关键词最小集合：`product` + `department/location` + `productKnowledgeNeeds` 主题词。
   - 可使用 `knowledgeSearchResult`（若上游已提供）或在本步骤内触发检索。
   - 知识来源必须来自产品知识 API；本地文件路径来源不得计入覆盖度。
   - 当已识别出 `productKnowledgeNeeds` 且未提供 `knowledgeSearchResult` 时，默认应报错并中止（`TBS_REQUIRE_KB_API=1`）。
4. 覆盖度计算：`coveredNeeds / totalNeeds`。
   - 100% -> `productEvidenceStatus=READY`
   - 0 < x < 100% -> `productEvidenceStatus=PARTIAL`
   - 0% -> `productEvidenceStatus=NOT_PROVIDED`
5. 仅当覆盖不足时追问用户，且只追问“未覆盖主题”所需资料，不得全量重问。

## 证据闸门（强制）

- 当 `productEvidenceStatus != READY`：
  - 允许：输出知识需求清单、追问、沟通框架草案。
  - 禁止：输出具体疗效/安全性定论、具体数值结论、无来源比较结论。
- 当 `productEvidenceStatus=READY`：
  - 允许进入后续内容生成，并在产物中保留来源可追溯信息。

## `missingFields` 输出规则（补充）

1. 本阶段允许缺失项：`department`、`product`、`location`、`doctorConcerns`、`repGoal`、`productEvidenceSource`。
2. 仅在知识库预检后仍缺失时，才把 `productEvidenceSource` 放入 `missingFields`。
3. `missingFields` 禁止暴露内部路径名（如 JSONPath），必须保持用户可理解。

## 覆盖度输出（建议）

- 建议同时返回：
  - `coveredNeeds`：已被 API 知识库命中的知识主题
  - `uncoveredNeeds`：未命中的知识主题（用于追问）
- 不应只返回缺失项，否则用户无法确认“已有知识范围”。
- 当用户仅请求“查看/展示当前结果”且未新增事实输入时，只允许回显已有字段与覆盖状态，不得扩写具体产品知识细节。

## `knowledgeSearchResult` 推荐结构（建议）

```json
{
  "sourceApi": "/api/v1/admin/basic/knowledge",
  "hits": [
    {
      "source": "api://product/vitco/overview-card",
      "score": 0.91,
      "coveredNeeds": [
        "产品基础认知与临床定位",
        "可及性与准入沟通策略"
      ]
    }
  ]
}
```

- `sourceApi`：必须标识知识来源接口，默认要求 `/api/v1/admin/basic/knowledge`。
- `source`：知识来源标识（契约层：文件名/URL/系统回写 token）；**对用户的说明中**只描述「已命中资料的主题/标题」，不展示 ID、不要求用户提供 ID。
- `score`：检索相关度分值（0-1，供排序或阈值过滤）。
- `coveredNeeds`：该命中项覆盖的知识需求主题（需与 `productKnowledgeNeeds` 同语义）。
- `source` 默认仅接受 `api://` 或 `https://` 前缀（可通过环境变量 `TBS_KB_SOURCE_PREFIXES` 覆盖）。
- 若需要临时关闭“必须先查 API”强约束，可设置 `TBS_REQUIRE_KB_API=0`。
- 若知识接口路径变更，可通过 `TBS_KNOWLEDGE_API_PATH` 覆盖默认值。

## 语义抽取验收方式（建议）

契约脚本只校验 `userText` 等**入参形状**；真正的语义抽取（生成缺口、填充字段、组织追问）在 OpenClaw 对话内由 Agent 完成。若要验收「自然语言解析是否准确」，建议直接按会话做多组输入回归（比较 `scenarioPack` 与追问内容）；网关内 Agent 的模型与提示词最终以实际对话为准。
