---
name: cms-config-myclaw
description: 一键交互式配置自己的 OpenClaw（龙虾）机器人，并查看自己已有的机器人。
skillCode: cms-config-myclaw
---

# cms-config-myclaw

这个 skill 用来完成两件事：

1. 配置并绑定自己的 `xg_cwork_im` 机器人到某个 OpenClaw agent
2. 查看自己当前账号下已经有哪些机器人

在这个 skill 里，用户提到"龙虾"或"虾"时，都默认等同于 `OpenClaw`。

## 能力总览

| # | 能力 | 脚本 |
|---|------|------|
| 1 | 配置 OpenClaw 机器人 | `scripts/setup_myclaw.py` |
| 2 | 查看已有机器人 | `scripts/list_my_robots.py` |

## 意图路由

| 用户说 | 执行 |
|---|---|
| "配置我的虾" / "配置我的龙虾" / "配置我的 OpenClaw 机器人" | `setup_myclaw.py` |
| "把龙虾接到公司内部通道上" / "把 xg_cwork_im 绑定到某个 agent" | `setup_myclaw.py` |
| "查看我的机器人" / "获取我的私人助理列表" | `list_my_robots.py` |

## 使用说明

### 配置 OpenClaw 机器人

```bash
python scripts/setup_myclaw.py
```

### 查看已有机器人

```bash
python scripts/list_my_robots.py
```

### 使用环境变量

```bash
CMS_CONFIG_MYCLAW_APP_KEY=your_app_key python scripts/setup_myclaw.py
```

## 文件结构

```
cms-config-myclaw/
├── SKILL.md
├── scripts/
│   ├── setup_myclaw.py
│   ├── list_my_robots.py
│   ├── auth_helper.py
│   └── openclaw_config.py
└── references/
    └── register_private_robot.md
```