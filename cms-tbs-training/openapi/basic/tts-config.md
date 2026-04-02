# GET https://sg-cwork-web.mediportal.com.cn/tbs/basic-info/tts-config

## 作用

获取TTS配置（根据Nacos配置的tts.vendor返回对应厂商的音色映射）。

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
        "ttsVendor": { "type": "string" },
        "voiceMapping": {
          "type": "object",
          "properties": {
            "scene": { "type": "string" },
            "question": { "type": "string" },
            "goldReply": { "type": "string" },
            "review": { "type": "string" }
          }
        }
      }
    }
  }
}
```

## 脚本映射

- `../../scripts/basic/tts-config.py`
