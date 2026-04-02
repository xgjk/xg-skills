# scene-image — 使用说明

## 什么时候使用

- 用户问"重置场景图片"

## 标准流程

1. 鉴权预检（按 `cms-auth-skills/common/auth.md` 获取 token）
2. 调用脚本执行
3. 输出结果摘要

## 接口说明

### reset - 重置场景图片
- 必填参数：sceneId, imageType, imageUrl
- imageType: SCENE_IMAGE-场景图，DIALOGUE_IMAGE-对话图
