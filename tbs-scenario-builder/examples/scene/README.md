# scene — 使用说明

## 什么时候使用

- 用户要**创建/配置/发布** TBS 训练场景，或描述「医药代表 vs 医生」等角色扮演练习背景。
- 用户提供 **createScenarioRequest** JSON，或自然语言场景背景。
- 用户明确 **publish_ready / 发布级**输出。
- 用户在通过校验后回复 **确认/取消**：回复`确认`开始落库，回复`取消`停止。

## 最短成功路径（3 步）

1. **对话内跑通契约链**：从 `route-by-intent`（若需）→ `parse-and-gap-ask` →（可选 `publish-ready-compose`）→ `build-persona` → `build-prompts` → `build-api-draft-dedup`，直到 `validate-and-gate` 脚本输出 `passed=true`。
2. **落库前主数据**：在用户表态【确认】/【取消】之前，执行 `preflight-tbs-master-data.py`（与落库共用解析逻辑，可提前暴露领域/科室/药品问题）。
3. **用户确认后落库**：仅当用户回复 **确认** 时，stdin 传入含 `validationReport.passed=true` 与 `userConfirmation: "确认"` 的 JSON，执行 `persist-and-execute.py`。

## 失败回退路径（2 步）

1. **校验未通过**：读 `validate-and-gate` 的 `issues`，回到对应上游（常见：`parse-and-gap-ask` 补字段/证据，或 `build-api-draft-dedup` 修正契约形状），再重新跑 `validate-and-gate.py`，直到 `passed=true`。
2. **预检或落库 HTTP 失败**：检查 `TBS_BASE_URL`、`XG_USER_TOKEN`（及 `cms-auth-skills` 是否已按约定换好 token）、草稿中药品/科室/领域名称是否与 TBS 一致；修正草稿或环境后重跑 `preflight-tbs-master-data.py`，再视用户意愿执行 `persist-and-execute.py`。

## 标准流程

1. **鉴权预检**：执行任意 `scripts/scene/*.py` 前设置 `XG_USER_TOKEN`（鉴权约定见 `cms-auth-skills/common/auth.md`；脚本侧会 `strip` 空白）。
2. **意图路由**：加载 `openapi/scene/route-by-intent.md`，必要时先运行 `route-by-intent.py` 校验stdin 契约。
3. **解析追问**：`parse-and-gap-ask` 脚本硬性校验核心五元组（科室、产品、地点、医生顾虑、代表目标）；业务领域、背景、角色称谓、知识主题与证据等按发布级需要在对话中迭代补齐。用户侧最多 5 问且脱敏。若缺业务领域（契约字段 `businessDomain`），必须按四选一追问：`临床推广` / `院外零售` / `学术合作` / `通用能力`。**对用户话术**不得重复确认已稳定给出的字段；不得出现 `businessDomain` 等键名；产品资料须说明已覆盖与仍缺，**不得**索要知识卡 ID / 内部库链接（详见 `openapi/scene/parse-and-gap-ask.md`）。
4. **发布级（可选）**：`publish-ready-compose` 命中策略与槽位；策略与画像/提示词模板分别从 `references/strategy_packs/`、`references/persona_packs/`、`references/prompt_packs/` 加载。
5. **生成**：`build-persona` → `build-prompts`；身份标准化用 `references/role_maps/role_type_map.json`。
6. **写库准备**：`build-api-draft-dedup` 产出 `apiDraft` 与 `dedupEvidence` 形状。
7. **终裁**：`validate-and-gate` 产出 `validationReport`。
8. **落库**：仅 `passed=true` 且用户确认后，运行 `persist-and-execute.py`（子进程调用 `tbs_write_executor.py`）。

## 对用户可见输出（强制）

- 不向用户展示任何写库契约 JSON（含 `scenarioPack` / `apiDraft` 片段及「API Draft 配置」类代码块）或原始 `validationReport`；见 `SKILL.md`「用户可见输出规范」第 9 条。
- 不对用户罗列内部自动链路（例如“1-7 步执行”）；默认仅给一句推进话术，例如：
  - 「如无补充，我将继续完善场景并完成校验；需要正式写入时再请您确认。」
  - 「当前信息已可继续，我先推进生成与检查，落库前会再次向您确认。」

## 契约脚本回归用例（JSON）

- 回归 payload **不在本技能包内**，位于与技能包同级的 **`tbs-scenario-builder-acceptance/regression/`**（说明见该目录 `README.md`；一键验收用 `test_user_visible_contract.py`）。
- 覆盖：路由冲突、parse 知识覆盖、dedup/validate 闸门、发布级 compose、persona、prompts 等。

## 用户可能会说

- 「帮我在呼吸内科做一个 X 产品的访视练习，医生担心安全性…」
- 「outputMode=publish_ready，场景背景如下…」
- 「信息无误，回复确认开始落库。 」（或回复取消停止）
