#!/usr/bin/env python3
"""
Skill 问题反馈。

用途：将 Skill 运行错误、用户反馈的问题整理后上报到技能管理平台。

使用方式：
  python3 cms-report-issue/scripts/issue_report/report_issue.py \
    --skill-code "work-collaboration" \
    --version "1.0.0" \
    --error "requests.exceptions.ConnectionError: 连接超时" \
    --message "用户调用汇报提交接口时连接超时，重试 3 次均失败" \
    --issue-type "bug" \
    --severity "critical"

  python3 some_script.py 2>&1 | python3 cms-report-issue/scripts/issue_report/report_issue.py \
    --skill-code "xxx" --version "1.0.0" --stdin --issue-type "bug"
"""

import argparse
import functools
import json
import os
import ssl
import sys
import time
import traceback
import urllib.error
import urllib.request

DEFAULT_API_BASE = 'https://skills.mediportal.com.cn'
API_BASE = DEFAULT_API_BASE
REPORT_ENDPOINT = '/api/skill/issues/report'

ALLOWED_ISSUE_TYPES = ('bug', 'feature', 'enhancement', 'docs', 'security', 'question')
ALLOWED_SEVERITIES = ('critical', 'major', 'minor')


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


def _signature(skill_code: str, version: str, error_message: str, user_message: str) -> str:
    import hashlib
    raw = f"{skill_code}|{version}|{error_message.strip()}|{user_message.strip()}"
    return hashlib.sha1(raw.encode('utf-8')).hexdigest()


def find_duplicate_open_issue(skill_code: str, signature: str, api_base: str = '') -> dict | None:
    """查询同一 skillCode 下是否已存在等效的 open 问题。失败时静默返回 None。"""
    base_url = (api_base or API_BASE).rstrip('/')
    url = f'{base_url}/api/skill/issues/list'
    payload = {'skillCode': skill_code, 'status': 'open'}
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    try:
        req = urllib.request.Request(url, data=body, headers=_get_auth_headers(), method='POST')
        with urllib.request.urlopen(req, context=_ssl_context(), timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        if data.get('resultCode') not in (None, 1):
            return None
        for issue in data.get('data', []) or []:
            existing_sig = _signature(
                skill_code,
                issue.get('version', ''),
                issue.get('errorMessage', '') or '',
                issue.get('userMessage', '') or '',
            )
            if existing_sig == signature:
                return issue
    except Exception:
        return None
    return None


def report_issue(
    skill_code: str,
    version: str = '1.0.0',
    skill_name: str = '',
    skill_description: str = '',
    error_message: str = '',
    error_stack: str = '',
    user_message: str = '',
    context: dict = None,
    issue_type: str = 'bug',
    severity: str = 'critical',
    api_base: str = '',
    sync_robot: bool = False,
    dedupe: bool = True,
) -> dict:
    base_url = (api_base or API_BASE).rstrip('/')
    url = f'{base_url}{REPORT_ENDPOINT}'

    if dedupe:
        sig = _signature(skill_code, version, error_message, user_message)
        existing = find_duplicate_open_issue(skill_code, sig, api_base)
        if existing:
            return {
                'deduped': True,
                'message': '检测到相同 open 问题，跳过重复上报',
                'existing': existing,
            }

    payload = {
        'skillCode': skill_code,
        'version': version,
        'skillName': skill_name,
        'skillDescription': skill_description,
        'errorMessage': error_message,
        'errorStack': error_stack,
        'userMessage': user_message,
        'context': context or {},
        'issueType': issue_type,
        'severity': severity,
        'syncRobot': sync_robot,
    }

    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    ctx = _ssl_context()
    headers = _get_auth_headers()
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')

    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                if result.get('resultCode') in (None, 1):
                    return result.get('data', result)
                raise RuntimeError(f"上报失败: {result.get('resultMsg', '未知错误')}")
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as error:
            last_error = error
            if attempt < 2:
                time.sleep(1)

    raise RuntimeError(f'上报失败（重试 3 次）: {last_error}')


def auto_catch(
    skill_code: str,
    version: str = '1.0.0',
    skill_name: str = '',
    skill_description: str = '',
    issue_type: str = 'bug',
    severity: str = 'critical',
    sync_robot: bool = False,
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                stack = traceback.format_exc()
                try:
                    report_issue(
                        skill_code=skill_code,
                        version=version,
                        skill_name=skill_name,
                        skill_description=skill_description,
                        error_message=str(error),
                        error_stack=stack,
                        user_message=f'脚本 {func.__name__} 执行异常',
                        context={
                            'function': func.__name__,
                            'module': func.__module__,
                            'args_count': len(args),
                        },
                        issue_type=issue_type,
                        severity=severity,
                        sync_robot=sync_robot,
                    )
                    print(
                        f"⚠️ 问题已自动上报到技能管理平台 {'(已触发机器人)' if sync_robot else ''}",
                        file=sys.stderr,
                    )
                except Exception as report_error:
                    print(f'⚠️ 自动上报失败: {report_error}', file=sys.stderr)
                raise

        return wrapper

    return decorator


def main():
    parser = argparse.ArgumentParser(description='Skill 问题反馈')
    parser.add_argument('--skill-code', '-c', required=True, help='Skill 唯一标识')
    parser.add_argument('--version', '-v', default='1.0.0', help='Skill 版本号')
    parser.add_argument('--skill-name', '-n', default='', help='Skill 显示名称')
    parser.add_argument('--skill-desc', default='', help='Skill 描述')
    parser.add_argument('--error', '-e', default='', help='错误信息')
    parser.add_argument('--stack', default='', help='错误堆栈')
    parser.add_argument('--message', '-m', default='', help='用户描述的问题')
    parser.add_argument('--issue-type', '-t', default='bug', choices=list(ALLOWED_ISSUE_TYPES), help='问题类型')
    parser.add_argument('--severity', '-s', default='critical', choices=list(ALLOWED_SEVERITIES), help='严重级别')
    parser.add_argument('--stdin', action='store_true', help='从 stdin 读取错误信息')
    parser.add_argument('--api-base', default='', help='后端地址')
    parser.add_argument('--sync-robot', '--sync-github', '--internal', action='store_true', help='是否同步触发机器人任务')
    parser.add_argument('--no-dedupe', action='store_true', help='跳过重复检测，强制上报')
    args = parser.parse_args()

    error_msg = args.error
    if args.stdin:
        stdin_data = sys.stdin.read().strip()
        if stdin_data:
            error_msg = f'{error_msg}\n{stdin_data}' if error_msg else stdin_data

    if not error_msg and not args.message:
        print('错误: 请提供 --error 或 --message（至少一个）', file=sys.stderr)
        sys.exit(1)

    try:
        result = report_issue(
            skill_code=args.skill_code,
            version=args.version,
            skill_name=args.skill_name,
            skill_description=args.skill_desc,
            error_message=error_msg,
            error_stack=args.stack,
            user_message=args.message,
            issue_type=args.issue_type,
            severity=args.severity,
            api_base=args.api_base,
            sync_robot=args.sync_robot,
            dedupe=not args.no_dedupe,
        )
        if isinstance(result, dict) and result.get('deduped'):
            print('ℹ️ 已存在等效 open 问题，跳过重复上报', file=sys.stderr)
        else:
            print('✅ 问题已上报', file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False))
    except RuntimeError as error:
        print(f'❌ {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
