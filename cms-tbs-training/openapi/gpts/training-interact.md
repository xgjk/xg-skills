# POST https://sg-cwork-web.mediportal.com.cn/tbs/gpts/nologin/training/interact

## 作用

训练交互接口。

**鉴权类型**
- `nologin`

**Headers**
- `Content-Type: application/json`

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `request` | object | 是 | GPTS请求参数 |
| `request.content` | string | 否 | 用户输入内容 |
| `request.msgList` | array | 否 | 历史消息列表 |
| `request.references` | array | 否 | 引用资源列表 |
| `request.sessionId` | string | 否 | 会话ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["request"],
  "properties": {
    "request": {
      "type": "object",
      "properties": {
        "content": { "type": "string" },
        "msgList": { "type": "array" },
        "references": { "type": "array" },
        "sessionId": { "type": "string" }
      }
    }
  }
}
```

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "timeout": { "type": "integer" }
  }
}
```

## 脚本映射

- `../../scripts/gpts/training-interact.py`
