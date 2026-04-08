#!/usr/bin/env python3
"""
更新已有 Skill

用途：更新已注册 Skill 的信息（名称、描述、下载地址等）（ClawHub 协议格式）

使用方式：
  python3 cms-push-skill/scripts/skill-management/update_skill.py --code <code> [--name <name>] [--description <desc>] [--download-url <url>] [--label <label>] [--version <ver>]

参数说明：
  --code          Skill 唯一标识（必须）
  --name          新的 Skill 显示名称
  --description   新的描述
  --download-url  新的下载地址
  --label         新的标签（逗号分隔）
  --version       版本号（semver 格式，如 1.2.0）

环境变量：
  XG_USER_TOKEN  — access-token（必须）
"""

import sys
import json
import argparse
import requests

from common import API_BASE, get_headers, get_token, parse_api_response

API_URL = f"{API_BASE}/api/skill/upgrade"


def call_api(token: str, payload: dict) -> dict:
    """更新 Skill 信息（ClawHub 格式）"""
    headers = get_headers(token)

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
        return parse_api_response(response, "更新 Skill")
    except Exception as e:
        print(f"错误: 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def build_upgrade_payload(args) -> dict:
    """构造升级 Skill 的请求体 (ClawHubUpgradeRequest)"""
    payload = {
        "name": args.code,
        "skillCode": args.code,
    }

    if args.change_log:
        payload["changeLog"] = args.change_log
    if args.download_url:
        payload["downloadUrl"] = args.download_url
    if args.version:
        payload["version"] = args.version

    # 保留元数据支持（后端 /upgrade 接口目前主要处理版本升级，元数据由 /update 处理）
    if args.name:
        payload["displayName"] = args.name
    if args.description:
        payload["description"] = args.description
    
    if args.label:
        tags = [t.strip() for t in args.label.split(",") if t.strip()] if args.label else []
        payload["metadata"] = {
            "openclaw": {
                "tags": tags,
            },
        }

    return payload


def main():
    parser = argparse.ArgumentParser(description="更新已有 Skill")
    parser.add_argument("--code", required=True, help="Skill 唯一标识")
    parser.add_argument("--name", default="", help="新的 Skill 显示名称")
    parser.add_argument("--description", default="", help="新的描述")
    parser.add_argument("--download-url", default="", help="新的下载地址")
    parser.add_argument("--label", default="", help="新的标签（逗号分隔）")
    parser.add_argument("--version", default="", help="版本号（semver 格式，如 1.2.0）")
    parser.add_argument("--change-log", default="", help="升级说明 (可选)")
    args = parser.parse_args()

    token = get_token()
    payload = build_upgrade_payload(args)
    result = call_api(token, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
