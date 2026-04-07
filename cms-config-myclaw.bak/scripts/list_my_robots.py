#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from getpass import getpass
from pathlib import Path
from typing import Any

from http_support import RequestFailure, ensure_result_success, extract_result_message, mask_secret, request_json, stringify

DEFAULT_ROBOT_API_BASE_URL = 'https://cwork-api-test.xgjktech.com.cn'
ROBOT_LIST_PATH = '/im/robot/getMyRobot'


def resolve_cms_auth_login_script() -> Path:
    current = Path(__file__).resolve()
    candidates: list[Path] = []
    for parent in (current.parent, *current.parents):
        candidates.append(parent / 'cms-auth-skills' / 'scripts' / 'auth' / 'login.py')
        candidates.append(parent / 'skills' / 'cms-auth-skills' / 'scripts' / 'auth' / 'login.py')

    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if candidate.is_file():
            return candidate

    raise RuntimeError('找不到 cms-auth-skills/scripts/auth/login.py，请先安装 cms-auth-skills')


def get_access_token(app_key: str) -> str:
    normalized = stringify(app_key)
    if not normalized:
        raise RequestFailure('登录失败：appKey 不能为空')

    result = subprocess.run(
        [sys.executable, str(resolve_cms_auth_login_script()), '--ensure', '--app-key', normalized],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        message = (result.stderr or '').strip() or (result.stdout or '').strip() or 'cms-auth-skills 登录失败'
        raise RequestFailure(message)

    lines = [line.strip() for line in (result.stdout or '').splitlines() if line.strip()]
    if not lines:
        raise RequestFailure('登录失败: cms-auth-skills 未返回 access-token')
    return lines[-1]


def print_title(title: str) -> None:
    print(f'\n=== {title} ===', flush=True)


def print_intro() -> None:
    print_title('说明')
    print('这个脚本会帮你查看当前账号下已经有哪些私人机器人。')
    print('适合在重新绑定或重新配置前先查一遍，避免重复创建。')
    print('如果当前上下文里已经有可用 appKey，建议直接复用，不需要重复输入。')


def prompt_app_key() -> str:
    while True:
        if sys.stdin.isatty() and sys.stderr.isatty():
            value = getpass('请输入工作协同 key(appKey): ')
        else:
            value = input('请输入工作协同 key(appKey): ')
        text = value.strip()
        if text:
            return text
        print('输入不能为空，请重新输入。')


def resolve_prefilled_app_key(args: argparse.Namespace) -> tuple[str | None, str | None]:
    cli_value = stringify(getattr(args, 'app_key', None))
    if cli_value:
        return cli_value, 'cli'
    env_value = stringify(os.environ.get('CMS_CONFIG_MYCLAW_APP_KEY'))
    if env_value:
        return env_value, 'env'
    return None, None


def resolve_api_base_url(args: argparse.Namespace) -> str:
    cli_value = stringify(getattr(args, 'api_base_url', None))
    env_value = stringify(os.environ.get('CMS_CONFIG_MYCLAW_ROBOT_API_BASE_URL'))
    raw = cli_value or env_value or DEFAULT_ROBOT_API_BASE_URL
    if raw.startswith(('http://', 'https://')):
        return raw.rstrip('/')
    return f'https://{raw.lstrip("/")}'.rstrip('/')


def fetch_my_robots(token: str, api_base_url: str) -> list[dict[str, Any]]:
    url = f'{api_base_url}{ROBOT_LIST_PATH}'
    payload = request_json(
        url,
        method='GET',
        headers={'access-token': token},
    )
    ensure_result_success(payload, '获取我的机器人失败')
    data = payload.get('data')
    if data is None:
        return []
    if not isinstance(data, list):
        raise RequestFailure(f'获取我的机器人失败: {extract_result_message(payload, "接口 data 不是列表")}')
    return [item for item in data if isinstance(item, dict)]


def format_time_millis(value: Any) -> str:
    if value in (None, ''):
        return '-'
    try:
        millis = int(value)
    except (TypeError, ValueError):
        return str(value)
    if millis <= 0:
        return '-'
    return datetime.fromtimestamp(millis / 1000).strftime('%Y-%m-%d %H:%M:%S')


def sanitize_robot(robot: dict[str, Any], *, show_app_key: bool) -> dict[str, Any]:
    payload = dict(robot)
    if not show_app_key:
        payload['appKey'] = mask_secret(payload.get('appKey'))
    return payload


def print_robots(robots: list[dict[str, Any]], *, show_app_key: bool, json_output: bool) -> None:
    print_title('我的机器人')
    if json_output:
        print(json.dumps([sanitize_robot(robot, show_app_key=show_app_key) for robot in robots], ensure_ascii=False, indent=2))
        return

    if not robots:
        print('未查到任何私人机器人。')
        print('如果你准备新建一个，可以直接运行 `setup_myclaw.py` 继续配置。')
        return

    print(f'共 {len(robots)} 个机器人：')
    for index, robot in enumerate(robots, start=1):
        name = stringify(robot.get('name')) or '-'
        agent_id = stringify(robot.get('agentId')) or '-'
        app_key = stringify(robot.get('appKey')) or '-'
        app_key_display = app_key if show_app_key else mask_secret(app_key)
        print(f'{index}. {name} [{agent_id}]')
        print(f'   appKey={app_key_display}')
        print(f'   robotId={stringify(robot.get("id")) or "-"} online={"是" if robot.get("isOnline") else "否"} default={"是" if robot.get("isDefault") else "否"}')
        print(f'   userId={stringify(robot.get("userId")) or "-"} ownerEmpId={stringify(robot.get("ownerEmpId")) or "-"}')
        print(f'   groupLabel={stringify(robot.get("groupLabel")) or "-"} visibleType={stringify(robot.get("visibleType")) or "-"}')
        print(f'   lastUseTime={format_time_millis(robot.get("lastUseTime"))} useCount={stringify(robot.get("useCount")) or "0"}')
        remark = stringify(robot.get('remark'))
        if remark:
            print(f'   remark={remark}')

    print('\n如果你要把其中某个机器人接入 OpenClaw，可以继续运行 `setup_myclaw.py` 完成绑定。')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='获取我的 xg_cwork_im 私人机器人列表')
    parser.add_argument('--app-key', type=str, help='预填工作协同 appKey；提供后不再交互询问。也可使用环境变量 CMS_CONFIG_MYCLAW_APP_KEY')
    parser.add_argument('--api-base-url', type=str, help=f'机器人接口基地址，默认 {DEFAULT_ROBOT_API_BASE_URL}；也可使用环境变量 CMS_CONFIG_MYCLAW_ROBOT_API_BASE_URL')
    parser.add_argument('--show-app-key', action='store_true', help='终端输出时显示完整机器人 appKey')
    parser.add_argument('--json', action='store_true', help='以 JSON 形式输出结果')
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        print_intro()
        prefilled_app_key, _app_key_source = resolve_prefilled_app_key(args)
        api_base_url = resolve_api_base_url(args)

        if prefilled_app_key:
            print(f'工作协同 key(appKey): 使用已有值 ({mask_secret(prefilled_app_key)})')
            app_key = prefilled_app_key
        else:
            app_key = prompt_app_key()

        print_title('获取 Access Token')
        token = get_access_token(app_key)
        print('已通过 cms-auth-skills 获取 access-token。')
        print(f'机器人接口地址: {api_base_url}')

        robots = fetch_my_robots(token, api_base_url)
        print_robots(robots, show_app_key=args.show_app_key, json_output=args.json)
        return 0
    except KeyboardInterrupt:
        print('\n已取消。')
        return 130
    except Exception as exc:  # noqa: BLE001
        print(f'\n错误: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
