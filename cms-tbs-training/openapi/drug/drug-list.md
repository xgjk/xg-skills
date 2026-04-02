# GET https://sg-cwork-web.mediportal.com.cn/tbs/training-flow/nologin/drugs

## 作用

获取所有已启用的药品列表，包含药品ID、名称、编码、生产厂家、状态等信息。

**鉴权类型**
- `nologin`

**Headers**
- `Content-Type: application/json`

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id": { "type": "integer" },
      "name": { "type": "string" },
      "code": { "type": "string" },
      "genericName": { "type": "string" },
      "companyName": { "type": "string" },
      "description": { "type": "string" },
      "status": { "type": "integer" },
      "sortOrder": { "type": "integer" }
    }
  }
}
```

## 脚本映射

- `../../scripts/drug/drug-list.py`
