# GET https://sg-cwork-web.mediportal.com.cn/tbs/speech/detail

## 作用

获取PPT场景详情，包含PPT标题、URL、评估提示词、评分维度、建议时长等信息。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `sceneId` | integer | 是 | 场景ID |
| `activityId` | integer | 否 | 活动ID（t_training_activity_scene.activity_id） |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["sceneId"],
  "properties": {
    "sceneId": { "type": "integer" },
    "activityId": { "type": "integer" }
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
        "sceneId": { "type": "integer" },
        "pptTaskId": { "type": "string" },
        "pptTitle": { "type": "string" },
        "pptUrl": { "type": "string" },
        "evalPrompt": { "type": "string" },
        "scoringDimensions": { "type": "array" },
        "passScore": { "type": "integer" },
        "suggestedDuration": { "type": "integer" },
        "repBriefing": { "type": "string" },
        "fileContentJson": { "type": "object" }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/speech/speech-detail.py`
