# scripts — 目录索引

本目录存放可执行脚本与内部复用工具。

## 模块

- `scene/`
  - 入口：`scene/README.md`
  - 包含场景链路脚本与落库执行脚本
- `common/`
  - 入口：`common/README.md`
  - 包含 TOON 编码与鉴权 token 解析等共享工具
- `tbs_assets/`
  - 入口：`tbs_assets/README.md`
  - 存放草稿、主数据字典与本地运行资产

## 执行原则

1. 先读 `openapi/scene/api-index.md` 与对应 endpoint 文档
2. 再执行 `scene/*.py`
3. 所有需要鉴权的步骤依赖 `XG_USER_TOKEN`
