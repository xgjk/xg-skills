#!/usr/bin/env python3
"""
scene / publish-ready-compose — 契约校验脚本（stdin JSON）。输出 TOON。
API_URL 须与 openapi/scene/publish-ready-compose.md 标题 URL 一致；本脚本不发起 HTTP。
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from auth_token import require_access_token
from toon_encoder import encode as toon_encode

API_URL = "https://scenario-builder.openclaw.internal/v1/scene/publish-ready-compose"

def _read_body():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)

def _ok(step, **extra):
    payload = {"ok": True, "step": step, **extra}
    print(toon_encode(payload))

def main():
    require_access_token()
    body = _read_body()
    sp = body.get("scenarioPack")
    mh = body.get("modeHints") or {}
    if not isinstance(sp, dict):
        print("错误: 缺少 scenarioPack", file=sys.stderr)
        sys.exit(2)
    pr = mh.get("publish_ready") or mh.get("outputMode") == "publish_ready"
    if not pr:
        print("错误: modeHints.publish_ready 或 outputMode=publish_ready 须成立", file=sys.stderr)
        sys.exit(2)
    _ok("publish-ready-compose")

if __name__ == "__main__":
    main()
