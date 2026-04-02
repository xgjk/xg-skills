# POST https://sg-al-cwork-web.mediportal.com.cn/gpts/accessToken/delUserToken

## 作用

释放并发token，用于训战结束后释放资源。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `appId` | string | 是 | 应用ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["appId"],
  "properties": {
    "appId": { "type": "string" }
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
    "resultMsg": { "type": "string" }
  }
}
```

## 脚本映射

- `../../scripts/gpts/del-user-token.py`
