# GET https://sg-al-cwork-web.mediportal.com.cn/gpts/gptApp/getDetailByIdV2

## 作用

获取GPT应用详情，用于训战初始化。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | 是 | 应用ID（appId） |
| `corpId` | string | 否 | 企业ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id"],
  "properties": {
    "id": { "type": "string" },
    "corpId": { "type": "string" }
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
        "id": { "type": "string" },
        "businessType": { "type": "string" }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/gpts/app-detail.py`
