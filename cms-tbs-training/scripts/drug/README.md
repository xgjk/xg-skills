# 脚本清单 — drug

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `drug-list.py` | `GET /tbs/training-flow/nologin/drugs` | 获取药品列表，输出 JSON 结果 |
| `scene-list.py` | `GET /tbs/scene/list-by-drug-external-id` | 根据external_id获取场景列表，输出 JSON 结果 |
| `scene-list-by-drug.py` | `GET /tbs/training-flow/nologin/scenes` | 根据药品ID获取场景列表，输出 JSON 结果 |
| `scene-doctor-titles.py` | `GET /tbs/scene/{sceneId}/doctor-titles` | 获取场景职称列表，输出 JSON 结果 |
| `scene-hotwords.py` | `GET /tbs/scene/{sceneId}/hotwords` | 获取场景热词列表，输出 JSON 结果 |

## 使用方式

```bash
# nologin 接口无需设置鉴权环境变量

# 执行脚本
python3 scripts/drug/drug-list.py
python3 scripts/drug/scene-list.py [externalId] [corpId]
python3 scripts/drug/scene-list-by-drug.py <drugId>
python3 scripts/drug/scene-doctor-titles.py <sceneId>
python3 scripts/drug/scene-hotwords.py <sceneId>
```

## 输出说明

所有脚本的输出均为 **JSON 格式**。

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **入参定义以** `openapi/` 文档为准
4. **重试策略**：间隔1秒、最多重试3次
