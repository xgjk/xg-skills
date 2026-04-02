---
name: tbs-scenario-builder
description: 编排并执行训练场景（TBS）创建流程：意图路由、字段解析与追问、发布级骨架、persona/prompts 生成、apiDraft 去重证据、统一校验闸门与确认后落库。**禁止**用浏览器自动化操作 TBS 管理后台；落库仅经脚本 API。
skillcode: tbs-scenario-builder
github: https://github.com/xgjk/xg-skills/tree/main/CMS-tbs-scenario-builder
dependencies:
  - cms-auth-skills
---

# tbs-scenario-builder — 索引

本文件提供**能力宪章 + 能力树 + 按需加载规则**。详细参数与流程见各模块 `openapi/` 与 `examples/`。

`scene` 模块为 **OpenClaw 编排契约层**逻辑端点（见宪章第 11 条）；鉴权与通用约束仍以 `cms-auth-skills/SKILL.md` 为准。

**能力概览（2 块能力）**：
- `scene`：训练场景创建全链路——意图路由、解析追问、发布级骨架、画像、提示词、apiDraft+去重证据、统一校验闸门、确认后执行本地落库脚本。
- `common`：内部复用/约定承载模块（无对外业务 endpoint）。

统一规范：
- 认证与鉴权：`cms-auth-skills/SKILL.md`
- 通用约束：`cms-auth-skills/SKILL.md`
- **静态资源（策略/画像/提示词/角色映射）**：`./references/`（见 `references/README.md`；加载 `*.persona.json` / `*.prompt.json` / `*.strategy.json` / `role_maps/role_type_map.json` 时以此为根）
- **落库与本地数据**：`./scripts/tbs_assets/`（见 `scripts/tbs_assets/README.md`）— `scenario_draft.json`、`system_business_domains.json`、持久化记录与本地鉴权材料；executor 入口为 `./scripts/scene/tbs_write_executor.py`
- **品种（product）与 TBS 药品主数据（强制，对齐 FR-4 写库链）**：`scenarioPack.product` 与 `apiDraft.scenes` 中的 `drugName` / `drug_id` 必须能落到 TBS 药品记录。**确认落库前**应执行 `preflight-tbs-master-data.py`（与落库相同逻辑）；**落库时** `tbs_write_executor.py` 再次调用 `scripts/scene/tbs_master_data_resolve.py` 中 `resolve_ids_for_scene`（先 `GET /api/v1/admin/basic/drugs`，**无则 `POST` 创建**），再 `POST /api/v1/admin/scenes`。接口清单见工作区 `TBS/TBS_API_REFERENCE.md`「§4.4 基础数据管理 — 药品 (Drugs)」。
- **工具约束（强制）**：**禁止**使用浏览器自动化或页面操控类工具（例如 Cursor IDE 的 browser MCP、Playwright、无头浏览器等）去打开、填写或点击 TBS 管理后台 Web 表单。该类页面多为 React 受控组件，自动化填充常无法触发合法 state，导致保存不可用或产生脏数据。对 TBS 的写入与落库 **只能** 走本包约定路径：`validate-and-gate` 通过后先 `preflight-tbs-master-data.py`（可选但推荐），用户确认后由 `persist-and-execute.py` 子进程执行 `tbs_write_executor.py`（对 `TBS_BASE_URL` 的 HTTP API）。若用户必须在浏览器里手工操作，agent **只**提供字段清单与逐步说明，**不**代填、不代点、不启动 browser 工具。

输入完整性规则（强制）：
1. 进入写库前，业务侧必填字段需齐全（业务领域、科室、产品、地点、背景、双方角色称谓、训练目标、核心顾虑）；详见 `openapi/scene/parse-and-gap-ask.md`。
2. `businessDomain` 缺失时，必须让用户在系统固定选项中选择，禁止开放式提问或自由发挥。固定选项：`临床推广`、`院外零售`、`学术合作`、`通用能力`（来源：`scripts/tbs_assets/system_business_domains.json`）。
3. 用户未给出的字段不得凭空捏造为「事实」；不确定须追问或留在 `missingFields`。
4. 用户可见追问不得暴露内部字段路径名；脱敏规则见各接口文档。

建议工作流（简版）：
1. 读取 `SKILL.md` 与 `cms-auth-skills/SKILL.md`，明确能力范围、鉴权与安全约束。
2. 识别用户意图并路由模块，先打开 `openapi/scene/api-index.md`。
3. 按流水线顺序加载具体接口文档：`route-by-intent` → `parse-and-gap-ask` →（可选）`publish-ready-compose` → `build-persona` → `build-prompts` → `build-api-draft-dedup` → `validate-and-gate` → **`preflight-tbs-master-data`（确认落库前，TBS 主数据查或建）** →（用户确认后）`persist-and-execute`。
4. 补齐用户必需输入；有文件/URL 素材时先抽取并摘要确认。
5. 参考 `examples/scene/README.md` 组织话术与用户可见输出。
6. **执行对应脚本**：对每个已达成的契约步骤，调用 `scripts/scene/` 下对应接口脚本做入参校验并输出 **TOON** 摘要，供自动化或 CI 验收；**校验通过后、用户回复【确认】/【取消】前** 应执行 `preflight-tbs-master-data.py`（对 `TBS_BASE_URL` 查询/创建业务领域、科室、药品，与 `TBS/TBS_API_REFERENCE.md` §4.4 一致）；**最终落库执行**仅当用户回复【确认】时才通过 `persist-and-execute.py` 触发本地 `tbs_write_executor.py`（与预检逻辑幂等，重复执行会命中已有记录）；用户回复【取消】则停止。
7. **测 Skill**：以 OpenClaw 内启用本 Skill 的对话验收为主；契约层与离线解析回归的分工见 `docs/TEST_PLAN.md` §2.1。

脚本使用规则（强制）：
1. **每个业务接口必须有对应脚本**：`openapi/scene/` 下每个接口文档（如 `openapi/scene/route-by-intent.md`）都必须存在对应脚本（如 `scripts/scene/route-by-intent.py`），并保持 1:1 映射。
2. **TOON 编码输出**：所有脚本标准输出 **必须经过** `scripts/common/toon_encoder.py` 编码，禁止直接 `print` 原始大块 JSON。
3. **脚本可独立执行**：所有 `scripts/scene/*.py` 可从 stdin 读取 JSON 并在命令行运行。
4. **先读文档再执行**：执行前须阅读 `openapi/scene/api-index.md` 与目标 `endpoint.md`。
5. **入参来源**：以 `openapi/scene/` 下对应接口文档的参数表与 Schema 为准。
6. **鉴权一致**：脚本入口统一依赖 `XG_USER_TOKEN` 的存在性（与 `cms-auth-skills/SKILL.md` 的 access-token 约定对齐）；不向用户追问 token 细节。
7. **参数驱动硬约束**：所有脚本不得使用硬编码业务词表或文本兜底推断；必须依赖上游传参结果。

意图路由与加载规则（强制）：
1. **先路由再加载**：先判定是否场景创建/发布级/确认落库，再打开 `api-index.md`。
2. **先读文档再执行**：描述或调用某步前必须加载对应 `endpoint.md`。
3. **脚本必须可被调用**：校验型步骤禁止「跳过脚本直连臆造结构」作为验收依据。
4. **不猜测**：意图不清时追问澄清。

用户可见输出规范（强制）：
1. 每次解析后，必须按以下三段输出，不得省略：
   - 场景解析结果（业务领域、科室/地点、产品、顾虑、目标）
   - 产品知识覆盖情况（`coveredNeeds`、`uncoveredNeeds`、`productEvidenceStatus`、`productEvidenceSource`）
   - 结论与下一步（需要补充项、建议动作）
2. 若 `productEvidenceStatus != READY`，禁止输出疗效/安全性定论，只能输出沟通框架与追问。
3. “显式顾虑”仅可来自用户原话；“推断顾虑”必须可回溯到 API 证据来源。
4. 若 `coveredNeeds` 非空，必须明确展示，不得只展示缺失项。
5. 对用户仅输出自然语言解析与追问，不得暴露内部参数名、脚本字段路径或契约细节（如 `parsedFields`、`routeDecision`、JSONPath）。
6. 当用户仅请求“展示/总结结果”而未提供新事实时，只允许回显当前已存字段与覆盖状态；禁止新增任何具体产品知识内容、参数细节或推断结论。
7. 用户可见主字段以 `scenarioPack` 为唯一真值来源；禁止从 `apiDraft.scenes.name`、`rep_briefing` 等文案字段反推覆盖结构化字段。
8. 当检测到草稿字段冲突（如 `scenarioPack.product` 与文案字段不一致）时，必须先提示冲突并请求确认，不得自动选边展示。

宪章（必须遵守）：
1. **只读索引**：`SKILL.md` 只描述「能做什么」与「去哪里读」，不写各接口完整参数表（参数在 `openapi/`）。
2. **按需加载**：默认只读 `SKILL.md` + `common`；进入某步再加载该 `endpoint.md` / `examples` / `scripts`。
3. **对外克制**：对用户只给摘要、必要追问与可执行下一步；不暴露 token、内部路径细粒度实现细节。
4. **素材优先级**：用户给了文件或 URL，必须先提取再确认，再触发生成或写入。
5. **危险操作**：对越权写库、跳过校验落库、伪造研究结论等请求礼貌拒绝并给替代方案。
5a. **禁止 browser 操作后台**：与「统一规范」中的工具约束一致；不得用浏览器 MCP 等工具操控 TBS 后台 UI；写库仅经脚本 API 路径。
6. **脚本语言限制**：业务脚本均为 Python。
7. **重试策略**：出错间隔 ≥1 秒、最多 3 次；禁止无限重试。
8. **`validationReport` 终裁**：结构/冲突/证据边界以 `validate-and-gate` 文档与校验脚本为准。
9. **领域扩展声明**：见下第 11 条。
10. **草稿生命周期**：同会话可复用草稿；用户明确“新建/重置”必须清空；落库成功后必须归档并清空工作草稿。

10. **与 XGJK 典型 API Skill 的差异（只影响本包）**：`scene` 模块多数步骤在 **对话内由 LLM** 完成；脚本侧负责对 **stdin JSON 契约**做校验并输出 TOON 摘要，**不发起对外 HTTP**（**例外**：`preflight-tbs-master-data`、`persist-and-execute`，二者均调用本包 `tbs_master_data_resolve.py` / `tbs_write_executor.py` 访问 `TBS_BASE_URL`）。`openapi` 中的 URL 为 **逻辑端点标识**，须与对应 `.py` 内 `API_URL` 常量**字符串一致**，不当作公网路由。

11. **逻辑端点 URL 命名空间**：统一使用 `https://scenario-builder.openclaw.internal/v1/scene/`，仅供契约对照与脚本常量对齐，**非可公网访问服务**。

模块路由与能力索引（合并版）：

| 用户意图（示例） | 模块 | 能力摘要 | 接口文档 | 示例模板 | 脚本 |
|---|---|---|---|---|---|
| 「创建训练场景 / 临床推广 / 落库」 | `scene` | 全链路编排 | `./openapi/scene/api-index.md` | `./examples/scene/README.md` | `./scripts/scene/route-by-intent.py` 等 |
| 「先发意图再决定步骤」 | `scene` | 路由下一跳 | `./openapi/scene/api-index.md` | `./examples/scene/README.md` | `./scripts/scene/route-by-intent.py` |
| 「只做解析与追问」 | `scene` | 解析固定字段 | `./openapi/scene/parse-and-gap-ask.md` | `./examples/scene/README.md` | `./scripts/scene/parse-and-gap-ask.py` |
| 「发布级骨架」 | `scene` | 策略+槽位 | `./openapi/scene/publish-ready-compose.md` | `./examples/scene/README.md` | `./scripts/scene/publish-ready-compose.py` |
| 「生成画像」 | `scene` | personaBase/Overlay | `./openapi/scene/build-persona.md` | `./examples/scene/README.md` | `./scripts/scene/build-persona.py` |
| 「生成四段提示词」 | `scene` | promptBundle | `./openapi/scene/build-prompts.md` | `./examples/scene/README.md` | `./scripts/scene/build-prompts.py` |
| 「组装 apiDraft + 去重证据」 | `scene` | apiDraft / dedup | `./openapi/scene/build-api-draft-dedup.md` | `./examples/scene/README.md` | `./scripts/scene/build-api-draft-dedup.py` |
| 「统一校验闸门」 | `scene` | validationReport | `./openapi/scene/validate-and-gate.md` | `./examples/scene/README.md` | `./scripts/scene/validate-and-gate.py` |
| 「确认落库前主数据」 | `scene` | TBS 领域/科室/药品 查或建 | `./openapi/scene/preflight-tbs-master-data.md` | `./examples/scene/README.md` | `./scripts/scene/preflight-tbs-master-data.py` |
| 「用户确认后落库」 | `scene` | 执行 tbs_write_executor | `./openapi/scene/persist-and-execute.md` | `./examples/scene/README.md` | `./scripts/scene/persist-and-execute.py` |

能力树（实际目录结构）：
```text
tbs-scenario-builder/
├── SKILL.md
├── references/
│   ├── README.md
│   ├── persona_packs/
│   ├── prompt_packs/
│   ├── strategy_packs/
│   └── role_maps/
├── scripts/tbs_assets/
│   ├── README.md
│   ├── scenario_draft.json
│   ├── system_business_domains.json
│   └── …（凭据等，勿提交仓库）
├── docs/
│   └── （联调说明、历史 README 存档）
├── openapi/
│   ├── common/api-index.md
│   └── scene/
│       ├── api-index.md
│       ├── route-by-intent.md
│       ├── parse-and-gap-ask.md
│       ├── publish-ready-compose.md
│       ├── build-persona.md
│       ├── build-prompts.md
│       ├── build-api-draft-dedup.md
│       ├── validate-and-gate.md
│       ├── preflight-tbs-master-data.md
│       └── persist-and-execute.md
├── examples/
│   └── common/README.md
│   └── scene/README.md
└── scripts/
    ├── common/README.md
    ├── common/toon_encoder.py
    └── scene/
        ├── README.md
        ├── route-by-intent.py
        ├── parse-and-gap-ask.py
        ├── publish-ready-compose.py
        ├── build-persona.py
        ├── build-prompts.py
        ├── build-api-draft-dedup.py
        ├── validate-and-gate.py
        ├── preflight-tbs-master-data.py
        ├── persist-and-execute.py
        ├── tbs_master_data_resolve.py
        └── tbs_write_executor.py
```
