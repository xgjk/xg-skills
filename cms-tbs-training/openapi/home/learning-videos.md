# GET https://sg-cwork-web.mediportal.com.cn/tbs/home/learning-videos

## 作用

获取首页视频学习任务列表，包含活动标题、学习任务标题、完成状态等信息。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
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
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "activityId": { "type": "integer" },
          "activityTitle": { "type": "string" },
          "title": { "type": "string" },
          "item": { "type": "string" },
          "isCompleted": { "type": "boolean" },
          "sortOrder": { "type": "integer" }
        }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/home/learning-videos.py`
