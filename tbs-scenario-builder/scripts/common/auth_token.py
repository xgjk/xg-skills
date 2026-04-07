#!/usr/bin/env python3
"""
Shared access-token resolver for scenario-builder scripts.

Aligned with cms-tbs-training: token is sourced from env `XG_USER_TOKEN`.
"""
import os
import sys


def resolve_access_token():
    token = (os.environ.get("XG_USER_TOKEN") or "").strip()
    if token:
        return token, "env:XG_USER_TOKEN"
    return None, None


def require_access_token():
    token, _ = resolve_access_token()
    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        raise SystemExit(1)
    return token
