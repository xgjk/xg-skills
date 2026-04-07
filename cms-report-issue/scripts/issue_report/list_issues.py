#!/usr/bin/env python3
"""
查看已上报的 Skill 问题列表。

使用方式：
  python3 cms-report-issue/scripts/issue_report/list_issues.py
  python3 cms-report-issue/scripts/issue_report/list_issues.py --skill-code "work-collaboration"
  python3 cms-report-issue/scripts/issue_report/list_issues.py --severity error
  python3 cms-report-issue/scripts/issue_report/list_issues.py --status open
"""

import argparse
import json
import os
import ssl
import sys
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


def list_issues(skill_code: str = '', status: str = '', severity: str = '', api_base: str = '') -> list:
    base_url = (api_base or API_BASE).rstrip('/')
    url = f'{base_url}/api/skill/issues/list'

    payload = {}
    if skill_code:
        payload['skillCode'] = skill_code
    if status:
        payload['status'] = status
    if severity:
        payload['severity'] = severity

    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    ctx = _ssl_context()
    req = urllib.request.Request(url, data=body, headers=_get_auth_headers(), method='POST')

    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))

    if data.get('resultCode') not in (None, 1):
        raise RuntimeError(f"查询失败: {data.get('resultMsg', '未知错误')}")

    return data.get('data', [])


def get_issue_stats(api_base: str = '') -> dict:
    base_url = (api_base or API_BASE).rstrip('/')
    url = f'{base_url}/api/skill/issues/stats'

    body = json.dumps({}).encode('utf-8')
    ctx = _ssl_context()
    req = urllib.request.Request(url, data=body, headers=_get_auth_headers(), method='POST')

    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))

    if data.get('resultCode') not in (None, 1):
        raise RuntimeError(f"查询统计失败: {data.get('resultMsg', '未知错误')}")

    return data.get('data', {})


def format_issues(issues: list) -> str:
    if not issues:
        return '（暂无问题记录）'

    lines = []
    lines.append(f"{'#':<4} {'级别':<8} {'Skill':<22} {'状态':<10} {'上报时间':<22} {'问题摘要'}")
    lines.append('-' * 112)

    for index, issue in enumerate(issues, 1):
        severity = issue.get('severity', 'error')
        skill = (issue.get('skillName') or issue.get('skillCode') or '')[:20]
        status = issue.get('status', 'open')
        reported_at = (issue.get('reportedAt') or '')[:19]
        message = (issue.get('userMessage') or issue.get('errorMessage') or '')[:40]
        lines.append(f'{index:<4} {severity:<8} {skill:<22} {status:<10} {reported_at:<22} {message}')

    lines.append(f'\n共 {len(issues)} 条记录')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='查看已上报的 Skill 问题')
    parser.add_argument('--skill-code', '-c', default='', help='按 Skill code 筛选')
    parser.add_argument('--status', '-s', default='', choices=['', 'open', 'resolved', 'closed'], help='按状态筛选')
    parser.add_argument('--severity', default='', choices=['', 'error', 'warning', 'info'], help='按级别筛选')
    parser.add_argument('--stats', action='store_true', help='显示统计概览')
    parser.add_argument('--json', action='store_true', help='输出原始 JSON')
    parser.add_argument('--api-base', default='', help='后端地址')
    args = parser.parse_args()

    try:
        if args.stats:
            stats = get_issue_stats(api_base=args.api_base)
            if args.json:
                print(json.dumps(stats, ensure_ascii=False, indent=2))
            else:
                print('📊 问题统计概览\n')
                print(f"  总 Skill 数: {stats.get('totalSkills', 0)}")
                print(f"  总问题数:   {stats.get('totalIssues', 0)}")
                by_status = stats.get('byStatus', {})
                by_severity = stats.get('bySeverity', {})
                print(f"  按状态:     open={by_status.get('open', 0)}, resolved={by_status.get('resolved', 0)}, closed={by_status.get('closed', 0)}")
                print(f"  按级别:     error={by_severity.get('error', 0)}, warning={by_severity.get('warning', 0)}, info={by_severity.get('info', 0)}")
            return

        issues = list_issues(
            skill_code=args.skill_code,
            status=args.status,
            severity=args.severity,
            api_base=args.api_base,
        )
        if args.json:
            print(json.dumps(issues, ensure_ascii=False, indent=2))
        else:
            print('📋 Skill 问题列表\n')
            print(format_issues(issues))
    except Exception as error:
        print(f'❌ {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
