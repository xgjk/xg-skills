# 脚本清单 — dialogue-flow

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `get-flow-detail.py` | `GET /tbs/training-dialogue-flow/nologin/getFlowDetail` | 获取对话流程详情，输出 JSON 结果 |

## 使用方式

```bash
# nologin 接口无需设置鉴权环境变量
python3 scripts/dialogue-flow/get-flow-detail.py [sceneRecordId]
```

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **重试策略**：间隔1秒、最多重试3次
