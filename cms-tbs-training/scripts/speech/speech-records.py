#!/usr/bin/env python3
"""
speech / speech-records 脚本

用途：获取演讲记录详情

使用方式：
  python3 scripts/speech/speech-records.py <trainingRecordId>

环境变量：
  XG_USER_TOKEN  — access-token（必须；由 cms-auth-skills 预先准备）

参数：
  trainingRecordId - 训练记录ID（必填）
"""

import sys
import os
import json
import urllib.request
import urllib.error
import ssl

# 接口完整 URL（与 openapi/speech/speech-records.md 中声明的一致）
API_URL = "https://sg-cwork-web.mediportal.com.cn/tbs/speech/records"
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


def call_api(training_record_id: str) -> dict:
    """调用接口，返回原始 JSON 响应"""
    headers = build_headers()

    if not training_record_id:
        print("错误: trainingRecordId 为必填参数", file=sys.stderr)
        sys.exit(1)

    url = f"{API_URL}/{training_record_id}"

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
        print("错误: trainingRecordId 为必填参数", file=sys.stderr)
        sys.exit(1)

    training_record_id = sys.argv[1]

    result = call_api(training_record_id)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
