#!/usr/bin/env python3
"""
drug / scene-doctor-titles 脚本

用途：根据场景ID获取该场景下默认医生的职称列表

使用方式：
  python3 scripts/drug/scene-doctor-titles.py <sceneId>

环境变量：
  无（nologin接口）

参数：
  sceneId - 场景ID（必填）
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL（与 openapi/drug/scene-doctor-titles.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/scene"
AUTH_MODE = "nologin"


def build_headers() -> dict:
    """根据鉴权模式构造请求头"""
    headers = {"Content-Type": "application/json"}
    return headers


def call_api(scene_id: str) -> dict:
    """调用接口，返回原始 JSON 响应"""
    headers = build_headers()

    if not scene_id:
        print("错误: sceneId 为必填参数", file=sys.stderr)
        sys.exit(1)

    url = f"{API_URL}/{scene_id}/doctor-titles"

    req = urllib.request.Request(url, headers=headers, method="GET")

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
    if len(sys.argv) < 2:
        print("错误: sceneId 为必填参数", file=sys.stderr)
        sys.exit(1)

    scene_id = sys.argv[1]

    # 调用接口，获取原始 JSON
    result = call_api(scene_id)

    # 输出结果
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
