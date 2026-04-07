# 脚本清单 — scene

## 共享依赖

- `../common/toon_encoder.py` — TOON 编码器；标准输出必须经过 `toon_encode()`。

## 脚本列表

| 脚本 | 逻辑端点 | 用途 |
|---|---|---|
| `route-by-intent.py` | `POST .../route-by-intent` | 校验路由契约并输出 TOON 摘要 |
| `parse-and-gap-ask.py` | `POST .../parse-and-gap-ask` | 校验解析草案字段契约 |
| `publish-ready-compose.py` | `POST .../publish-ready-compose` | 校验 publish_ready 前置契约 |
| `build-persona.py` | `POST .../build-persona` | 校验 persona 相关子树存在性 |
| `build-prompts.py` | `POST .../build-prompts` | 校验 promptBundle 四键占位 |
| `build-api-draft-dedup.py` | `POST .../build-api-draft-dedup` | 校验 apiDraft + 去重证据形状 |
| `validate-and-gate.py` | `POST .../validate-and-gate` | 校验终检输入非空 |
| `preflight-tbs-master-data.py` | `POST .../preflight-tbs-master-data` | 确认落库前：对 TBS 业务领域/科室/药品 GET 匹配，无则 POST（与 executor 共用 `tbs_master_data_resolve.py`） |
| `persist-and-execute.py` | `POST .../persist-and-execute` | 写草稿并子进程执行 `tbs_write_executor.py` |
| `enforce-draft-text.py` | （校验工具） | 校验草稿文本字段完整性与关键路径非空，不做文本重建/兜底 |
| `tbs_master_data_resolve.py` | （共享模块） | `TBSClient`、`resolve_ids_for_scene`；供 preflight 与 executor 使用 |
| `tbs_write_executor.py` | （HTTP 落库，无逻辑端点 URL） | 调用 TBS Admin API；品种经 `GET/POST .../drugs` 查或建后再创建场景 |
| `scenario_pack_normalizer.py` | （共享模块） | 统一新旧 `scenarioPack` 字段映射，避免生成链路断裂 |

## 使用方式

```bash
export XG_USER_TOKEN="your-access-token"

# 从 stdin 传入 JSON 契约
python3 scripts/scene/parse-and-gap-ask.py < payload.json
```

## 输出说明

所有脚本标准输出均为 **TOON**（非原始 JSON）。

## 规范

1. **Python 3**
2. **必须经过 toon_encoder**
3. **鉴权**：`XG_USER_TOKEN` 缺失则退出码 1（鉴权约定见 `cms-auth-skills/common/auth.md`）
4. **入参**：以 `openapi/scene/*.md` 为准
