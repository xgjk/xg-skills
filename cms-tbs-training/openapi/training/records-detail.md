# GET https://sg-cwork-web.mediportal.com.cn/tbs/training/records/{id}

## 作用

获取训战记录详情（含对话回溯），返回记录详细信息、对话消息列表、评分、亮点、改进建议等。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Path 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | integer | 是 | 训战记录ID |

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "integer" },
    "resultMsg": { "type": "string" },
    "data": {
      "type": "object",
      "properties": {
        "id": { "type": "string" },
        "sceneId": { "type": "integer" },
        "sceneTitle": { "type": "string" },
        "sceneName": { "type": "string" },
        "sceneType": { "type": "string" },
        "drugName": { "type": "string" },
        "departmentName": { "type": "string" },
        "difficulty": { "type": "string" },
        "score": { "type": "integer" },
        "totalScore": { "type": "integer" },
        "durationSeconds": { "type": "integer" },
        "sourceType": { "type": "string" },
        "sourceId": { "type": "integer" },
        "cloudCategoryId": { "type": "string" },
        "startTime": { "type": "string" },
        "summary": { "type": "string" },
        "reviewSummary": { "type": "string" },
        "highlights": { "type": "array" },
        "improvements": { "type": "array" },
        "scoreDimensions": { "type": "string" },
        "dialogueMessages": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "round": { "type": "integer" },
              "sequence": { "type": "integer" },
              "role": { "type": "string" },
              "type": { "type": "string" },
              "content": { "type": "string" },
              "aiResponse": { "type": "string" },
              "replyType": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/training/records-detail.py`
