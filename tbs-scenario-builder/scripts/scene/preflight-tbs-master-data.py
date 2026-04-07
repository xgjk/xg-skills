#!/usr/bin/env python3
"""
scene / preflight-tbs-master-data — 确认落库前：对 TBS 业务领域 / 科室 / 药品做 GET 匹配，不存在则 POST 创建。
与 tbs_write_executor 使用同一套 resolve_ids_for_scene 逻辑；stdout 为 TOON。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from auth_token import resolve_access_token
from toon_encoder import encode as toon_encode  # type: ignore[reportMissingImports]

from tbs_master_data_resolve import TBSClient, resolve_ids_for_scene

API_URL = "https://scenario-builder.openclaw.internal/v1/scene/preflight-tbs-master-data"


def _normalize_scenes(api_draft: dict):
    raw = api_draft.get("scenes") or {}
    if isinstance(raw, list):
        return raw[0] if raw else {}
    return raw if isinstance(raw, dict) else {}


def main():
    ap = argparse.ArgumentParser(description="Preflight TBS master data before persist-and-execute.")
    ap.add_argument(
        "--input",
        default=None,
        help="Path to draft JSON (default: stdin only if not set; use - for stdin file)",
    )
    ap.add_argument("--base-url", default=os.environ.get("TBS_BASE_URL", "https://sg-tbs-manage.mediportal.com.cn"))
    ap.add_argument("--access-token", default=None)
    ap.add_argument("--insecure-ssl", action="store_true", help="Skip SSL certificate verification.")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Only GET/list matching; do not POST create (report would_create).",
    )
    args = ap.parse_args()

    env_token, _ = resolve_access_token()
    access_token = (args.access_token or env_token or "").strip()
    if not access_token:
        print("错误: 缺少 access-token / XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)

    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            draft = json.load(f)
    else:
        raw = sys.stdin.read()
        if not raw.strip():
            print("错误: 请通过 stdin 传入草稿 JSON，或使用 --input", file=sys.stderr)
            sys.exit(2)
        draft = json.loads(raw)

    api_draft = draft.get("apiDraft") or {}
    api_draft_scenes = _normalize_scenes(api_draft)

    client = TBSClient(
        base_url=args.base_url,
        access_token=access_token,
        insecure_ssl=bool(args.insecure_ssl),
    )

    try:
        resolved, report = resolve_ids_for_scene(
            client,
            api_draft_scenes,
            dry_run=bool(args.dry_run),
            with_report=True,
        )
    except Exception as e:
        print(
            toon_encode(
                {
                    "ok": False,
                    "step": "preflight-tbs-master-data",
                    "message": str(e),
                }
            )
        )
        sys.exit(3)

    ok = bool(
        resolved.get("department_id")
        and resolved.get("business_domain_id")
        and resolved.get("drug_id")
    )
    print(
        toon_encode(
            {
                "ok": ok,
                "step": "preflight-tbs-master-data",
                "resolvedIds": resolved,
                "resolutionReport": report,
                "dryRun": bool(args.dry_run),
            }
        )
    )
    sys.exit(0 if ok else 4)


if __name__ == "__main__":
    main()
