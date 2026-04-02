# DELETE https://sg-cwork-web.mediportal.com.cn/tbs/training-prepare/clear-opening-guidance-cache/inner

## 作用

清空开场指导缓存。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `sceneId` | string | 是 | 场景ID |
| `doctorId` | integer | 否 | 医生ID（不传则清空该场景下所有医生的缓存） |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["sceneId"],
  "properties": {
    "sceneId": { "type": "string" },
    "doctorId": { "type": "integer" }
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

- `../../scripts/prepare/opening-guidance-clear.py`
