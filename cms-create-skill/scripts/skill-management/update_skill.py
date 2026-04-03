#!/usr/bin/env python3
"""
更新已有 Skill

用途：更新已注册 Skill 的信息（名称、描述、下载地址等）（ClawHub 协议格式）

使用方式：
  python3 cms-create-skill/scripts/skill-management/update_skill.py --code <code> [--name <name>] [--description <desc>] [--download-url <url>] [--label <label>] [--version <ver>] [--internal]

参数说明：
  --code          Skill 唯一标识（必须）
  --name          新的 Skill 显示名称
  --description   新的描述
  --download-url  新的下载地址
  --label         新的标签（逗号分隔）
  --version       版本号（semver 格式，如 1.2.0）
  --internal      标记为内部 Skill

环境变量：
  XG_USER_TOKEN  — access-token（必须）
"""

import sys
import os
import json
import argparse
import requests
import warnings

# 禁用 InsecureRequestWarning (因为 verify=False)
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

DEFAULT_API_BASE = 'https://skills.mediportal.com.cn'
API_BASE = DEFAULT_API_BASE
API_URL = f"{API_BASE.rstrip('/')}/im/skill/upgrade"


def parse_api_response(response: requests.Response, action: str) -> dict:
    data = response.json()
    if isinstance(data, dict) and data.get('resultCode') not in (None, 1):
        message = data.get('resultMsg') or data.get('detailMsg') or response.text
        raise RuntimeError(f'{action}失败: {message}')
    return data


def call_api(token: str, payload: dict) -> dict:
    """更新 Skill 信息（ClawHub 格式）"""
    headers = {
        "access-token": token,
        "Content-Type": "application/json",
    }

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
        return parse_api_response(response, '更新 Skill')
    except Exception as e:
        print(f"错误: 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def build_upgrade_payload(args) -> dict:
    """构造升级 Skill 的请求体 (AiSkillUpgradeRequest)"""
    payload = {
        "code": args.code,
    }

    if args.change_log:
        payload["changeLog"] = args.change_log
    if args.download_url:
        payload["downloadUrl"] = args.download_url
    if args.version:
        payload["version"] = args.version

    # 保留旧参数的支持 (如果后端兼容)
    if args.name:
        payload["displayName"] = args.name
    if args.description:
        payload["description"] = args.description
    
    if args.label or args.internal:
        tags = [t.strip() for t in args.label.split(",") if t.strip()] if args.label else []
        payload["metadata"] = {
            "openclaw": {
                "tags": tags,
            },
            "xgjk": {
                "isInternal": args.internal,
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
    parser.add_argument("--internal", action="store_true", help="标记为内部 Skill")
    args = parser.parse_args()

    token = os.environ.get("XG_USER_TOKEN") or os.environ.get("access-token") or os.environ.get("ACCESS_TOKEN")
    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)

    payload = build_upgrade_payload(args)
    result = call_api(token, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
