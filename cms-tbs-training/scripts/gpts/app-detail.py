#!/usr/bin/env python3
"""
gpts / app-detail 脚本

用途：获取GPT应用详情

使用方式：
  python3 scripts/gpts/app-detail.py <appId> [corpId]

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）

参数：
  appId  - 应用ID（必填）
  corpId - 企业ID（可选）
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL（与 openapi/gpts/app-detail.md 中声明的一致）
BASE_URL = "https://sg-al-cwork-web.mediportal.com.cn"
API_URL = f"{BASE_URL}/gpts/gptApp/getDetailByIdV2"
AUTH_MODE = "access-token"


def build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("XG_USER_TOKEN")
    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)
    headers["access-token"] = token
    return headers


def call_api(app_id: str, corp_id: str = None) -> dict:
    headers = build_headers()
    if not app_id:
        print("错误: appId 为必填参数", file=sys.stderr)
        sys.exit(1)

    params = [f"id={urllib.parse.quote(app_id)}"]
    if corp_id:
        params.append(f"corpId={urllib.parse.quote(corp_id)}")

    url = f"{API_URL}?{'&'.join(params)}"
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
        print("错误: appId 为必填参数", file=sys.stderr)
        sys.exit(1)

    app_id = sys.argv[1]
    corp_id = sys.argv[2] if len(sys.argv) > 2 else None

    result = call_api(app_id, corp_id)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
