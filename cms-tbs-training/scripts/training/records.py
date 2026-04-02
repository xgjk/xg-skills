#!/usr/bin/env python3
"""
training / records 脚本

用途：获取训战记录列表（分页）

使用方式：
  python3 scripts/training/records.py [page] [size] [sourceType]

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）

参数：
  page      - 页码，从1开始（可选）
  size      - 每页条数（可选）
  sourceType - 来源类型：battle-训战，practice-练习（可选）
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL（与 openapi/training/records.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/training/records"
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


def call_api(page: str = None, size: str = None, source_type: str = None) -> dict:
    """调用接口，返回原始 JSON 响应"""
    headers = build_headers()

    params = []
    if page:
        params.append(f"page={urllib.parse.quote(page)}")
    if size:
        params.append(f"size={urllib.parse.quote(size)}")
    if source_type:
        params.append(f"sourceType={urllib.parse.quote(source_type)}")

    url = API_URL
    if params:
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
    page = sys.argv[1] if len(sys.argv) > 1 else None
    size = sys.argv[2] if len(sys.argv) > 2 else None
    source_type = sys.argv[3] if len(sys.argv) > 3 else None

    result = call_api(page, size, source_type)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
