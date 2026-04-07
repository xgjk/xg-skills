#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import os
import sys
import warnings
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import auth_support

try:
    import requests
except ImportError:
    requests = None

CHECK_VERSION_URL = 'https://skills.mediportal.com.cn/api/skill/checkVersion'
CHECK_INTERVAL_SECONDS = 2 * 60 * 60
UPDATE_REQUIRED_EXIT_CODE = 20
TZ_UTC = timezone.utc
CHECK_STATE_FILE = 'version-check.json'


if requests is not None:
    try:
        warnings.filterwarnings(
            'ignore',
            category=requests.packages.urllib3.exceptions.InsecureRequestWarning,
        )
    except Exception:
        pass


def _skill_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def _version_file():
    return os.path.join(_skill_root(), 'version.json')


def _load_version_payload():
    with open(_version_file(), 'r', encoding='utf-8') as file_obj:
        payload = json.load(file_obj)

    if not isinstance(payload, dict):
        raise RuntimeError('version.json 必须是 JSON 对象')

    skillcode = auth_support.stringify(payload.get('skillcode'))
    version = auth_support.stringify(payload.get('version'))
    if not skillcode or not version:
        raise RuntimeError('version.json 缺少 skillcode/version')

    payload['skillcode'] = skillcode
    payload['version'] = version
    return payload


def _check_state_file():
    return auth_support.runtime_state_file(CHECK_STATE_FILE)


def _load_check_state(legacy_payload):
    state_path = _check_state_file()
    try:
        if os.path.exists(state_path):
            with open(state_path, 'r', encoding='utf-8') as file_obj:
                payload = json.load(file_obj)
            if isinstance(payload, dict):
                return payload
    except Exception as exc:
        auth_support.write_log('WARN', '读取版本检查状态失败: %s' % exc)

    fallback = {}
    if isinstance(legacy_payload, dict):
        if 'lastCheckAt' in legacy_payload:
            fallback['lastCheckAt'] = legacy_payload.get('lastCheckAt')
        if 'lastNeedUpdate' in legacy_payload:
            fallback['lastNeedUpdate'] = legacy_payload.get('lastNeedUpdate')
    return fallback


def _parse_last_check_at(value):
    value = auth_support.stringify(value)
    if not value:
        return None

    for fmt in (
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
    ):
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.replace(tzinfo=TZ_UTC)
        except ValueError:
            continue

    try:
        return datetime.fromtimestamp(float(value), TZ_UTC)
    except Exception:
        return None


def _format_last_check_at(now_utc):
    return now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')


def _parse_saved_need_update(value):
    if value is True:
        return True
    if value is False:
        return False

    normalized = auth_support.stringify(value)
    if normalized == 'true':
        return True
    if normalized == 'false':
        return False
    return False


def _update_message():
    return '检测到 cms-auth-skills 有新版本，请通过 ClawHub 更新当前 Skill 后重新执行。'


def _log(level, message):
    auth_support.write_log(level, '[self-update] %s' % message)


def _should_check(last_check_at, now_utc):
    if last_check_at is None:
        return True
    elapsed = now_utc - last_check_at
    return elapsed.total_seconds() >= CHECK_INTERVAL_SECONDS


def _write_check_state(skillcode, version, now_utc, need_update):
    state_path = _check_state_file()
    next_payload = {
        'skillcode': skillcode,
        'version': version,
        'lastCheckAt': _format_last_check_at(now_utc),
        'lastNeedUpdate': bool(need_update),
    }
    temp_path = str(state_path) + '.tmp'
    try:
        state_dir = os.path.dirname(str(state_path))
        if state_dir:
            os.makedirs(state_dir, exist_ok=True)
        with open(temp_path, 'w', encoding='utf-8') as file_obj:
            json.dump(next_payload, file_obj, ensure_ascii=False, indent=2)
            file_obj.write('\n')
        os.replace(temp_path, state_path)
    except Exception as exc:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass
        auth_support.write_log('WARN', '写入版本检查状态失败: %s' % exc)


def _request_check_version(skillcode, version):
    if requests is None:
        raise RuntimeError('版本检查失败: 缺少 requests 依赖')

    try:
        response = requests.post(
            CHECK_VERSION_URL,
            json={
                'skillcode': skillcode,
                'version': version,
            },
            headers={'Content-Type': 'application/json'},
            verify=False,
            allow_redirects=True,
            timeout=60,
        )
        response.raise_for_status()
    except Exception as exc:
        raise RuntimeError('版本检查请求失败: %s' % exc)

    try:
        payload = response.json()
    except ValueError:
        raise RuntimeError('版本检查失败: 接口返回了无法解析的 JSON')

    if not isinstance(payload, dict):
        raise RuntimeError('版本检查失败: 接口返回格式异常')

    if payload.get('needUpdate') is True:
        return True
    if payload.get('needUpdate') is False:
        return False

    normalized = auth_support.stringify(payload.get('needUpdate'))
    if normalized == 'true':
        return True
    if normalized == 'false':
        return False

    raise RuntimeError('版本检查失败: 接口返回缺少 needUpdate')


def check_for_update():
    payload = None
    cached_need_update = False
    try:
        payload = _load_version_payload()
        check_state = _load_check_state(payload)
        now_utc = datetime.now(TZ_UTC)
        last_check_at = _parse_last_check_at(check_state.get('lastCheckAt'))
        cached_need_update = _parse_saved_need_update(check_state.get('lastNeedUpdate'))
        _log('INFO', '开始检查版本 skillcode=%s version=%s' % (payload['skillcode'], payload['version']))
        if not _should_check(last_check_at, now_utc):
            _log(
                'INFO',
                '跳过远端检查 skillcode=%s cachedNeedUpdate=%s lastCheckAt=%s'
                % (payload['skillcode'], bool(cached_need_update), check_state.get('lastCheckAt') or ''),
            )
            return {
                'checked': False,
                'needUpdate': cached_need_update,
                'message': _update_message() if cached_need_update else '',
            }

        need_update = _request_check_version(payload['skillcode'], payload['version'])
        _write_check_state(payload['skillcode'], payload['version'], now_utc, need_update)
        if need_update:
            _log('WARN', '检测到新版本 skillcode=%s version=%s' % (payload['skillcode'], payload['version']))
            return {
                'checked': True,
                'needUpdate': True,
                'message': _update_message(),
            }
        _log('INFO', '版本检查完成，无需更新 skillcode=%s version=%s' % (payload['skillcode'], payload['version']))
        return {
            'checked': True,
            'needUpdate': False,
            'message': '',
        }
    except Exception as exc:
        if payload is not None:
            _write_check_state(payload['skillcode'], payload['version'], datetime.now(TZ_UTC), cached_need_update)
        auth_support.write_log('WARN', '版本检查已跳过: %s' % exc)
        return {
            'checked': False,
            'needUpdate': cached_need_update,
            'message': _update_message() if cached_need_update else '',
        }
