# training — 使用说明

## 什么时候使用

- 用户问"我的训战统计"、"统计数据"
- 用户问"训战记录"、"记录列表"
- 用户问"记录详情"、"查看某个记录"

## 标准流程

1. 鉴权预检（按 `cms-auth-skills/common/auth.md` 获取 token）
2. 确定需要调用的具体接口
3. 调用对应脚本执行
4. 输出结果摘要

## 接口说明

### my-stats - 我的统计数据
- 无需参数
- 返回当前用户的训战统计数据

### records - 记录列表
- 可选参数：page, size, sourceType
- sourceType: battle-训战，practice-练习

### records-detail - 记录详情
- 必填参数：id（记录ID）
- 返回记录详情含对话回溯
