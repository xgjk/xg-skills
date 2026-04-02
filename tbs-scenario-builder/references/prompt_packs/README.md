## prompt_packs

本目录用于承载 **`tbs-scenario-builder` Skill** 的**提示词模板包**（promptBundle 生成来源）。

动机：`promptBundle` 当前偏“医药代表训练”专用。当场景变成“推广经理 ↔ 医药代表”、或“系统推广/流程上线”等非医药代表场景时，需要自动切换提示词模板，而不是沿用原有角色与评分口径。

### 文件约定
- `prompt.schema.json`：提示词包 JSON Schema（用于自检与协作对齐）
- `*.prompt.json`：一个提示词包（可按行业/角色/训练类型分组）

### 提示词包如何被使用（由 Agent 执行）
- 读取本目录下所有 `*.prompt.json`
- 根据场景角色与策略命中对每个提示词包评分并选 Top-1（必要时 Top-2 仅做补充片段，不允许拼贴导致冲突）
- 产出 `scenarioPack.promptBundle` 四段文本：
  - `roleplaySystemPrompt`：AI 扮演者的系统提示（对话侧）
  - `openingCoachPrompt`：访前规划/开场带教（教练侧）
  - `interactionCoachPrompt`：实时互动教练（教练侧，严格 JSON 输出规则可在此包中定义）
  - `reviewExaminerPrompt`：复盘评分官（教练侧，评分维度与规则应与场景类型匹配）

