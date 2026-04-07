#!/usr/bin/env python3
"""
scene / persist-and-execute — 将草稿落盘并调用 tbs_write_executor.py；stdout 为 TOON。
"""
import json
import os
import subprocess
import sys
import ssl
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from auth_token import resolve_access_token
from toon_encoder import encode as toon_encode

API_URL = "https://scenario-builder.openclaw.internal/v1/scene/persist-and-execute"

def _skill_root() -> str:
    here = os.path.dirname(os.path.realpath(__file__))
    return os.path.normpath(os.path.join(here, "..", ".."))

def _runtime_dir() -> str:
    """Backward-compat: fallback assets live under `runtime/`."""
    return os.path.join(_skill_root(), "runtime")


def _assets_dir() -> str:
    """
    Prefer non-`runtime/` assets location.

    - Set env `TBS_ASSETS_DIR` to fully override.
    - Else if `scripts/tbs_assets/` exists, use it.
    - Else fall back to legacy `runtime/`.
    """
    env = os.environ.get("TBS_ASSETS_DIR")
    if env:
        return env
    skill_root = _skill_root()
    candidate = os.path.join(skill_root, "scripts", "tbs_assets")
    if os.path.isdir(candidate):
        return candidate
    candidate2 = os.path.join(skill_root, "assets", "tbs_assets")
    if os.path.isdir(candidate2):
        return candidate2
    return _runtime_dir()


def _auth_probe(base_url: str, access_token: str, insecure_ssl: bool = True):
    url = base_url.rstrip("/") + "/api/v1/admin/basic/business-domains"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "access-token": access_token,
    }
    req = urllib.request.Request(url=url, method="GET", headers=headers)
    try:
        ssl_ctx = ssl._create_unverified_context() if insecure_ssl else None
        with urllib.request.urlopen(req, timeout=20, context=ssl_ctx) as resp:
            return int(resp.status), ""
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        return int(e.code), raw[-500:]
    except Exception as e:
        return None, str(e)

def main():
    body = json.loads(sys.stdin.read() or "{}")
    vr = body.get("validationReport") or {}
    if not vr.get("passed"):
        print("错误: validationReport.passed 须为 true", file=sys.stderr)
        sys.exit(2)
    user_confirmation = body.get("userConfirmation")
    if not user_confirmation:
        print("错误: 缺少 userConfirmation", file=sys.stderr)
        sys.exit(2)

    user_confirmation = str(user_confirmation).strip()
    if user_confirmation == "取消":
        # Cancel is not an error; it should stop persistence gracefully.
        print(
            toon_encode(
                {
                    "ok": False,
                    "step": "persist-and-execute",
                    "message": "user_cancelled",
                    "hint": "用户已取消，本次不执行落库。",
                }
            )
        )
        sys.exit(0)
    if user_confirmation != "确认":
        print(
            toon_encode(
                {
                    "ok": False,
                    "step": "persist-and-execute",
                    "message": "invalid_userConfirmation",
                    "got": user_confirmation,
                    "hint": "userConfirmation 仅允许填入：确认 或 取消。",
                }
            )
        )
        sys.exit(2)
    assets_dir = _assets_dir()
    base_url = os.environ.get("TBS_BASE_URL", "https://sg-tbs-manage.mediportal.com.cn")
    access_token, token_source = resolve_access_token()
    if not access_token:
        print(
            toon_encode(
                {
                    "ok": False,
                    "step": "persist-and-execute",
                    "message": "missing_access_token",
                    "hint": "Set XG_USER_TOKEN before running persist-and-execute.",
                }
            )
        )
        sys.exit(1)

    probe_status, probe_error = _auth_probe(base_url=base_url, access_token=access_token, insecure_ssl=True)
    if probe_status != 200:
        print(
            toon_encode(
                {
                    "ok": False,
                    "step": "persist-and-execute",
                    "message": "auth_preflight_failed",
                    "tokenSource": token_source,
                    "probeUrl": base_url.rstrip("/") + "/api/v1/admin/basic/business-domains",
                    "probeStatus": probe_status,
                    "probeError": probe_error,
                }
            )
        )
        sys.exit(4)

    default_draft_assets = os.path.join(assets_dir, "scenario_draft.json")
    default_draft_runtime = os.path.join(_runtime_dir(), "scenario_draft.json")
    if os.path.isfile(default_draft_assets):
        default_draft = default_draft_assets
    else:
        default_draft = default_draft_runtime

    draft_path = body.get("draftPath") or default_draft
    payload = body.get("draftPayload")
    if payload is not None:
        with open(draft_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    # Executor 入口统一迁移到 scripts/scene/
    exe = os.path.join(os.path.dirname(__file__), "tbs_write_executor.py")
    if not os.path.isfile(exe):
        # fallback: older layout (tbs_assets wrapper)
        exe_fallback = os.path.join(assets_dir, "tbs_write_executor.py")
        exe = exe_fallback if os.path.isfile(exe_fallback) else exe

    if not os.path.isfile(exe):
        print(
            toon_encode(
                {
                    "ok": False,
                    "step": "persist-and-execute",
                    "message": "executor_missing",
                    "path": exe,
                }
            )
        )
        sys.exit(3)
    proc = subprocess.run(
        [sys.executable, exe, "--insecure-ssl", "--input", str(draft_path)],
        capture_output=True,
        text=True,
        timeout=600,
        env=os.environ,
    )
    print(toon_encode({
        "ok": proc.returncode == 0,
        "step": "persist-and-execute",
        "tokenSource": token_source,
        "probeStatus": probe_status,
        "returncode": proc.returncode,
        "stdoutTail": (proc.stdout or "")[-2000:],
        "stderrTail": (proc.stderr or "")[-2000:],
    }))
    if proc.returncode != 0:
        sys.exit(proc.returncode)

if __name__ == "__main__":
    main()
