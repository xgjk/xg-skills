# 脚本清单 — prepare

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `opening-guidance.py` | `POST /tbs/training-prepare/get-opening-guidance` | 获取开场指导，输出 JSON 结果 |
| `opening-guidance-clear.py` | `DELETE /tbs/training-prepare/clear-opening-guidance-cache/inner` | 清空开场缓存，输出 JSON 结果 |

## 使用方式

```bash
export XG_USER_TOKEN="your-access-token"
python3 scripts/prepare/opening-guidance.py <sceneId>
python3 scripts/prepare/opening-guidance-clear.py <sceneId> [doctorId]
```

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **重试策略**：间隔1秒、最多重试3次
