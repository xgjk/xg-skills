#!/usr/bin/env python3
"""
Skill 问题反馈 — 自动收集并上报用户使用 Skill 时遇到的问题

用途：将 Skill 运行错误、用户反馈的问题自动整理并 POST 到技能管理平台

使用方式（命令行）：
  python3 cms-push-skill/scripts/issue_report/report_issue.py \
    --skill-code "work-collaboration" \
    --version "1.0.0" \
    --error "requests.exceptions.ConnectionError: 连接超时" \
    --message "用户调用汇报提交接口时连接超时，重试3次均失败"

  # 从 stdin 读取错误堆栈
  python3 some_script.py 2>&1 | python3 cms-push-skill/scripts/issue_report/report_issue.py \
    --skill-code "xxx" --version "1.0.0" --stdin

被其他脚本引用：
  from issue_report.report_issue import report_issue, auto_catch

  # 方式 1：手动上报
  report_issue(skill_code="xxx", version="1.0.0", error_message="...", user_message="...")

  # 方式 2：装饰器自动捕获
  @auto_catch(skill_code="xxx", version="1.0.0")
  def my_function():
      ...
"""

import sys
import os
import json
import time
import traceback
import argparse
import urllib.request
import urllib.error
import ssl
import functools

# 技能管理平台后端地址
API_BASE = "https://skills.mediportal.com.cn"
REPORT_ENDPOINT = "/api/skill/issues/report"


def _ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _get_auth_headers():
    """获取认证头（如果有 access-token）"""
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("XG_USER_TOKEN", "")
    if token:
        headers["access-token"] = token
    return headers


def report_issue(
    skill_code: str,
    version: str = "1.0.0",
    skill_name: str = "",
    skill_description: str = "",
    error_message: str = "",
    error_stack: str = "",
    user_message: str = "",
    context: dict = None,
    severity: str = "error",
    api_base: str = "",
) -> dict:
    """
    上报问题到技能管理平台。

    通过后端 /api/skill/issues/report 接口上报，后端转发到远端 /im/skill/issues/report。

    Args:
        skill_code:        Skill 唯一标识（必填）
        version:           Skill 版本号（必填，如 "1.0.0"）
        skill_name:        Skill 显示名称（可选）
        skill_description: Skill 描述（可选）
        error_message:     错误信息（与 user_message 至少填一个）
        error_stack:       错误堆栈（可选）
        user_message:      用户描述的问题（与 error_message 至少填一个）
        context:           附加上下文信息（可选，如参数、环境等）
        severity:          严重级别：error / warning / info（默认 error）
        api_base:          后端地址（可选，默认从环境变量或 localhost:8787）

    Returns:
        dict: API 响应

    Raises:
        RuntimeError: 上报失败
    """
    base_url = (api_base or API_BASE).rstrip("/")
    url = f"{base_url}{REPORT_ENDPOINT}"

    payload = {
        "skillCode": skill_code,
        "clawVersion": version,
        "skillName": skill_name,
        "skillDescription": skill_description,
        "errorMessage": error_message,
        "errorStack": error_stack,
        "userMessage": user_message,
        "context": context or {},
        "severity": severity,
    }

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ctx = _ssl_context()
    headers = _get_auth_headers()

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    # 重试机制：最多 3 次，间隔 1 秒
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                if result.get("resultCode") == 1:
                    return result.get("data", result)
                else:
                    raise RuntimeError(f"上报失败: {result.get('resultMsg', '未知错误')}")
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            last_error = e
            if attempt < 2:
                time.sleep(1)

    raise RuntimeError(f"上报失败（重试 3 次）: {last_error}")


def auto_catch(skill_code: str, version: str = "1.0.0", skill_name: str = "", skill_description: str = "", severity: str = "error"):
    """
    装饰器：自动捕获函数异常并上报。

    用法：
        @auto_catch(skill_code="my-skill", version="1.0.0")
        def main():
            ...

    异常会被上报后重新抛出，不影响原有逻辑。
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                stack = traceback.format_exc()
                try:
                    report_issue(
                        skill_code=skill_code,
                        version=version,
                        skill_name=skill_name,
                        skill_description=skill_description,
                        error_message=str(e),
                        error_stack=stack,
                        user_message=f"脚本 {func.__name__} 执行异常",
                        context={
                            "function": func.__name__,
                            "module": func.__module__,
                            "args_count": len(args),
                        },
                        severity=severity,
                    )
                    print(f"⚠️ 问题已自动上报到技能管理平台", file=sys.stderr)
                except Exception as report_err:
                    print(f"⚠️ 自动上报失败: {report_err}", file=sys.stderr)
                raise
        return wrapper
    return decorator


def main():
    parser = argparse.ArgumentParser(description="Skill 问题反馈")
    parser.add_argument("--skill-code", "-c", required=True, help="Skill 唯一标识（skillCode）")
    parser.add_argument("--version", "-v", default="1.0.0", help="Skill 版本号（如 1.0.0）")
    parser.add_argument("--skill-name", "-n", default="", help="Skill 显示名称")
    parser.add_argument("--skill-desc", default="", help="Skill 描述")
    parser.add_argument("--error", "-e", default="", help="错误信息")
    parser.add_argument("--stack", default="", help="错误堆栈")
    parser.add_argument("--message", "-m", default="", help="用户描述的问题")
    parser.add_argument("--severity", "-s", default="error", choices=["error", "warning", "info"], help="严重级别")
    parser.add_argument("--stdin", action="store_true", help="从 stdin 读取错误信息（追加到 --error）")
    parser.add_argument("--api-base", default="", help="后端地址（默认 http://localhost:8787）")
    args = parser.parse_args()

    error_msg = args.error
    if args.stdin:
        stdin_data = sys.stdin.read().strip()
        if stdin_data:
            error_msg = f"{error_msg}\n{stdin_data}" if error_msg else stdin_data

    if not error_msg and not args.message:
        print("错误: 请提供 --error 或 --message（至少一个）", file=sys.stderr)
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
            severity=args.severity,
            api_base=args.api_base,
        )
        print(f"✅ 问题已上报", file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False))
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
