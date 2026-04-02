# POST https://sg-al-cwork-web.mediportal.com.cn/gpts/sseClient/ai/suggest

## 作用

SSE核心接口，用于训战对话交互。支持的 action：
- `start_training`：开始训练
- `submit_dialogue`：提交对话
- `generate_ai_comment`：生成AI点评
- `next_level`：下一关

**鉴权类型**
- `access-token`

**Headers（必须）**
```json
{
  "accept": "text/event-stream",
  "appkey": "WtEkxhUvmHhiE4wjaYTaVcHWKiYTiLJ8",
  "content-type": "application/json",
  "access-token": "动态获取",
  "corpid": "动态获取（data.corpId）",
  "employeeid": "动态获取（data.empId）",
  "personid": "动态获取（data.personId）"
}
```

**Body 参数（统一格式）**
```json
{
  "sessionId": "会话ID",
  "content": "内容",
  "extMap": { ... },
  "msgList": [],
  "appId": "应用ID"
}
```

### start_training
```json
{
  "sessionId": "会话ID",
  "content": "进入训练",
  "extMap": {
    "action": "start_training",
    "sceneId": "场景ID",
    "doctorId": null,
    "sourceId": 58,
    "cloudCategoryId": "124",
    "trainingType": "practice",
    "mode": true
  },
  "msgList": [],
  "appId": "应用ID"
}
```

**注意**：
- `doctorId` 必须是 `null`，不是空字符串 `""`
- `sourceId` 必须是**数字** `58`，不是字符串 `"58"`

### submit_dialogue
```json
{
  "sessionId": "会话ID",
  "content": "用户回答内容",
  "extMap": {
    "action": "submit_dialogue",
    "trainingRecordId": "训练记录ID",
    "type": "user",
    "round": 1
  },
  "msgList": [],
  "appId": "应用ID"
}
```

**注意**：`round` 从 1 开始，每轮递增

### generate_ai_comment
```json
{
  "sessionId": "会话ID",
  "content": "生成AI点评",
  "extMap": {
    "action": "generate_ai_comment",
    "trainingRecordId": "训练记录ID"
  },
  "msgList": [],
  "appId": "应用ID"
}
```

**注意**：`content` **不能为空**，必须是 `"生成AI点评"`

### next_level
```json
{
  "sessionId": "会话ID",
  "content": "下一关",
  "extMap": {
    "action": "next_level",
    "trainingRecordId": "训练记录ID"
  },
  "msgList": [],
  "appId": "应用ID"
}
```

## SSE 事件说明

SSE 返回以下事件类型：
- `info`：业务结构化数据（trainingRecordId、openingText、score 等）
- `message`：流式文本片段
- `error`：业务错误
- `success`：流式结束/成功通知

## 脚本映射

- `../../scripts/gpts/sse-suggest.py`
