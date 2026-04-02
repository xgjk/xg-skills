# drug — 使用说明

## 什么时候使用

- 用户问"有哪些药品"、"获取药品列表"
- 用户问"查看场景列表"、"根据药品查场景"
- 用户问"场景详情"、"场景职称"、"场景热词"

## 标准流程

1. 确定需要调用的具体接口
2. 调用对应脚本执行查询
3. 输出结果摘要

## 接口说明

### drug-list - 药品列表
- 无需参数
- 返回所有已启用的药品

### scene-list - 场景列表（by external_id）
- 可选参数：externalId, corpId
- 根据药品external_id查询场景

### scene-list-by-drug - 场景列表（by drugId）
- 必填参数：drugId
- 根据药品ID查询场景

### scene-doctor-titles - 场景职称
- 必填参数：sceneId
- 获取场景下默认医生的职称

### scene-hotwords - 场景热词
- 必填参数：sceneId
- 获取场景热词（格式：词1|5,词2|5）
