# GET https://sg-cwork-web.mediportal.com.cn/tbs/basic-info/gpt-id

## 作用

获取GPT ID（从Nacos配置中心获取）。

**鉴权类型**
- `nologin`

**Headers**
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
      "type": "object",
      "properties": {
        "gptId": { "type": "string" }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/basic/gpt-id.py`
