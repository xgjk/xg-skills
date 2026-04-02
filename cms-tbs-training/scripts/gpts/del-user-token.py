#!/usr/bin/env python3
"""
gpts / del-user-token 脚本

用途：释放并发token

使用方式：
  python3 scripts/gpts/del-user-token.py <appId>

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）
  XG_CORP_ID     — corpId（必须；由 cms-auth-skills 预先准备）
  XG_EMPLOYEE_ID — employeeId（必须；由 cms-auth-skills 预先准备）
  XG_PERSON_ID   — personId（必须；由 cms-auth-skills 预先准备）

参数：
  appId - 应用ID（必填）
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL（与 openapi/gpts/del-user-token.md 中声明的一致）
BASE_URL = "https://sg-al-cwork-web.mediportal.com.cn"
API_URL = f"{BASE_URL}/gpts/accessToken/delUserToken"


def build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("XG_USER_TOKEN")
    corp_id = os.environ.get("XG_CORP_ID")
    employee_id = os.environ.get("XG_EMPLOYEE_ID")
    person_id = os.environ.get("XG_PERSON_ID")

    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)
    if not corp_id:
        print("错误: 请设置环境变量 XG_CORP_ID", file=sys.stderr)
        sys.exit(1)
    if not employee_id:
        print("错误: 请设置环境变量 XG_EMPLOYEE_ID", file=sys.stderr)
        sys.exit(1)
    if not person_id:
        print("错误: 请设置环境变量 XG_PERSON_ID", file=sys.stderr)
        sys.exit(1)

    headers["access-token"] = token
    headers["corpid"] = corp_id
    headers["employeeid"] = employee_id
    headers["personid"] = person_id

    return headers


def call_api(app_id: str) -> dict:
    headers = build_headers()
    if not app_id:
        print("错误: appId 为必填参数", file=sys.stderr)
        sys.exit(1)

    url = f"{API_URL}?appId={urllib.parse.quote(app_id)}"
    req = urllib.request.Request(url, headers=headers, method="POST")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
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
    result = call_api(app_id)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
