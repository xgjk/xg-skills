#!/usr/bin/env python3
"""
scene / build-prompts — 契约校验脚本（stdin JSON）。输出 TOON。
API_URL 须与 openapi/scene/build-prompts.md 标题 URL 一致；本脚本不发起 HTTP。
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from auth_token import require_access_token
from toon_encoder import encode as toon_encode
from scenario_pack_normalizer import normalize_scenario_pack

API_URL = "https://scenario-builder.openclaw.internal/v1/scene/build-prompts"
ALLOWED_EVIDENCE_STATUS = {"NOT_PROVIDED", "PARTIAL", "READY"}

def _read_body():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)

def _ok(step, **extra):
    payload = {"ok": True, "step": step, **extra}
    print(toon_encode(payload))


def _missing_core_fields(scenario_pack: dict) -> list:
    required = ["businessDomain", "department", "product", "location", "repGoal"]
    return [k for k in required if not scenario_pack.get(k)]

def main():
    require_access_token()
    body = _read_body()
    sp = body.get("scenarioPack")
    if not isinstance(sp, dict):
        print("错误: scenarioPack 必填", file=sys.stderr)
        sys.exit(2)
    sp = normalize_scenario_pack(sp)

    missing_core = _missing_core_fields(sp)
    if missing_core:
        print(f"错误: scenarioPack 缺少核心字段: {', '.join(missing_core)}", file=sys.stderr)
        sys.exit(2)

    has_persona = any(k in sp for k in ("personaConfig", "personaBase", "personaOverlay"))
    if not has_persona:
        print("错误: 需先具备 persona 产物（personaConfig/personaBase/personaOverlay）", file=sys.stderr)
        sys.exit(2)

    evidence_status = sp.get("productEvidenceStatus", "NOT_PROVIDED")
    if evidence_status not in ALLOWED_EVIDENCE_STATUS:
        print("错误: productEvidenceStatus 非法", file=sys.stderr)
        sys.exit(2)

    _ok(
        "build-prompts",
        evidenceStatus=evidence_status,
        constrainedGeneration=evidence_status != "READY",
    )

if __name__ == "__main__":
    main()
