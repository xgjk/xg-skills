# GET https://sg-cwork-web.mediportal.com.cn/tbs/home/product-scenes

## 作用

获取产品场景列表（含训战-练习按钮状态），返回场景ID、名称、类型、最高分、训战次数等信息。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `productId` | integer | 否 | 产品ID（来自首页 product item 的 id 字段） |
| `activityId` | integer | 否 | 活动ID（来自首页 product item 的 activityId 字段） |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "productId": { "type": "integer" },
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
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "type": { "type": "string" },
          "sceneType": { "type": "string" },
          "productId": { "type": "string" },
          "productName": { "type": "string" },
          "activityId": { "type": "integer" },
          "activityName": { "type": "string" },
          "maxScore": { "type": ["integer", "null"] },
          "passScore": { "type": "integer" },
          "practiceCount": { "type": "integer" },
          "showBattleButton": { "type": "boolean" },
          "showPracticeButton": { "type": "boolean" }
        }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/home/product-scenes.py`
