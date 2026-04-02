#!/usr/bin/env python3
"""
home / product-scenes 脚本

用途：获取产品场景列表（含训战-练习按钮状态）

使用方式：
  python3 scripts/home/product-scenes.py [productId] [activityId]

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）

参数：
  productId   - 产品ID（可选）
  activityId  - 活动ID（可选）
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL（与 openapi/home/product-scenes.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/home/product-scenes"
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


def call_api(product_id: str = None, activity_id: str = None) -> dict:
    """调用接口，返回原始 JSON 响应"""
    headers = build_headers()

    # 构建查询参数
    params = []
    if product_id:
        params.append(f"productId={urllib.parse.quote(product_id)}")
    if activity_id:
        params.append(f"activityId={urllib.parse.quote(activity_id)}")

    url = API_URL
    if params:
        url = f"{API_URL}?{'&'.join(params)}"

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
    product_id = sys.argv[1] if len(sys.argv) > 1 else None
    activity_id = sys.argv[2] if len(sys.argv) > 2 else None

    # 调用接口，获取原始 JSON
    result = call_api(product_id, activity_id)

    # 输出结果
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
