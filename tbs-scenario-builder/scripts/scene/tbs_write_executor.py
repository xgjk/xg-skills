#!/usr/bin/env python3
import argparse
import difflib
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from auth_token import resolve_access_token
from toon_encoder import encode as toon_encode  # type: ignore

from tbs_master_data_resolve import (
    TBSClient,
    extract_data,
    get_list,
    guess_entity_name,
    guess_entity_id,
    pick_best_match_id,
    resolve_ids_for_scene,
)

# 默认资产目录（兼容从 `runtime/` 迁移到其它路径）
def _find_skill_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(8):
        if os.path.isfile(os.path.join(here, "SKILL.md")):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    # fallback: assume current file is inside skill_root/runtime/
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _assets_dir() -> str:
    """
    - Set env `TBS_ASSETS_DIR` to override.
    - Else prefer `skill_root/scripts/tbs_assets/`.
    - Else fall back to legacy `skill_root/runtime/`.
    """
    env = os.environ.get("TBS_ASSETS_DIR")
    if env:
        return env
    skill_root = _find_skill_root()
    candidate = os.path.join(skill_root, "scripts", "tbs_assets")
    required = [
        "scenario_draft.json",
        "P1_persisted_ids.md",
    ]
    def _has_required(d: str) -> bool:
        return all(os.path.isfile(os.path.join(d, f)) for f in required)

    if os.path.isdir(candidate) and _has_required(candidate):
        return candidate
    candidate2 = os.path.join(skill_root, "assets", "tbs_assets")
    if os.path.isdir(candidate2) and _has_required(candidate2):
        return candidate2
    return os.path.join(skill_root, "runtime")


_RUNTIME_DIR = _assets_dir()


def normalize_text(s: str) -> str:
    if s is None:
        return ""
    # Normalize whitespace for stable fingerprinting.
    return re.sub(r"\s+", " ", str(s)).strip()


def fingerprint_sha256_of_text(s: str) -> str:
    n = normalize_text(s)
    return hashlib.sha256(n.encode("utf-8")).hexdigest()


def read_first_line(path: str):
    if not path:
        return None
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            line = f.readline().strip()
            return line if line else None
    except Exception:
        return None


def find_doctor_by_name_and_title(items, name: str, title: str):
    name = (name or "").strip()
    title = (title or "").strip()
    if not items:
        return None
    # Try to match name first; then title.
    for it in items:
        nm = (guess_entity_name(it) or "").strip()
        # Some list endpoints may use different keys for name/title.
        it_title = (it.get("title") or it.get("doctor_title") or "").strip() if isinstance(it, dict) else ""
        it_name = (it.get("name") or it.get("doctor_name") or nm or "").strip() if isinstance(it, dict) else ""
        if name and it_name == name:
            if title:
                if it_title == title:
                    return guess_entity_id(it)
            else:
                return guess_entity_id(it)
    # Fallback: fuzzy name match
    names = []
    id_by_name = {}
    for it in items:
        it_name = (it.get("name") or it.get("doctor_name") or "").strip()
        if it_name:
            names.append(it_name)
            id_by_name[it_name] = guess_entity_id(it)
    best = difflib.get_close_matches(name, names, n=1, cutoff=0.6)
    if best:
        return id_by_name.get(best[0])
    return None


def _default_surname_from_name(name: str) -> str:
    name = (name or "").strip()
    if name and name[0] in "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦许何吕施张孔曹严华金魏陶姜":
        return name[0]
    return "王"


def _build_default_persona_config(scenario_pack: dict, doctor_draft: dict) -> str:
    sp = scenario_pack or {}
    dd = doctor_draft or {}
    concern = (
        _safe_get(sp, ["criticalInfo", "coreConcern"])
        or sp.get("coreConcern")
        or sp.get("concerns")
        or "长期预后与依从性"
    )
    concern = _first_sentence(_ensure_nonempty_str(concern), max_len=60) or "长期预后与依从性"
    return "\n".join(
        [
            "## 性格特征",
            "- 理性",
            "- 专业",
            "- 稳健",
            "",
            "## 沟通风格",
            "你对新治疗方案并不排斥，但只在安全边界和逻辑清楚的前提下才会继续讨论。",
            "你不会主动推动用药，而是通过问题判断对方是否真的理解临床场景。",
            "",
            "## 行为倾向映射",
            "- 清楚说明适用人群 -> 愿意继续",
            "- 主动说明风险与边界 -> 信任上升",
            "- 过度承诺或泛化疗效 -> 明显警惕",
            f"- 能结合真实临床场景并回应“{concern}” -> 兴趣增加",
        ]
    )


def create_doctor_if_missing(client: TBSClient, doctor_draft: dict, scenario_pack: dict = None, dry_run: bool = False):
    doctors = get_list(client, "/api/v1/resources/doctors")
    name = doctor_draft.get("name") or doctor_draft.get("doctor_name") or doctor_draft.get("persona_name")
    title = doctor_draft.get("title") or doctor_draft.get("doctor_title") or ""

    found_id = find_doctor_by_name_and_title(doctors, name, title)
    if found_id:
        return found_id

    if dry_run:
        return None

    surname = _ensure_nonempty_str(doctor_draft.get("surname") or doctor_draft.get("last_name") or doctor_draft.get("family_name"))
    if not surname:
        surname = _default_surname_from_name(name)

    description = _ensure_nonempty_str(
        doctor_draft.get("description")
        or doctor_draft.get("desc")
        or doctor_draft.get("summary")
    )
    if not description:
        description = "专业理性，在安全与边界清楚的前提下愿意讨论新方案的医生，是理想训练对象。"

    persona_cfg = doctor_draft.get("persona_config", {})
    if not persona_cfg:
        persona_cfg = _build_default_persona_config(scenario_pack or {}, doctor_draft or {})
    # If persona_config is already a string (Markdown/JSON text), pass it through.
    if isinstance(persona_cfg, str):
        persona_cfg_text = persona_cfg
    else:
        persona_cfg_text = json.dumps(persona_cfg, ensure_ascii=False)

    body = {
        "name": name,
        "surname": surname,
        "title": title,
        "description": description,
        "persona_config": persona_cfg_text,
        "is_preset": False,
    }
    # Some APIs accept optional trust_initial/patience_initial; keep minimal to reduce incompatibility.
    resp = client.request_json("POST", "/api/v1/admin/basic/doctors", body=body)
    data = extract_data(resp)
    return data


def load_persisted_knowledge_ids(persisted_ids_path: str):
    # Very small heuristic parser for the existing markdown.
    if not os.path.exists(persisted_ids_path):
        return []
    text = open(persisted_ids_path, "r", encoding="utf-8").read()
    ids = []
    # Compatible with formats like: - `52`（产品特性） / - 52（产品特性）
    for m in re.finditer(r"-\s*`?\s*(\d+)\s*`?\s*（", text):
        ids.append(m.group(1))
    # Dedup while preserving order
    seen = set()
    out = []
    for x in ids:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def infer_intent_keywords(scenario_pack: dict) -> dict:
    """
    Return boolean intent flags inferred from scenario text.
    Heuristic only; selection still degrades gracefully to persisted IDs.
    """
    text = ""
    try:
        text = " ".join(
            [
                scenario_pack.get("sceneBasic", {}).get("sceneBackground", "") or "",
                scenario_pack.get("criticalInfo", {}).get("coreConcern", "") or "",
                scenario_pack.get("criticalInfo", {}).get("trainingGoal", "") or "",
                scenario_pack.get("sceneBasic", {}).get("repBriefing", "") or "",
            ]
        )
    except Exception:
        text = ""
    text = normalize_text(text)

    def has_any(words):
        return any(w in text for w in words)

    return {
        "price": has_any(["价格", "价差", "贵", "便宜", "值不值", "溢价", "质价比", "买贵", "预算"]),
        "safety": has_any(["安全", "风险", "合规", "无菌", "结节", "肿胀", "副作用", "迟发", "边界", "风险边界"]),
        "recovery": has_any(["恢复", "肿胀", "肿", "工作", "出镜", "社交", "恢复期"]),
        "naturalness": has_any(["自然", "假", "假脸", "自然感", "不自然", "僵硬"]),
        "mechanism": has_any(["PLLA", "聚左旋乳酸", "CMC", "甘露醇", "胶原", "再生", "代谢", "分解", "长效", "过程"]),
        "differentiation": has_any(["差异", "区别", "专利", "工艺", "微球", "粒径", "双粒径", "双规格", "优势", "卖点", "背书", "质价比", "价值"]),
        "indications": has_any(["适应症", "皱纹", "鼻唇沟", "纠正", "中重度"]),
        "spec": has_any(["规格", "mg/瓶", "368mg", "184mg", "粒径", "注射层次", "平均粒径"]),
    }


def score_knowledge_item(item: dict, intent_flags: dict) -> int:
    category = normalize_text(item.get("category") or "")
    title = normalize_text(item.get("title") or "")
    content = normalize_text(item.get("content") or "")

    score = 0

    def bump_if(keyword_list, bonus):
        nonlocal score
        for kw in keyword_list:
            if kw and (kw in title or kw in content or kw in category):
                score += bonus

    # Category/title keywords provide stronger hints than raw content.
    if intent_flags.get("price"):
        score += 3 if ("优势" in category or "卖点" in category) else 0
        bump_if(["价值", "优势", "卖点", "背书", "质价比"], 2)

    if intent_flags.get("safety"):
        bump_if(["安全", "风险", "无菌", "合规", "无细胞毒", "NMPA"], 3)
        score += 2 if "安全" in category else 0

    if intent_flags.get("recovery"):
        bump_if(["恢复", "肿胀", "消肿", "影响", "迟发"], 2)

    if intent_flags.get("naturalness"):
        bump_if(["自然", "假", "自然感", "不自然", "胶原再生"], 2)

    if intent_flags.get("mechanism"):
        bump_if(["PLLA", "胶原", "再生", "代谢", "分解", "长效"], 3)

    if intent_flags.get("differentiation"):
        bump_if(["专利", "工艺", "微球", "粒径", "双粒径", "双规格", "差异", "背书"], 3)

    if intent_flags.get("indications"):
        bump_if(["适应", "皱纹", "鼻唇沟", "纠正"], 3)

    if intent_flags.get("spec"):
        bump_if(["规格", "mg/瓶", "粒径", "注射层次", "平均粒径"], 3)

    # Weak fallback: any overlap in content words helps ranking.
    # Keep it small to avoid noise.
    overlap_tokens = ["PLLA", "CMC", "甘露醇", "NMPA", "无菌", "粒径", "胶原"]
    for tok in overlap_tokens:
        if tok and tok in title:
            score += 1
        if tok and tok in content:
            score += 1

    return score


def select_knowledge_ids_by_intent(client: TBSClient, drug_id: str, scenario_pack: dict, top_n: int = 4):
    """
    When user didn't provide productKnowledge, select the most relevant existing knowledge
    by matching intent from scenario text against knowledge title/content/category.
    """
    intent_flags = infer_intent_keywords(scenario_pack or {})

    # Fetch candidate knowledge list for this drug.
    path = f"/api/v1/resources/knowledge?drug_id={drug_id}"
    try:
        payload = client.request_json("GET", path)
    except Exception:
        return [], {
            "mode": "intent_select",
            "inferred_intents": [k for k, v in intent_flags.items() if v],
            "covered_intents": [],
            "low_coverage_intents": [k for k, v in intent_flags.items() if v],
            "error": "failed_to_fetch_knowledge_list",
        }

    existing = extract_data(payload)
    if isinstance(existing, dict) and "data" in existing:
        existing = existing["data"]
    if not isinstance(existing, list):
        inferred_true_intents = [k for k, v in intent_flags.items() if v]
        return [], {
            "mode": "intent_select",
            "inferred_intents": inferred_true_intents,
            "covered_intents": [],
            "low_coverage_intents": inferred_true_intents,
            "error": "knowledge_list_not_a_list",
        }

    scored = []
    for it in existing:
        if not isinstance(it, dict):
            continue
        s = score_knowledge_item(it, intent_flags)
        scored.append((s, it.get("id")))

    # Sort descending by score.
    scored.sort(key=lambda x: x[0], reverse=True)

    # If everything scores 0, don't force wrong picks.
    max_s = 0
    for s, kid in scored:
        if kid is not None:
            max_s = max(max_s, int(s or 0))
    if max_s <= 0:
        inferred_true_intents = [k for k, v in intent_flags.items() if v]
        return [], {
            "mode": "intent_select",
            "inferred_intents": inferred_true_intents,
            "covered_intents": [],
            "low_coverage_intents": inferred_true_intents,
            "note": "no_relevant_knowledge_scored",
        }

    # Otherwise take top_n even if some are 0, to keep enough knowledge coverage.
    best = [kid for s, kid in scored[:top_n] if kid is not None]
    # Build coverage report (heuristic) to decide whether user might want to provide extra productKnowledge.
    # Only report intents that are inferred as true in this scenario.
    intent_flags = infer_intent_keywords(scenario_pack or {})
    intent_keywords_map = {
        "price": ["优势", "卖点", "价值", "质价比", "背书", "买贵", "溢价"],
        "safety": ["安全", "风险", "无菌", "合规", "NMPA", "无细胞毒"],
        "recovery": ["恢复", "肿胀", "消肿", "迟发", "影响", "恢复期"],
        "naturalness": ["自然", "假", "自然感", "不自然", "胶原再生", "假脸", "僵硬"],
        "mechanism": ["PLLA", "聚左旋乳酸", "CMC", "甘露醇", "胶原", "再生", "代谢", "分解", "长效", "过程"],
        "differentiation": ["差异", "区别", "专利", "工艺", "微球", "粒径", "双粒径", "双规格", "优势", "背书"],
        "indications": ["适应", "皱纹", "鼻唇沟", "纠正", "中重度"],
        "spec": ["规格", "mg/瓶", "粒径", "注射层次", "平均粒径"],
    }

    def item_matches_intent(it: dict, intent_key: str) -> bool:
        if not isinstance(it, dict):
            return False
        title = normalize_text(it.get("title") or "")
        content = normalize_text(it.get("content") or "")
        category = normalize_text(it.get("category") or "")
        hay = category + " " + title + " " + content
        for kw in intent_keywords_map.get(intent_key, []):
            if kw and (kw in hay):
                return True
        return False

    selected_items = [it for it in existing if isinstance(it, dict) and str(it.get("id")) in set([str(x) for x in best])]

    covered_intents = []
    for k, v in intent_flags.items():
        if not v:
            continue
        # If any selected knowledge matches the intent heuristically, consider covered.
        if any(item_matches_intent(it, k) for it in selected_items):
            covered_intents.append(k)

    inferred_true_intents = [k for k, v in intent_flags.items() if v]
    low_coverage_intents = [k for k in inferred_true_intents if k not in covered_intents]

    report = {
        "mode": "intent_select",
        "inferred_intents": inferred_true_intents,
        "covered_intents": covered_intents,
        "low_coverage_intents": low_coverage_intents,
    }

    return best, report


def _safe_get(d: dict, path: list):
    cur = d
    for k in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def build_doctor_only_context_from_scenario_pack(scenario_pack: dict) -> str:
    """
    Build publish-ish markdown for the system 'AI角色画像设定' field from scenarioPack.
    Fallback when apiDraft.scenes.doctor_only_context is missing or too thin.
    """
    sp = scenario_pack or {}
    scene_bg = (_safe_get(sp, ["sceneBasic", "sceneBackground"]) or sp.get("sceneBackground") or "").strip()
    core_concern = (_safe_get(sp, ["criticalInfo", "coreConcern"]) or sp.get("coreConcern") or "").strip()
    ai_role = (_safe_get(sp, ["roleSetup", "aiRoleTitle"]) or sp.get("aiRoleTitle") or "").strip()

    persona_base = _safe_get(sp, ["personaConfig", "personaBase"]) or {}
    persona_overlay = _safe_get(sp, ["personaConfig", "personaOverlay"]) or {}

    known = []
    if ai_role:
        known.append(f"- 你当前以“{ai_role}”身份参与对话")
    if scene_bg:
        known.append(f"- 场景背景：{scene_bg}")

    lines = ["## 已知背景"]
    lines.extend(known[:4] if known else ["- （待补充）"])

    lines += ["", "## 核心顾虑（仅1个核心顾虑）"]
    lines.append(f"- {core_concern}" if core_concern else "- （待补充：对方最在意的一个问题）")

    base_name = persona_base.get("name") if isinstance(persona_base, dict) else None
    role_type = persona_base.get("roleType") if isinstance(persona_base, dict) else None
    if base_name or role_type:
        lines += ["", "## 人设要点"]
        if base_name:
            lines.append(f"- 底座画像：{base_name}")
        if role_type:
            lines.append(f"- 角色类型：{role_type}")

    if isinstance(persona_overlay, dict) and persona_overlay:
        triggers = persona_overlay.get("triggers")
        sig = persona_overlay.get("signaturePhrases")
        qs = persona_overlay.get("questionStyle")
        lines += ["", "## 追问风格与触发器"]
        if qs:
            lines.append(f"- 追问风格：{str(qs).strip()}")
        if isinstance(triggers, list) and triggers:
            for t in triggers[:3]:
                if t:
                    lines.append(f"- 触发降温：{str(t).strip()}")
        if isinstance(sig, list) and sig:
            lines += ["", "## 常用句式（示例）"]
            for p in sig[:3]:
                if p:
                    lines.append(f"- {str(p).strip()}")

    return "\n".join(lines).strip() + "\n"


def _first_sentence(text: str, max_len: int = 120) -> str:
    t = (text or "").strip()
    if not t:
        return ""
    # Prefer Chinese sentence separators; fallback to first chunk.
    for sep in ["。", "！", "？", "；", ";", "\n"]:
        if sep in t:
            t = t.split(sep, 1)[0].strip()
            break
    return t[:max_len].strip()


def _extract_time_desc(scenario_pack: dict) -> str:
    """
    Time is required by contract/quality gates.
    - Prefer explicit dates found in scenario background/meta.
    - Otherwise use a safe relative time anchor to avoid fabricating a specific event date.
    """
    sp = scenario_pack or {}

    # Try common meta fields.
    meta = sp.get("meta")
    if isinstance(meta, dict):
        for k in ["timestamp", "date", "time"]:
            v = meta.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()

    # Old nested structure.
    scene_basic = sp.get("sceneBasic") if isinstance(sp.get("sceneBasic"), dict) else {}
    for v in [scene_basic.get("sceneBackground"), scene_basic.get("repBriefing")]:
        if isinstance(v, str) and v.strip():
            # YYYY年 / YYYY-MM / YYYY/MM etc.
            m = re.search(r"(\d{4}年\s*\d{1,2}月\s*\d{1,2}日|\d{4}年\s*\d{1,2}月|\d{4}[-/]\d{1,2}[-/]\d{1,2})", v)
            if m:
                return m.group(1).strip()

    # Current simplified structure: scenarioPack.background.
    bg = sp.get("background") if isinstance(sp.get("background"), str) else ""
    m = re.search(r"(\d{4}年\s*\d{1,2}月\s*\d{1,2}日|\d{4}年\s*\d{1,2}月|\d{4}[-/]\d{1,2}[-/]\d{1,2})", bg)
    if m:
        return m.group(1).strip()

    # Relative anchor: accurate as "this conversation time".
    return "在本次沟通当下"


def _ensure_nonempty_str(v) -> str:
    return (v if isinstance(v, str) else "").strip()


def build_rep_briefing_from_scenario_pack(scenario_pack: dict, api_draft_scenes: dict, api_draft_doctors: dict) -> str:
    """
    Enforce rep_briefing quality:
    - time, location, department
    - doctor/product current status
    - medical rep objective
    - communication entry point
    """
    sp = scenario_pack or {}
    scenes = api_draft_scenes or {}
    doc = api_draft_doctors or {}

    # Time/Location/Department.
    time_desc = _extract_time_desc(sp)
    location = _ensure_nonempty_str(scenes.get("location") or sp.get("location"))
    department = _ensure_nonempty_str(scenes.get("departmentName") or scenes.get("department") or sp.get("department"))
    product = _ensure_nonempty_str(scenes.get("drugName") or scenes.get("drug") or sp.get("product"))

    # Doctor status and name/title.
    doctor_name = _ensure_nonempty_str(doc.get("name") or (sp.get("roleSetup", {}).get("ai", {}).get("name") if isinstance(sp.get("roleSetup"), dict) else None))
    doctor_title = _ensure_nonempty_str(doc.get("title") or "")
    doctor_persona = _ensure_nonempty_str(doc.get("persona") or doc.get("persona_config") or doc.get("personaConfig") or "")
    doctor_persona_short = _first_sentence(doctor_persona, max_len=160)

    # Product status comes from scenario background/goals.
    bg = _ensure_nonempty_str(sp.get("background") or _ensure_nonempty_str(sp.get("sceneBackground")))
    product_status_short = _first_sentence(bg, max_len=160)
    if not doctor_persona_short and bg:
        # If doctor persona is missing, derive a "doctor/product current status" snippet from background.
        doctor_persona_short = product_status_short

    # Rep objective and entry point.
    rep_objective_raw = sp.get("goals") or sp.get("trainingGoal") or ""
    if not rep_objective_raw and isinstance(sp.get("criticalInfo"), dict):
        rep_objective_raw = sp.get("criticalInfo", {}).get("trainingGoal") or ""
    rep_objective = _ensure_nonempty_str(rep_objective_raw)

    entry_point_raw = sp.get("concerns") or sp.get("coreConcern") or ""
    if not entry_point_raw and isinstance(sp.get("criticalInfo"), dict):
        entry_point_raw = sp.get("criticalInfo", {}).get("coreConcern") or ""
    entry_point_raw = _ensure_nonempty_str(entry_point_raw)
    entry_point = _first_sentence(entry_point_raw, max_len=120)

    # Enforce minimal non-empty required dimensions.
    missing = []
    if not time_desc:
        missing.append("时间")
    if not location:
        missing.append("地点")
    if not department:
        missing.append("科室")
    if not product:
        missing.append("产品")
    if not doctor_persona_short:
        missing.append("医生与产品现状")
    if not rep_objective:
        missing.append("医药代表目标")
    if not entry_point:
        missing.append("沟通切入点")
    if missing:
        raise RuntimeError(f"rep_briefing quality gate missing required fields: {','.join(missing)}")

    def _truncate(s: str, max_len: int) -> str:
        s = (s or "").strip()
        if len(s) <= max_len:
            return s
        if max_len <= 3:
            return s[:max_len]
        return s[: max_len - 3] + "..."

    # Hard budget for "<= 180 Chinese characters" requirement.
    # We prefer truncating long variable parts rather than dropping key dimensions.
    limit = 180

    entry_suffix_full = "沟通切入点聚焦{entry}，先承接关切，再给出可核验要点，并提出轻量下一步。"
    entry_suffix_short = "沟通切入点聚焦{entry}，先承接关切，再给要点并约定下一步。"

    def _clean_fragment(text: str) -> str:
        """Remove trailing punctuation to avoid duplicated separators like '。；'."""
        return re.sub(r"[。；;，、,\s]+$", "", (text or "").strip())

    def _compose(dp: str, ps: str, obj: str, entry: str, use_short_suffix: bool) -> str:
        entry_suffix = entry_suffix_short if use_short_suffix else entry_suffix_full
        doctor_identity = f"{doctor_name}{'（' + doctor_title + '）' if doctor_title else ''}"
        dp_clean = _clean_fragment(dp)
        ps_clean = _clean_fragment(ps or dp)
        obj_clean = _clean_fragment(obj)
        entry_clean = _clean_fragment(entry)

        # If product status semantically equals persona summary, skip duplicate clause.
        status_clause = ""
        if normalize_text(ps_clean) and normalize_text(ps_clean) != normalize_text(dp_clean):
            status_clause = f"{product}现状为{ps_clean}；"

        return (
            f"{time_desc}，在{location}的{department}，"
            f"{doctor_identity}当前关注点是{dp_clean}；"
            f"{status_clause}"
            f"代表目标是{obj_clean}；"
            f"{entry_suffix.format(entry=entry_clean)}"
        )

    # Try full first; if too long, progressively truncate variable parts.
    full_text = _compose(doctor_persona_short, product_status_short or doctor_persona_short, rep_objective, entry_point, use_short_suffix=False)
    if len(full_text) <= limit:
            return full_text.strip() + "\n"

    # Truncate strategy for short form.
    dp_max, ps_max, obj_max, entry_max = 45, 45, 35, 35
    while True:
        short_text = _compose(
            dp=_truncate(doctor_persona_short, dp_max),
            ps=_truncate(product_status_short or doctor_persona_short, ps_max),
            obj=_truncate(rep_objective, obj_max),
            entry=_truncate(entry_point, entry_max),
            use_short_suffix=True,
        )
        if len(short_text) <= limit or (dp_max <= 15 and ps_max <= 15 and obj_max <= 15 and entry_max <= 15):
            return short_text[:limit].rstrip() + "\n"
        dp_max -= 5
        ps_max -= 5
        obj_max -= 5
        entry_max -= 5


def build_rep_briefing_relaxed(scenario_pack: dict, api_draft_scenes: dict, api_draft_doctors: dict) -> str:
    """
    Relaxed fallback when strict quality gates cannot be satisfied.
    Ensures rep_briefing is never empty while still avoiding fabricated details.
    """
    sp = scenario_pack or {}
    scenes = api_draft_scenes or {}
    doc = api_draft_doctors or {}

    time_desc = _extract_time_desc(sp)
    location = _ensure_nonempty_str(scenes.get("location") or sp.get("location")) or "当前沟通场景"
    department = _ensure_nonempty_str(scenes.get("departmentName") or scenes.get("department") or sp.get("department")) or "相关科室"
    product = _ensure_nonempty_str(scenes.get("drugName") or scenes.get("drug") or sp.get("product") or sp.get("productName")) or "目标产品"
    doctor_name = _ensure_nonempty_str(doc.get("name")) or "对方客户"
    background = _ensure_nonempty_str(scenes.get("background") or sp.get("background") or sp.get("sceneBackground"))
    concern = _first_sentence(_ensure_nonempty_str(sp.get("concerns") or sp.get("coreConcern")), max_len=40) or "价值、安全与恢复影响"

    if background:
        bg_short = _first_sentence(background, max_len=80)
        return (
            f"{time_desc}，在{location}的{department}，"
            f"围绕{product}开展沟通。当前对话对象为{doctor_name}，"
            f"其核心顾虑聚焦{concern}，并基于“{bg_short}”推进本轮沟通。"
        ).strip() + "\n"

    return (
        f"{time_desc}，在{location}的{department}，围绕{product}进行沟通，"
        f"对话对象为{doctor_name}，本轮优先回应其对{concern}的关切并推进下一步。"
    ).strip() + "\n"


def _doctor_only_context_quality_ok(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False

    doctor_required = [
        "## 已知背景",
        "## 核心顾虑",
        "## 今日状态",
        "## 终止条件",
        "必须等待对方回答",
        "只有你可以标记对话结束",
        "## 对话结束规则（关键）",
        "## 追问路径（强制）",
        "只追问场景注入/已给出的参考资料",
        "## 输出长度控制",
        "## 单问原则",
        "## 提问限制",
        "只能基于已注入的参考资料/场景信息提问",
        "[对话结束]",
    ]
    if not all(r in t for r in doctor_required):
        return False
    # Require explicit output length constraints to avoid vague "保持简练".
    if not re.search(r"30\s*[-~至]\s*50\s*字|30-50字|30-50 字", t):
        return False
    return True

def build_doctor_only_context_from_simple_scenario_pack(scenario_pack: dict, api_draft_doctors: dict, api_draft_scenes: dict = None) -> str:
    """
    Build doctor_only_context in your requested format:
    - # 行为规范 ... (4 parts)
    - # 当前场景背景
    - 终止条件 / 对话结束规则 / 重要提醒
    """
    sp = scenario_pack or {}
    doc = api_draft_doctors or {}
    scenes = api_draft_scenes or {}

    # Universal doctor template (non-BP).
    department = _ensure_nonempty_str(sp.get("department") or scenes.get("departmentName") or scenes.get("department")) or "相关科室"
    location = _ensure_nonempty_str(sp.get("location") or scenes.get("location")) or "当前沟通场景"
    product = _ensure_nonempty_str(sp.get("product") or sp.get("productName") or scenes.get("drugName") or scenes.get("drug")) or "目标产品"

    doctor_persona = _ensure_nonempty_str(doc.get("persona") or doc.get("persona_config") or doc.get("personaConfig") or "")
    doctor_persona_short = _first_sentence(doctor_persona, max_len=220)

    concerns = _ensure_nonempty_str(sp.get("concerns") or sp.get("coreConcern") or "")
    core_concern = _first_sentence(concerns, max_len=220) or "价值、安全性与恢复影响"
    bg = _ensure_nonempty_str(sp.get("background") or scenes.get("background") or "")
    time_desc = _extract_time_desc(sp)

    known_bg = bg if bg else f"科室与场景信息：科室={department}；地点={location}；推广产品={product}。"

    return "\n".join(
        [
            "## 已知背景",
            f"- {known_bg}",
            "",
            "## 核心顾虑（仅1个核心顾虑）",
            f"- {core_concern}",
            "",
            "## 今日状态",
            f"- 当前时间：{time_desc}",
            f"- 你的态度：{doctor_persona_short or '愿意沟通，但强调合规与逻辑清楚'}",
            "",
            "## 终止条件",
            "**核心规则**：提问或提出要求后必须等待对方回答，在对方回答后再判断是否结束对话。",
            "",
            "**结束对话的条件**（对方回答后判断）：",
            "- 夸大疗效或绝对化承诺",
            "- 回避核心问题",
            "- 不尊重对方的关切",
            "- 推销味过重（过度承诺、夸大效果；注意：专业使用建议不算推销）",
            "",
            "## 对话结束规则（关键）",
            "- **唯一标记**：只有你可以标记对话结束，在回复末尾追加 [对话结束]。",
            "- **禁止提问**：一旦决定结束对话，绝对不能再提问或提出任何要求。必须检查并删除回复中所有的问号（？）或疑问句。",
            "- **互斥执行检查**：若本轮包含任何问句，则必须不输出 [对话结束]。",
            "- **终止流程**：使用陈述句/结束语表达结束，严禁在最后一轮再提问。",
            "",
            "## 追问路径（强制）",
            "- 优先关注：只追问场景注入/已给出的参考资料中与核心顾虑相关的信息要点；若资料不覆盖“剂型/专利/起效时间”等细节，则转为追问可核验的适用条件、合规边界或需要回去核对的口径来源。",
            "",
            "## 输出长度控制",
            "- 每次回复控制在30-50字左右，保持真实医生沟通的自然简洁；避免一次提出过多问题。",
            "",
            "## 单问原则",
            "- 每轮最多只能包含1个问号（问号≤1）。如果想到第二个问题，必须留到下一轮再问。",
            "",
            "## 提问限制",
            "- 只能基于已注入的参考资料/场景信息提问，禁止询问未提供的具体数值、技术参数或研究/对比结论。",
            "- 若参考资料仅有定性描述，不询问具体数值或定量结论。",
            "- 当出现信息缺口且无法从参考资料判断时，表述为需要回去核对资料或请对方补充口径后再讨论。",
            "",
            "## 输出格式（强制）",
            "- 只输出纯文本对话内容，不要包含动作描述。",
            "- 禁止使用任何额外格式化标记（如加粗/斜体/标题/代码符号）。如需强调使用自然措辞或中文引号。",
            "- 禁止出现具体姓名或可识别称呼，只使用“我”“你”或职业称谓。",
        ]
    ).strip() + "\n"


def build_coach_only_context_from_scenario_pack(scenario_pack: dict) -> str:
    """
    Build publish-ish markdown for the system '教练专属设定' field from scenarioPack.
    Fallback when apiDraft.scenes.coach_only_context is missing or too thin.
    """
    sp = scenario_pack or {}
    training_goal = (_safe_get(sp, ["criticalInfo", "trainingGoal"]) or sp.get("trainingGoal") or "").strip()
    core_concern = (_safe_get(sp, ["criticalInfo", "coreConcern"]) or sp.get("coreConcern") or "").strip()
    product = (_safe_get(sp, ["product"]) or sp.get("product") or sp.get("drugName") or sp.get("drug") or "").strip()
    learner_role = (_safe_get(sp, ["roleSetup", "learnerRoleTitle"]) or sp.get("learnerRoleTitle") or "学习者").strip()
    scene_type = (
        _safe_get(sp, ["criticalInfo", "sceneType"])
        or _safe_get(sp, ["criticalInfo", "contextType"])
        or sp.get("sceneType")
        or sp.get("contextType")
        or ""
    )
    scene_type = str(scene_type or "").strip().lower()

    # Product facts in coach context must come from scene/background injection; avoid hardcoding drug-specific claims.
    product_brief = _first_sentence((_safe_get(sp, ["background"]) or sp.get("background") or "").strip(), max_len=160)
    if not product_brief:
        product_brief = f"产品：{product or '（待补充）'}（以场景注入的产品知识为准）"

    content_name = product or "该内容"

    # NOTE: We intentionally do NOT infer "what sections to include" via keywords in free text.
    # Use a structured scene type signal (sceneType/contextType) when available.
    is_training = scene_type in {"training", "enablement", "internal_training", "system_training", "system-enablement", "system"}

    lines = ["## 期望学习者行为"]
    if is_training:
        lines.append("- 开场与目标：说明培训/演示范围，征得对方同意，明确本次要解决的问题与预期产出。")
        lines.append("- 结构化讲解：按步骤/模块讲清流程与关键概念，遇到疑点先澄清再继续。")
        lines.append(f"- 关键信息点：准确说明{content_name}的用途/流程/关键差异点（以场景注入资料为准），不编造证据与结论。")
        if training_goal:
            lines.append(f"- 目标对齐：{training_goal}")
        lines.append("- 主动确认理解：用简短提问或复述确认对方是否理解关键步骤与注意事项。")
        lines.append("- 注意事项与常见误区（必须）：只陈述场景注入资料已覆盖的注意点；未提供的细节要明确“需要回去核对资料”，禁止编造。")
        lines.append("- 练习/检查点（必须）：给出1-3个可执行检查点（如：当场演示一次、复盘一次关键步骤、用清单核对必填项）。")
        lines.append("- 下一步行动：给出可选的后续动作（如：补充材料、二次培训、答疑），不强制要求具体日期时间。")
    else:
        lines.append("- 自然开场：以请教或分享切入，先征得对方同意，说明想简单交流与对方最关心点相关内容。")
        lines.append("- 倾听与回应：认真听对方对核心顾虑的看法，用简短语言表达理解与共情。")
        lines.append(f"- 简要信息介绍：准确说明{content_name}的用途与关键差异点（以场景注入资料为准），不编造证据与结论。")
        if training_goal:
            lines.append(f"- 目标对齐：{training_goal}")
        lines.append("- 探寻顾虑：围绕“{核心顾虑}”探寻对方真实关注点（可包括合规边界、可操作性、资源约束与风险点等维度）。".replace("{核心顾虑}", core_concern or "核心顾虑"))
        lines.append("- 讨论效果与边界：在对方愿意了解的前提下，简要说明可预期的效果与适用条件，并强调以场景注入口径为准。")
        lines.append("- 风险与边界（必须）：主动说明风险边界、适用条件与不适用情况；若场景未注入风险信息，则必须承认信息缺口并回到“说明书/指南/合规口径需核对”，禁止编造。")
        lines.append("- 尝试缔结（必须给出具体时间）：在尊重对方的前提下，提出下一步并给出具体时间点，例如：“下周三/下次会议前，我准备要点资料并约定再对齐一次口径与适用场景”。")

    lines += ["", "## 终止条件"]
    lines.append("- 夸大承诺或绝对化表达。")
    lines.append("- 回避核心问题或口径反复。")
    lines.append("- 不尊重对方专业判断或明显逼迫推进。")

    return "\n".join(lines).strip() + "\n"


def _coach_only_context_quality_ok(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    base_required = [
        "## 期望学习者行为",
        "## 终止条件",
    ]
    if not all(r in t for r in base_required):
        return False

    # Accept either template:
    # - "go-to-market / sales" flavor: must include risk+close sections
    # - "training" flavor: must include training-specific required sections
    gtm_required = ["风险与边界", "尝试缔结"]
    training_required = ["注意事项与常见误区", "练习/检查点"]
    return all(r in t for r in gtm_required) or all(r in t for r in training_required)


def _coach_only_context_matches_scene_type(scenario_pack: dict, coach_only_context: str) -> bool:
    sp = scenario_pack or {}
    scene_type = (
        _safe_get(sp, ["criticalInfo", "sceneType"])
        or _safe_get(sp, ["criticalInfo", "contextType"])
        or sp.get("sceneType")
        or sp.get("contextType")
        or ""
    )
    scene_type = str(scene_type or "").strip().lower()
    is_training = scene_type in {"training", "enablement", "internal_training", "system_training", "system-enablement", "system"}

    t = (coach_only_context or "").strip()
    if not t:
        return False

    gtm_markers = ["风险与边界", "尝试缔结"]
    training_markers = ["注意事项与常见误区", "练习/检查点"]

    if is_training:
        return all(m in t for m in training_markers)
    return all(m in t for m in gtm_markers)


def create_knowledge_if_needed_by_dedup(
    client: TBSClient,
    drug_id,
    knowledge_draft: dict,
    category: str,
    content_fingerprint: str = None,
    dry_run: bool = False,
):
    # Fetch existing knowledge and try to match by normalized-content fingerprint.
    # Endpoint supports: GET /api/v1/resources/knowledge?drug_id=...&category=...
    # (Query params aren't fully specified in the reference doc, so we keep best-effort.)
    def fetch_existing():
        path = f"/api/v1/resources/knowledge?drug_id={drug_id}"
        if category:
            path += f"&category={urllib.parse.quote(category)}"
        payload = client.request_json("GET", path)
        return extract_data(payload)

    try:
        existing = fetch_existing()
    except Exception:
        existing = []

    if isinstance(existing, dict) and "data" in existing:
        existing = existing["data"]
    if not isinstance(existing, list):
        existing = []

    title = knowledge_draft.get("title") or ""
    content = knowledge_draft.get("content") or ""
    content_fp = content_fingerprint or fingerprint_sha256_of_text(content)

    # Match existing by fingerprint of content.
    for it in existing:
        it_id = guess_entity_id(it)
        it_content = it.get("content") if isinstance(it, dict) else None
        it_content = it_content if it_content is not None else it.get("text") if isinstance(it, dict) else None
        it_fp = fingerprint_sha256_of_text(it_content or "")
        if it_id and it_fp == content_fp:
            return it_id

    # Not found => create
    if dry_run:
        return None

    body = {
        "drug_id": drug_id,
        "category": category,
        "title": title,
        "content": content,
    }
    resp = client.request_json("POST", "/api/v1/admin/basic/knowledge", body=body)
    data = extract_data(resp)
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        default=os.path.join(_RUNTIME_DIR, "scenario_draft.json"),
        help="Path to scenario_draft.json (or apiDraft JSON). Use '-' to read draft JSON from stdin.",
    )
    ap.add_argument("--scene-id", default=None, help="If provided, skip scene creation and only generate snapshot+publish for this scene.")
    ap.add_argument("--base-url", default=os.environ.get("TBS_BASE_URL", "https://sg-tbs-manage.mediportal.com.cn"))
    ap.add_argument("--access-token", default=None)
    ap.add_argument("--insecure-ssl", action="store_true", help="Skip SSL certificate verification (staging only).")
    ap.add_argument("--persisted-ids", default=os.path.join(_RUNTIME_DIR, "P1_persisted_ids.md"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strict-param-only", action="store_true", help="Disable all fallback/auto-rebuild behavior.")
    args = ap.parse_args()
    strict_param_only = True if os.environ.get("TBS_STRICT_PARAM_ONLY", "1") == "1" else bool(args.strict_param_only)

    env_token, _ = resolve_access_token()
    access_token = (args.access_token or env_token or "").strip()
    if not access_token:
        raise SystemExit("Missing --access-token / env XG_USER_TOKEN")

    client = TBSClient(
        base_url=args.base_url,
        access_token=access_token,
        insecure_ssl=bool(args.insecure_ssl),
    )

    if args.input == "-":
        raw = sys.stdin.read()
        if not raw.strip():
            raise SystemExit("Missing draft JSON on stdin (use --input -).")
        draft = json.loads(raw)
    else:
        with open(args.input, "r", encoding="utf-8") as f:
            draft = json.load(f)

    api_draft = draft.get("apiDraft") or {}
    scenario_pack = draft.get("scenarioPack") or {}

    api_draft_doctors_raw = api_draft.get("doctors") or {}
    api_draft_scenes_raw = api_draft.get("scenes") or {}

    # Normalize shapes:
    # - Some sessions write apiDraft.doctors/scenes as arrays (list[object])
    # - Others write them as dicts (object)
    api_draft_doctors = api_draft_doctors_raw
    if isinstance(api_draft_doctors_raw, list):
        api_draft_doctors = api_draft_doctors_raw[0] if api_draft_doctors_raw else {}

    api_draft_scenes = api_draft_scenes_raw
    if isinstance(api_draft_scenes_raw, list):
        api_draft_scenes = api_draft_scenes_raw[0] if api_draft_scenes_raw else {}

    resolved_scene_ids = resolve_ids_for_scene(client, api_draft_scenes, dry_run=bool(args.dry_run))
    dep_id = resolved_scene_ids["department_id"]
    bd_id = resolved_scene_ids["business_domain_id"]
    drug_id = resolved_scene_ids["drug_id"]
    if not dep_id or not bd_id or not drug_id:
        raise RuntimeError(f"Failed to resolve ids: department={dep_id}, business_domain={bd_id}, drug={drug_id}")

    doctor_persona_id = create_doctor_if_missing(
        client,
        api_draft_doctors,
        scenario_pack=scenario_pack,
        dry_run=bool(args.dry_run),
    )
    if not doctor_persona_id and args.dry_run:
        raise RuntimeError("Dry-run: doctor persona not found; cannot create in dry-run.")

    # Knowledge ids:
    # - Prefer apiDraft.knowledge if present (user provided productKnowledge)
    # - Else: select best matching existing knowledge by intent from scenario_pack
    # - Final fallback: persisted IDs (for continuity in early integration stages)
    knowledge_ids = []

    # Support multiple keys for the knowledge draft array.
    knowledge_drafts = (
        api_draft.get("knowledge")
        or api_draft.get("apiDraftKnowledge")
        or api_draft.get("apiDraftKnowledges")
        or []
    )

    if isinstance(knowledge_drafts, dict) and "items" in knowledge_drafts:
        knowledge_drafts = knowledge_drafts["items"]

    if isinstance(knowledge_drafts, list) and knowledge_drafts:
        for kd in knowledge_drafts:
            if not isinstance(kd, dict):
                continue
            category = kd.get("category") or kd.get("knowledge_category") or ""
            content = kd.get("content") or ""
            fp = fingerprint_sha256_of_text(content)
            knowledge_id = create_knowledge_if_needed_by_dedup(
                client=client,
                drug_id=drug_id,
                knowledge_draft=kd,
                category=category,
                content_fingerprint=fp,
                dry_run=bool(args.dry_run),
            )
            if knowledge_id:
                knowledge_ids.append(str(knowledge_id))
    else:
        if strict_param_only:
            raise RuntimeError("strict-param-only: apiDraft.knowledge 必须由上游参数提供，禁止 fallback 选择。")
        knowledge_ids, knowledge_selection_report = select_knowledge_ids_by_intent(client, drug_id, scenario_pack, top_n=4)
        if not knowledge_ids:
            raise RuntimeError(
                "未命中可用产品知识。请先提供 knowledge 草案后重试："
                "每条需包含 drug(或drug_id)、category、title、content；"
                "系统将创建后自动记录并关联 knowledge_id。"
            )

    # Scene create
    scene_title = api_draft_scenes.get("title") or api_draft_scenes.get("name")
    rep_briefing = api_draft_scenes.get("rep_briefing") or ""
    doctor_only_context = api_draft_scenes.get("doctor_only_context") or ""
    coach_only_context = api_draft_scenes.get("coach_only_context") or ""
    if strict_param_only:
        if not scene_title:
            raise RuntimeError("strict-param-only: scenes.title/name 必填。")
        if not isinstance(rep_briefing, str) or not rep_briefing.strip():
            raise RuntimeError("strict-param-only: scenes.rep_briefing 必填，禁止文本兜底。")
        if not isinstance(doctor_only_context, str) or not doctor_only_context.strip():
            raise RuntimeError("strict-param-only: scenes.doctor_only_context 必填，禁止文本兜底。")
        if not isinstance(coach_only_context, str) or not coach_only_context.strip():
            raise RuntimeError("strict-param-only: scenes.coach_only_context 必填，禁止文本兜底。")

    # Fallback: build richer publish-ish markdown from scenarioPack if too thin.
    # The UI expects structured blocks; older drafts often store only short sentences.
    if not isinstance(doctor_only_context, str):
        doctor_only_context = str(doctor_only_context or "")
    if not isinstance(coach_only_context, str):
        coach_only_context = str(coach_only_context or "")

    # Enforce rep_briefing quality first (rep_briefing has no fallback previously).
    if not strict_param_only:
        try:
            need_rebuild = (
                not isinstance(rep_briefing, str)
                or not rep_briefing.strip()
                or ("【" in rep_briefing or "】" in rep_briefing)
                or "待补充" in rep_briefing
                or (len(rep_briefing) > 180)
                or (scenario_pack.get("location") and str(scenario_pack.get("location")) not in rep_briefing)
                or (scenario_pack.get("department") and str(scenario_pack.get("department")) not in rep_briefing)
                or (scenario_pack.get("product") and str(scenario_pack.get("product")) not in rep_briefing)
            )
            if need_rebuild:
                rep_briefing = build_rep_briefing_from_scenario_pack(scenario_pack, api_draft_scenes, api_draft_doctors)
        except Exception:
            rep_briefing = build_rep_briefing_relaxed(scenario_pack, api_draft_scenes, api_draft_doctors)

    # Doctor-only: enforce strict 3-section structure; rebuild when it doesn't match.
    if strict_param_only:
        if (not _doctor_only_context_quality_ok(doctor_only_context)):
            raise RuntimeError("strict-param-only: doctor_only_context 质量不达标，禁止自动重建。")
    else:
        if (
            (not doctor_only_context.strip())
            or ("待补充" in doctor_only_context)
            or (not _doctor_only_context_quality_ok(doctor_only_context))
        ):
            doctor_only_context = build_doctor_only_context_from_simple_scenario_pack(scenario_pack, api_draft_doctors, api_draft_scenes)
            if (not doctor_only_context.strip()) or ("##" not in doctor_only_context):
                doctor_only_context = build_doctor_only_context_from_scenario_pack(scenario_pack)

    if strict_param_only:
        if (not _coach_only_context_quality_ok(coach_only_context)) or (not _coach_only_context_matches_scene_type(scenario_pack, coach_only_context)):
            raise RuntimeError("strict-param-only: coach_only_context 质量不达标，禁止自动重建。")
    else:
        if (not coach_only_context.strip()) or (not _coach_only_context_quality_ok(coach_only_context)) or (not _coach_only_context_matches_scene_type(scenario_pack, coach_only_context)):
            coach_only_context = build_coach_only_context_from_scenario_pack(scenario_pack)

    # Optional: write back enforced fields into input draft.
    # This helps debugging and keeps downstream artefacts consistent.
    if not bool(args.dry_run):
        try:
            api_draft_scenes["rep_briefing"] = rep_briefing
            api_draft_scenes["doctor_only_context"] = doctor_only_context
            with open(args.input, "w", encoding="utf-8") as f:
                json.dump(draft, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # Rounds: derive from constraints if present; else default.
    rounds = 5
    constraints = scenario_pack.get("constraints") or {}
    try:
        mt = constraints.get("maxTurns") or constraints.get("max_turns")
        if isinstance(mt, int) and mt > 0:
            rounds = mt
        elif isinstance(mt, str) and mt.isdigit():
            rounds = int(mt)
    except Exception:
        pass

    persona_ids = [
        {
            "persona_id": str(doctor_persona_id),
            "difficulty": "medium",
            "is_default": True,
            "rounds": rounds,
        }
    ]

    scene_location = api_draft_scenes.get("location")
    if strict_param_only and (not isinstance(scene_location, str) or not scene_location.strip()):
        raise RuntimeError("strict-param-only: scenes.location 必填，禁止从 scenarioPack 兜底。")
    scene_body = {
        "title": scene_title,
        "department_id": dep_id,
        "drug_id": drug_id,
        "business_domain_id": bd_id,
        "location": scene_location if isinstance(scene_location, str) else (api_draft_scenes.get("location") or scenario_pack.get("location") or ""),
        "doctor_only_context": doctor_only_context,
        "coach_only_context": coach_only_context,
        "rep_briefing": rep_briefing,
        "persona_ids": persona_ids,
        "knowledge_ids": knowledge_ids,
        # status omitted => backend default
    }

    if args.dry_run:
        knowledge_report = knowledge_selection_report if "knowledge_selection_report" in locals() else None
        print(
            toon_encode(
                {
                    "ok": True,
                    "step": "tbs_write_executor",
                    "dryRun": True,
                    "resolvedIds": {
                        "department_id": str(dep_id),
                        "business_domain_id": str(bd_id),
                        "drug_id": str(drug_id),
                        "persona_id": str(doctor_persona_id),
                    },
                    "knowledgeIds": [str(x) for x in knowledge_ids],
                    "knowledgeSelectionReport": knowledge_report,
                    "sceneBodyPreview": scene_body,
                }
            )
        )
        return

    if args.scene_id:
        scene_id = str(args.scene_id)
    else:
        scene_resp = client.request_json("POST", "/api/v1/admin/scenes", body=scene_body)
        scene_data = extract_data(scene_resp)
        scene_id = None
        if isinstance(scene_data, dict):
            scene_id = scene_data.get("id") or scene_data.get("scene_id") or guess_entity_id(scene_data)
        else:
            scene_id = scene_data
        if not scene_id:
            raise RuntimeError(f"Scene creation failed: {scene_resp}")
        scene_id = str(scene_id)

    snapshot_resp = client.request_json(
        "POST",
        f"/api/v1/scenes/{scene_id}/snapshot",
        body={"doctor_id": int(str(doctor_persona_id))},
    )
    snapshot_data = extract_data(snapshot_resp)
    snapshot_id = None
    if isinstance(snapshot_data, dict):
        snapshot_id = snapshot_data.get("id") or snapshot_data.get("snapshot_id") or guess_entity_id(snapshot_data)
    else:
        snapshot_id = snapshot_data
    if not snapshot_id:
        raise RuntimeError(f"Snapshot creation failed: {snapshot_resp}")
    snapshot_id = str(snapshot_id)

    publish_resp = client.request_json("POST", f"/api/v1/snapshots/{snapshot_id}/publish", body={})

    out = {
        "scene_id": str(scene_id),
        "snapshot_id": str(snapshot_id),
        "publish_response": publish_resp,
        "knowledge_selection_report": knowledge_selection_report if "knowledge_selection_report" in locals() else None,
        "resolved": {
            "department_id": str(dep_id),
            "business_domain_id": str(bd_id),
            "drug_id": str(drug_id),
            "persona_id": str(doctor_persona_id),
            "knowledge_ids": [str(x) for x in knowledge_ids],
        },
    }
    print(toon_encode({"ok": True, "step": "tbs_write_executor", "result": out}))


if __name__ == "__main__":
    # Fix: urllib.parse is used in create_knowledge_if_needed_by_dedup; import here to keep top clean.
    import urllib.parse  # noqa: E402

    main()

