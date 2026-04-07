#!/usr/bin/env python3
"""
scene / build-api-draft-dedup — 契约校验脚本（stdin JSON）。输出 TOON。
API_URL 须与 openapi/scene/build-api-draft-dedup.md 标题 URL 一致；本脚本不发起 HTTP。
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from auth_token import require_access_token
from toon_encoder import encode as toon_encode
from scenario_pack_normalizer import normalize_scenario_pack

API_URL = "https://scenario-builder.openclaw.internal/v1/scene/build-api-draft-dedup"
ALLOWED_EVIDENCE_STATUS = {"NOT_PROVIDED", "PARTIAL", "READY"}

def _read_body():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)

def _ok(step, **extra):
    payload = {"ok": True, "step": step, **extra}
    print(toon_encode(payload))


def _contains_blocked_fact_claims(node, blocked_keys):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in blocked_keys:
                return True
            if _contains_blocked_fact_claims(value, blocked_keys):
                return True
    elif isinstance(node, list):
        for item in node:
            if _contains_blocked_fact_claims(item, blocked_keys):
                return True
    return False


def _contains_blocked_fact_phrases(node, blocked_phrases):
    if isinstance(node, str):
        text = re.sub(r"\s+", "", node)
        return any(p in text for p in blocked_phrases)
    if isinstance(node, dict):
        return any(_contains_blocked_fact_phrases(v, blocked_phrases) for v in node.values())
    if isinstance(node, list):
        return any(_contains_blocked_fact_phrases(v, blocked_phrases) for v in node)
    return False

def main():
    require_access_token()
    body = _read_body()
    sp = body.get("scenarioPack")
    api_draft = body.get("apiDraft")
    policy = body.get("factGuardPolicy")
    if not isinstance(sp, dict) or not isinstance(api_draft, dict):
        print("错误: scenarioPack 与 apiDraft 必填", file=sys.stderr)
        sys.exit(2)
    if not isinstance(policy, dict):
        print("错误: 缺少 factGuardPolicy（必须由上游参数传入）", file=sys.stderr)
        sys.exit(2)
    blocked_keys = policy.get("blockedFactKeys")
    blocked_phrases = policy.get("blockedPhrases")
    if not isinstance(blocked_keys, list) or not all(isinstance(x, str) for x in blocked_keys):
        print("错误: factGuardPolicy.blockedFactKeys 必须为字符串数组", file=sys.stderr)
        sys.exit(2)
    if not isinstance(blocked_phrases, list) or not all(isinstance(x, str) for x in blocked_phrases):
        print("错误: factGuardPolicy.blockedPhrases 必须为字符串数组", file=sys.stderr)
        sys.exit(2)
    sp = normalize_scenario_pack(sp)

    evidence_status = sp.get("productEvidenceStatus", "NOT_PROVIDED")
    if evidence_status not in ALLOWED_EVIDENCE_STATUS:
        print("错误: productEvidenceStatus 非法", file=sys.stderr)
        sys.exit(2)

    if evidence_status != "READY":
        if _contains_blocked_fact_claims(api_draft, set(blocked_keys)):
            print("错误: 证据未 READY，apiDraft 不得包含事实性结论字段", file=sys.stderr)
            sys.exit(2)
        if _contains_blocked_fact_phrases(api_draft, blocked_phrases):
            print("错误: 证据未 READY，apiDraft 不得包含结论性事实表述", file=sys.stderr)
            sys.exit(2)

        confirmation_marked = bool(api_draft.get("needsEvidenceConfirmation"))
        if not confirmation_marked:
            print("错误: 证据未 READY 时，apiDraft 需标记 needsEvidenceConfirmation=true", file=sys.stderr)
            sys.exit(2)

    _ok(
        "build-api-draft-dedup",
        evidenceStatus=evidence_status,
        constrainedGeneration=evidence_status != "READY",
    )

if __name__ == "__main__":
    main()
