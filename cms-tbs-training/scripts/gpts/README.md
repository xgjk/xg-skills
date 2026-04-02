# 脚本清单 — gpts

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `app-detail.py` | `GET /gpts/gptApp/getDetailByIdV2` | 获取GPT应用详情，输出 JSON 结果 |
| `session.py` | `POST /gpts/session/getSessionByBusinessId` | 获取/创建会话，输出 JSON 结果 |
| `sse-suggest.py` | `POST /gpts/sseClient/ai/suggest` | SSE核心接口（开始训练/提交对话/生成点评），输出 JSON 结果 |
| `del-user-token.py` | `POST /gpts/accessToken/delUserToken` | 释放并发token，输出 JSON 结果 |

## 使用方式

```bash
export XG_USER_TOKEN="your-access-token"

# 获取GPT应用详情
python3 scripts/gpts/app-detail.py <appId> [corpId]

# 获取/创建会话
python3 scripts/gpts/session.py <appId> <businessId> <businessType> [isForce]

# SSE：开始训练
python3 scripts/gpts/sse-suggest.py <sessionId> <appId> start_training "进入训练"

# SSE：提交对话
python3 scripts/gpts/sse-suggest.py <sessionId> <appId> submit_dialogue "用户回答" <trainingRecordId> <round> <type>

# SSE：生成AI点评
python3 scripts/gpts/sse-suggest.py <sessionId> <appId> generate_ai_comment "" <trainingRecordId>

# 释放并发token
python3 scripts/gpts/del-user-token.py <appId>
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **入参定义以** `openapi/` 文档为准
4. **重试策略**：间隔1秒、最多重试3次
