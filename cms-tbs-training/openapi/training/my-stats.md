# GET https://sg-cwork-web.mediportal.com.cn/tbs/training/my-stats

## 作用

获取当前用户的训战统计数据。

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
    "data": { "type": "object" }
  }
}
```

## 脚本映射

- `../../scripts/training/my-stats.py`
