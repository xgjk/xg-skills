# GET https://sg-cwork-web.mediportal.com.cn/tbs/learning/video-detail

## 作用

获取学习视频详情，包含视频标题、URL、缩略图、进度、完成状态等。

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
        "title": { "type": "string" },
        "fileName": { "type": "string" },
        "downloadUrl": { "type": "string" },
        "thumbnailUrl": { "type": "string" },
        "size": { "type": "integer" },
        "suffix": { "type": "string" },
        "progress": { "type": "number" },
        "pageIndex": { "type": "integer" },
        "isCompleted": { "type": "boolean" },
        "activityId": { "type": "integer" },
        "activityTitle": { "type": "string" },
        "openWith": { "type": "integer" }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/learning/video-detail.py`
