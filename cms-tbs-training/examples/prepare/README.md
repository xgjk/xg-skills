# prepare — 使用说明

## 什么时候使用

- 用户问"开场指导"、"获取开场话术"
- 用户问"清除开场缓存"

## 标准流程

1. 鉴权预检（按 `cms-auth-skills/common/auth.md` 获取 token）
2. 调用对应脚本执行
3. 输出结果摘要

## 接口说明

### opening-guidance - 获取开场指导
- 必填参数：sceneId
- 返回策略建议、话术选项、洞察信息

### opening-guidance-clear - 清除开场缓存
- 必填参数：sceneId
- 可选参数：doctorId
