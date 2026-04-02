# GET https://sg-cwork-web.mediportal.com.cn/tbs/feedback/nologin/app-detail

## 作用

获取反馈功能的应用详情（返回反馈功能的应用ID等信息）。

**鉴权类型**
- `nologin`

**Headers**
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
        "appId": { "type": "string" }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/feedback/app-detail.py`
