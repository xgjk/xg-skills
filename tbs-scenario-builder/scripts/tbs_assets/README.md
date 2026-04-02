# tbs_assets — 本地执行器资产（脚本入口迁移）

本目录用于落盘/承载写库所需的本地资产（如 `scenario_draft.json`、枚举缓存等）；并保留 `tbs_write_executor.py` 的兼容入口（委托到 `scripts/scene/`）。

当前工程支持以下回退策略：
- 若目录内缺少资产文件，则执行器会回退到 legacy 的 `runtime/` 资产目录。

## 发布声明（必读）

本目录中的文件属于**本地运行时资产**，不是通用业务素材。发布 skill 时，请按以下规则处理：

- 不随包分发任何真实凭据或企业标识（例如 token、corp id、登录态缓存）。
- 不随包分发真实业务草稿（例如包含客户/产品上下文的 `scenario_draft.json`）。
- 运行时文件应由脚本在用户本地会话中生成或覆盖，不应作为“默认业务数据”发布。

## 首次使用要求

使用落库相关脚本前，需在启动 OpenClaw 的同一终端设置：

- `XG_USER_TOKEN=your_access_token`

执行器只读取当前会话环境变量完成鉴权，不应引导用户在仓库内保存 token 明文文件。

## 推荐的发布形态

- 保留本 README 与非敏感静态文件（如 `system_business_domains.json`）。
- `scenario_draft.json` 建议使用空模板或由脚本首次执行时自动创建。
- 若发现本目录存在真实 token、corp id、历史业务草稿，请在发布前清理。

