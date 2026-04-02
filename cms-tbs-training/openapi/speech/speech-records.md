# GET https://sg-cwork-web.mediportal.com.cn/tbs/speech/records/{trainingRecordId}

## 作用

获取演讲记录详情，包含综合评分、各维度评分、亮点、改进建议、每页回顾等信息。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Path 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `trainingRecordId` | integer | 是 | 训练记录ID |

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
        "trainingRecordId": { "type": "integer" },
        "sceneId": { "type": "integer" },
        "sceneTitle": { "type": "string" },
        "drugName": { "type": "string" },
        "score": { "type": "integer" },
        "isPassed": { "type": "boolean" },
        "durationSeconds": { "type": "integer" },
        "sourceType": { "type": "string" },
        "sourceId": { "type": "integer" },
        "createTime": { "type": "string" },
        "highlights": { "type": "array" },
        "improvements": { "type": "array" },
        "reviewSummary": { "type": "string" },
        "scoreDimensions": { "type": "object" },
        "pages": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "pageIndex": { "type": "integer" },
              "pageTitle": { "type": "string" },
              "transcriptText": { "type": "string" },
              "audioUrl": { "type": "string" },
              "durationSeconds": { "type": "integer" },
              "pageScore": { "type": "integer" },
              "pageReviewText": { "type": "string" },
              "refPageSnapshot": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/speech/speech-records.py`
