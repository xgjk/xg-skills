# GET https://sg-cwork-web.mediportal.com.cn/tbs/learning/video-progress

## 作用

查询视频播放进度。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `learningItemId` | integer | 是 | 学习任务ID |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["learningItemId"],
  "properties": {
    "learningItemId": { "type": "integer" }
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
        "learningItemId": { "type": "integer" },
        "progress": { "type": "number" },
        "pageIndex": { "type": "integer" },
        "isCompleted": { "type": "boolean" }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/learning/video-progress-get.py`
