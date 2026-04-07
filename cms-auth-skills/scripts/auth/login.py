#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一鉴权解析模块（简化版）。

核心能力只保留三件事：
1. get_token_by_app_key: 通过 appKey 获取 access-token
2. get_app_key_by_sender: 通过 sender_id + account_id 获取 appKey（带缓存）
3. get_env_auth: 从环境变量获取 appKey / access-token

对外入口保持不变：
- resolve_app_key(...)
- ensure_token(...)
"""

from __future__ import print_function

import argparse
import os
import sys
import warnings
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import auth_support
import self_update

try:
    import requests
except ImportError:
    requests = None

TOKEN_AUTH_URL = 'https://sg-cwork-web.mediportal.com.cn/user/login/appkey'
APP_CODE = 'cms_gpt'

APPKEY_API_URL = 'https://sg-al-cwork-web.mediportal.com.cn/user/appkey/getAppKeyByDingUserId/nologin'
APPKEY_REQUEST_KEY = 'MTrBkZsNFFghxH5SmKxWWc93KJqe0'

DING_CORP_ID_RULES = (
    ('xgjk', 'ding0b8223c4cde4879dee0f45d8e4f7c288'),
    ('kangzhe', 'dingf57b758b536306eea1320dcb25e91351'),
    ('demei', 'ding452d1e907f3ae594f2c783f7214b6d69'),
    ('xgjkrtest', 'dingf019ee9a572ee7daa39a90f97fcb1e09'),
)


if requests is not None:
    try:
        warnings.filterwarnings(
            'ignore',
            category=requests.packages.urllib3.exceptions.InsecureRequestWarning,
        )
    except Exception:
        pass


def _request_json(url, method='GET', body=None, params=None):
    if requests is None:
        raise RuntimeError('请求失败: 缺少 requests 依赖，请先安装 requests')

    log_url = url
    if params:
        try:
            prepared = requests.Request(method=method, url=url, params=params).prepare()
            if prepared.url:
                log_url = prepared.url
        except Exception:
            pass

    try:
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=body,
            verify=False,
            allow_redirects=True,
            timeout=60,
        )
        response.raise_for_status()
    except Exception as exc:
        status = 'N/A'
        resp_text = str(exc)
        if hasattr(exc, 'response') and exc.response is not None:
            status = exc.response.status_code
            try:
                resp_text = exc.response.text
            except Exception:
                pass
        auth_support.write_log(
            'ERROR',
            'RequestError method=%s url=%s status=%s error=%s'
            % (method, auth_support.sanitize_url(log_url), status, resp_text[:2000]),
        )
        if status == 'N/A':
            raise RuntimeError('请求失败: %s' % exc)
        raise RuntimeError('请求失败 (HTTP %s): %s' % (status, resp_text))

    try:
        payload = response.json()
    except ValueError:
        auth_support.write_log(
            'ERROR',
            'JSONDecodeError method=%s url=%s'
            % (method, auth_support.sanitize_url(log_url)),
        )
        raise RuntimeError('请求失败：接口返回了无法解析的 JSON')

    if not isinstance(payload, dict):
        auth_support.write_log(
            'ERROR',
            'InvalidPayload method=%s url=%s raw=%s'
            % (method, auth_support.sanitize_url(log_url), response.text[:2000]),
        )
        raise RuntimeError('请求失败：接口返回格式异常')

    return payload


def _resolve_ding_corp_id(account_id):
    account_id = auth_support.stringify(account_id)
    if not account_id:
        raise RuntimeError('无法自动获取 appKey')

    account_prefix = account_id.lower().split('_', 1)[0].split('-', 1)[0]
    for keyword, ding_corp_id in DING_CORP_ID_RULES:
        if keyword == account_prefix:
            return ding_corp_id
    raise RuntimeError('无法自动获取 appKey')


def _extract_app_key(payload):
    data = payload.get('data')
    if isinstance(data, dict):
        return auth_support.pick_non_empty(data.get('appKey'), data.get('app_key'), data.get('appkey'))
    return auth_support.pick_non_empty(payload.get('appKey'), payload.get('app_key'), payload.get('appkey'))


def _extract_token(payload):
    data = payload.get('data')
    if not isinstance(data, dict):
        return None
    return auth_support.pick_non_empty(data.get('xgToken'), data.get('token'), data.get('access-token'))


# 能力 1：通过 appKey 获取 token
def get_token_by_app_key(app_key):
    app_key = auth_support.stringify(app_key)
    if not app_key:
        raise RuntimeError('登录失败：appKey 不能为空')

    payload = _request_json(
        TOKEN_AUTH_URL,
        method='GET',
        params={'appCode': APP_CODE, 'appKey': app_key},
    )

    token = _extract_token(payload)
    if token:
        return token

    message = auth_support.pick_non_empty(
        payload.get('resultMsg'),
        payload.get('detailMsg'),
        payload.get('message'),
    ) or '未知错误'
    raise RuntimeError('登录失败: %s' % message)


# 能力 2：通过 sender_id + account_id 获取 appKey（带缓存）
def get_app_key_by_sender(sender_id, account_id, force_update=False):
    sender_id = auth_support.stringify(sender_id)
    account_id = auth_support.stringify(account_id)
    if not sender_id or not account_id:
        raise RuntimeError('无法自动获取 appKey')

    if not force_update:
        cached_app_key = auth_support.get_cached_value(sender_id, 'appKey')
        if cached_app_key:
            return cached_app_key

    payload = _request_json(
        APPKEY_API_URL,
        method='POST',
        body={
            'requestKey': APPKEY_REQUEST_KEY,
            'dingCorpId': _resolve_ding_corp_id(account_id),
            'dingUserId': sender_id,
        },
    )

    app_key = _extract_app_key(payload)
    if app_key:
        auth_support.update_cache(sender_id, 'appKey', app_key)
        return app_key

    message = auth_support.pick_non_empty(
        payload.get('resultMsg'),
        payload.get('detailMsg'),
        payload.get('message'),
    ) or '未知错误'
    raise RuntimeError('获取 appKey 失败: %s' % message)


# 能力 3：从环境变量获取 appKey / token
def get_env_auth():
    return (
        auth_support.stringify(os.environ.get('XG_BIZ_API_KEY')),
        auth_support.stringify(os.environ.get('XG_USER_TOKEN')),
    )


def _cache_auth_values(sender_id, app_key=None, token=None):
    auth_support.update_cache(sender_id, 'appKey', app_key)
    auth_support.update_cache(sender_id, 'token', token)


def resolve_app_key(
    context=None,
    quiet=False,
    force_update=False,
    app_key=None,
    access_token=None,
    sender_id=None,
    account_id=None,
):
    _ = quiet
    inputs = auth_support.build_inputs(
        context=context,
        app_key=app_key,
        access_token=access_token,
        sender_id=sender_id,
        account_id=account_id,
    )

    if inputs.app_key:
        auth_support.update_cache(inputs.sender_id, 'appKey', inputs.app_key)
        return inputs.app_key

    env_app_key, _ = get_env_auth()
    if env_app_key:
        auth_support.update_cache(inputs.sender_id, 'appKey', env_app_key)
        return env_app_key

    if inputs.sender_id:
        if not force_update:
            cached_app_key = auth_support.get_cached_value(inputs.sender_id, 'appKey')
            if cached_app_key:
                return cached_app_key

        if inputs.account_id:
            return get_app_key_by_sender(inputs.sender_id, inputs.account_id, force_update=force_update)

    raise RuntimeError('未能自动获取 appKey，请向用户索要 appKey（工作协同 key / cowork key）。')


def ensure_token(
    context=None,
    quiet=False,
    force_update=False,
    app_key=None,
    access_token=None,
    sender_id=None,
    account_id=None,
):
    _ = quiet
    inputs = auth_support.build_inputs(
        context=context,
        app_key=app_key,
        access_token=access_token,
        sender_id=sender_id,
        account_id=account_id,
    )

    # 步骤 A：明确已有 token 就直接返回
    if inputs.access_token:
        auth_support.update_cache(inputs.sender_id, 'token', inputs.access_token)
        return inputs.access_token

    # 步骤 B：明确已有 appKey，按需换 token
    if inputs.app_key:
        token = get_token_by_app_key(inputs.app_key)
        _cache_auth_values(inputs.sender_id, app_key=inputs.app_key, token=token)
        return token

    # 步骤 C：环境变量
    env_app_key, env_token = get_env_auth()
    if env_token:
        auth_support.update_cache(inputs.sender_id, 'token', env_token)
        return env_token
    if env_app_key:
        token = get_token_by_app_key(env_app_key)
        _cache_auth_values(inputs.sender_id, app_key=env_app_key, token=token)
        return token

    # 步骤 D：sender_id 相关缓存 + sender_id/account_id 自动获取 appKey，再换 token
    if inputs.sender_id:
        if not force_update:
            cached_token = auth_support.get_cached_value(inputs.sender_id, 'token')
            if cached_token:
                return cached_token

            cached_app_key = auth_support.get_cached_value(inputs.sender_id, 'appKey')
            if cached_app_key:
                token = get_token_by_app_key(cached_app_key)
                _cache_auth_values(inputs.sender_id, app_key=cached_app_key, token=token)
                return token

        if inputs.account_id:
            resolved_app_key = get_app_key_by_sender(inputs.sender_id, inputs.account_id, force_update=force_update)
            token = get_token_by_app_key(resolved_app_key)
            _cache_auth_values(inputs.sender_id, app_key=resolved_app_key, token=token)
            return token

    raise RuntimeError('未能自动获取 access-token，请先向用户索要 appKey（工作协同 key / cowork key）。')


def main():
    update_state = self_update.check_for_update()
    if update_state.get('needUpdate'):
        print(update_state.get('message') or '检测到新版本，请先更新 cms-auth-skills。', file=sys.stderr, flush=True)
        sys.exit(self_update.UPDATE_REQUIRED_EXIT_CODE)

    parser = argparse.ArgumentParser(description='统一鉴权解析：appKey / access-token')
    parser.add_argument('--app-key', '-k', type=str, help='显式传入 appKey（工作协同 key / cowork key）')
    parser.add_argument('--access-token', type=str, help='显式传入 access-token')
    parser.add_argument('--sender-id', type=str, help='显式传入 sender_id')
    parser.add_argument('--account-id', type=str, help='显式传入 account_id')
    parser.add_argument('--context-json', type=str, default='', help='兼容旧调用的上下文 JSON，推荐改用显式参数')

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--resolve-app-key', action='store_true', help='输出一个可用的 appKey')
    mode_group.add_argument('--ensure', action='store_true', help='输出一个可用的 access-token')
    parser.add_argument('--update', action='store_true', help='强制刷新缓存（跳过缓存读取，重新获取）')
    args = parser.parse_args()

    auth_support.cleanup_old_logs()

    inputs = auth_support.build_inputs(
        context=args.context_json,
        app_key=args.app_key,
        access_token=args.access_token,
        sender_id=args.sender_id,
        account_id=args.account_id,
    )

    try:
        if args.resolve_app_key:
            print(
                resolve_app_key(
                    force_update=args.update,
                    app_key=inputs.app_key,
                    access_token=inputs.access_token,
                    sender_id=inputs.sender_id,
                    account_id=inputs.account_id,
                ),
                flush=True,
            )
            return

        print(
            ensure_token(
                force_update=args.update,
                app_key=inputs.app_key,
                access_token=inputs.access_token,
                sender_id=inputs.sender_id,
                account_id=inputs.account_id,
            ),
            flush=True,
        )
    except (RuntimeError, ValueError) as exc:
        auth_support.write_log('ERROR', '脚本执行失败: %s' % exc)
        print('错误: %s' % exc, file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
