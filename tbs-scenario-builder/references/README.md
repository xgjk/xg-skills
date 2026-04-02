# references — 技能随附静态资源

本目录存放 **`tbs-scenario-builder`** 在编排流程中需按需加载的 JSON/说明文件（非 XGJK 规范强制目录，为本技能包约定）。

| 子目录 | 用途 |
|--------|------|
| `persona_packs/` | 底座画像候选（`*.persona.json`） |
| `prompt_packs/` | 提示词模板包（`*.prompt.json`） |
| `strategy_packs/` | 发布级策略包（`*.strategy.json`） |
| `role_maps/` | 角色类型映射（`role_type_map.json`） |

Agent 解析相对路径时，以 **`tbs-scenario-builder/`**（本包根目录，与 `SKILL.md` 同级）为基准，例如：

- `./references/persona_packs/`
- `./references/prompt_packs/`
- `./references/strategy_packs/`
- `./references/role_maps/role_type_map.json`

执行器与 `system_business_domains.json` 等业务数据见本包 [`../scripts/tbs_assets/README.md`](../scripts/tbs_assets/README.md)（若目录不存在则回退 `runtime/`）。
