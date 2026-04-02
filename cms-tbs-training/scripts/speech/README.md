# 脚本清单 — speech

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `speech-detail.py` | `GET /tbs/speech/detail` | 获取PPT场景详情，输出 JSON 结果 |
| `speech-finish.py` | `POST /tbs/speech/finish` | 完成演讲并生成复盘，输出 JSON 结果 |
| `speech-records.py` | `GET /tbs/speech/records/{trainingRecordId}` | 获取演讲记录详情，输出 JSON 结果 |

## 使用方式

```bash
# 先通过 cms-auth-skills 准备 access-token，再设置环境变量
export XG_USER_TOKEN="your-access-token"

# 执行脚本
python3 scripts/speech/speech-detail.py <sceneId> [activityId]
python3 scripts/speech/speech-finish.py <sceneId> [activityId] [totalDurationSeconds] [sourceType]
python3 scripts/speech/speech-records.py <trainingRecordId>
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **入参定义以** `openapi/` 文档为准
4. **重试策略**：间隔1秒、最多重试3次
