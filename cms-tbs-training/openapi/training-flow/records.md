# GET https://sg-cwork-web.mediportal.com.cn/tbs/training-flow/nologin/records

## 作用

根据场景ID获取训练记录列表（支持按用户姓名查询、按日期查询、按时间倒序、分页）。

**鉴权类型**
- `nologin`

**Headers**
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `sceneId` | integer | 是 | 场景ID |
| `pageNum` | integer | 否 | 页码（从1开始） |
| `pageSize` | integer | 否 | 每页数量 |
| `userName` | string | 否 | 用户姓名（用于模糊查询） |
| `startDate` | string | 否 | 开始日期（格式：yyyy-MM-dd） |
| `endDate` | string | 否 | 结束日期（格式：yyyy-MM-dd） |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["sceneId"],
  "properties": {
    "sceneId": { "type": "integer" },
    "pageNum": { "type": "integer" },
    "pageSize": { "type": "integer" },
    "userName": { "type": "string" },
    "startDate": { "type": "string" },
    "endDate": { "type": "string" }
  }
}
```

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id": { "type": "integer" },
      "sceneId": { "type": "integer" },
      "sceneTitle": { "type": "string" },
      "userId": { "type": "integer" },
      "userName": { "type": "string" },
      "userDepartmentName": { "type": "string" },
      "userTitle": { "type": "string" },
      "totalScore": { "type": "integer" },
      "durationSeconds": { "type": "integer" },
      "status": { "type": "string" },
      "startTime": { "type": "string" },
      "endTime": { "type": "string" },
      "difficulty": { "type": "string" },
      "drugName": { "type": "string" },
      "departmentName": { "type": "string" },
      "personaName": { "type": "string" },
      "trainingType": { "type": "string" }
    }
  }
}
```

## 脚本映射

- `../../scripts/training-flow/records.py`
