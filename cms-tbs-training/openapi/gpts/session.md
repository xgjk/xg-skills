# POST https://sg-al-cwork-web.mediportal.com.cn/gpts/session/getSessionByBusinessId

## 作用

获取或创建会话，返回 session.id 用于 SSE 通信。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `appId` | string\|number | 是 | 应用ID |
| `businessId` | string | 是 | 业务ID |
| `businessType` | string | 是 | 业务类型 |
| `isForce` | boolean | 否 | 是否强制创建新会话 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["appId", "businessId", "businessType"],
  "properties": {
    "appId": { "type": ["string", "integer"] },
    "businessId": { "type": "string" },
    "businessType": { "type": "string" },
    "isForce": { "type": "boolean" }
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
        "id": { "type": "string" }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/gpts/session.py`
