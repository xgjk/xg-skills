# gpts — 使用说明

## 什么时候使用

- 用户问"开始训练"、"发起训战"
- 用户问"提交对话"、"回答问题"
- 用户问"生成点评"
- 用户问"下一关"

## 标准流程

1. 鉴权预检（按 `cms-auth-skills/common/auth.md` 获取 token）
2. 设置环境变量
3. 调用对应脚本执行
4. 输出结果摘要

## 环境变量设置

```bash
export XG_USER_TOKEN="your-access-token"
export XG_CORP_ID="your-corpId"
export XG_EMPLOYEE_ID="your-employeeId"
export XG_PERSON_ID="your-personId"
```

## 使用示例

### 1. 开始训练

```bash
python3 scripts/gpts/sse-suggest.py start_training <sessionId> <appId> <sceneId> [sourceId] [cloudCategoryId] [trainingType] [mode]
```

示例：
```bash
python3 scripts/gpts/sse-suggest.py start_training 2039636541957173250 2012072758615355394 7440607489067843593 58 124 practice true
```

### 2. 提交对话

```bash
python3 scripts/gpts/sse-suggest.py submit_dialogue <sessionId> <appId> <content> <trainingRecordId> <round> [type]
```

示例：
```bash
python3 scripts/gpts/sse-suggest.py submit_dialogue 2039636541957173250 2012072758615355394 "医生你好" 2039636542783377409 1 user
```

### 3. 生成AI点评

```bash
python3 scripts/gpts/sse-suggest.py generate_ai_comment <sessionId> <appId> <trainingRecordId>
```

示例：
```bash
python3 scripts/gpts/sse-suggest.py generate_ai_comment 2039636541957173250 2012072758615355394 2039636542783377409
```

### 4. 下一关

```bash
python3 scripts/gpts/sse-suggest.py next_level <sessionId> <appId> <trainingRecordId>
```

## 重要说明

### SSE Headers

必须包含以下 Headers：
- `accept`: `text/event-stream`
- `appkey`: `WtEkxhUvmHhiE4wjaYTaVcHWKiYTiLJ8`
- `content-type`: `application/json`
- `access-token`: 动态获取
- `corpid`: 动态获取
- `employeeid`: 动态获取
- `personid`: 动态获取

### start_training 注意事项

- `doctorId` 必须是 `null`，不是空字符串
- `sourceId` 必须是**数字**，不是字符串
- `mode`: `true`=练习，`false`=训战

### submit_dialogue 注意事项

- `round` 从 1 开始，每轮递增
- `type`: `user`=用户回答，`coach`=教练

### generate_ai_comment 注意事项

- `content` **不能为空**，必须填 `"生成AI点评"`（脚本自动处理）
