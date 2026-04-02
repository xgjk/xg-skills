#!/usr/bin/env python3
"""
Shared self-update helper for notex-skills entry scripts.

Behavior:
- Read static metadata from ../version.json
- Use version.json mtime as the "installed-at" timestamp
- Check remote version only when the local install is older than 24 hours
- Fail open on every exception so business scripts keep working
- Restart the current script immediately after a successful update so the business flow continues on the new version
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
import requests
import warnings
import zipfile

# 禁用 InsecureRequestWarning (因为 verify=False)
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

REGISTRY_API_URL = "https://sg-cwork-api.mediportal.com.cn/im/skill/nologin/list"
CHECK_INTERVAL_SECONDS = 24 * 60 * 60
SKIP_ENV_NAME = "NOTEX_SKILLS_SKIP_SELF_UPDATE"


def _log(message: str) -> None:
    print(f"[self-update] {message}", file=sys.stderr, flush=True)


def _result(
    *,
    status: str,
    checked: bool = False,
    updated: bool = False,
    current_version: str = "",
    remote_version: str = "",
    message: str = "",
    error: str = "",
) -> dict:
    return {
        "status": status,
        "checked": checked,
        "updated": updated,
        "currentVersion": current_version,
        "remoteVersion": remote_version,
        "message": message,
        "error": error,
    }


def _scripts_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _skill_root() -> str:
    return os.path.abspath(os.path.join(_scripts_dir(), ".."))


def _version_file() -> str:
    return os.path.join(_skill_root(), "version.json")


def _load_version_meta(version_path: str) -> dict:
    with open(version_path, "r", encoding="utf-8") as file_obj:
        payload = json.load(file_obj)

    if not isinstance(payload, dict):
        raise RuntimeError("version.json must contain a JSON object")

    skillcode = str(payload.get("skillcode", "")).strip()
    version = str(payload.get("version", "")).strip()
    if not skillcode or not version:
        raise RuntimeError("version.json must include skillcode and version")

    return {"skillcode": skillcode, "version": version}


def _version_key(raw: object) -> tuple[int, ...]:
    text = str(raw or "").strip()
    if not text:
        raise RuntimeError("empty version")

    parts = []
    current = []
    for char in text:
        if char.isdigit():
            current.append(char)
            continue
        if current:
            parts.append(int("".join(current)))
            current = []
    if current:
        parts.append(int("".join(current)))

    if not parts:
        raise RuntimeError(f"invalid version: {text}")

    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)




def _http_get(url: str, timeout: int = 15) -> str:
    """发起 HTTP GET 请求并返回内容。"""
    try:
        response = requests.get(
            url,
            verify=False,
            allow_redirects=True,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        raise RuntimeError(f"请求失败: {e}")


def _fetch_remote_skill(skillcode: str) -> dict | None:
    payload = json.loads(_http_get(REGISTRY_API_URL, timeout=60))

    skills = payload if isinstance(payload, list) else payload.get("data") or payload.get("resultData") or []
    normalized = skillcode.lower()
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        if str(skill.get("code", "")).strip().lower() == normalized:
            return skill
    return None


def _download_zip(url: str, dest_path: str) -> None:
    try:
        response = requests.get(
            url,
            verify=False,
            allow_redirects=True,
            timeout=120,
            stream=True,
        )
        response.raise_for_status()
        with open(dest_path, "wb") as file_obj:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file_obj.write(chunk)
    except Exception as e:
        raise RuntimeError(f"下载失败: {e}")


def _extract_skill_root(zip_path: str, stage_parent: str, skillcode: str) -> str:
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        names = zip_file.namelist()
        top_entries = {name.split("/")[0] for name in names if name.split("/")[0]}

        has_single_root = False
        root_name = ""
        if len(top_entries) == 1:
            root_name = next(iter(top_entries))
            has_single_root = all(
                name == root_name or name.startswith(root_name + "/")
                for name in names
            )

        if has_single_root:
            zip_file.extractall(stage_parent)
            return os.path.join(stage_parent, root_name)

        fallback_root = os.path.join(stage_parent, skillcode)
        os.makedirs(fallback_root, exist_ok=True)
        zip_file.extractall(fallback_root)
        return fallback_root


def _swap_skill_root(skill_root: str, staged_root: str) -> None:
    backup_root = f"{skill_root}.__backup__.{int(time.time())}"

    if os.path.isdir(backup_root):
        shutil.rmtree(backup_root, ignore_errors=True)

    moved_old = False
    try:
        if os.path.isdir(skill_root):
            os.rename(skill_root, backup_root)
            moved_old = True

        shutil.move(staged_root, skill_root)
        if moved_old:
            shutil.rmtree(backup_root, ignore_errors=True)
    except Exception:
        if os.path.isdir(skill_root):
            shutil.rmtree(skill_root, ignore_errors=True)
        if moved_old and os.path.isdir(backup_root):
            os.rename(backup_root, skill_root)
        raise


def _restart_current_process() -> None:
    script_path = os.path.abspath(sys.argv[0]) if sys.argv else ""
    if not script_path:
        raise RuntimeError("missing current script path")

    env = os.environ.copy()
    env[SKIP_ENV_NAME] = "1"
    argv = [sys.executable, script_path, *sys.argv[1:]]
    os.execve(sys.executable, argv, env)


def maybe_self_update() -> dict:
    if os.environ.get(SKIP_ENV_NAME, "").strip():
        return _result(status="skipped", message="skip self-update after restart")

    try:
        version_path = _version_file()
        metadata = _load_version_meta(version_path)
        current_version = metadata["version"]

        version_age_seconds = time.time() - os.path.getmtime(version_path)
        if version_age_seconds < CHECK_INTERVAL_SECONDS:
            return _result(
                status="skipped",
                current_version=current_version,
                message="local install is newer than 24 hours threshold",
            )

        remote_skill = _fetch_remote_skill(metadata["skillcode"])
        if not remote_skill:
            message = f"platform skill not found: {metadata['skillcode']}"
            return _result(
                status="no-remote-skill",
                checked=True,
                current_version=current_version,
                message=message,
            )

        remote_version = str(remote_skill.get("version", "")).strip()
        download_url = str(remote_skill.get("downloadUrl", "")).strip()
        if not remote_version or not download_url:
            message = "remote version or downloadUrl is missing"
            return _result(
                status="invalid-remote-metadata",
                checked=True,
                current_version=current_version,
                remote_version=remote_version,
                message=message,
            )

        if _version_key(remote_version) <= _version_key(current_version):
            message = f"already up to date ({current_version})"
            return _result(
                status="up-to-date",
                checked=True,
                current_version=current_version,
                remote_version=remote_version,
                message=message,
            )

        _log(f"upgrading {metadata['skillcode']} {current_version} -> {remote_version}")
        skill_root = _skill_root()
        parent_dir = os.path.dirname(skill_root)
        with tempfile.TemporaryDirectory(prefix=f"{metadata['skillcode']}-update-", dir=parent_dir) as tmp_dir:
            zip_path = os.path.join(tmp_dir, "skill.zip")
            stage_parent = os.path.join(tmp_dir, "stage")
            os.makedirs(stage_parent, exist_ok=True)

            _download_zip(download_url, zip_path)
            if not zipfile.is_zipfile(zip_path):
                raise RuntimeError("downloaded payload is not a ZIP archive")

            staged_root = _extract_skill_root(zip_path, stage_parent, metadata["skillcode"])
            staged_meta = _load_version_meta(os.path.join(staged_root, "version.json"))
            if staged_meta["skillcode"] != metadata["skillcode"]:
                raise RuntimeError("downloaded skillcode does not match current package")

            if _version_key(staged_meta["version"]) <= _version_key(current_version):
                message = "downloaded package did not advance local version"
                return _result(
                    status="stale-package",
                    checked=True,
                    current_version=current_version,
                    remote_version=staged_meta["version"],
                    message=message,
                )

            _swap_skill_root(skill_root, staged_root)
            try:
                os.utime(version_path, None)
            except OSError:
                pass

        refreshed = _load_version_meta(version_path)
        if _version_key(refreshed["version"]) <= _version_key(current_version):
            message = "local version did not advance after install"
            return _result(
                status="install-noop",
                checked=True,
                current_version=current_version,
                remote_version=remote_version,
                message=message,
            )

        _log(f"update applied, restarting script with version {refreshed['version']}")
        _restart_current_process()
        return _result(
            status="updated",
            checked=True,
            updated=True,
            current_version=refreshed["version"],
            remote_version=remote_version,
            message="update applied successfully",
        )
    except Exception as exc:
        return _result(
            status="error",
            checked=False,
            message="self-update skipped because of an exception",
            error=str(exc),
        )


if __name__ == "__main__":
    result = maybe_self_update()
    if result.get("updated"):
        print(json.dumps(result, ensure_ascii=False, indent=2))
