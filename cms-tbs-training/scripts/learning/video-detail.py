#!/usr/bin/env python3
"""
learning / video-detail 脚本

用途：获取学习视频详情

使用方式：
  python3 scripts/learning/video-detail.py <learningItemId>

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）

参数：
  learningItemId - 学习任务ID（必填）
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL（与 openapi/learning/video-detail.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/learning/video-detail"
AUTH_MODE = "access-token"


def build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("XG_USER_TOKEN")
    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)
    headers["access-token"] = token
    return headers


def call_api(learning_item_id: str) -> dict:
    headers = build_headers()
    if not learning_item_id:
        print("错误: learningItemId 为必填参数", file=sys.stderr)
        sys.exit(1)
    url = f"{API_URL}?learningItemId={urllib.parse.quote(learning_item_id)}"
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
        print("错误: learningItemId 为必填参数", file=sys.stderr)
        sys.exit(1)
    result = call_api(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
