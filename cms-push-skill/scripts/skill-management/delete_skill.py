#!/usr/bin/env python3
"""
下架（删除）Skill

用途：将已发布的 Skill 下架

使用方式：
  python3 cms-push-skill/scripts/skill-management/delete_skill.py --id <skill-id> [--reason <下架原因>]

参数说明：
  --id       Skill ID（必须）
  --reason   下架原因（可选）

环境变量：
  XG_USER_TOKEN  — access-token（必须）
"""

import sys
import json
import argparse
import requests

from common import API_BASE, get_headers, get_token, parse_api_response

API_URL = f"{API_BASE}/api/skill/delete"


def call_api(token: str, skill_id: str, reason: str = "") -> dict:
    """下架 Skill"""
    headers = get_headers(token)

    payload = {"id": skill_id}
    if reason:
        payload["delistReason"] = reason

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            verify=False,
            allow_redirects=True,
            timeout=60,
        )
        response.raise_for_status()
        return parse_api_response(response, "下架 Skill")
    except Exception as e:
        print(f"错误: 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="下架（删除）Skill")
    parser.add_argument("--id", required=True, help="Skill ID")
    parser.add_argument("--reason", default="", help="下架原因")
    args = parser.parse_args()

    token = get_token()
    result = call_api(token, args.id, args.reason)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
