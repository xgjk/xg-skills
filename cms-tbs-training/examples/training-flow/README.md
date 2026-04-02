# training-flow — 使用说明

## 什么时候使用

- 用户问"获取药品列表（公开）"
- 用户问"训练记录列表（公开）"
- 用户问"场景列表（公开）"

## 标准流程

1. 调用对应脚本执行
2. 输出结果摘要

## 接口说明

### drugs - 药品列表
- 无需参数

### records - 训练记录列表
- 必填参数：sceneId
- 可选参数：pageNum, pageSize, userName, startDate, endDate

### scenes - 场景列表
- 必填参数：drugId
