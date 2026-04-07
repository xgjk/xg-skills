#!/usr/bin/env python3
"""
scene / validate-and-gate — 契约校验脚本（stdin JSON）。输出 TOON。
API_URL 须与 openapi/scene/validate-and-gate.md 标题 URL 一致；本脚本不发起 HTTP。
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from auth_token import require_access_token
from toon_encoder import encode as toon_encode
from scenario_pack_normalizer import normalize_scenario_pack

API_URL = "https://scenario-builder.openclaw.internal/v1/scene/validate-and-gate"
ALLOWED_EVIDENCE_STATUS = {"NOT_PROVIDED", "PARTIAL", "READY"}

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
    for k in ("scenarioPack", "apiDraft", "validationReport"):
        if k not in body or not isinstance(body[k], dict):
            print(f"错误: 缺少 {k}", file=sys.stderr)
            sys.exit(2)
    sp = normalize_scenario_pack(body["scenarioPack"])
    api_draft = body["apiDraft"]
    vr = body["validationReport"]

    evidence_status = sp.get("productEvidenceStatus", "NOT_PROVIDED")
    if evidence_status not in ALLOWED_EVIDENCE_STATUS:
        print("错误: productEvidenceStatus 非法", file=sys.stderr)
        sys.exit(2)

    issues = list(vr.get("issues") or [])
    if evidence_status != "READY":
        if not api_draft.get("needsEvidenceConfirmation"):
            issues.append("apiDraft.needsEvidenceConfirmation 必须为 true（证据未 READY）")
        if not sp.get("productEvidenceSource"):
            issues.append("缺少 productEvidenceSource，需补充知识来源")

    passed = bool(vr.get("passed"))
    if issues:
        passed = False

    _ok(
        "validate-and-gate",
        passed=passed,
        evidenceStatus=evidence_status,
        issues=issues,
    )

if __name__ == "__main__":
    main()
