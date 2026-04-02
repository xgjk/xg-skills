# POST https://sg-cwork-web.mediportal.com.cn/tbs/speech/finish

## 作用

完成演讲并生成复盘。提交演讲结果后返回综合评分和训练记录ID。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `sceneId` | integer | 是 | 场景ID |
| `activityId` | integer | 否 | 活动ID |
| `totalDurationSeconds` | integer | 否 | 总时长(秒) |
| `sourceType` | string | 否 | 来源类型：practice/battle |
| `mode` | integer | 否 | 模式：1-practice 0-battle |
| `pages` | array | 否 | 每页结果 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["sceneId"],
  "properties": {
    "sceneId": { "type": "integer" },
    "activityId": { "type": "integer" },
    "totalDurationSeconds": { "type": "integer" },
    "sourceType": { "type": "string" },
    "mode": { "type": "integer" },
    "pages": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "pageIndex": { "type": "integer" },
          "pageTitle": { "type": "string" },
          "transcriptText": { "type": "string" },
          "audioUrl": { "type": "string" },
          "durationSeconds": { "type": "integer" }
        }
      }
    }
  }
}
```

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
        "score": { "type": "integer" },
        "trainingRecordId": { "type": "integer" }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/speech/speech-finish.py`
