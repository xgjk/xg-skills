# learning — 使用说明

## 什么时候使用

- 用户问"视频详情"、"学习视频"
- 用户问"播放进度"、"看了多少"
- 用户问"保存进度"、"标记完成"

## 标准流程

1. 鉴权预检（按 `cms-auth-skills/common/auth.md` 获取 token）
2. 调用对应脚本执行
3. 输出结果摘要

## 接口说明

### video-detail - 视频详情
- 必填参数：learningItemId

### video-progress-get - 查询进度
- 必填参数：learningItemId

### video-progress-save - 保存进度
- 必填参数：learningItemId, pageIndex, progress
- 可选参数：isCompleted
