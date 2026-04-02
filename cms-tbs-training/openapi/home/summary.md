# GET https://sg-cwork-web.mediportal.com.cn/tbs/home/summary

## 作用

获取首页训战摘要信息，包含本周训战统计数据（次数、均分、超越同事百分比）以及活动分类列表。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

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
        "stats": {
          "type": "object",
          "properties": {
            "weeklyCount": { "type": "integer" },
            "effectiveCount": { "type": "integer" },
            "avgScore": { "type": "number" },
            "beatRate": { "type": "integer" }
          }
        },
        "categories": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": { "type": "string" },
              "name": { "type": "string" },
              "items": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "id": { "type": "string" },
                    "name": { "type": "string" },
                    "type": { "type": "string" },
                    "activityId": { "type": "integer" },
                    "activityName": { "type": "string" },
                    "productId": { "type": "string" },
                    "productName": { "type": "string" },
                    "sceneType": { "type": "string" },
                    "total": { "type": "integer" },
                    "completed": { "type": "integer" },
                    "maxScore": { "type": ["integer", "null"] },
                    "passScore": { "type": "integer" },
                    "practiceCount": { "type": "integer" },
                    "showBattleButton": { "type": "boolean" },
                    "showPracticeButton": { "type": "boolean" },
                    "badgeLabel": { "type": "string" },
                    "badgeType": { "type": "string" },
                    "lastTime": { "type": "string" }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/home/summary.py`
