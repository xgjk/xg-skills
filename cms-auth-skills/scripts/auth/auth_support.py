#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import os
import re
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOG_RETENTION_DAYS = 30
TZ_CN = timezone(timedelta(hours=8))
SKILL_CODE = 'cms-auth-skills'
RUNTIME_ROOT_NAME = '.cms-log'
LOG_DIR_NAME = 'log'
STATE_DIR_NAME = 'state'
LEGACY_RUNTIME_ROOT_NAMES = ('.cms-auth', 'cms-auth')
MIGRATION_SKIP_NAMES = ('skills',)


class AuthInputs(object):
    def __init__(self, app_key=None, access_token=None, sender_id=None, account_id=None):
        self.app_key = app_key
        self.access_token = access_token
        self.sender_id = sender_id
        self.account_id = account_id

def _load_json_object(path):
    if not path.exists() or not path.is_file():
        return None
    with open(str(path), 'r', encoding='utf-8') as file_obj:
        payload = json.load(file_obj)
    return payload if isinstance(payload, dict) else None


def _write_json_object(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(path), 'w', encoding='utf-8') as file_obj:
        json.dump(payload, file_obj, ensure_ascii=False, indent=2)
        file_obj.write('\n')


def _move_missing_items(source_dir, target_dir):
    if not source_dir.exists() or not source_dir.is_dir() or source_dir == target_dir:
        return
    target_dir.mkdir(parents=True, exist_ok=True)
    for child in source_dir.iterdir():
        if child.name in MIGRATION_SKIP_NAMES:
            continue
        target_child = target_dir / child.name
        if target_child.exists():
            if child.is_dir():
                _move_missing_items(child, target_child)
            continue
        child.rename(target_child)
    try:
        source_dir.rmdir()
    except OSError:
        pass


def _merge_auth_cache_file(source_path, target_path):
    if not source_path.exists() or not source_path.is_file():
        return

    try:
        source_payload = _load_json_object(source_path) or {}
    except (ValueError, OSError):
        source_payload = {}

    if not target_path.exists():
        target_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.rename(target_path)
        return

    try:
        target_payload = _load_json_object(target_path) or {}
    except (ValueError, OSError):
        target_payload = {}

    for sender_id, source_value in source_payload.items():
        if sender_id not in target_payload:
            target_payload[sender_id] = source_value
            continue
        if isinstance(source_value, dict) and isinstance(target_payload.get(sender_id), dict):
            for key, value in source_value.items():
                target_payload[sender_id].setdefault(key, value)

    _write_json_object(target_path, target_payload)
    try:
        source_path.unlink()
    except OSError:
        pass


def _runtime_log_dir(runtime_root, skillcode=SKILL_CODE):
    return runtime_root / LOG_DIR_NAME / skillcode


def _runtime_state_dir(runtime_root, skillcode=SKILL_CODE):
    return runtime_root / STATE_DIR_NAME / skillcode


def _runtime_state_file(runtime_root, filename, skillcode=SKILL_CODE):
    return _runtime_state_dir(runtime_root, skillcode) / filename


def _legacy_runtime_root_candidates(workspace_root, skills_dir=None):
    candidates = []
    for legacy_name in LEGACY_RUNTIME_ROOT_NAMES:
        candidates.append(workspace_root / legacy_name)

    if skills_dir:
        for legacy_name in (RUNTIME_ROOT_NAME,) + LEGACY_RUNTIME_ROOT_NAMES:
            candidates.append(skills_dir / legacy_name)
        if skills_dir.parent.name in (RUNTIME_ROOT_NAME,) + LEGACY_RUNTIME_ROOT_NAMES:
            candidates.append(skills_dir.parent)
    return candidates


def _migrate_legacy_runtime_root(legacy_root, runtime_root):
    if not legacy_root.exists() or legacy_root == runtime_root:
        return

    _merge_auth_cache_file(legacy_root / 'auth.json', _runtime_state_file(runtime_root, 'auth.json'))
    _move_missing_items(legacy_root / 'logs', _runtime_log_dir(runtime_root))
    _move_missing_items(legacy_root / LOG_DIR_NAME / SKILL_CODE, _runtime_log_dir(runtime_root))
    _move_missing_items(legacy_root / STATE_DIR_NAME / SKILL_CODE, _runtime_state_dir(runtime_root))


def _find_runtime_root():
    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent.parent
    skills_ancestors = [current for current in (skill_dir,) + tuple(skill_dir.parents) if current.name == 'skills']
    skills_dir = skills_ancestors[0] if skills_ancestors else None
    workspace_root = skills_dir.parent if skills_dir else skill_dir.parent

    runtime_root = workspace_root / RUNTIME_ROOT_NAME
    runtime_root.mkdir(parents=True, exist_ok=True)

    for legacy_root in _legacy_runtime_root_candidates(workspace_root, skills_dir=skills_dir):
        _migrate_legacy_runtime_root(legacy_root, runtime_root)

    return runtime_root


def _ensure_logs_dir():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_state_dir():
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def runtime_state_file(filename, skillcode=SKILL_CODE):
    return _runtime_state_file(RUNTIME_ROOT, filename, skillcode=skillcode)


RUNTIME_ROOT = _find_runtime_root()
STATE_DIR = _runtime_state_dir(RUNTIME_ROOT)
AUTH_JSON = runtime_state_file('auth.json')
LOGS_DIR = _runtime_log_dir(RUNTIME_ROOT)


def stringify(value):
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
    else:
        try:
            text = str(value).strip()
        except Exception:
            return None
    if text.lower() in ('', 'null', 'none', 'undefined'):
        return None
    return text


def pick_non_empty(*values):
    for value in values:
        normalized = stringify(value)
        if normalized:
            return normalized
    return None


def mask_sensitive(value):
    value = stringify(value)
    if not value or len(value) <= 6:
        return '***'
    return value[:6] + '***'


def _normalize_log_key(key):
    if not key:
        return ''
    return str(key).strip().lower().replace('_', '-')


def _is_sensitive_log_key(key):
    return _normalize_log_key(key) in (
        'appkey',
        'app-key',
        'access-token',
        'token',
        'authorization',
        'requestkey',
        'request-key',
    )


def sanitize_url(url):
    parsed = urllib.parse.urlsplit(url)
    if not parsed.query:
        return url

    query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    sanitized_pairs = []
    for key, value in query_pairs:
        if _is_sensitive_log_key(key):
            sanitized_pairs.append((key, mask_sensitive(value)))
        else:
            sanitized_pairs.append((key, value))

    return urllib.parse.urlunsplit((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        urllib.parse.urlencode(sanitized_pairs, doseq=True),
        parsed.fragment,
    ))


_URL_PATTERN = re.compile(r'https?://[^\s]+')
_SENSITIVE_ASSIGN_PATTERN = re.compile(
    r'(?i)(["\']?(?:appkey|app-key|access-token|authorization|requestkey|request-key|token)["\']?\s*[:=]\s*)(["\']?)([^"\'\s,}&]+)(\2)'
)
_SENSITIVE_WORD_PATTERN = re.compile(
    r'(?i)(\b(?:appkey|app-key|access-token|authorization|requestkey|request-key|token)\b\s+)([^\s,}&]+)'
)


def sanitize_log_message(message):
    text = str(message)
    text = _URL_PATTERN.sub(lambda match: sanitize_url(match.group(0)), text)
    text = _SENSITIVE_ASSIGN_PATTERN.sub(
        lambda match: '%s%s%s%s' % (
            match.group(1),
            match.group(2),
            mask_sensitive(match.group(3)),
            match.group(4),
        ),
        text,
    )
    text = _SENSITIVE_WORD_PATTERN.sub(
        lambda match: '%s%s' % (match.group(1), mask_sensitive(match.group(2))),
        text,
    )
    return text


def log_file_path():
    return LOGS_DIR / ('%s.log' % datetime.now(TZ_CN).strftime('%Y-%m-%d'))


def _iter_log_lines(message):
    lines = str(message).splitlines()
    return lines or ['']


def write_log(level, message):
    try:
        _ensure_logs_dir()
        now = datetime.now(TZ_CN).strftime('%Y-%m-%d %H:%M:%S')
        safe_message = sanitize_log_message(message)
        with open(str(log_file_path()), 'a', encoding='utf-8') as file_obj:
            for line in _iter_log_lines(safe_message):
                file_obj.write('[%s] 【skillcode】: %s [%s] %s\n' % (now, SKILL_CODE, level, line))
    except Exception:
        pass


def cleanup_old_logs():
    try:
        if not LOGS_DIR.exists():
            return
        cutoff = datetime.now(TZ_CN) - timedelta(days=LOG_RETENTION_DAYS)
        cutoff_str = cutoff.strftime('%Y-%m-%d')
        for log_file in LOGS_DIR.glob('*.log'):
            if len(log_file.stem) == 10 and log_file.stem < cutoff_str:
                try:
                    os.remove(str(log_file))
                except OSError:
                    pass
    except Exception:
        pass


def load_auth_cache():
    try:
        if AUTH_JSON.exists():
            with open(str(AUTH_JSON), 'r', encoding='utf-8') as file_obj:
                data = json.load(file_obj)
            if isinstance(data, dict):
                return data
    except (ValueError, OSError):
        write_log('WARN', '读取缓存文件失败: %s' % AUTH_JSON)
    return {}


def save_auth_cache(cache):
    try:
        _ensure_state_dir()
        _write_json_object(AUTH_JSON, cache)
    except OSError as exc:
        write_log('ERROR', '写入缓存文件失败: %s' % exc)


def get_cached_value(sender_id, key):
    sender_id = stringify(sender_id)
    if not sender_id:
        return None
    cache = load_auth_cache()
    user_data = cache.get(sender_id, {})
    if not isinstance(user_data, dict):
        return None
    value = user_data.get(key)
    return stringify(value)


def update_cache(sender_id, key, value):
    sender_id = stringify(sender_id)
    value = stringify(value)
    if not sender_id or not value:
        return
    cache = load_auth_cache()
    user_data = cache.get(sender_id)
    if not isinstance(user_data, dict):
        user_data = {}
        cache[sender_id] = user_data
    user_data[key] = value
    user_data['updated_at'] = datetime.now(TZ_CN).isoformat()
    save_auth_cache(cache)


def parse_context(context):
    if isinstance(context, dict):
        return context
    if not isinstance(context, str):
        return {}
    text = context.strip()
    if not text:
        return {}
    try:
        payload = json.loads(text)
    except ValueError:
        return {}
    return payload if isinstance(payload, dict) else {}


def build_inputs(context=None, app_key=None, access_token=None, sender_id=None, account_id=None):
    payload = parse_context(context)
    return AuthInputs(
        app_key=pick_non_empty(app_key, payload.get('appKey'), payload.get('app_key'), payload.get('appkey')),
        access_token=pick_non_empty(
            access_token,
            payload.get('access-token'),
            payload.get('access_token'),
            payload.get('token'),
        ),
        sender_id=pick_non_empty(
            sender_id,
            payload.get('sender_id'),
            payload.get('senderId'),
            payload.get('send_id'),
            payload.get('sendId'),
        ),
        account_id=pick_non_empty(account_id, payload.get('account_id'), payload.get('accountId')),
    )
