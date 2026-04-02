# 脚本清单 — basic

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `gpt-id.py` | `GET /tbs/basic-info/gpt-id` | 获取GPT ID，输出 JSON 结果 |
| `tts-config.py` | `GET /tbs/basic-info/tts-config` | 获取TTS配置，输出 JSON 结果 |

## 使用方式

```bash
# nologin 接口无需设置鉴权环境变量
python3 scripts/basic/gpt-id.py
python3 scripts/basic/tts-config.py
```

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **重试策略**：间隔1秒、最多重试3次
