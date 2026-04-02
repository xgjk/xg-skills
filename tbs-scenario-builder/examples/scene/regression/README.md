# Scene Regression Cases

最小回归集合，覆盖 `route-by-intent`、`parse-and-gap-ask`、`build-api-draft-dedup`、`validate-and-gate` 的关键闸门行为。

## 运行前提

```bash
export XG_USER_TOKEN="your-token"
```

## 用例与预期

1. `01_route_conflict.json`
   - 目标：同句出现“校验 + 落库”时，路由降级 `UNKNOWN` 并澄清。
2. `02_parse_partial_coverage.json`
   - 目标：知识库部分命中时，`productEvidenceStatus=PARTIAL`，并输出 `uncoveredNeeds`。
3. `03_parse_full_coverage.json`
   - 目标：知识库全命中时，`productEvidenceStatus=READY`，不应缺失 `productEvidenceSource`。
4. `04_dedup_block_fact_claims.json`
   - 目标：证据未 READY 且含结论性表述时，`build-api-draft-dedup.py` 应报错退出。
5. `05_validate_gate_not_ready.json`
   - 目标：证据未 READY 但缺少确认标记/来源时，`validate-and-gate` 输出 `passed=false` 与 `issues`。
6. `06_parse_non_weituke_param_driven.json`
   - 目标：非“维图可”产品（如三九胃泰）可通过 `productCandidates` 参数驱动识别，无文本兜底。

## 示例命令

```bash
python3 scripts/scene/route-by-intent.py < examples/scene/regression/01_route_conflict.json
python3 scripts/scene/parse-and-gap-ask.py < examples/scene/regression/02_parse_partial_coverage.json
python3 scripts/scene/parse-and-gap-ask.py < examples/scene/regression/03_parse_full_coverage.json
python3 scripts/scene/build-api-draft-dedup.py < examples/scene/regression/04_dedup_block_fact_claims.json
python3 scripts/scene/validate-and-gate.py < examples/scene/regression/05_validate_gate_not_ready.json
python3 scripts/scene/parse-and-gap-ask.py < examples/scene/regression/06_parse_non_weituke_param_driven.json
```
