# GET https://sg-cwork-web.mediportal.com.cn/tbs/file/upload-by-url

## 作用

通过URL上传文件，返回文件ID、名称、URL、大小、时长等信息。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `fileUrl` | string | 是 | 文件URL地址 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["fileUrl"],
  "properties": {
    "fileUrl": { "type": "string" }
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
        "fileId": { "type": "integer" },
        "name": { "type": "string" },
        "url": { "type": "string" },
        "fsize": { "type": "integer" },
        "duration": { "type": "integer" }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/file/upload-by-url.py`
