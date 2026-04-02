# POST https://sg-cwork-web.mediportal.com.cn/tbs/scene-image/reset

## 作用

重置场景图片。

**鉴权类型**
- `access-token`

**Headers**
- `access-token`
- `Content-Type: application/json`

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `sceneId` | string | 是 | 场景ID |
| `imageType` | string | 是 | 图片类型(SCENE_IMAGE-场景图/DIALOGUE_IMAGE-对话图) |
| `imageUrl` | string | 是 | 图片URL |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["sceneId", "imageType", "imageUrl"],
  "properties": {
    "sceneId": { "type": "string" },
    "imageType": { "type": "string" },
    "imageUrl": { "type": "string" }
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

- `../../scripts/scene-image/reset.py`
