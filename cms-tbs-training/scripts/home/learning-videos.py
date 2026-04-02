#!/usr/bin/env python3
"""
home / learning-videos 脚本

用途：获取首页视频学习任务列表

使用方式：
  python3 scripts/home/learning-videos.py

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）
"""

import sys
import os
import json
import urllib.request
import urllib.error
import ssl

# 接口完整 URL（与 openapi/home/learning-videos.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/home/learning-videos"
AUTH_MODE = "access-token"


def build_headers() -> dict:
    """根据鉴权模式构造请求头"""
    headers = {"Content-Type": "application/json"}

    if AUTH_MODE == "access-token":
        token = os.environ.get("XG_USER_TOKEN")
        if not token:
            print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
            sys.exit(1)
        headers["access-token"] = token

    return headers


def call_api() -> dict:
    """调用接口，返回原始 JSON 响应"""
    headers = build_headers()

    req = urllib.request.Request(API_URL, headers=headers, method="GET")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # 重试策略：间隔1秒，最多重试3次
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
    # 调用接口，获取原始 JSON
    result = call_api()

    # 输出结果
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
