# 脚本清单 — file

## 共享依赖

无

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `upload-by-url.py` | `GET /tbs/file/upload-by-url` | URL上传文件，输出 JSON 结果 |

## 使用方式

```bash
export XG_USER_TOKEN="your-access-token"
python3 scripts/file/upload-by-url.py <fileUrl>
```

## 规范

1. **必须使用 Python** 编写
2. **鉴权遵循** `cms-auth-skills/common/auth.md` 规范
3. **重试策略**：间隔1秒、最多重试3次
