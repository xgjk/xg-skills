# 脚本清单 — common

该目录承载 Skill 内部复用工具，不对应外部业务 endpoint。

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `toon_encoder.py` | （内部工具） | 将结构化 JSON 压缩为 TOON 字符串，用于脚本契约输出 |
| `auth_token.py` | （内部工具） | 从环境变量 `XG_USER_TOKEN` 解析 access-token（`strip` 后使用） |

## 使用方式

该工具通常由各脚本内部 `import` 使用，不建议直接面向用户运行。

