#!/usr/bin/env python3
"""
learning / video-progress-save 脚本

用途：保存视频播放进度

使用方式：
  python3 scripts/learning/video-progress-save.py <learningItemId> <pageIndex> <progress> [isCompleted]

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）

参数：
  learningItemId - 学习任务ID（必填）
  pageIndex       - 当前播放到的片段索引，从0开始（必填）
  progress        - 当前片段已播放时长秒数（必填）
  isCompleted     - 是否已完成观看 true/false（可选）
"""

import sys
import os
import json
import urllib.request
import urllib.error
import ssl

# 接口完整 URL（与 openapi/learning/video-progress-save.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/learning/video-progress"
AUTH_MODE = "access-token"


def build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("XG_USER_TOKEN")
    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)
    headers["access-token"] = token
    return headers


def call_api(learning_item_id: str, page_index: str, progress: str, is_completed: str = None) -> dict:
    headers = build_headers()
    if not learning_item_id or not page_index or not progress:
        print("错误: learningItemId, pageIndex, progress 为必填参数", file=sys.stderr)
        sys.exit(1)
    body = {
        "learningItemId": int(learning_item_id),
        "pageIndex": int(page_index),
        "progress": float(progress)
    }
    if is_completed:
        body["isCompleted"] = is_completed.lower() == "true"
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
        print("错误: learningItemId, pageIndex, progress 为必填参数", file=sys.stderr)
        sys.exit(1)
    is_completed = sys.argv[4] if len(sys.argv) > 4 else None
    result = call_api(sys.argv[1], sys.argv[2], sys.argv[3], is_completed)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
