# GET https://sg-cwork-web.mediportal.com.cn/tbs/training-dialogue-flow/nologin/getFlowDetail

## 作用

获取训练对话流程详情（可视化），返回对话节点列表、AI响应、评分等信息。

**鉴权类型**
- `nologin`

**Headers**
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `sceneRecordId` | integer | 否 | 场景记录ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "sceneRecordId": { "type": "integer" }
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
        "sceneRecordId": { "type": "integer" },
        "sceneId": { "type": "string" },
        "sessionId": { "type": "string" },
        "category": { "type": "string" },
        "difficulty": { "type": "string" },
        "score": { "type": "integer" },
        "compliancePassed": { "type": "boolean" },
        "startTime": { "type": "object" },
        "endTime": { "type": "object" },
        "totalDuration": { "type": "integer" },
        "endingType": { "type": "string" },
        "nodes": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": { "type": "integer" },
              "round": { "type": "integer" },
              "type": { "type": "string" },
              "typeDesc": { "type": "string" },
              "content": { "type": "string" },
              "aiResponse": { "type": "string" },
              "replyType": { "type": "string" },
              "prompt": { "type": "string" },
              "userPrompt": { "type": "string" },
              "systemPrompt": { "type": "string" },
              "aiCallStartTime": { "type": "object" },
              "aiCallEndTime": { "type": "object" },
              "aiCallDuration": { "type": "integer" }
            }
          }
        }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/dialogue-flow/get-flow-detail.py`
