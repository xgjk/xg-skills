#!/usr/bin/env python3
"""
Normalize scenarioPack fields between new/legacy schemas.
"""

from copy import deepcopy


def normalize_scenario_pack(scenario_pack: dict) -> dict:
    sp = deepcopy(scenario_pack or {})

    # New -> legacy compatibility for downstream generators.
    if "sceneBasic" not in sp:
        sp["sceneBasic"] = {
            "department": sp.get("department"),
            "product": sp.get("product"),
            "location": sp.get("location"),
        }

    if "roleSetup" not in sp:
        sp["roleSetup"] = {
            "doctorRole": "主任",
            "repRole": "医药代表",
            "department": sp.get("department"),
        }

    if "personaConfig" not in sp:
        sp["personaConfig"] = {
            "doctorConcerns": sp.get("doctorConcerns", []),
            "repGoal": sp.get("repGoal"),
            "styleHints": sp.get("styleHints", []),
        }

    if "personaBase" not in sp and sp.get("personaConfig"):
        sp["personaBase"] = {"config": sp.get("personaConfig")}

    # Keep product evidence fields explicit for gating.
    sp["productEvidenceStatus"] = sp.get("productEvidenceStatus", "NOT_PROVIDED")
    sp["productEvidenceSource"] = sp.get("productEvidenceSource", [])
    return sp
