# 脚本清单 — training-flow

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `drugs.py` | `GET /tbs/training-flow/nologin/drugs` | 获取药品列表，输出 JSON 结果 |
| `records.py` | `GET /tbs/training-flow/nologin/records` | 获取训练记录列表，输出 JSON 结果 |
| `scenes.py` | `GET /tbs/training-flow/nologin/scenes` | 获取场景列表，输出 JSON 结果 |

## 使用方式

```bash
# nologin 接口无需设置鉴权环境变量
python3 scripts/training-flow/drugs.py
python3 scripts/training-flow/records.py <sceneId> [pageNum] [pageSize] [userName] [startDate] [endDate]
python3 scripts/training-flow/scenes.py <drugId>
```

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **重试策略**：间隔1秒、最多重试3次
