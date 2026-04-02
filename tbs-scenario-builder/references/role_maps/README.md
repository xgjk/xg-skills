## role_maps

本目录用于承载“角色身份标准化”的可维护映射表。

目标：当用户输入出现新的角色称谓（例如新岗位、新业务角色）时，不需要改 Skill 核心流程，只需要更新映射表即可让：
- `persona_packs` 更稳定命中合适的底座画像
- `prompt_packs` 更稳定命中合适的提示词模板

### 文件
- `role_type_map.json`：同义词/关键词到 roleType 的映射（支持多标签）

### roleType 建议集合（可扩展）
- 对话对象（AI）常用：`doctor` / `customer` / `patient` / `business_manager` / `system_admin` / `other`
- 学习者常用：`pharma_rep` / `sales_rep` / `employee` / `other`

