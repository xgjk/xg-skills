#!/usr/bin/env python3
"""
training-flow / scenes 脚本

用途：根据药品ID获取已发布的场景列表（公开接口）

使用方式：
  python3 scripts/training-flow/scenes.py <drugId>

环境变量：
  无（nologin接口）

参数：
  drugId - 药品ID（必填）
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL（与 openapi/training-flow/scenes.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/training-flow/nologin/scenes"
AUTH_MODE = "nologin"


def build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    return headers


def call_api(drug_id: str) -> dict:
    headers = build_headers()
    if not drug_id:
        print("错误: drugId 为必填参数", file=sys.stderr)
        sys.exit(1)
    url = f"{API_URL}?drugId={urllib.parse.quote(drug_id)}"
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
    if len(sys.argv) < 2:
        print("错误: drugId 为必填参数", file=sys.stderr)
        sys.exit(1)
    result = call_api(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
