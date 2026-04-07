#!/usr/bin/env python3
"""
上传文件到七牛云存储

用途：获取七牛上传凭证 → 上传文件 → 返回下载地址

使用方式：
  python3 cms-push-skill/scripts/skill-management/upload_to_qiniu.py <file-path> [--file-key <key>] [--corp-id <id>]

参数说明：
  file-path     要上传的文件路径（必须）
  --file-key    七牛文件 key（可选，默认为 时间戳-文件名）
  --corp-id     企业 ID（可选，也可通过环境变量 XG_CORP_ID 设置）

环境变量：
  XG_USER_TOKEN  — access-token（必须，用于获取七牛上传凭证）
  XG_CORP_ID     — 企业 ID（可选，也可通过 --corp-id 参数传入）

示例：
  python3 cms-push-skill/scripts/skill-management/upload_to_qiniu.py ./im-robot.zip
  python3 cms-push-skill/scripts/skill-management/upload_to_qiniu.py ./im-robot.zip --file-key "skills/im-robot-v1.zip"

输出：
  成功时输出下载地址到 stdout，可直接作为 register_skill.py 的 --download-url 参数。
"""

import sys
import os
import time
import argparse
import requests

from common import API_BASE, get_headers, get_token, parse_api_response

# 七牛上传凭证接口
QINIU_AUTH_URL = f"{API_BASE}/api/qiniu/token"

# 七牛上传地址（z2 区域）
QINIU_UPLOAD_URL = "https://up-z2.qiniup.com/"


def get_qiniu_token(access_token: str, file_key: str, corp_id: str = "") -> dict:
    """获取七牛上传凭证，返回 {token, domain}。"""
    headers = get_headers(access_token)
    params = {"fileKey": file_key, "corpId": corp_id}

    try:
        response = requests.post(
            QINIU_AUTH_URL,
            json=params,
            headers=headers,
            verify=False,
            allow_redirects=True,
            timeout=60,
        )
        response.raise_for_status()
        data = parse_api_response(response, "获取七牛凭证")
        if not data.get("data") or not data["data"].get("token") or not data["data"].get("domain"):
            raise RuntimeError(f"获取七牛凭证失败: {response.text}")
        return data["data"]
    except Exception as e:
        raise RuntimeError(f"获取七牛凭证失败: {e}")


def upload_file(qiniu_token: str, file_key: str, file_path: str, max_retries: int = 3) -> bool:
    """通过 multipart/form-data 上传文件到七牛，带指数退避重试。"""
    file_name = os.path.basename(file_path)

    def do_upload(url):
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f, 'application/octet-stream')}
            data = {'token': qiniu_token, 'key': file_key}
            return requests.post(
                url,
                files=files,
                data=data,
                verify=False,
                allow_redirects=True,
                timeout=300,
            )

    last_err = None
    for attempt in range(1, max_retries + 1):
        response = None
        try:
            response = do_upload(QINIU_UPLOAD_URL)

            # 处理七牛区域重定向 (400 错误且含有 "please use <host>")
            if response.status_code == 400 and "please use" in response.text:
                import re
                region_match = re.search(r'please use\s+([a-z0-9.-]+)', response.text, re.IGNORECASE)
                if region_match:
                    new_host = region_match.group(1)
                    new_url = f"https://{new_host}/"
                    print(f"区域重定向: {new_url}", file=sys.stderr)
                    response = do_upload(new_url)

            response.raise_for_status()
            return True
        except Exception as e:
            last_err = response.text if response is not None else str(e)
            if attempt < max_retries:
                backoff = 2 ** (attempt - 1)
                print(f"七牛上传第 {attempt} 次失败，{backoff}s 后重试: {last_err}", file=sys.stderr)
                time.sleep(backoff)
            else:
                raise RuntimeError(f"七牛上传失败（已重试 {max_retries} 次）: {last_err}")


def main():
    parser = argparse.ArgumentParser(description="上传文件到七牛云存储")
    parser.add_argument("file_path", help="要上传的文件路径")
    parser.add_argument("--file-key", default="", help="七牛文件 key（默认自动生成）")
    parser.add_argument("--corp-id", default="", help="企业 ID（也可通过 XG_CORP_ID 环境变量设置）")
    args = parser.parse_args()

    token = get_token()
    corp_id = os.environ.get("XG_CORP_ID", "")
    corp_id = args.corp_id or corp_id

    file_path = os.path.abspath(args.file_path)
    if not os.path.isfile(file_path):
        print(f"错误: 文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)

    file_name = os.path.basename(file_path)
    file_key = args.file_key or f"{int(time.time() * 1000)}-{file_name}"

    # Step 1: 获取七牛上传凭证
    print(f"[1/2] 获取七牛上传凭证 (fileKey={file_key}) ...", file=sys.stderr)
    creds = get_qiniu_token(token, file_key, corp_id)
    qiniu_token = creds["token"]
    domain = creds["domain"]
    print(f"[1/2] 凭证获取成功，domain={domain}", file=sys.stderr)

    # Step 2: 上传文件
    size_kb = os.path.getsize(file_path) / 1024
    print(f"[2/2] 上传 {file_name} ({size_kb:.1f} KB) ...", file=sys.stderr)
    upload_file(qiniu_token, file_key, file_path)

    # 构造下载地址
    base_url = domain if domain.startswith("http") else f"https://{domain}"
    base_url = base_url.rstrip("/")
    download_url = f"{base_url}/{file_key}"

    print(f"[2/2] 上传成功!", file=sys.stderr)
    print(f"下载地址: {download_url}", file=sys.stderr)

    # 输出下载地址到 stdout（方便管道）
    print(download_url)


if __name__ == "__main__":
    main()
