#!/usr/bin/env python3
"""
gpts / training-interact 脚本

用途：训练交互

使用方式：
  python3 scripts/gpts/training-interact.py [content] [sessionId]

环境变量：
  无（nologin接口）

参数：
  content   - 用户输入内容（可选）
  sessionId - 会话ID（可选）
"""

import sys
import os
import json
import urllib.request
import urllib.error
import ssl

# 接口完整 URL（与 openapi/gpts/training-interact.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/gpts/nologin/training/interact"
AUTH_MODE = "nologin"


def build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    return headers


def call_api(content: str = None, session_id: str = None) -> dict:
    headers = build_headers()
    body = {
        "request": {
            "content": content or "",
            "sessionId": session_id or ""
        }
    }
    req_body = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(API_URL, data=req_body, headers=headers, method="POST")
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
    content = sys.argv[1] if len(sys.argv) > 1 else None
    session_id = sys.argv[2] if len(sys.argv) > 2 else None
    result = call_api(content, session_id)
    print(json.dumps(result, ensure_ascii=False))


if __name -- "__main__":
    main()
