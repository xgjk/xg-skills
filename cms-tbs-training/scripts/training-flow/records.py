#!/usr/bin/env python3
"""
training-flow / records 脚本

用途：获取训练记录列表（公开接口）

使用方式：
  python3 scripts/training-flow/records.py <sceneId> [pageNum] [pageSize] [userName] [startDate] [endDate]

环境变量：
  无（nologin接口）

参数：
  sceneId  - 场景ID（必填）
  pageNum  - 页码从1开始（可选）
  pageSize - 每页数量（可选）
  userName - 用户姓名用于模糊查询（可选）
  startDate - 开始日期格式yyyy-MM-dd（可选）
  endDate  - 结束日期格式yyyy-MM-dd（可选）
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL（与 openapi/training-flow/records.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/training-flow/nologin/records"
AUTH_MODE = "nologin"


def build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    return headers


def call_api(scene_id: str, page_num: str = None, page_size: str = None, user_name: str = None, start_date: str = None, end_date: str = None) -> dict:
    headers = build_headers()
    if not scene_id:
        print("错误: sceneId 为必填参数", file=sys.stderr)
        sys.exit(1)
    params = [f"sceneId={urllib.parse.quote(scene_id)}"]
    if page_num:
        params.append(f"pageNum={urllib.parse.quote(page_num)}")
    if page_size:
        params.append(f"pageSize={urllib.parse.quote(page_size)}")
    if user_name:
        params.append(f"userName={urllib.parse.quote(user_name)}")
    if start_date:
        params.append(f"startDate={urllib.parse.quote(start_date)}")
    if end_date:
        params.append(f"endDate={urllib.parse.quote(end_date)}")
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
    page_num = sys.argv[2] if len(sys.argv) > 2 else None
    page_size = sys.argv[3] if len(sys.argv) > 3 else None
    user_name = sys.argv[4] if len(sys.argv) > 4 else None
    start_date = sys.argv[5] if len(sys.argv) > 5 else None
    end_date = sys.argv[6] if len(sys.argv) > 6 else None
    result = call_api(scene_id, page_num, page_size, user_name, start_date, end_date)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
