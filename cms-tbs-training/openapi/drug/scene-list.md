# GET https://sg-cwork-web.mediportal.com.cn/tbs/scene/list-by-drug-external-id

## 作用

根据药品的 external_id 列表获取已发布的场景列表。返回场景ID、标题、科室、药品、难度、状态等信息。

**鉴权类型**
- `nologin`

**Headers**
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `externalId` | string | 否 | 药品的external_id列表，多个用逗号分隔（不传则返回所有） |
| `corpId` | integer | 否 | 企业ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "externalId": { "type": "string" },
    "corpId": { "type": "integer" }
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

- `../../scripts/drug/scene-list.py`
