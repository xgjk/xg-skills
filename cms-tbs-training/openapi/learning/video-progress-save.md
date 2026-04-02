# POST https://sg-cwork-web.mediportal.com.cn/tbs/learning/video-progress

## 作用

保存视频播放进度。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `learningItemId` | integer | 是 | 学习任务ID |
| `pageIndex` | integer | 是 | 当前播放到的片段索引（从0开始） |
| `progress` | number | 是 | 当前片段已播放时长（秒），支持小数 |
| `isCompleted` | boolean | 否 | 是否已完成观看 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["learningItemId", "pageIndex", "progress"],
  "properties": {
    "learningItemId": { "type": "integer" },
    "pageIndex": { "type": "integer" },
    "progress": { "type": "number" },
    "isCompleted": { "type": "boolean" }
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

- `../../scripts/learning/video-progress-save.py`
