#!/usr/bin/env python3
"""
scene / route-by-intent — 契约校验脚本（stdin JSON）。输出 TOON。
API_URL 须与 openapi/scene/route-by-intent.md 标题 URL 一致；本脚本不发起 HTTP。
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from auth_token import require_access_token
from toon_encoder import encode as toon_encode

API_URL = "https://scenario-builder.openclaw.internal/v1/scene/route-by-intent"

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
    user_text = (body.get("userText") or "").strip()
    if not user_text:
        print("错误: 缺少 userText", file=sys.stderr)
        sys.exit(2)
    route_decision = body.get("routeDecision")
    if not isinstance(route_decision, dict):
        print("错误: 缺少 routeDecision（必须由上游参数传入）", file=sys.stderr)
        sys.exit(2)

    intent = route_decision.get("intent")
    next_step = route_decision.get("nextStep")
    reason = route_decision.get("reason", "provided-by-upstream")
    need_clarification = bool(route_decision.get("needClarification", False))
    clarify_question = route_decision.get("clarifyQuestion", "")
    preconditions = list(route_decision.get("preconditions") or [])

    if not intent or not next_step:
        print("错误: routeDecision.intent 与 routeDecision.nextStep 必填", file=sys.stderr)
        sys.exit(2)

    session_state = body.get("sessionState") if isinstance(body.get("sessionState"), dict) else {}
    if intent == "PERSIST_CONFIRM":
        vr = session_state.get("validationReport") if isinstance(session_state.get("validationReport"), dict) else {}
        if not vr.get("passed"):
            preconditions.append("缺少 validationReport.passed=true")
            need_clarification = True
            if not clarify_question:
                clarify_question = "当前还没有通过校验，是否先执行校验？"
            next_step = "validate-and-gate"
            reason = "persist-request-without-passed-validation"

    _ok(
        "route-by-intent",
        intent=intent,
        nextStep=next_step,
        reason=reason,
        needClarification=need_clarification,
        clarifyQuestion=clarify_question,
        preconditions=preconditions,
    )

if __name__ == "__main__":
    main()
