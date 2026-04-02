#!/usr/bin/env python3
"""
gpts / session 脚本

用途：获取或创建会话

使用方式：
  python3 scripts/gpts/session.py <appId> <businessId> <businessType> [isForce]

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）

参数：
  appId       - 应用ID（必填）
  businessId  - 业务ID（必填）
  businessType - 业务类型（必填）
  isForce     - 是否强制创建新会话 true/false（可选，默认false）
"""

import sys
import os
import json
import urllib.request
import urllib.error
import ssl

# 接口完整 URL（与 openapi/gpts/session.md 中声明的一致）
BASE_URL = "https://sg-al-cwork-web.mediportal.com.cn"
API_URL = f"{BASE_URL}/gpts/session/getSessionByBusinessId"
AUTH_MODE = "access-token"


def build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("XG_USER_TOKEN")
    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)
    headers["access-token"] = token
    return headers


def call_api(app_id: str, business_id: str, business_type: str, is_force: bool = False) -> dict:
    headers = build_headers()
    if not app_id or not business_id or not business_type:
        print("错误: appId, businessId, businessType 为必填参数", file=sys.stderr)
        sys.exit(1)

    body = {
        "appId": app_id,
        "businessId": business_id,
        "businessType": business_type,
        "isForce": is_force
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
    if len(sys.argv) < 4:
        print("错误: appId, businessId, businessType 为必填参数", file=sys.stderr)
        sys.exit(1)

    app_id = sys.argv[1]
    business_id = sys.argv[2]
    business_type = sys.argv[3]
    is_force = sys.argv[4].lower() == "true" if len(sys.argv) > 4 else False

    result = call_api(app_id, business_id, business_type, is_force)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
