#!/usr/bin/env python3
"""
更新 Skill 问题状态

用途：将已上报的问题标记为已解决（resolved）或已关闭（closed）

使用方式：
  # 标记为已解决
  python3 cms-push-skill/scripts/issue_report/update_issue.py \
    --issue-id "abc123" \
    --status resolved \
    --resolution "已修复连接超时问题，增加了重试机制"

  # 标记为已关闭
  python3 cms-push-skill/scripts/issue_report/update_issue.py \
    --issue-id "abc123" \
    --status closed

环境变量：
  XG_USER_TOKEN   — access-token（必须）
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error
import ssl

API_BASE = "https://skills.mediportal.com.cn"


def _ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _get_auth_headers():
    """获取认证头"""
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("XG_USER_TOKEN", "")
    if token:
        headers["access-token"] = token
    return headers


def update_issue(
    issue_id: str,
    status: str = "",
    resolution: str = "",
    api_base: str = "",
) -> dict:
    """
    更新问题状态。

    通过后端 POST /api/skill/issues/update 接口更新。

    Args:
        issue_id:    问题 ID（必填）
        status:      新状态：open / resolved / closed（可选）
        resolution:  解决方案描述（可选）
        api_base:    后端地址（可选）

    Returns:
        dict: API 响应

    Raises:
        RuntimeError: 更新失败
    """
    base_url = (api_base or API_BASE).rstrip("/")
    url = f"{base_url}/api/skill/issues/update"

    payload = {"issueId": issue_id}
    if status:
        payload["status"] = status
    if resolution:
        payload["resolution"] = resolution

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ctx = _ssl_context()
    headers = _get_auth_headers()

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"更新失败 (HTTP {e.code}): {error_body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"连接失败: {e.reason}")

    if data.get("resultCode") != 1:
        raise RuntimeError(f"更新失败: {data.get('resultMsg', '未知错误')}")

    return data.get("data", data)


def main():
    parser = argparse.ArgumentParser(description="更新 Skill 问题状态")
    parser.add_argument("--issue-id", "-i", required=True, help="问题 ID")
    parser.add_argument("--status", "-s", required=True, choices=["open", "resolved", "closed"], help="新状态")
    parser.add_argument("--resolution", "-r", default="", help="解决方案描述")
    parser.add_argument("--api-base", default="", help="后端地址（默认 http://localhost:8787）")
    args = parser.parse_args()

    token = os.environ.get("XG_USER_TOKEN", "")
    if not token:
        print("⚠️ 未设置 XG_USER_TOKEN 环境变量，可能导致认证失败", file=sys.stderr)

    try:
        result = update_issue(
            issue_id=args.issue_id,
            status=args.status,
            resolution=args.resolution,
            api_base=args.api_base,
        )
        print(f"✅ 问题状态已更新为 {args.status}", file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False))
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
