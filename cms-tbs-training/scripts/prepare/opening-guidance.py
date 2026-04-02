#!/usr/bin/env python3
"""
prepare / opening-guidance 脚本

用途：获取开场指导

使用方式：
  python3 scripts/prepare/opening-guidance.py <sceneId>

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）

参数：
  sceneId - 场景ID（必填）
"""

import sys
import os
import json
import urllib.request
import urllib.error
import ssl

# 接口完整 URL（与 openapi/prepare/opening-guidance.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/training-prepare/get-opening-guidance"
AUTH_MODE = "access-token"


def build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("XG_USER_TOKEN")
    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)
    headers["access-token"] = token
    return headers


def call_api(scene_id: str) -> dict:
    headers = build_headers()
    if not scene_id:
        print("错误: sceneId 为必填参数", file=sys.stderr)
        sys.exit(1)
    body = json.dumps({"sceneId": scene_id}).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")
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
        print("错误: sceneId 为必填参数", file=sys.stderr)
        sys.exit(1)
    result = call_api(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
