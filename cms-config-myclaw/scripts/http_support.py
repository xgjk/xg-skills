#!/usr/bin/env python3
from __future__ import annotations

import json
import ssl
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class RequestFailure(RuntimeError):
    pass


def stringify(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {'null', 'none', 'undefined'}:
        return None
    return text


def pick_non_empty(*values: Any) -> str | None:
    for value in values:
        text = stringify(value)
        if text:
            return text
    return None


def mask_secret(value: Any) -> str:
    text = stringify(value)
    if not text:
        return '***'
    if len(text) <= 6:
        return '***'
    return text[:6] + '***'


def extract_result_data(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get('data')
    return data if isinstance(data, dict) else {}


def extract_result_message(payload: dict[str, Any], fallback: str = '未知错误') -> str:
    return pick_non_empty(
        payload.get('resultMsg'),
        payload.get('detailMsg'),
        payload.get('message'),
        fallback,
    ) or fallback


def ensure_result_success(payload: dict[str, Any], fallback: str) -> None:
    code = payload.get('resultCode')
    if code in (0, 1, 200):
        return
    alt_code = payload.get('code')
    if alt_code == 200:
        return
    raise RequestFailure(f'{fallback}: {extract_result_message(payload, fallback)}')


def _build_url(url: str, params: dict[str, Any] | None) -> str:
    if not params:
        return url
    encoded = urlencode({key: value for key, value in params.items() if value is not None})
    if not encoded:
        return url
    separator = '&' if '?' in url else '?'
    return f'{url}{separator}{encoded}'


def _decode_json(raw_text: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise RequestFailure(f'接口返回了无法解析的 JSON: {exc}') from exc
    if not isinstance(payload, dict):
        raise RequestFailure('接口返回格式异常：期望 JSON object')
    return payload


def request_json(
    url: str,
    *,
    method: str = 'GET',
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 60,
    retries: int = 3,
) -> dict[str, Any]:
    request_url = _build_url(url, params)
    request_headers = {'Content-Type': 'application/json'}
    ssl_context = ssl._create_unverified_context()
    if headers:
        request_headers.update(headers)

    request_body = None
    if body is not None and method.upper() != 'GET':
        request_body = json.dumps(body, ensure_ascii=False).encode('utf-8')

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        request = Request(
            request_url,
            data=request_body,
            headers=request_headers,
            method=method.upper(),
        )
        try:
            with urlopen(request, timeout=timeout, context=ssl_context) as response:
                charset = response.headers.get_content_charset() or 'utf-8'
                raw_text = response.read().decode(charset, errors='replace')
            return _decode_json(raw_text)
        except HTTPError as exc:
            raw_text = exc.read().decode('utf-8', errors='replace')
            try:
                payload = _decode_json(raw_text)
                message = extract_result_message(payload, raw_text[:300] or str(exc))
            except RequestFailure:
                message = raw_text[:300] or str(exc)
            last_error = RequestFailure(f'请求失败 (HTTP {exc.code}): {message}')
            if 500 <= exc.code < 600 and attempt < retries:
                time.sleep(1)
                continue
            raise last_error from exc
        except URLError as exc:
            last_error = RequestFailure(f'请求失败: {exc.reason}')
            if attempt < retries:
                time.sleep(1)
                continue
            raise last_error from exc

    raise RequestFailure(str(last_error or '请求失败'))
