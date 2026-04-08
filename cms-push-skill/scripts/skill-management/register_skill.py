#!/usr/bin/env python3
"""
发布（注册）新 Skill

用途：向平台注册一个新的 AI Skill（ClawHub 协议格式）

使用方式：
  python3 cms-push-skill/scripts/skill-management/register_skill.py --code <code> --name <name> [--description <desc>] [--download-url <url>] [--label <label>]

参数说明：
  --code          Skill 唯一标识（必须）
  --name          Skill 显示名称（必须）
  --description   Skill 描述
  --download-url  Skill 包下载地址
  --label         Skill 标签（逗号分隔）
  --version       版本号（semver 格式，如 1.0.0，默认 0.0.1）

环境变量：
  XG_USER_TOKEN  — access-token（必须）
"""

import sys
import json
import argparse
import requests

from common import API_BASE, get_headers, get_token, parse_api_response

API_URL = f"{API_BASE}/api/skill/register"


def call_api(token: str, payload: dict) -> dict:
    """注册新 Skill（ClawHub 格式）"""
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
        return parse_api_response(response, "注册 Skill")
    except Exception as e:
        print(f"错误: 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def build_clawhub_payload(args) -> dict:
    """将 CLI 参数转换为 ClawHub 协议格式。"""
    tags = [t.strip() for t in args.label.split(",") if t.strip()] if args.label else []

    payload = {
        "name": args.code,
        "skillCode": args.code,
        "displayName": args.name,
        "version": args.version,
        "description": args.description,
        "downloadUrl": args.download_url,
        "metadata": {
            "openclaw": {
                "tags": tags,
            },
        },
    }
    return payload


def main():
    parser = argparse.ArgumentParser(description="发布（注册）新 Skill")
    parser.add_argument("--code", required=True, help="Skill 唯一标识")
    parser.add_argument("--name", required=True, help="Skill 显示名称")
    parser.add_argument("--description", default="", help="Skill 描述")
    parser.add_argument("--download-url", default="", help="Skill 包下载地址")
    parser.add_argument("--label", default="", help="Skill 标签（逗号分隔）")
    parser.add_argument("--version", default="0.0.1", help="版本号（semver，默认 0.0.1）")
    args = parser.parse_args()

    token = get_token()
    payload = build_clawhub_payload(args)
    result = call_api(token, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
