---
name: cms-config-myclaw
description: 一键交互式配置自己的 OpenClaw（龙虾）机器人，并查看自己已有的机器人。
skillcode: cms-config-myclaw
dependencies:
  - cms-auth-skills
---

# cms-config-myclaw

这个 skill 用来完成两件事：

1. 配置并绑定自己的 `xg_cwork_im` 机器人到某个 OpenClaw agent
2. 查看自己当前账号下已经有哪些机器人

在这个 skill 里，用户提到“龙虾”或“虾”时，都默认等同于 `OpenClaw`。

这个 skill 的默认形态必须是 CLI 交互式向导。
也就是说，用户应该是跟着终端一步一步完成配置，而不是直接丢一段 JSON 或让 AI 静默改配置。

## 什么时候使用

- “配置我的虾”
- “配置我的龙虾”
- “配置我的 OpenClaw 机器人”
- “把龙虾接到公司内部通道上”
- “把 xg_cwork_im 绑定到某个 agent”
- “重建我的龙虾机器人配置”
- “查看我的机器人”
- “获取我的私人助理列表”

## 绑定的意义

绑定不只是把一段配置写进 `openclaw.json`。

真正的作用是：

- 把公司内部的 `xg_cwork_im` channel 接入 OpenClaw
- 为你创建或更新一个工作协同机器人
- 把这台机器人的消息路由到你指定的 agent
- 让你后续可以直接在互动页面里给这个 agent 发消息

用户选择哪个 agent，后续这台机器人收到的消息就会交给哪个 agent 处理。

换句话说：

- 机器人负责“收消息”
- `xg_cwork_im` 插件负责“把公司内部工作平台里的消息接进 OpenClaw”
- binding 负责“决定这些消息最终交给哪个 agent”

如果没有绑定，机器人虽然存在，但 OpenClaw 不知道该把消息交给谁。

## 用户视角怎么理解这件事

从用户视角看，这不是在“配一堆技术参数”，而是在做一件更直白的事：

“我想把公司内部的这个 channel 接到我本地的 OpenClaw 上，这样我就可以通过公司内部的互动页面，远程和某个 agent 说话。”

所以整个 skill 的目标其实是把下面这条链路打通：

`appKey -> cms-auth-skills -> access-token -> 创建机器人 -> 安装/启用插件 -> 写入 channels/accounts/bindings -> 重启 Gateway -> 打开互动页面发消息`

## 配置前用户需要准备什么

用户只需要准备：

1. 一个可用的工作协同 `appKey`
2. 想绑定到哪个 agent
3. 想给机器人起什么名字

其中：

- 如果上下文或已有参数里已经有 `appKey`，默认直接复用
- `avatar`、`groupLabel`、`remark` 都不是必要输入，统一使用默认空值

## CLI 交互应该怎么引导

向导应该始终按下面这种节奏引导用户：

1. 先告诉用户“这是什么、为什么要绑定、完成后能怎么用”
2. 再列出全部 agent，让用户选择
3. 再收集 `appKey` 和机器人名称
4. 在真正写入前展示执行摘要，并解释本次绑定会产生什么效果
5. 配置写入完成后，先告诉用户“已经配置完成”，再提示即将重启 Gateway
6. 重启后明确告诉用户去打开互动链接，并建议发一条测试消息验证

## 用户实际怎么用

典型使用方式是：

1. 运行 `setup_myclaw.py`
2. 按提示选择一个 agent
3. 输入或复用 `appKey`
4. 输入机器人名称
5. 确认执行
6. 等待脚本自动完成注册、插件检查、配置写入和 Gateway 重启
7. 打开脚本输出的公司内部互动链接
8. 在公司内部互动页面里给机器人发一条测试消息，确认回复来自你绑定的 agent

## 用户完成后怎么用

配置成功后，脚本会输出一个互动链接：

`https://sg-al-cwork-web.mediportal.com.cn/xg-claw/web/dist/?xgToken=xxx`

用户打开这个链接后，就可以直接进入公司内部互动页面，给自己的机器人发送消息。
这一步的实际意义是：通过公司内部的 channel，远程和本地 OpenClaw 上的目标 agent 互动。

推荐用户配置完成后立刻做一次最小验证：

1. 打开互动链接
2. 发一条简单消息，比如“你好”
3. 确认是否由目标 agent 正常回复

如果这一步正常，就说明整个绑定链路已经打通。

如果用户不知道第一句该发什么，可以建议动态一点的话术，而不是写死成某个固定角色：

1. “你好，我现在正在验证你是否已经接到这个 agent，请先回复我一句。”
2. “请告诉我，你现在对应的是哪个 agent。”
3. “我刚完成绑定，请用一句简短的话确认你已经可以正常工作。”

用户视角里，后续不需要继续理解 channels、bindings、插件这些内部结构。
对用户来说，更自然的理解应该是：

“我已经把公司内部的这个 channel 接到了当前选择的 agent 上，后面我只需要打开互动链接和它说话。”

## 执行方式

主向导：

```bash
npx clawhub@latest install cms-auth-skills --force
python3 cms-config-myclaw/scripts/setup_myclaw.py
```

查看我已有的机器人：

```bash
npx clawhub@latest install cms-auth-skills --force
python3 cms-config-myclaw/scripts/list_my_robots.py
```

如果已经有可复用的 `appKey`，默认优先复用，不要重复追问。可以直接这样执行：

```bash
CMS_CONFIG_MYCLAW_APP_KEY=your_app_key python3 cms-config-myclaw/scripts/setup_myclaw.py
```

```bash
CMS_CONFIG_MYCLAW_APP_KEY=your_app_key python3 cms-config-myclaw/scripts/list_my_robots.py
```

## 交互规则

1. 默认只通过脚本执行，不默认手工改 `openclaw.json`。
2. 任何写操作前都必须向用户展示摘要并获得确认。
3. 如果目标 agent 已有 `xg_cwork_im` account 或 binding，必须先展示旧状态，再确认是否覆盖。
4. 这个 skill 依赖 `cms-auth-skills`，`appKey -> access-token` 统一交给依赖 skill 处理。
5. 当脚本已经列出全部 agent 后，后续说明里也必须继续完整列出，不要把候选缩成少数几个推荐项。
6. 交互式向导默认只向用户询问必要信息：`appKey` 和机器人名称；`avatar`、`groupLabel`、`remark` 使用默认空值。
7. 如果上下文、已有记忆或已知参数里已经存在可用 `appKey`，默认直接复用；只有在没有现成 `appKey`，或用户明确要求更换时才再问。
8. 每次执行时，都要让用户明确知道“当前进行到哪一步、下一步会发生什么”，保持 CLI 交互的连续感。
9. 不要把引导文案写死到某个固定 agent、固定角色或固定业务场景上；应尽量围绕用户当前选择的 agent 动态说明。
10. 对用户的解释重点应围绕“这是公司内部 channel 的接入与绑定”，而不是只围绕配置文件字段本身。

## 可选参数

```bash
python3 cms-config-myclaw/scripts/setup_myclaw.py --dry-run
```

```bash
python3 cms-config-myclaw/scripts/setup_myclaw.py --config-file /path/to/openclaw.json
```

```bash
python3 cms-config-myclaw/scripts/list_my_robots.py --json
```

```bash
python3 cms-config-myclaw/scripts/list_my_robots.py --show-app-key
```
