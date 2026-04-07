# SKILL.md 编写规范

`SKILL.md` 是 Skill 的入口文件，负责告诉 AI 和开发者“这个 Skill 能做什么、应该怎么用、去哪里执行”，而不是把所有实现细节堆在一个文件里。

## 1. YAML 头要求

最小 YAML 头如下：

```yaml
---
name: <skill-name>
description: <一句话描述>
skillcode: <skill-code>
github: https://github.com/xgjk/xg-skills/tree/main/<skill-code>
dependencies:
  - cms-auth-skills
---
```

## 2. 必备章节

`SKILL.md` 至少包含以下内容：

1. 当前版本
2. 接口版本
3. 能力概览
4. 统一规范
5. 授权依赖
6. 输入完整性规则
7. 建议工作流
8. 脚本使用规则
9. 路由与加载规则
10. 宪章
11. 模块路由表
12. 能力树

## 3. 内容边界

`SKILL.md` 负责写：

- Skill 的能力范围
- 使用顺序和加载顺序
- 用户意图与模块/脚本的映射关系
- 对外输出边界、危险操作规则、鉴权依赖入口

`SKILL.md` 不负责写：

- 大段请求字段定义
- 每个脚本的完整实现细节
- 运行时日志路径的硬编码说明
- 与当前 Skill 无关的通用平台文档

## 4. 模块路由表格式

推荐使用以下列：

| 用户意图 | 模块 | 能力摘要 | 模块说明 | 脚本 |
|---|---|---|---|---|
| 查看机器人列表 | `robot` | 获取机器人清单与状态 | `./references/robot/README.md` | `./scripts/robot/list_robots.py` |
| 发送机器人消息 | `message` | 发送通知消息 | `./references/message/README.md` | `./scripts/message/send_message.py` |

要求：

- `用户意图` 写用户真实会说的话
- `模块` 与目录名一致
- `模块说明` 指向真实存在的 `README.md`
- `脚本` 指向真实存在的 `.py`

## 5. 能力树格式

推荐在文末保留实际目录树：

```text
<skill-name>/
├── SKILL.md
├── references/
│   ├── robot/README.md
│   └── message/README.md
└── scripts/
    ├── robot/
    │   ├── README.md
    │   └── list_robots.py
    └── message/
        ├── README.md
        └── send_message.py
```

## 6. 最小正文示例

```markdown
# <Skill 名称> — 索引

本文件提供能力边界、路由规则与使用约束。详细说明见 `references/`，实际执行见 `scripts/`。

**当前版本**: 0.1.0
**接口版本**: v1

**能力概览（2 块能力）**：
- `robot`：查看机器人列表、状态和基础信息
- `message`：发送通知消息并返回发送结果

统一规范：
- 鉴权依赖：`cms-auth-skills/SKILL.md`
- 运行日志：`.cms-log/`

授权依赖：
- 需要鉴权时先读取 `cms-auth-skills/SKILL.md`
- 缺失时先安装依赖，再继续执行

建议工作流（简版）：
1. 先读取 `SKILL.md`，确认能力边界和限制
2. 根据用户意图定位模块
3. 读取对应模块说明
4. 补齐必要输入
5. 执行对应脚本

模块路由与能力索引：
| 用户意图 | 模块 | 能力摘要 | 模块说明 | 脚本 |
|---|---|---|---|---|
| 查看机器人列表 | `robot` | 获取机器人清单与状态 | `./references/robot/README.md` | `./scripts/robot/list_robots.py` |
```

## 7. 一致性要求

- `SKILL.md` 的模块清单必须覆盖实际模块目录
- 路由表必须覆盖实际可执行脚本
- 能力树必须能反映实际文件结构
- 不允许残留任何模板占位符
