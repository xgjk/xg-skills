"""
Shared TBS Admin HTTP helpers and resolve_ids_for_scene (business domain / department / drug).

Used by tbs_write_executor.py and preflight-tbs-master-data.py.
"""
import difflib
import json
import ssl
import urllib.error
import urllib.request


def safe_json_loads(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


def extract_data(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if "data" in payload:
            return payload["data"]
        if "result" in payload:
            return payload["result"]
    return payload


def guess_entity_name(item: dict):
    for k in ["name", "title", "department_name", "drug_name", "business_domain_name", "code"]:
        v = item.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def guess_entity_id(item: dict):
    for k in ["id", "department_id", "drug_id", "business_domain_id", "persona_id", "doctor_id", "knowledge_id"]:
        if k in item and isinstance(item[k], (str, int)) and str(item[k]).strip():
            return item[k]
    return None


def pick_best_match_id(items, target_name: str):
    if not items:
        return None
    target_name = (target_name or "").strip()
    if not target_name:
        return None

    for it in items:
        nm = guess_entity_name(it)
        if nm == target_name:
            return guess_entity_id(it)

    names = []
    id_by_name = {}
    for it in items:
        nm = guess_entity_name(it)
        if nm:
            names.append(nm)
            id_by_name[nm] = guess_entity_id(it)

    best = difflib.get_close_matches(target_name, names, n=1, cutoff=0.55)
    if not best:
        return None
    return id_by_name.get(best[0])


class TBSClient:
    def __init__(
        self,
        base_url: str,
        access_token: str,
        timeout_s: int = 30,
        insecure_ssl: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.timeout_s = timeout_s
        self.insecure_ssl = insecure_ssl

    def _headers(self):
        h = {
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        if self.access_token:
            h["access-token"] = self.access_token
        return h

    def request_json(self, method: str, path: str, body=None):
        url = self.base_url + path if path.startswith("/") else self.base_url + "/" + path
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url=url, method=method, headers=self._headers(), data=data)
        try:
            ssl_ctx = None
            if self.insecure_ssl:
                ssl_ctx = ssl._create_unverified_context()
            with urllib.request.urlopen(req, timeout=self.timeout_s, context=ssl_ctx) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                payload = safe_json_loads(raw)
                return payload if payload is not None else raw
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
            raise RuntimeError(f"HTTP {e.code} {method} {url}: {raw}") from e


def get_list(client: TBSClient, path: str):
    payload = client.request_json("GET", path)
    data = extract_data(payload)
    return data if isinstance(data, list) else []


def resolve_ids_for_scene(
    client: TBSClient,
    api_draft_scenes: dict,
    dry_run: bool = False,
    with_report: bool = False,
):
    """
    GET lists to match by name; POST create when no match (unless dry_run).
    If with_report, returns (ids_dict, report_dict); else ids_dict only.
    """
    dep_in = api_draft_scenes.get("department_id") or api_draft_scenes.get("departmentName") or ""
    bd_in = api_draft_scenes.get("business_domain_id") or api_draft_scenes.get("businessDomainName") or ""
    drug_in = api_draft_scenes.get("drug_id") or api_draft_scenes.get("drugName") or ""

    report: dict = {}

    def maybe_int_id(x):
        sx = str(x).strip()
        if sx.isdigit():
            return sx
        return None

    def try_get_list(path: str):
        try:
            return get_list(client, path)
        except Exception:
            return []

    def resolve_or_create_business_domain(bd_value: str):
        bd_value = (bd_value or "").strip()
        bd_id = maybe_int_id(bd_value)
        if bd_id:
            if with_report:
                report["business_domain"] = {"action": "matched_by_id", "id": bd_id, "input": bd_value}
            return bd_id

        business_domains = try_get_list("/api/v1/admin/basic/business-domains")

        if isinstance(bd_value, str) and bd_value and bd_value in ["医美", "医美业务", "医美推广"]:
            for it in business_domains:
                nm = guess_entity_name(it) or ""
                if nm.strip() in ["临床推广"]:
                    rid = str(guess_entity_id(it))
                    if with_report:
                        report["business_domain"] = {
                            "action": "matched",
                            "id": rid,
                            "input": bd_value,
                            "note": "alias_to_临床推广",
                        }
                    return rid

        bd_id = pick_best_match_id(business_domains, bd_value)
        if bd_id:
            if with_report:
                report["business_domain"] = {"action": "matched", "id": str(bd_id), "input": bd_value}
            return str(bd_id)

        if dry_run:
            if with_report:
                report["business_domain"] = {"action": "would_create", "id": None, "input": bd_value}
            return None

        body = {"name": bd_value}
        try:
            resp = client.request_json("POST", "/api/v1/admin/basic/business-domains", body=body)
            created = extract_data(resp)
            if created is not None:
                cid = str(created.get("id") if isinstance(created, dict) else created)
                if with_report:
                    report["business_domain"] = {"action": "created", "id": cid, "input": bd_value}
                return cid
        except RuntimeError as e:
            if "HTTP 409" not in str(e):
                raise

        business_domains = try_get_list("/api/v1/admin/basic/business-domains")
        bd_id = pick_best_match_id(business_domains, bd_value)
        out = str(bd_id) if bd_id else None
        if with_report:
            report["business_domain"] = {
                "action": "matched_after_conflict",
                "id": out,
                "input": bd_value,
            }
        return out

    def resolve_or_create_department(dep_value: str, bd_id: str):
        dep_value = (dep_value or "").strip()
        dep_id = maybe_int_id(dep_value)
        if dep_id:
            if with_report:
                report["department"] = {"action": "matched_by_id", "id": dep_id, "input": dep_value}
            return dep_id

        departments = try_get_list("/api/v1/admin/basic/departments")
        dep_id = pick_best_match_id(departments, dep_value)
        if dep_id:
            if with_report:
                report["department"] = {"action": "matched", "id": str(dep_id), "input": dep_value}
            return str(dep_id)

        if dry_run:
            if with_report:
                report["department"] = {"action": "would_create", "id": None, "input": dep_value}
            return None

        body = {"name": dep_value}
        if bd_id:
            body["business_domain_id"] = bd_id

        try:
            resp = client.request_json("POST", "/api/v1/admin/basic/departments", body=body)
            created = extract_data(resp)
            if created is not None:
                cid = str(created.get("id") if isinstance(created, dict) else created)
                if with_report:
                    report["department"] = {"action": "created", "id": cid, "input": dep_value}
                return cid
        except RuntimeError as e:
            if "HTTP 409" not in str(e):
                raise

        departments = try_get_list("/api/v1/admin/basic/departments")
        dep_id = pick_best_match_id(departments, dep_value)
        out = str(dep_id) if dep_id else None
        if with_report:
            report["department"] = {
                "action": "matched_after_conflict",
                "id": out,
                "input": dep_value,
            }
        return out

    def resolve_or_create_drug(drug_value: str, bd_id: str):
        """GET /api/v1/admin/basic/drugs then POST if missing."""
        drug_value = (drug_value or "").strip()
        drug_id = maybe_int_id(drug_value)
        if drug_id:
            if with_report:
                report["drug"] = {"action": "matched_by_id", "id": drug_id, "input": drug_value}
            return drug_id

        drugs = try_get_list("/api/v1/admin/basic/drugs")
        drug_id = pick_best_match_id(drugs, drug_value)
        if drug_id:
            if with_report:
                report["drug"] = {"action": "matched", "id": str(drug_id), "input": drug_value}
            return str(drug_id)

        if dry_run:
            if with_report:
                report["drug"] = {"action": "would_create", "id": None, "input": drug_value}
            return None

        body = {"name": drug_value}
        if bd_id:
            body["business_domain_id"] = bd_id

        try:
            resp = client.request_json("POST", "/api/v1/admin/basic/drugs", body=body)
            created = extract_data(resp)
            if created is not None:
                cid = str(created.get("id") if isinstance(created, dict) else created)
                if with_report:
                    report["drug"] = {"action": "created", "id": cid, "input": drug_value}
                return cid
        except RuntimeError as e:
            if "HTTP 409" not in str(e):
                raise

        drugs = try_get_list("/api/v1/admin/basic/drugs")
        drug_id = pick_best_match_id(drugs, drug_value)
        out = str(drug_id) if drug_id else None
        if with_report:
            report["drug"] = {
                "action": "matched_after_conflict",
                "id": out,
                "input": drug_value,
            }
        return out

    bd_id = resolve_or_create_business_domain(str(bd_in))
    dep_id = resolve_or_create_department(str(dep_in), bd_id)
    drug_id = resolve_or_create_drug(str(drug_in), bd_id)

    ids = {"department_id": dep_id, "business_domain_id": bd_id, "drug_id": drug_id}
    if with_report:
        return ids, report
    return ids
