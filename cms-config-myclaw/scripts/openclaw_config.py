#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

CHANNEL_ID = 'xg_cwork_im'
DEFAULT_BASE_URL = 'https://sg-al-cwork-api.mediportal.com.cn'
DEFAULT_WS_BASE_URL = 'wss://sg-al-cwork-api.mediportal.com.cn'


def stringify(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {'null', 'none', 'undefined'}:
        return None
    return text


def mask_secret(value: Any) -> str:
    text = stringify(value)
    if not text:
        return '***'
    if len(text) <= 6:
        return '***'
    return text[:6] + '***'


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strip_known_schemes(value: str) -> str:
    text = value.strip()
    while True:
        lowered = text.lower()
        matched = False
        for prefix in ('https://', 'http://', 'wss://', 'ws://'):
            if lowered.startswith(prefix):
                text = text[len(prefix):]
                matched = True
                break
        if not matched:
            break
    return text.lstrip('/').rstrip('/')


def _normalize_http_url(value: Any, fallback: str) -> str:
    text = stringify(value)
    if not text:
        return fallback
    core = _strip_known_schemes(text)
    scheme = 'http://' if text.startswith('http://') else 'https://'
    return f'{scheme}{core}'.rstrip('/')


def _normalize_ws_url(value: Any, fallback: str) -> str:
    text = stringify(value)
    if not text:
        return fallback
    core = _strip_known_schemes(text)
    scheme = 'ws://' if text.startswith('ws://') else 'wss://'
    return f'{scheme}{core}'.rstrip('/')


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        raise RuntimeError(f'配置文件不存在: {config_path}')
    with config_path.open('r', encoding='utf-8') as file_obj:
        payload = json.load(file_obj)
    if not isinstance(payload, dict):
        raise RuntimeError(f'配置文件格式异常: {config_path}')
    return payload


def save_config(config_path: Path, payload: dict[str, Any]) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open('w', encoding='utf-8') as file_obj:
        json.dump(payload, file_obj, ensure_ascii=False, indent=2)
        file_obj.write('\n')


def backup_config(config_path: Path) -> Path:
    timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    backup_path = config_path.with_name(f'{config_path.name}.bak.{timestamp}')
    shutil.copy2(config_path, backup_path)
    return backup_path


def restore_config(config_path: Path, backup_path: Path) -> None:
    shutil.copy2(backup_path, config_path)


def get_agents(config: dict[str, Any]) -> list[dict[str, Any]]:
    agents = _safe_list(_safe_dict(config.get('agents')).get('list'))
    result = []
    for agent in agents:
        if not isinstance(agent, dict):
            continue
        agent_id = stringify(agent.get('id'))
        if not agent_id:
            continue
        result.append(agent)
    if not result:
        raise RuntimeError('当前 openclaw.json 中未找到可用的 agents.list')
    return result


def summarize_agent(agent: dict[str, Any]) -> str:
    agent_id = stringify(agent.get('id')) or '<unknown>'
    name = stringify(agent.get('name')) or agent_id
    workspace = stringify(agent.get('workspace')) or '-'
    return f'{name} [{agent_id}] workspace={workspace}'


def summarize_existing_state(config: dict[str, Any], agent_id: str) -> dict[str, Any]:
    channels = _safe_dict(config.get('channels'))
    channel_config = _safe_dict(channels.get(CHANNEL_ID))
    accounts = _safe_dict(channel_config.get('accounts'))
    raw_account = accounts.get(agent_id)

    account_summary = None
    if isinstance(raw_account, dict):
        account_summary = {
            'appKey': mask_secret(raw_account.get('appKey')),
            'agentId': stringify(raw_account.get('agentId')),
            'name': stringify(raw_account.get('name')),
        }

    binding_summaries = []
    for binding in _safe_list(config.get('bindings')):
        if not isinstance(binding, dict):
            continue
        match = _safe_dict(binding.get('match'))
        channel = stringify(match.get('channel'))
        binding_agent_id = stringify(binding.get('agentId'))
        account_id = stringify(match.get('accountId'))
        if channel != CHANNEL_ID:
            continue
        if binding_agent_id == agent_id or account_id == agent_id:
            binding_summaries.append({
                'type': stringify(binding.get('type')) or 'default',
                'agentId': binding_agent_id,
                'accountId': account_id,
            })

    return {
        'has_existing': bool(account_summary or binding_summaries),
        'account': account_summary,
        'bindings': binding_summaries,
    }


def format_existing_state(summary: dict[str, Any]) -> str:
    lines = []
    account = summary.get('account')
    if account:
        lines.append('已有 account:')
        lines.append(
            f'  appKey={account.get("appKey")} agentId={account.get("agentId")} name={account.get("name") or "-"}'
        )
    bindings = summary.get('bindings') or []
    if bindings:
        lines.append('已有 bindings:')
        for binding in bindings:
            lines.append(
                f'  type={binding.get("type")} agentId={binding.get("agentId") or "-"} accountId={binding.get("accountId") or "-"}'
            )
    return '\n'.join(lines) if lines else '未检测到已有 xg_cwork_im 配置'


def _binding_conflicts(binding: Any, agent_id: str) -> bool:
    if not isinstance(binding, dict):
        return False
    match = _safe_dict(binding.get('match'))
    if stringify(match.get('channel')) != CHANNEL_ID:
        return False
    binding_agent_id = stringify(binding.get('agentId'))
    account_id = stringify(match.get('accountId'))
    return binding_agent_id == agent_id or account_id == agent_id


def merge_myclaw_config(
    config: dict[str, Any],
    *,
    agent_id: str,
    app_key: str,
    robot_name: str,
    base_url: str | None,
    ws_base_url: str | None,
) -> dict[str, Any]:
    next_config = copy.deepcopy(config)

    channels = _safe_dict(next_config.get('channels'))
    next_config['channels'] = channels

    channel_config = _safe_dict(channels.get(CHANNEL_ID))
    channels[CHANNEL_ID] = channel_config

    channel_config['baseUrl'] = _normalize_http_url(base_url, DEFAULT_BASE_URL)
    channel_config['wsBaseUrl'] = _normalize_ws_url(ws_base_url, DEFAULT_WS_BASE_URL)
    channel_config['debug'] = False

    accounts = _safe_dict(channel_config.get('accounts'))
    channel_config['accounts'] = accounts

    default_account = _safe_dict(accounts.get('default'))
    default_account['groupPolicy'] = 'mention'
    accounts['default'] = default_account

    target_account = _safe_dict(accounts.get(agent_id))
    target_account['appKey'] = app_key
    target_account['agentId'] = agent_id
    target_account['name'] = robot_name
    accounts[agent_id] = target_account

    bindings = _safe_list(next_config.get('bindings'))
    next_config['bindings'] = [binding for binding in bindings if not _binding_conflicts(binding, agent_id)]
    next_config['bindings'].append({
        'type': 'route',
        'agentId': agent_id,
        'match': {
            'channel': CHANNEL_ID,
            'accountId': agent_id,
        },
    })

    plugins = _safe_dict(next_config.get('plugins'))
    next_config['plugins'] = plugins

    allow = _safe_list(plugins.get('allow'))
    if CHANNEL_ID not in allow:
        allow.append(CHANNEL_ID)
    plugins['allow'] = allow

    entries = _safe_dict(plugins.get('entries'))
    plugins['entries'] = entries
    plugin_entry = _safe_dict(entries.get(CHANNEL_ID))
    plugin_entry['enabled'] = True
    entries[CHANNEL_ID] = plugin_entry

    return next_config
