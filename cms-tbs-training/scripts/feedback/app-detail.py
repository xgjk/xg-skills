#!/usr/bin/env python3
"""
feedback / app-detail 脚本

用途：获取反馈功能的应用详情

使用方式：
  python3 scripts/feedback/app-detail.py

环境变量：
  无（nologin接口）
"""

import sys
import os
import json
import urllib.request
import urllib.error
import ssl

# 接口完整 URL（与 openapi/feedback/app-detail.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/feedback/nologin/app-detail"
AUTH_MODE = "nologin"


def build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    return headers


def call_api() -> dict:
    headers = build_headers()
    req = urllib.request.Request(API_URL, headers=headers, method="GET")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
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
    result = call_api()
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
