# TBS训战平台 - 接口规范（最终版 v0.6）

## 用户身份信息（动态获取）

| 字段 | 值 | 来源 |
|------|-----|------|
| `personid` | 1686208053803053058 | `/user/login/appkey` 返回的 personId |
| `employeeid` | 1686208053807247361 | `/user/login/appkey` 返回的 empId |
| `corpid` | 1509805893730611201 | `/user/login/appkey` 返回的 corpId |
| `access-token` | 登录获取 | `/user/login/appkey` 返回的 xgToken |

## SSE 接口固定 Header

| Header | 值 |
|--------|-----|
| `accept` | `text/event-stream` |
| `appkey` | `WtEkxhUvmHhiE4wjaYTaVcHWKiYTiLJ8` |
| `content-type` | `application/json` |

**动态 Headers**：`access-token`、`corpid`、`employeeid`、`personid`（从登录接口获取）

## 训战完整流程

### Step 1: 创建会话
```
POST /gpts/session/getSessionByBusinessId
Body: { "appId": "xxx", "businessId": "sceneId", "businessType": "training", "isForce": false }
```

### Step 2: 开始训练
```
POST /gpts/sseClient/ai/suggest
Body: {
  "sessionId": "xxx",
  "content": "进入训练",
  "extMap": {
    "action": "start_training",
    "sceneId": "xxx",
    "doctorId": null,
    "sourceId": 58,
    "cloudCategoryId": "124",
    "trainingType": "practice",
    "mode": true
  },
  "msgList": [],
  "appId": "xxx"
}
```

### Step 3: 获取开场白建议（仅练习模式）
```
POST /tbs/training-prepare/get-opening-guidance
Body: { "sceneId": "xxx" }
```

### Step 4: 对话循环
```
POST /gpts/sseClient/ai/suggest
Body: {
  "sessionId": "xxx",
  "content": "用户回答内容",
  "extMap": {
    "action": "submit_dialogue",
    "trainingRecordId": "xxx",
    "type": "user",
    "round": 1
  },
  "msgList": [],
  "appId": "xxx"
}
```

### Step 5: 生成AI点评（对话结束后自动调用）
当医生回复中出现 `[对话结束]` 或 `【对话结束】` 时：
```
POST /gpts/sseClient/ai/suggest
Body: {
  "sessionId": "xxx",
  "content": "生成AI点评",
  "extMap": {
    "action": "generate_ai_comment",
    "trainingRecordId": "xxx"
  },
  "msgList": [],
  "appId": "xxx"
}
```

**注意**：`content` **必须填 `"生成AI点评"**，不能为空！

### Step 6: 释放token
```
POST /gpts/accessToken/delUserToken?appId=xxx
```

## 业务规则说明

### 练习模式 vs 训战模式

| 项目 | 练习 (mode=true) | 训战 (mode=false) |
|------|-----------------|------------------|
| 开场白建议 | ✅ 有 | ❌ 没有 |
| 教练点评 (coachGuidance) | ✅ 有 | ❌ 没有 |
| 金牌建议话术 (demoResponse) | ✅ 有 | ❌ 没有 |

**结论**：
- **练习模式 (mode=true)**：完整功能 - 开场白建议、教练点评、金牌建议话术都有
- **训战模式 (mode=false)**：纯实战 - 什么都没有，全靠自己

### 对话结束判断

当医生回复中出现以下标记时，表示对话结束：
- `[对话结束]`
- `【对话结束】`

此时应自动调用 `generate_ai_comment` 生成AI点评。
