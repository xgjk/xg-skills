#!/usr/bin/env python3
"""
feedback / gpt-id 脚本

用途：获取反馈功能的GPT ID

使用方式：
  python3 scripts/feedback/gpt-id.py [type]

环境变量：
  无（nologin接口）

参数：
  type - 类型：speech返回PPT演讲反馈GPT（可选）
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL（与 openapi/feedback/gpt-id.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/feedback/nologin/gpt-id"
AUTH_MODE = "nologin"


def build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    return headers


def call_api(type_val: str = None) -> dict:
    headers = build_headers()
    url = API_URL
    if type_val:
        url = f"{API_URL}?type={urllib.parse.quote(type_val)}"
    req = urllib.request.Request(url, headers=headers, method="GET")
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
    type_val = sys.argv[1] if len(sys.argv) > 1 else None
    result = call_api(type_val)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
