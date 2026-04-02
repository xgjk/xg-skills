# 脚本清单 — learning

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `video-detail.py` | `GET /tbs/learning/video-detail` | 获取视频详情，输出 JSON 结果 |
| `video-progress-get.py` | `GET /tbs/learning/video-progress` | 查询播放进度，输出 JSON 结果 |
| `video-progress-save.py` | `POST /tbs/learning/video-progress` | 保存播放进度，输出 JSON 结果 |

## 使用方式

```bash
export XG_USER_TOKEN="your-access-token"
python3 scripts/learning/video-detail.py <learningItemId>
python3 scripts/learning/video-progress-get.py <learningItemId>
python3 scripts/learning/video-progress-save.py <learningItemId> <pageIndex> <progress> [isCompleted]
```

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **重试策略**：间隔1秒、最多重试3次
