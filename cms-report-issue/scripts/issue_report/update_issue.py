#!/usr/bin/env python3
"""
更新 Skill 问题状态。

使用方式：
  python3 cms-report-issue/scripts/issue_report/update_issue.py \
    --issue-id "abc123" \
    --status resolved \
    --resolution "已修复连接超时问题，增加了重试机制"

  python3 cms-report-issue/scripts/issue_report/update_issue.py \
    --issue-id "abc123" \
    --status closed
"""

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

DEFAULT_API_BASE = 'https://skills.mediportal.com.cn'
API_BASE = DEFAULT_API_BASE


def _ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _get_auth_headers():
    headers = {'Content-Type': 'application/json'}
    token = (
        os.environ.get('XG_USER_TOKEN')
        or os.environ.get('access-token')
        or os.environ.get('ACCESS_TOKEN')
        or ''
    )
    if token:
        headers['access-token'] = token
    return headers


def update_issue(issue_id: str, status: str = '', resolution: str = '', api_base: str = '') -> dict:
    base_url = (api_base or API_BASE).rstrip('/')
    url = f'{base_url}/api/skill/issues/update'

    payload = {'issueId': issue_id}
    if status:
        payload['status'] = status
    if resolution:
        payload['resolution'] = resolution

    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    ctx = _ssl_context()
    req = urllib.request.Request(url, data=body, headers=_get_auth_headers(), method='POST')

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as error:
        error_body = error.read().decode('utf-8', errors='replace')
        raise RuntimeError(f'更新失败 (HTTP {error.code}): {error_body}')
    except urllib.error.URLError as error:
        raise RuntimeError(f'连接失败: {error.reason}')

    if data.get('resultCode') not in (None, 1):
        raise RuntimeError(f"更新失败: {data.get('resultMsg', '未知错误')}")

    return data.get('data', data)


def main():
    parser = argparse.ArgumentParser(description='更新 Skill 问题状态')
    parser.add_argument('--issue-id', '-i', required=True, help='问题 ID')
    parser.add_argument('--status', '-s', required=True, choices=['open', 'resolved', 'closed'], help='新状态')
    parser.add_argument('--resolution', '-r', default='', help='解决方案描述')
    parser.add_argument('--api-base', default='', help='后端地址')
    args = parser.parse_args()

    token = (
        os.environ.get('XG_USER_TOKEN')
        or os.environ.get('access-token')
        or os.environ.get('ACCESS_TOKEN')
        or ''
    )
    if not token:
        print('⚠️ 尚未通过 cms-auth-skills 准备 access-token，可能导致认证失败', file=sys.stderr)

    try:
        result = update_issue(
            issue_id=args.issue_id,
            status=args.status,
            resolution=args.resolution,
            api_base=args.api_base,
        )
        print(f'✅ 问题状态已更新为 {args.status}', file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False))
    except RuntimeError as error:
        print(f'❌ {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
