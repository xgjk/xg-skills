#!/usr/bin/env python3
"""
training / my-stats 脚本

用途：获取当前用户的训战统计数据

使用方式：
  python3 scripts/training/my-stats.py

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）
"""

import sys
import os
import json
import urllib.request
import urllib.error
import ssl

# 接口完整 URL（与 openapi/training/my-stats.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/training/my-stats"
AUTH_MODE = "access-token"


def build_headers() -> dict:
    """根据鉴权模式构造请求头"""
    headers = {"Content-Type": "application/json"}

    token = os.environ.get("XG_USER_TOKEN")
    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)
    headers["access-token"] = token

    return headers


def call_api() -> dict:
    """调用接口，返回原始 JSON 响应"""
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
