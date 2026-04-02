#!/usr/bin/env python3
"""
drug / drug-list 脚本

用途：获取所有已启用的药品列表

使用方式：
  python3 scripts/drug/drug-list.py

环境变量：
  无（nologin接口）
"""

import sys
import os
import json
import urllib.request
import urllib.error
import ssl

# 接口完整 URL（与 openapi/drug/drug-list.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/training-flow/nologin/drugs"
AUTH_MODE = "nologin"


def build_headers() -> dict:
    """根据鉴权模式构造请求头"""
    headers = {"Content-Type": "application/json"}
    return headers


def call_api() -> dict:
    """调用接口，返回原始 JSON 响应"""
    headers = build_headers()

    req = urllib.request.Request(API_URL, headers=headers, method="GET")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # 重试策略：间隔1秒，最多重试3次
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as e:
            if attempt < 2:
                import time
                time.sleep(1)
                continue
            print(f"错误: 请求失败 - {e}", file=sys.stderr)
            sys.exit(1)


def main():
    # 调用接口，获取原始 JSON
    result = call_api()

    # 输出结果
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
