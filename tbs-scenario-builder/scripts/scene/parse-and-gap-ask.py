#!/usr/bin/env python3
"""
scene / parse-and-gap-ask — 契约校验脚本（stdin JSON）。输出 TOON。
API_URL 须与 openapi/scene/parse-and-gap-ask.md 标题 URL 一致；本脚本不发起 HTTP。
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from auth_token import require_access_token
from toon_encoder import encode as toon_encode
from scenario_pack_normalizer import normalize_scenario_pack

API_URL = "https://scenario-builder.openclaw.internal/v1/scene/parse-and-gap-ask"
API_SOURCE_PREFIXES = tuple(
    p.strip() for p in os.environ.get("TBS_KB_SOURCE_PREFIXES", "api://,https://").split(",") if p.strip()
)
REQUIRE_KB_API = os.environ.get("TBS_REQUIRE_KB_API", "1") == "1"
KNOWLEDGE_API_PATH = os.environ.get("TBS_KNOWLEDGE_API_PATH", "/api/v1/admin/basic/knowledge")
_TOKEN_PAT = re.compile(r"[\s\-_:/（）()，,。；;、]+")

def _read_body():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)

def _ok(step, **extra):
    payload = {"ok": True, "step": step, **extra}
    print(toon_encode(payload))


def _norm_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return _TOKEN_PAT.sub("", text).lower()


def _char_ngrams(text: str, min_n: int = 2, max_n: int = 4) -> set[str]:
    norm = _norm_text(text)
    if not norm:
        return set()
    grams = set()
    length = len(norm)
    for n in range(min_n, max_n + 1):
        if length < n:
            continue
        for i in range(length - n + 1):
            grams.add(norm[i:i + n])
    return grams


def _iter_hit_phrases(hit: dict):
    for key in ("title", "category", "content", "summary"):
        v = hit.get(key)
        if isinstance(v, str) and v.strip():
            yield v.strip()
    for key in ("tags", "keywords", "coveredNeeds"):
        arr = hit.get(key)
        if not isinstance(arr, list):
            continue
        for item in arr:
            if isinstance(item, str) and item.strip():
                yield item.strip()


def _need_matches_hit(need: str, hit_texts: list[str]) -> bool:
    need_norm = _norm_text(need)
    if not need_norm:
        return False
    for t in hit_texts:
        t_norm = _norm_text(t)
        if not t_norm:
            continue
        if need_norm in t_norm or t_norm in need_norm:
            return True

    # 完全数据驱动：按字符 n-gram 相似度做弱语义匹配，不依赖硬编码业务词。
    need_grams = _char_ngrams(need_norm)
    if not need_grams:
        return False
    for t in hit_texts:
        hit_grams = _char_ngrams(t)
        if not hit_grams:
            continue
        overlap = len(need_grams & hit_grams)
        union = len(need_grams | hit_grams)
        if union == 0:
            continue
        jaccard = overlap / union
        if jaccard >= 0.30:
            return True
    return False


def _extract_product(body: dict) -> tuple[str | None, list]:
    # 1) explicit candidates from caller
    candidates = []
    for item in body.get("productCandidates") or []:
        if isinstance(item, str) and item.strip():
            candidates.append(item.strip())
        elif isinstance(item, dict):
            name = item.get("name")
            if isinstance(name, str) and name.strip():
                candidates.append(name.strip())

    # 2) candidates from knowledge API hits (optional)
    ksr = body.get("knowledgeSearchResult")
    if isinstance(ksr, dict):
        for hit in ksr.get("hits") or []:
            if not isinstance(hit, dict):
                continue
            pn = hit.get("productName")
            if isinstance(pn, str) and pn.strip():
                candidates.append(pn.strip())

    # de-dup keep order
    uniq = []
    seen = set()
    for c in candidates:
        if c in seen:
            continue
        seen.add(c)
        uniq.append(c)

    if uniq:
        # fallback choose first candidate
        return uniq[0], [{"value": uniq[0], "confidence": 0.75, "source": "param_or_api"}]

    return None, []


def _extract_fields(body: dict) -> dict:
    pack = {}
    candidates = {}
    parsed_fields = body.get("parsedFields")
    if isinstance(parsed_fields, dict):
        pack.update(parsed_fields)

    product, product_candidates = _extract_product(body)
    if product:
        pack["product"] = product
        candidates["product"] = product_candidates

    if candidates:
        pack["candidates"] = candidates

    return pack


def _coverage_from_search_result(search_result: dict, needs: list) -> tuple[str, list, list, list]:
    if not isinstance(search_result, dict):
        return "NOT_PROVIDED", [], [], list(needs)
    source_api = search_result.get("sourceApi")
    if REQUIRE_KB_API and source_api != KNOWLEDGE_API_PATH:
        return "NOT_PROVIDED", [], [], list(needs)
    hits = search_result.get("hits")
    if not isinstance(hits, list):
        return "NOT_PROVIDED", [], [], list(needs)

    covered = set()
    sources = []
    need_set = [n for n in needs if isinstance(n, str) and n.strip()]
    for h in hits:
        if not isinstance(h, dict):
            continue
        src = h.get("source")
        if not isinstance(src, str) or not src:
            continue
        if not src.startswith(API_SOURCE_PREFIXES):
            continue
        sources.append(src)
        score = h.get("score")
        if isinstance(score, (int, float)) and score < 0.5:
            continue
        hit_texts = list(_iter_hit_phrases(h))

        # 先保留显式 coveredNeeds（若有）。
        for item in h.get("coveredNeeds", []):
            if isinstance(item, str) and item.strip():
                covered.add(item.strip())

        # 再做语义匹配兜底：允许 need 与 title/category/tags 的同义表达互相命中。
        for need in need_set:
            if need in covered:
                continue
            if _need_matches_hit(need, hit_texts):
                covered.add(need)

    total = len(needs)
    covered_needs = [n for n in needs if n in covered]
    covered_count = len(covered_needs)
    if total == 0:
        return "NOT_PROVIDED", sources, [], []
    if covered_count == total:
        return "READY", sources, covered_needs, []
    if covered_count > 0:
        uncovered = [n for n in needs if n not in covered]
        return "PARTIAL", sources, covered_needs, uncovered
    return "NOT_PROVIDED", sources, [], list(needs)

def main():
    require_access_token()
    body = _read_body()
    user_text = (body.get("userText") or "").strip()
    if not user_text:
        print("错误: 缺少 userText", file=sys.stderr)
        sys.exit(2)
    if not isinstance(body.get("parsedFields"), dict):
        print("错误: 缺少 parsedFields（必须由上游参数传入，脚本不做文本兜底）", file=sys.stderr)
        sys.exit(2)
    existing = body.get("scenarioPack") if isinstance(body.get("scenarioPack"), dict) else {}
    pack = {**existing, **_extract_fields(body)}

    required = ["department", "product", "location", "doctorConcerns", "repGoal"]
    missing_fields = [k for k in required if not pack.get(k)]

    needs = pack.get("productKnowledgeNeeds", [])
    has_search_result = isinstance(body.get("knowledgeSearchResult"), dict)
    if needs and REQUIRE_KB_API and not has_search_result:
        print("错误: 检测到产品知识需求，但缺少 knowledgeSearchResult；请先调用产品知识API并回传结果", file=sys.stderr)
        sys.exit(2)

    status, sources, covered, uncovered = _coverage_from_search_result(body.get("knowledgeSearchResult"), needs)
    pack["productEvidenceStatus"] = status
    pack["productEvidenceSource"] = sources
    if status != "READY":
        missing_fields.append("productEvidenceSource")

    clarify_questions = []
    question_map = {
        "department": "主要沟通的是哪个科室或门诊？",
        "product": "这次要传递的是哪个具体产品或通用名？",
        "location": "本次拜访发生在什么机构与场景（门诊/病区/院外）？",
        "doctorConcerns": "主任当前最在意的是可及性、疗效证据，还是使用风险？",
        "repGoal": "本次沟通最想达成的一个结果是什么？",
        "productEvidenceSource": "为保证内容准确，请补充可核对的产品资料：说明书要点、关键研究摘要，或可公开访问的说明/文献链接（无需提供内部系统编号）。",
    }
    seen = set()
    for mf in missing_fields:
        if mf in seen:
            continue
        seen.add(mf)
        q = question_map.get(mf)
        if q:
            clarify_questions.append(q)

    pack = normalize_scenario_pack(pack)

    _ok(
        "parse-and-gap-ask",
        scenarioPack=pack,
        missingFields=sorted(seen),
        coveredNeeds=covered,
        uncoveredNeeds=uncovered,
        clarifyQuestions=clarify_questions,
        acceptedSourcePrefixes=list(API_SOURCE_PREFIXES),
    )

if __name__ == "__main__":
    main()
