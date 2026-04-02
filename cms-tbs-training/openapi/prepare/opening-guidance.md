# POST https://sg-cwork-web.mediportal.com.cn/tbs/training-prepare/get-opening-guidance

## 作用

获取开场指导，包含策略建议、可选开场话术列表、洞察信息等。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `sceneId` | string | 是 | 场景ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["sceneId"],
  "properties": {
    "sceneId": { "type": "string" }
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
        "strategy": {
          "type": "object",
          "properties": {
            "primaryGoal": { "type": "string" },
            "verificationQuestions": { "type": "array" }
          }
        },
        "options": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "label": { "type": "string" },
              "text": { "type": "string" }
            }
          }
        },
        "insight": {
          "type": "object",
          "properties": {
            "personaSummary": { "type": "string" },
            "mentorObservation": { "type": "string" }
          }
        }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/prepare/opening-guidance.py`
