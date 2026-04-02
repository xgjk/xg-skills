# GET https://sg-cwork-web.mediportal.com.cn/tbs/feedback/nologin/gpt-id

## 作用

获取反馈功能的GPT ID。type不传则返回默认反馈GPT；type=speech返回PPT演讲反馈GPT。

**鉴权类型**
- `nologin`

**Headers**
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `type` | string | 否 | 类型：speech返回PPT演讲反馈GPT |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "type": { "type": "string" }
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
        "gptId": { "type": "string" }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/feedback/gpt-id.py`
