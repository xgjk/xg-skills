# home — 使用说明

## 什么时候使用

- 用户问"首页有什么"、"本周训战统计"、"查看活动分类"
- 用户问"有哪些学习视频"、"视频任务"
- 用户问"产品场景列表"、"场景的训战按钮状态"

## 标准流程

1. 鉴权预检（按 `cms-auth-skills/common/auth.md` 获取 token）
2. 确定需要调用的具体接口（summary / learning-videos / product-scenes）
3. 调用对应脚本执行查询
4. 输出结果摘要（统计数据、活动分类、视频任务列表等）

## 接口说明

### summary - 首页摘要
- 无需额外参数
- 返回本周训战统计数据和活动分类列表

### learning-videos - 视频学习任务
- 无需额外参数
- 返回视频学习任务列表含完成状态

### product-scenes - 产品场景
- 可选参数：productId, activityId
- 返回场景列表含训战/练习按钮状态
