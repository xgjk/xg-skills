# GET https://sg-cwork-web.mediportal.com.cn/tbs/scene/{sceneId}/doctor-titles

## 作用

根据场景ID获取该场景下默认医生的职称列表。

**鉴权类型**
- `nologin`

**Headers**
- `Content-Type: application/json`

**Path 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `sceneId` | integer | 是 | 场景ID |

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "integer" },
    "resultMsg": { "type": "string" },
    "data": { "type": "string" }
  }
}
```

## 脚本映射

- `../../scripts/drug/scene-doctor-titles.py`
