# TBS 训战平台 - 接口规范（最终版 v0.8）

## 用户身份信息（动态获取）

| 字段           | 值                  | 来源                                 |
| -------------- | ------------------- | ------------------------------------ |
| `personid`     | 1686208053803053058 | `/user/login/appkey` 返回的 personId |
| `employeeid`   | 1686208053807247361 | `/user/login/appkey` 返回的 empId    |
| `corpid`       | 1509805893730611201 | `/user/login/appkey` 返回的 corpId   |
| `access-token` | 登录获取            | `/user/login/appkey` 返回的 xgToken  |

## SSE 接口固定 Header

| Header         | 值                                 |
| -------------- | ---------------------------------- |
| `accept`       | `text/event-stream`                |
| `appkey`       | `WtEkxhUvmHhiE4wjaYTaVcHWKiYTiLJ8` |
| `content-type` | `application/json`                 |

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

每轮都要**完整输出**：

- 用户的回答
- 医生的回复
- 教练点评

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

### Step 5: 生成 AI 点评

**触发条件**：当医生回复中出现 `[对话结束]` 或 `【对话结束】` 时

**注意**：要先完整展示当前轮的对话（用户回答、医生回复、教练点评），然后再调用 generate_ai_comment

**必须调用 generate_ai_comment**：

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

**注意**：`content` **必须填 `"生成 AI 点评"**，不能为空！

**输出**：总分、维度评分、亮点、改进建议、合规状态

### Step 6: 释放 token

```
POST /gpts/accessToken/delUserToken?appId=xxx
```

## 业务规则说明

### 练习模式 vs 训战模式

| 项目                        | 练习 (mode=true) | 训战 (mode=false) |
| --------------------------- | ---------------- | ----------------- |
| 开场白建议                  | ✅ 有            | ❌ 没有           |
| 教练点评 (coachGuidance)    | ✅ 有            | ❌ 没有           |
| 金牌建议话术 (demoResponse) | ✅ 有            | ❌ 没有           |

**结论**：

- **练习模式 (mode=true)**：完整功能 - 开场白建议、教练点评、金牌建议话术都有
- **训战模式 (mode=false)**：纯实战 - 什么都没有，全靠自己

### 对话结束判断

当医生回复中出现以下标记时，表示对话结束：

- `[对话结束]`
- `【对话结束】`

### 完整对话流程示例

```
=== 第1轮对话 ===
【你的回答】
开场白...

【医生回复】
医生回复内容

【教练点评】
评价: ...
医生意图: ...
合规: ✅
金牌话术: ...
提示: ...

=== 第2轮对话 ===
【你的回答】
回答内容...

【医生回复】
医生回复内容...

【教练点评】
评价: ...
医生意图: ...
合规: ✅
金牌话术: ...
提示: ...

=== 第N轮对话（循环进行）===
【你的回答】
回答内容...

【医生回复】
医生回复内容...

【教练点评】
评价: ...
医生意图: ...
合规: ✅
金牌话术: ...
提示: ...

...（按上述结构持续循环）

当某一轮医生回复出现 `[对话结束]` 或 `【对话结束】` 时，当前轮完整展示后结束并进入AI点评流程

==================================================
【对话结束，自动调用生成AI点评】
==================================================

【总分】92
【总评】表现优秀...
【维度评分】
  - 需求洞察: 18
  - 开场与礼貌边界: 18
  - ...
【亮点】
  - 专业基础知识扎实...
【改进建议】
  - 应在结尾处更积极提出下一步行动...
【合规】✅

==================================================
练习完成！
==================================================
```

## 重要提醒

1. **每轮对话都要完整展示**：用户回答、医生回复、教练点评
2. **检测到对话结束后**：先展示完整对话，再调用 generate_ai_comment，最后展示 AI 点评结果
3. **generate_ai_comment 的 content 必须填 `"生成 AI 点评"**，不能为空
