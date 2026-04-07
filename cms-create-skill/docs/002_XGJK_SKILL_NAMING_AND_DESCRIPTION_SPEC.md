# 命名和描述规范

本规范用于统一 Skill 的命名、字段声明和一句话描述方式，避免同类 Skill 在目录、展示名和发布标识上各写各的。

## 1. Skill 命名规则

Skill 的目录名、`name`、`skillcode` 应尽量保持一致，统一遵循以下规则：

1. 只允许使用小写字母、数字和连字符 `-`
2. 推荐使用 `cms-业务域-动作` 风格
3. 不使用空格、下划线、中文和临时缩写
4. 不使用 `demo`、`test`、`new`、`final` 这类不稳定词

推荐示例：

- `cms-im-robot`
- `cms-order-sync`
- `cms-report-export`

不推荐示例：

- `IMRobot`
- `cms_order_sync`
- `new-skill-demo`

## 2. 模块与脚本命名规则

- 模块名使用小写英文名词或名词短语，如 `robot`、`message`、`report`
- 脚本文件名使用清晰动作名，如 `list_robots.py`、`send_message.py`
- 一个脚本只负责一个清晰动作，不把多个无关动作混在一个文件里
- `SKILL.md`、模块说明、脚本索引中的脚本路径必须完全一致

## 3. 描述写法

`description` 只写业务价值，不写实现细节。推荐一句话说清楚：

`为谁做什么，产出什么结果`

推荐写法：

- `管理企业 IM 机器人并发送通知消息`
- `同步订单状态并输出异常订单摘要`
- `汇总日报数据并生成可直接发送的简报`

不推荐写法：

- `一个很强大的 Skill`
- `调用接口并处理返回值`
- `用于测试脚本功能`

## 4. YAML 头必填字段

`SKILL.md` 的 YAML 头至少包含以下字段：

```yaml
---
name: cms-im-robot
description: 管理企业 IM 机器人并发送通知消息
skillcode: cms-im-robot
github: https://github.com/xgjk/xg-skills/tree/main/cms-im-robot
dependencies:
  - cms-auth-skills
---
```

约束说明：

- `name` 与目录名保持一致
- `skillcode` 与发布标识保持一致
- `github` 指向目标 Skill 的仓库路径
- `dependencies` 里保留 `cms-auth-skills`

## 5. 占位符处理

以下占位符只允许出现在协议模板阶段，不允许出现在最终 Skill 包里：

- `<skill-name>`
- `<skill-code>`
- `<module>`
- `<action>`
- `<一句话描述>`

交付前必须全文搜索并清零。
