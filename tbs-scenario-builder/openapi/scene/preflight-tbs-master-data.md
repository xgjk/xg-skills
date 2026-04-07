# POST https://scenario-builder.openclaw.internal/v1/scene/preflight-tbs-master-data

## 作用

在 **`validate-and-gate` 通过之后、用户确认 `persist-and-execute` 之前**，对 TBS 后台 **业务领域、科室、药品** 做一次与落库相同的解析：先 `GET` 列表按名称匹配，**已存在则不新建**；不存在则 **`POST` 创建**（除非 `--dry-run`）。保证确认落库时主数据已就绪，且 agent 可向用户展示 `resolutionReport`（匹配 / 新建）。

实现与 `tbs_write_executor.py` 共用 `scripts/scene/tbs_master_data_resolve.py` 中的 `resolve_ids_for_scene(..., with_report=True)`。

**Headers**

- `access-token`：执行前须设置 `XG_USER_TOKEN`（鉴权约定见 `cms-auth-skills/common/auth.md`）。
- 实际 HTTP 目标为 `TBS_BASE_URL`（默认生产环境见 `persist-and-execute` / executor）。

**鉴权类型**
- `access-token`

## 输入

- **stdin** 或 `--input`：与 `scenario_draft.json` 同形，至少包含 `apiDraft.scenes`（对象或数组）。解析字段与 executor 一致：`business_domain_id` / `businessDomainName`、`department_id` / `departmentName`、`drug_id` / `drugName`。

## 命令行参数

| 参数 | 说明 |
|---|---|
| `--input` | 草稿 JSON 路径（缺省则读 stdin） |
| `--base-url` | 默认 `TBS_BASE_URL` 环境变量或生产基址 |
| `--access-token` | 默认 `XG_USER_TOKEN` |
| `--insecure-ssl` | 跳过 TLS 校验（仅必要时） |
| `--dry-run` | 只查询匹配，不 `POST`；报告中对需创建项为 `would_create` |

## 响应（脚本 TOON）

- `ok`：三项 ID 是否均解析成功
- `resolvedIds`：`department_id`、`business_domain_id`、`drug_id`
- `resolutionReport`：各实体 `action`：`matched_by_id` | `matched` | `created` | `matched_after_conflict` | `would_create`（仅 dry-run）
- `dryRun`：是否 `--dry-run`

## 脚本映射

- `../../scripts/scene/preflight-tbs-master-data.py`
