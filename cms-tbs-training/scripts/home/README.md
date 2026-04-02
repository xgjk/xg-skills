# 脚本清单 — home

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `summary.py` | `GET /tbs/home/summary` | 获取首页训战摘要（统计数据+活动分类），输出 JSON 结果 |
| `learning-videos.py` | `GET /tbs/home/learning-videos` | 获取首页视频学习任务列表，输出 JSON 结果 |
| `product-scenes.py` | `GET /tbs/home/product-scenes` | 获取产品场景列表（含按钮状态），输出 JSON 结果 |

## 使用方式

```bash
# 先通过 cms-auth-skills 准备 access-token，再设置环境变量
export XG_USER_TOKEN="your-access-token"

# 执行脚本
python3 scripts/home/summary.py
python3 scripts/home/learning-videos.py
python3 scripts/home/product-scenes.py [productId] [activityId]
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **入参定义以** `openapi/` 文档为准
4. **重试策略**：间隔1秒、最多重试3次
