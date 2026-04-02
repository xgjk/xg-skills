#!/usr/bin/env python3
"""
speech / speech-detail 脚本

用途：获取PPT场景详情

使用方式：
  python3 scripts/speech/speech-detail.py <sceneId> [activityId]

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）

参数：
  sceneId   - 场景ID（必填）
  activityId - 活动ID（可选）
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL（与 openapi/speech/speech-detail.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/speech/detail"
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


def call_api(scene_id: str, activity_id: str = None) -> dict:
    """调用接口，返回原始 JSON 响应"""
    headers = build_headers()

    if not scene_id:
        print("错误: sceneId 为必填参数", file=sys.stderr)
        sys.exit(1)

    params = [f"sceneId={urllib.parse.quote(scene_id)}"]
    if activity_id:
        params.append(f"activityId={urllib.parse.quote(activity_id)}")

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
        print("错误: sceneId 为必填参数", file=sys.stderr)
        sys.exit(1)

    scene_id = sys.argv[1]
    activity_id = sys.argv[2] if len(sys.argv) > 2 else None

    result = call_api(scene_id, activity_id)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
