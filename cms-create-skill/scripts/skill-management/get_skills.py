#!/usr/bin/env python3
"""
发现 Skill — 浏览、搜索、查看详情

完整实现位于 cms-find-skills/scripts/skill_registry/get_skills.py。
本文件作为薄封装，自动定位并复用该实现，避免双份维护。

使用方式：
  python3 cms-create-skill/scripts/skill-management/get_skills.py
  python3 cms-create-skill/scripts/skill-management/get_skills.py --search "机器人"
  python3 cms-create-skill/scripts/skill-management/get_skills.py --detail "im-robot"
"""

from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
_FIND_SKILLS_REGISTRY = os.path.join(
    _REPO_ROOT, "cms-find-skills", "scripts", "skill_registry"
)

if not os.path.isdir(_FIND_SKILLS_REGISTRY):
    print(
        f"找不到 cms-find-skills/scripts/skill_registry: {_FIND_SKILLS_REGISTRY}",
        file=sys.stderr,
    )
    sys.exit(1)

sys.path.insert(0, _FIND_SKILLS_REGISTRY)

from get_skills import main  # type: ignore  # noqa: E402

if __name__ == "__main__":
    main()
