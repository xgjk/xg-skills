#!/usr/bin/env python3
"""
cms-push-skill 共享工具

集中以下逻辑，避免在 register/update/delete/publish 等脚本中重复实现：
  - parse_api_response: 解析平台 API 响应
  - get_token:          统一从环境变量获取 access-token
  - get_headers:        构造带鉴权头的请求头
"""

from __future__ import annotations

import os
import sys
import warnings
from typing import Optional

import requests

# 禁用 InsecureRequestWarning（因为 verify=False）
warnings.filterwarnings(
    "ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning
)

DEFAULT_API_BASE = "https://skills.mediportal.com.cn"
API_BASE = os.environ.get("CMS_API_BASE", DEFAULT_API_BASE).rstrip("/")

# token 环境变量优先级
_TOKEN_ENV_KEYS = ("XG_USER_TOKEN", "access-token", "ACCESS_TOKEN")


def parse_api_response(response: requests.Response, action: str) -> dict:
    """解析平台 API 响应，统一成功判定：resultCode 为 None 或 1 视为成功。"""
    data = response.json()
    if isinstance(data, dict) and data.get("resultCode") not in (None, 1):
        message = data.get("resultMsg") or data.get("detailMsg") or response.text
        raise RuntimeError(f"{action}失败: {message}")
    return data


def get_token(required: bool = True) -> Optional[str]:
    """从环境变量统一读取 access-token。

    required=True 时，缺失会输出友好提示并退出（提示先跑 cms-auth-skills）。
    """
    for key in _TOKEN_ENV_KEYS:
        token = os.environ.get(key)
        if token:
            return token
    if required:
        print("错误: 未找到 access-token", file=sys.stderr)
        print(
            "  请先通过 cms-auth-skills 取得 token，或手动设置环境变量："
            " XG_USER_TOKEN / access-token / ACCESS_TOKEN",
            file=sys.stderr,
        )
        sys.exit(1)
    return None


def get_headers(token: Optional[str] = None, json_body: bool = True) -> dict:
    """构造带鉴权头的请求头。token 缺省时自动从环境变量获取。"""
    if token is None:
        token = get_token(required=True)
    headers = {"access-token": token}
    if json_body:
        headers["Content-Type"] = "application/json"
    return headers
