# GET https://sg-cwork-web.mediportal.com.cn/tbs/training/records

## 作用

获取训战记录列表（分页），返回记录ID、场景、分数、时长、状态等信息。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `page` | integer | 否 | 页码，从1开始 |
| `size` | integer | 否 | 每页条数 |
| `sourceType` | string | 否 | 来源类型过滤：battle-训战，practice-练习，不传则全部 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "page": { "type": "integer" },
    "size": { "type": "integer" },
    "sourceType": { "type": "string" }
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
    "data": { "type": "object" }
  }
}
```

## 脚本映射

- `../../scripts/training/records.py`
