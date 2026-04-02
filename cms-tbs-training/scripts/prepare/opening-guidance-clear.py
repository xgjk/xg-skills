#!/usr/bin/env python3
"""
prepare / opening-guidance-clear 脚本

用途：清空开场指导缓存

使用方式：
  python3 scripts/prepare/opening-guidance-clear.py <sceneId> [doctorId]

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）

参数：
  sceneId  - 场景ID（必填）
  doctorId - 医生ID（可选，不传则清空该场景下所有医生的缓存）
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL（与 openapi/prepare/opening-guidance-clear.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/training-prepare/clear-opening-guidance-cache/inner"
AUTH_MODE = "access-token"


def build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("XG_USER_TOKEN")
    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)
    headers["access-token"] = token
    return headers


def call_api(scene_id: str, doctor_id: str = None) -> dict:
    headers = build_headers()
    if not scene_id:
        print("错误: sceneId 为必填参数", file=sys.stderr)
        sys.exit(1)
    params = [f"sceneId={urllib.parse.quote(scene_id)}"]
    if doctor_id:
        params.append(f"doctorId={urllib.parse.quote(doctor_id)}")
    url = f"{API_URL}?{'&'.join(params)}"
    req = urllib.request.Request(url, headers=headers, method="DELETE")
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
    doctor_id = sys.argv[2] if len(sys.argv) > 2 else None
    result = call_api(sys.argv[1], doctor_id)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
