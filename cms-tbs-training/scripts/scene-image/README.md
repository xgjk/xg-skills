# 脚本清单 — scene-image

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `reset.py` | `POST /tbs/scene-image/reset` | 重置场景图片，输出 JSON 结果 |

## 使用方式

```bash
export XG_USER_TOKEN="your-access-token"
python3 scripts/scene-image/reset.py <sceneId> <imageType> <imageUrl>
```

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **重试策略**：间隔1秒、最多重试3次
