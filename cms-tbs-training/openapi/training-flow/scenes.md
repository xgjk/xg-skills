# GET https://sg-cwork-web.mediportal.com.cn/tbs/training-flow/nologin/scenes

## 作用

根据药品ID获取已发布的场景列表（公开接口）。

**鉴权类型**
- `nologin`

**Headers**
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `drugId` | integer | 是 | 药品ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["drugId"],
  "properties": {
    "drugId": { "type": "integer" }
  }
}
```

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id": { "type": "integer" },
      "title": { "type": "string" },
      "status": { "type": "integer" },
      "drugId": { "type": "integer" },
      "drugName": { "type": "string" },
      "externalId": { "type": "string" },
      "departmentId": { "type": "integer" },
      "departmentName": { "type": "string" },
      "diseaseId": { "type": "integer" },
      "diseaseName": { "type": "string" },
      "location": { "type": "string" },
      "repBriefing": { "type": "string" }
    }
  }
}
```

## 脚本映射

- `../../scripts/training-flow/scenes.py`
