#!/usr/bin/env python3
"""
speech / speech-finish 脚本

用途：完成演讲并生成复盘

使用方式：
  python3 scripts/speech/speech-finish.py <sceneId> [activityId] [totalDurationSeconds] [sourceType]

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）

参数：
  sceneId            - 场景ID（必填）
  activityId         - 活动ID（可选）
  totalDurationSeconds - 总时长秒数（可选）
  sourceType         - 来源类型：practice/battle（可选）
"""

import sys
import os
import json
import urllib.request
import urllib.error
import ssl

# 接口完整 URL（与 openapi/speech/speech-finish.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/speech/finish"
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


def call_api(scene_id: str, activity_id: str = None, total_duration: int = None, source_type: str = None) -> dict:
    """调用接口，返回原始 JSON 响应"""
    headers = build_headers()

    if not scene_id:
        print("错误: sceneId 为必填参数", file=sys.stderr)
        sys.exit(1)

    body = {"sceneId": int(scene_id)}

    if activity_id:
        body["activityId"] = int(activity_id)
    if total_duration:
        body["totalDurationSeconds"] = int(total_duration)
    if source_type:
        body["sourceType"] = source_type

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
    if len(sys.argv) < 2:
        print("错误: sceneId 为必填参数", file=sys.stderr)
        sys.exit(1)

    scene_id = sys.argv[1]
    activity_id = sys.argv[2] if len(sys.argv) > 2 else None
    total_duration = sys.argv[3] if len(sys.argv) > 3 else None
    source_type = sys.argv[4] if len(sys.argv) > 4 else None

    result = call_api(scene_id, activity_id, total_duration, source_type)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
