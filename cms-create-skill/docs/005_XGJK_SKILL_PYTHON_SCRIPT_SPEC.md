# Python 脚本规范

本规范用于统一 `scripts/` 下 Python 脚本的写法，确保脚本既能被 AI 调用，也能在命令行独立执行。

## 1. 文件与职责

- 所有业务脚本必须使用 `.py` 后缀
- 一个脚本只负责一个明确动作
- 每个脚本都必须能直接在命令行运行
- 每个脚本都必须在模块说明和脚本索引里有明确入口

## 2. 推荐文件结构

推荐结构如下：

```python
"""
简要说明脚本作用、依赖的鉴权前置条件和最小调用示例。
"""

import argparse
import json
import time
import requests

API_URL = 'https://example.com/api'
AUTH_MODE = 'access-token'
TIMEOUT = 60
MAX_RETRIES = 3
RETRY_INTERVAL = 1


def build_headers() -> dict:
    ...


def call_api(payload: dict) -> dict:
    ...


def main() -> None:
    ...


if __name__ == '__main__':
    main()
```

## 3. 命令行要求

- 使用 `argparse` 解析参数
- 参数名与文档中的字段名保持一致
- 缺失必填参数时，应给出明确报错
- 不把复杂业务逻辑塞进命令行参数描述里

## 4. 请求与重试要求

- 使用 `requests` 发起请求
- 显式设置 `timeout`
- 如业务允许重试，间隔至少 1 秒，最多 3 次
- 严禁无限循环重试
- 超过最大次数后必须抛出或输出明确错误
- 如需关闭证书校验或跟随跳转，应在代码中显式写出，而不是依赖默认行为

## 5. 输出要求

- 默认输出结构化 JSON
- 成功输出应优先保留最小必要字段
- 失败输出应包含明确错误原因
- 非调试场景不直接回显整段原始响应
- 输出需兼顾 AI 可读性与命令行可读性

## 6. 鉴权要求

- 鉴权模式必须与模块说明、脚本索引保持一致
- 需要 `appKey` 或 `access-token` 时，统一通过 `cms-auth-skills` 获取
- `nologin` 动作不依赖额外鉴权获取流程
- 业务脚本不负责登录、不负责换取 token

## 7. 日志与状态

- 如脚本需要日志，统一写入 `.cms-log/log/<skillcode>/`
- 如脚本需要缓存或状态，统一写入 `.cms-log/state/<skillcode>/`
- 日志中不得输出 token、appKey、authorization 等敏感值
- 不将运行时状态写回 Skill 包目录

## 8. 交付前自检

每个脚本完成后，至少检查以下事项：

- 脚本文件名是否与路由表一致
- 参数名是否与文档一致
- 鉴权模式是否与文档一致
- 超时、重试、错误退出是否明确
- `main()` 和 `if __name__ == '__main__'` 是否齐全
