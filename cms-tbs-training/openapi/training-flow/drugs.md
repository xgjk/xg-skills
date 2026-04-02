# GET https://sg-cwork-web.mediportal.com.cn/tbs/training-flow/nologin/drugs

## 作用

获取所有启用的药品列表（公开接口）。

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
      "status": { "type": "integer" }
    }
  }
}
```

## 脚本映射

- `../../scripts/training-flow/drugs.py`
