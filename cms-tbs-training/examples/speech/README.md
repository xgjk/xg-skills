# speech — 使用说明

## 什么时候使用

- 用户问"PPT详情"、"查看演讲场景"
- 用户问"完成演讲"、"提交演讲结果"
- 用户问"演讲记录"、"演讲历史"

## 标准流程

1. 鉴权预检（按 `cms-auth-skills/common/auth.md` 获取 token）
2. 确定需要调用的具体接口
3. 调用对应脚本执行
4. 输出结果摘要

## 接口说明

### speech-detail - PPT场景详情
- 必填参数：sceneId
- 可选参数：activityId
- 返回PPT标题、URL、评分维度、建议时长等

### speech-finish - 完成演讲
- 必填参数：sceneId
- 可选参数：activityId, totalDurationSeconds, sourceType
- 返回综合评分和训练记录ID

### speech-records - 演讲记录详情
- 必填参数：trainingRecordId
- 返回演讲记录详情含每页回顾
