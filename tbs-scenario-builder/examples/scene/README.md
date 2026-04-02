# scene — 使用说明

## 什么时候使用

- 用户要**创建/配置/发布** TBS 训练场景，或描述「医药代表 vs 医生」等角色扮演练习背景。
- 用户提供 **createScenarioRequest** JSON，或自然语言场景背景。
- 用户明确 **publish_ready / 发布级**输出。
- 用户在通过校验后回复 **确认/取消**：回复`确认`开始落库，回复`取消`停止。

## 标准流程

1. **鉴权预检**：执行任意 `scripts/scene/*.py` 前设置 `XG_USER_TOKEN`（鉴权约定见 `cms-auth-skills/SKILL.md`）。
2. **意图路由**：加载 `openapi/scene/route-by-intent.md`，必要时先运行 `route-by-intent.py` 校验stdin 契约。
3. **解析追问**：`parse-and-gap-ask` 补齐 9 项固定字段；用户侧最多 5 问且脱敏。若缺 `businessDomain`，必须按四选一追问：`临床推广` / `院外零售` / `学术合作` / `通用能力`。
4. **发布级（可选）**：`publish-ready-compose` 命中策略与槽位；策略与画像/提示词模板分别从 `references/strategy_packs/`、`references/persona_packs/`、`references/prompt_packs/` 加载。
5. **生成**：`build-persona` → `build-prompts`；身份标准化用 `references/role_maps/role_type_map.json`。
6. **写库准备**：`build-api-draft-dedup` 产出 `apiDraft` 与 `dedupEvidence` 形状。
7. **终裁**：`validate-and-gate` 产出 `validationReport`。
8. **落库**：仅 `passed=true` 且用户确认后，运行 `persist-and-execute.py`（子进程调用 `tbs_write_executor.py`）。

## 回归用例

- 最小回归集合：`./regression/README.md`
- 覆盖冲突路由、知识库覆盖分流、证据闸门、终检闭环。

## 用户可能会说

- 「帮我在呼吸内科做一个 X 产品的访视练习，医生担心安全性…」
- 「outputMode=publish_ready，场景背景如下…」
- 「信息无误，回复确认开始落库。 」（或回复取消停止）
