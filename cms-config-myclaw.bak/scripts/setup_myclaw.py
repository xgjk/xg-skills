#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from getpass import getpass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from http_support import RequestFailure, ensure_result_success, extract_result_data, mask_secret, request_json, stringify
from openclaw_config import DEFAULT_BASE_URL, DEFAULT_WS_BASE_URL, backup_config, format_existing_state, get_agents, load_config, merge_myclaw_config, restore_config, save_config, summarize_agent, summarize_existing_state

ROBOT_REGISTER_URL = 'https://sg-al-cwork-api.mediportal.com.cn/im/robot/private/register'
WEB_INTERACT_URL = 'https://sg-al-cwork-web.mediportal.com.cn/xg-claw/web/dist/'
PLUGIN_ID = 'xg_cwork_im'
PLUGIN_SPEC = '@xgjktech/xg_cwork_im'
DEFAULT_CONFIG_PATH = Path('~/.openclaw/openclaw.json').expanduser()


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
    print('这是一个 CLI 交互式向导，你只需要按提示一步一步输入或确认即可。')
    print('它配置的不是普通参数，而是把公司内部的一个消息 channel 接到你的 OpenClaw 上。')
    print('\n这个向导会帮你完成三件事：')
    print('1. 创建或更新你的工作协同私人机器人')
    print('2. 把这台机器人绑定到你选择的 OpenClaw agent')
    print('3. 写入 OpenClaw 配置并重启 Gateway，使绑定正式生效')
    print('\n开始前你只需要准备：')
    print('1. 一个可用的工作协同 key(appKey)')
    print('2. 想绑定到哪个 agent')
    print('3. 你希望这个机器人显示成什么名字')
    print('\n接下来你会经历这几个步骤：')
    print('1. 先选择要绑定的 agent')
    print('2. 再确认 appKey 和机器人名称')
    print('3. 脚本自动完成注册机器人、检查插件、写入配置')
    print('4. 最后自动重启 Gateway，并给你互动链接')
    print('\n为什么要绑定？')
    print('因为这个插件本质上是一个公司内部 channel。')
    print('只有完成绑定后，这个 channel 进来的消息，才会被路由到你选中的 OpenClaw agent。')
    print('你选择哪个 agent，后续这台机器人收到的消息就会交给哪个 agent 处理。')
    print('不绑定的话，即使机器人创建出来了，OpenClaw 也不知道应该把消息交给哪个 agent。')
    print('\n配置完成后怎么用？')
    print('脚本会给你一个公司内部互动链接。')
    print('打开这个链接后，你就可以在公司内部互动页面里直接给机器人发送消息。')
    print('这相当于通过公司的 channel，远程和你本地这台 OpenClaw 所绑定的 agent 互动。')


def confirm(prompt: str) -> bool:
    value = input(f'{prompt} [y/N]: ').strip().lower()
    return value in {'y', 'yes'}


def prompt_required(prompt: str, *, secret: bool = False) -> str:
    while True:
        if secret:
            if sys.stdin.isatty() and sys.stderr.isatty():
                value = getpass(f'{prompt}: ')
            else:
                value = input(f'{prompt}: ')
        else:
            value = input(f'{prompt}: ')
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


def resolve_active_config_path(explicit_path: str | None) -> Path:
    if explicit_path:
        return Path(explicit_path).expanduser().resolve()

    openclaw = shutil.which('openclaw')
    if not openclaw:
        return DEFAULT_CONFIG_PATH

    result = subprocess.run(
        [openclaw, 'config', 'file'],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = (result.stdout or '').splitlines()
    for line in reversed(output):
        candidate = line.strip()
        if candidate.endswith('.json'):
            return Path(candidate).expanduser().resolve()
    return DEFAULT_CONFIG_PATH


def build_openclaw_env(config_path: Path) -> dict[str, str]:
    env = os.environ.copy()
    env['OPENCLAW_CONFIG_PATH'] = str(config_path)
    if config_path.name == 'openclaw.json':
        env.setdefault('OPENCLAW_STATE_DIR', str(config_path.parent))
    return env


def run_openclaw(
    args: list[str],
    *,
    env: dict[str, str],
    description: str,
    check: bool = True,
    echo: bool = True,
) -> subprocess.CompletedProcess[str]:
    openclaw = shutil.which('openclaw')
    if not openclaw:
        raise RuntimeError('未找到 openclaw 命令，请先安装或加入 PATH')

    result = subprocess.run(
        [openclaw] + args,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env=env,
    )
    output = (result.stdout or '').strip()
    if output and echo:
        print(output)
    if check and result.returncode != 0:
        raise RuntimeError(f'{description}失败:\n{output or "(无输出)"}')
    return result


def plugin_installed(env: dict[str, str]) -> bool:
    result = run_openclaw(
        ['plugins', 'info', PLUGIN_ID, '--json'],
        env=env,
        description=f'检测 {PLUGIN_ID} 插件状态',
        check=False,
        echo=False,
    )
    return result.returncode == 0


def reinstall_plugin(env: dict[str, str]) -> None:
    print_title('插件检查')
    if plugin_installed(env):
        print(f'检测到 {PLUGIN_ID} 已安装，本次保留现有安装，仅确保启用。')
    else:
        print(f'未检测到 {PLUGIN_ID}，开始安装。')
        run_openclaw(
            ['plugins', 'install', PLUGIN_SPEC, '--pin'],
            env=env,
            description=f'安装 {PLUGIN_ID} 插件',
        )

    run_openclaw(
        ['plugins', 'enable', PLUGIN_ID],
        env=env,
        description=f'启用 {PLUGIN_ID} 插件',
    )


def capture_plugin_state(config: dict[str, Any], env: dict[str, str]) -> dict[str, Any]:
    installs = (((config.get('plugins') or {}).get('installs') or {}).get(PLUGIN_ID) or {})
    entries = (((config.get('plugins') or {}).get('entries') or {}).get(PLUGIN_ID) or {})
    allow = (((config.get('plugins') or {}).get('allow') or []))
    restore_spec = stringify(installs.get('resolvedSpec')) or stringify(installs.get('spec'))
    return {
        'present': plugin_installed(env),
        'restoreSpec': restore_spec,
        'enabled': bool(entries.get('enabled')) or PLUGIN_ID in allow,
    }


def ensure_preflight_ready(previous_plugin_state: dict[str, Any], env: dict[str, str]) -> None:
    validate_config(env)
    if previous_plugin_state.get('present') and not stringify(previous_plugin_state.get('restoreSpec')):
        raise RuntimeError(
            f'当前 {PLUGIN_ID} 插件已安装，但缺少可恢复的 install record(spec/resolvedSpec)。'
            ' 为避免卸载后无法回滚，已中止执行。请先修复 plugins.installs.xg_cwork_im。'
        )


def restore_plugin_state(previous_state: dict[str, Any] | None, env: dict[str, str]) -> None:
    if not previous_state:
        return

    plugin_is_present_now = plugin_installed(env)
    if not previous_state.get('present'):
        if plugin_is_present_now:
            run_openclaw(
                ['plugins', 'uninstall', PLUGIN_ID, '--force'],
                env=env,
                description=f'回滚 {PLUGIN_ID} 插件',
            )
        return

    restore_spec = stringify(previous_state.get('restoreSpec'))
    if not restore_spec:
        return

    if plugin_is_present_now:
        print(f'正在恢复原有 {PLUGIN_ID} 插件状态。')
    else:
        run_openclaw(
            ['plugins', 'install', restore_spec, '--pin'],
            env=env,
            description=f'回滚安装 {PLUGIN_ID} 插件',
        )
    if previous_state.get('enabled'):
        run_openclaw(
            ['plugins', 'enable', PLUGIN_ID],
            env=env,
            description=f'回滚启用 {PLUGIN_ID} 插件',
        )


def validate_config(env: dict[str, str]) -> None:
    result = run_openclaw(
        ['config', 'validate', '--json'],
        env=env,
        description='校验 openclaw 配置',
        check=False,
        echo=False,
    )
    if result.returncode != 0:
        output = (result.stdout or '').strip()
        raise RuntimeError(f'OpenClaw 配置校验失败:\n{output or "(无输出)"}')


def build_interact_url(token: str) -> str:
    return f'{WEB_INTERACT_URL}?xgToken={quote(token, safe="")}'


def _gateway_status_ready(output: str) -> bool:
    lowered = output.lower()
    return 'runtime: running' in lowered and 'rpc probe: ok' in lowered


def restart_gateway_and_check(env: dict[str, str], *, quiet: bool = False) -> str:
    if not quiet:
        print_title('重启 Gateway')

    restart_result = run_openclaw(
        ['gateway', 'restart', '--json'],
        env=env,
        description='重启 Gateway',
        check=False,
        echo=False,
    )
    if restart_result.returncode != 0:
        start_result = run_openclaw(
            ['gateway', 'start', '--json'],
            env=env,
            description='启动 Gateway',
            check=False,
            echo=False,
        )
        if start_result.returncode != 0:
            restart_output = (restart_result.stdout or '').strip()
            start_output = (start_result.stdout or '').strip()
            raise RuntimeError(
                'Gateway 重启失败。\n'
                f'restart 输出:\n{restart_output or "(无输出)"}\n'
                f'start 输出:\n{start_output or "(无输出)"}'
            )

    last_output = ''
    for _ in range(15):
        status_result = run_openclaw(
            ['gateway', 'status'],
            env=env,
            description='检查 Gateway 状态',
            check=False,
            echo=False,
        )
        last_output = (status_result.stdout or '').strip()
        if status_result.returncode == 0 and _gateway_status_ready(last_output):
            return last_output
        time.sleep(1)

    raise RuntimeError(f'Gateway 重启后状态检查未通过:\n{last_output or "(无输出)"}')


def choose_agent(agents: list[dict[str, Any]]) -> dict[str, Any]:
    print_title('选择 Agent')
    print('当前可绑定的 agent 如下：')
    for index, agent in enumerate(agents, start=1):
        print(f'{index}. {summarize_agent(agent)}')

    while True:
        raw = input('请输入编号或 agentId: ').strip()
        if not raw:
            print('输入不能为空，请重新输入。')
            continue
        if raw.isdigit():
            number = int(raw)
            if 1 <= number <= len(agents):
                return agents[number - 1]
        for agent in agents:
            if stringify(agent.get('id')) == raw:
                return agent
        print('未找到对应 agent，请重新输入。')


def collect_inputs(prefilled_app_key: str | None = None) -> dict[str, str]:
    print_title('输入配置参数')
    if prefilled_app_key:
        app_key = prefilled_app_key
        print(f'工作协同 key(appKey): 使用已有值 ({mask_secret(app_key)})')
        app_key_source = 'prefilled'
    else:
        app_key = prompt_required('请输入工作协同 key(appKey)', secret=True)
        app_key_source = 'prompt'

    robot_name = input('请输入机器人名称（回车使用服务端默认）: ').strip()
    return {
        'appKey': app_key,
        'name': robot_name,
        'avatar': '',
        'groupLabel': '',
        'remark': '',
        'appKeySource': app_key_source,
    }


def print_summary(
    *,
    config_path: Path,
    agent: dict[str, Any],
    inputs: dict[str, str],
    existing_state: dict[str, Any],
    dry_run: bool,
) -> None:
    print_title('执行摘要')
    agent_id = stringify(agent.get('id')) or '<unknown>'
    agent_name = stringify(agent.get('name')) or agent_id
    print(f'配置文件: {config_path}')
    print(f'目标 agent: {agent_name} [{agent_id}]')
    print(f'机器人名称: {inputs["name"] or "<服务端默认>"}')
    print(f'appKey: {"复用已有值" if inputs.get("appKeySource") != "prompt" else "本次输入"}')
    print('头像/分组/备注: 使用默认值')
    print(f'将写入 channel account: channels.xg_cwork_im.accounts.{agent_id}')
    print('绑定意义: 这台机器人后续收到的消息，会路由到上面选中的 agent。')
    print('使用结果: 以后你在互动页面里给这台机器人发消息，实际上就是在和这个 agent 对话。')
    print(f'模式: {"dry-run" if dry_run else "正式执行"}')
    if existing_state.get('has_existing'):
        print('\n检测到当前 agent 已存在 xg_cwork_im 配置:')
        print(format_existing_state(existing_state))


def build_register_body(agent_id: str, inputs: dict[str, str]) -> dict[str, str]:
    body = {'agentId': agent_id}
    for key in ('name', 'avatar', 'groupLabel', 'remark'):
        value = inputs.get(key, '').strip()
        if value:
            body[key] = value
    return body


def register_robot(token: str, agent_id: str, inputs: dict[str, str]) -> dict[str, Any]:
    payload = request_json(
        ROBOT_REGISTER_URL,
        method='POST',
        body=build_register_body(agent_id, inputs),
        headers={'access-token': token},
    )
    ensure_result_success(payload, '创建机器人失败')
    data = extract_result_data(payload)
    if not data:
        raise RequestFailure('创建机器人失败: 接口未返回 data')
    return data


def validate_robot_registration(agent_id: str, robot_data: dict[str, Any]) -> str:
    returned_agent_id = stringify(robot_data.get('agentId'))
    if returned_agent_id and returned_agent_id != agent_id:
        raise RequestFailure(
            f'创建机器人失败: 接口返回的 agentId={returned_agent_id} 与目标 agentId={agent_id} 不一致'
        )

    returned_app_key = stringify(robot_data.get('appKey'))
    if not returned_app_key:
        raise RequestFailure('创建机器人失败: 接口未返回机器人 appKey，无法写入 OpenClaw channel account')
    return returned_app_key


def print_before_restart(
    *,
    config_path: Path,
    agent_id: str,
    account_id: str,
    robot_name: str,
    interact_url: str,
) -> None:
    print_title('配置已完成')
    print('OpenClaw 配置已经写入完成。')
    print(f'配置文件: {config_path}')
    print(f'agentId: {agent_id}')
    print(f'accountId: {account_id}')
    print(f'机器人名称: {robot_name}')
    print(f'互动链接: {interact_url}')
    print('你可以通过这个公司内部链接进入互动页面，直接给机器人发送消息。')
    print('下一步将自动重启 Gateway，使新配置正式生效。')
    print('Gateway 重启完成后，这个 channel 就可以正式开始接收并转发消息。')


def print_success(
    *,
    config_path: Path,
    agent_id: str,
    account_id: str,
    robot_name: str,
    overwrite_existing: bool,
    backup_path: Path | None,
    interact_url: str,
) -> None:
    print_title('完成')
    print(f'配置文件: {config_path}')
    print(f'agentId: {agent_id}')
    print(f'accountId: {account_id}')
    print(f'机器人名称: {robot_name}')
    print(f'已写入 channel account: channels.xg_cwork_im.accounts.{account_id}')
    print(f'覆盖旧配置: {"是" if overwrite_existing else "否"}')
    if backup_path:
        print(f'配置备份: {backup_path}')
    print('Gateway 已重启并通过状态检查。')
    print(f'互动链接: {interact_url}')
    print('现在可以打开上面的公司内部互动链接，进入互动页面直接给机器人发送消息。')
    print('\n建议你现在马上做一次验证：')
    print('1. 打开上面的互动链接')
    print('2. 给机器人发送一条简单消息，比如“你好”')
    print(f'3. 确认最终是由 {agent_id} 返回内容')
    print('如果能正常回复，就说明 channel、binding、插件和 Gateway 都已经生效。')
    print('\n如果你不知道第一句该发什么，可以直接试下面这些：')
    print(f'1. 你好，我现在正在验证 {robot_name} 是否已经接到 {agent_id}，请先回复我一句。')
    print(f'2. 请告诉我，你现在对应的是哪个 agent；我预期应该是 {agent_id}。')
    print(f'3. 我刚完成绑定，请用一句简短的话确认 {robot_name} 已经可以正常工作。')
    print('\n怎么理解后续使用：')
    print('以后你不需要再关心 channels、bindings、插件这些配置细节。')
    print('你只需要打开这个公司内部互动链接，把这台机器人当成当前所选 agent 的远程互动入口来使用。')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='交互式配置 OpenClaw xg_cwork_im 机器人')
    parser.add_argument('--dry-run', action='store_true', help='只做检查和摘要，不执行远端调用或本地写入')
    parser.add_argument('--config-file', type=str, help='显式指定要修改的 openclaw.json')
    parser.add_argument('--app-key', type=str, help='预填工作协同 appKey；提供后不再交互询问。也可使用环境变量 CMS_CONFIG_MYCLAW_APP_KEY')
    return parser


def main() -> int:
    args = build_parser().parse_args()

    backup_path: Path | None = None
    config_path: Path | None = None
    env: dict[str, str] | None = None
    local_mutation_started = False
    plugin_mutation_started = False
    gateway_restart_attempted = False
    previous_plugin_state: dict[str, Any] | None = None

    try:
        print_intro()

        config_path = resolve_active_config_path(args.config_file)
        env = build_openclaw_env(config_path)

        if not shutil.which('openclaw'):
            raise RuntimeError('未找到 openclaw 命令，请先安装 OpenClaw CLI')

        config = load_config(config_path)
        agents = get_agents(config)
        agent = choose_agent(agents)
        agent_id = stringify(agent.get('id')) or ''
        if not agent_id:
            raise RuntimeError('选中的 agent 缺少 id')

        existing_state = summarize_existing_state(config, agent_id)
        prefilled_app_key, _ = resolve_prefilled_app_key(args)
        inputs = collect_inputs(prefilled_app_key)

        print_summary(
            config_path=config_path,
            agent=agent,
            inputs=inputs,
            existing_state=existing_state,
            dry_run=args.dry_run,
        )

        overwrite_existing = False
        if args.dry_run:
            if existing_state.get('has_existing'):
                print('\nDry-run 提示: 正式执行时会要求你确认是否覆盖已有 xg_cwork_im 配置。')
            print('\nDry-run 完成，未执行任何远端或本地变更。')
            return 0

        if existing_state.get('has_existing'):
            overwrite_existing = True
            if not confirm('检测到已有配置，是否重建并覆盖当前 agent 的 xg_cwork_im 配置'):
                print('已取消，未执行任何变更。')
                return 0

        if not confirm('确认继续执行远端注册和本地配置写入'):
            print('已取消，未执行任何变更。')
            return 0

        previous_plugin_state = capture_plugin_state(config, env)
        ensure_preflight_ready(previous_plugin_state, env)

        print_title('获取 Access Token')
        token = get_access_token(inputs['appKey'])
        interact_url = build_interact_url(token)
        print('已通过 cms-auth-skills 获取 access-token。')

        print_title('注册机器人')
        robot_data = register_robot(token, agent_id, inputs)
        final_app_key = validate_robot_registration(agent_id, robot_data)
        final_name = (
            stringify(robot_data.get('name'))
            or inputs['name']
            or stringify(agent.get('name'))
            or agent_id
        )

        backup_path = backup_config(config_path)
        print(f'\n已创建配置备份: {backup_path}')

        local_mutation_started = True
        plugin_mutation_started = True
        reinstall_plugin(env)

        current_config = load_config(config_path)
        next_config = merge_myclaw_config(
            current_config,
            agent_id=agent_id,
            app_key=final_app_key,
            robot_name=final_name,
            base_url=DEFAULT_BASE_URL,
            ws_base_url=DEFAULT_WS_BASE_URL,
        )
        save_config(config_path, next_config)
        validate_config(env)

        print_before_restart(
            config_path=config_path,
            agent_id=agent_id,
            account_id=agent_id,
            robot_name=final_name,
            interact_url=interact_url,
        )

        gateway_restart_attempted = True
        restart_gateway_and_check(env)

        print_success(
            config_path=config_path,
            agent_id=agent_id,
            account_id=agent_id,
            robot_name=final_name,
            overwrite_existing=overwrite_existing,
            backup_path=backup_path,
            interact_url=interact_url,
        )
        return 0
    except KeyboardInterrupt:
        if config_path and backup_path and local_mutation_started:
            try:
                restore_config(config_path, backup_path)
                print('\n已恢复原始配置备份。')
            except Exception as restore_error:  # noqa: BLE001
                print(f'\n中断后回滚失败: {restore_error}', file=sys.stderr)
            if plugin_mutation_started and env:
                try:
                    restore_plugin_state(previous_plugin_state, env)
                    print('已恢复插件状态。')
                except Exception as restore_error:  # noqa: BLE001
                    print(f'插件状态回滚失败: {restore_error}', file=sys.stderr)
            if gateway_restart_attempted and env:
                try:
                    restart_gateway_and_check(env, quiet=True)
                    print('已尝试恢复 Gateway。')
                except Exception as restore_error:  # noqa: BLE001
                    print(f'Gateway 恢复失败: {restore_error}', file=sys.stderr)
        else:
            print('\n已取消。')
        return 130
    except Exception as exc:  # noqa: BLE001
        if config_path and backup_path and local_mutation_started:
            try:
                restore_config(config_path, backup_path)
                print('\n发生错误，已恢复原始配置备份。', file=sys.stderr)
            except Exception as restore_error:  # noqa: BLE001
                print(f'\n发生错误且回滚失败: {restore_error}', file=sys.stderr)
            if plugin_mutation_started and env:
                try:
                    restore_plugin_state(previous_plugin_state, env)
                    print('已恢复插件状态。', file=sys.stderr)
                except Exception as restore_error:  # noqa: BLE001
                    print(f'插件状态回滚失败: {restore_error}', file=sys.stderr)
            if gateway_restart_attempted and env:
                try:
                    restart_gateway_and_check(env, quiet=True)
                    print('已尝试恢复 Gateway。', file=sys.stderr)
                except Exception as restore_error:  # noqa: BLE001
                    print(f'Gateway 恢复失败: {restore_error}', file=sys.stderr)
        print(f'\n错误: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
