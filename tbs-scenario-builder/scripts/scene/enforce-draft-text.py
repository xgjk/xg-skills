#!/usr/bin/env python3
"""
enforce-draft-text — 仅做校验，不做任何文本重建/兜底。
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))
from toon_encoder import encode as toon_encode  # type: ignore


def _normalize_scene_doctors(api_draft: dict):
    doctors = api_draft.get("doctors") or {}
    if isinstance(doctors, list):
        doctors = doctors[0] if doctors else {}

    scenes = api_draft.get("scenes") or {}
    if isinstance(scenes, list):
        scenes = scenes[0] if scenes else {}

    return doctors, scenes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=os.path.join("scripts", "tbs_assets", "scenario_draft.json"))
    ap.add_argument("--write-back", action="store_true", help="Rewrite input JSON in-place.")
    args = ap.parse_args()

    input_path = args.input
    if not os.path.isfile(input_path):
        raise SystemExit(f"Missing input file: {input_path}")

    # Import quality check helpers only; no generation fallback.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from tbs_write_executor import (  # type: ignore
        _doctor_only_context_quality_ok,
        _coach_only_context_quality_ok,
        _coach_only_context_matches_scene_type,
    )

    with open(input_path, "r", encoding="utf-8") as f:
        draft = json.load(f)

    scenario_pack = draft.get("scenarioPack") or {}
    api_draft = draft.get("apiDraft") or {}
    api_draft_doctors, api_draft_scenes = _normalize_scene_doctors(api_draft)

    if not isinstance(api_draft_scenes, dict):
        raise SystemExit("Invalid draft shape: apiDraft.scenes must be an object (or a list with first element as object).")

    rep_briefing_old = api_draft_scenes.get("rep_briefing") or ""
    location = scenario_pack.get("location")
    department = scenario_pack.get("department")
    product = scenario_pack.get("product")
    rep_briefing_invalid = (
        (not isinstance(rep_briefing_old, str))
        or (not rep_briefing_old.strip())
        or ("【" in rep_briefing_old or "】" in rep_briefing_old)
        or "待补充" in rep_briefing_old
        or (len(rep_briefing_old) > 180)
        or (location and str(location) not in rep_briefing_old)
        or (department and str(department) not in rep_briefing_old)
        or (product and str(product) not in rep_briefing_old)
    )
    doc_ctx_old = api_draft_scenes.get("doctor_only_context") or ""
    coach_ctx_old = api_draft_scenes.get("coach_only_context") or ""
    doctor_ctx_invalid = (not isinstance(doc_ctx_old, str)) or (not _doctor_only_context_quality_ok(doc_ctx_old))
    coach_ctx_invalid = (not isinstance(coach_ctx_old, str)) or (not _coach_only_context_quality_ok(coach_ctx_old)) or (not _coach_only_context_matches_scene_type(scenario_pack, coach_ctx_old))

    issues = []
    if rep_briefing_invalid:
        issues.append("rep_briefing_invalid")
    if doctor_ctx_invalid:
        issues.append("doctor_only_context_invalid")
    if coach_ctx_invalid:
        issues.append("coach_only_context_invalid")

    if args.write_back:
        raise SystemExit("禁止 write-back：本脚本仅校验，不做文本重建。")

    out = {
        "input": input_path,
        "valid": len(issues) == 0,
        "issues": issues,
    }
    print(toon_encode(out))


if __name__ == "__main__":
    main()

