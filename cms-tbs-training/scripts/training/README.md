# 脚本清单 — training

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `my-stats.py` | `GET /tbs/training/my-stats` | 获取我的训战统计数据，输出 JSON 结果 |
| `records.py` | `GET /tbs/training/records` | 获取训战记录列表，输出 JSON 结果 |
| `records-detail.py` | `GET /tbs/training/records/{id}` | 获取训战记录详情，输出 JSON 结果 |

## 使用方式

```bash
# 先通过 cms-auth-skills 准备 access-token，再设置环境变量
export XG_USER_TOKEN="your-access-token"

# 执行脚本
python3 scripts/training/my-stats.py
python3 scripts/training/records.py [page] [size] [sourceType]
python3 scripts/training/records-detail.py <id>
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **入参定义以** `openapi/` 文档为准
4. **重试策略**：间隔1秒、最多重试3次
