## strategy_packs

本目录用于承载 **`tbs-scenario-builder` Skill** 的**可扩展策略层**（publish_ready）。

目标：把“追问路径/最佳实践/语气与推进方式”的规则从 `AGENTS.md` 拆出来，变成**可插拔、可新增、可灰度**的策略包；同时保留 `AGENTS.md` 中的“硬闸门”（结构/证据/一致性）作为发布质量与合规底线。

### 文件约定
- `strategy.schema.json`：策略包 JSON Schema（用于自检与协作对齐）
- `*.strategy.json`：一个策略包文件（可按行业/产品线/通用能力分组）

### 策略包使用方式（由 Agent 执行）
- 读取本目录下所有 `*.strategy.json`
- 对每个策略包计算匹配分数（见 `AGENTS.md` 的“策略选择评分”规则）
- 允许多策略组合：选择 Top-K（建议 K=1~2），并在冲突时以“硬闸门”为准

