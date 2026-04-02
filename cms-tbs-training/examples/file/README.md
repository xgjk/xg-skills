# file — 使用说明

## 什么时候使用

- 用户问"上传文件"、"URL上传"

## 标准流程

1. 鉴权预检（按 `cms-auth-skills/common/auth.md` 获取 token）
2. 调用脚本执行
3. 输出结果摘要

## 接口说明

### upload-by-url - URL上传文件
- 必填参数：fileUrl
