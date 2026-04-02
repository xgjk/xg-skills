# 脚本清单 — feedback

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `app-detail.py` | `GET /tbs/feedback/nologin/app-detail` | 获取反馈应用详情，输出 JSON 结果 |
| `gpt-id.py` | `GET /tbs/feedback/nologin/gpt-id` | 获取反馈GPT ID，输出 JSON 结果 |

## 使用方式

```bash
# nologin 接口无需设置鉴权环境变量
python3 scripts/feedback/app-detail.py
python3 scripts/feedback/gpt-id.py [type]
```

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **重试策略**：间隔1秒、最多重试3次
