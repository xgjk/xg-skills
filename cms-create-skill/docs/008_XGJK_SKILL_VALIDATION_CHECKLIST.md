# Skills 规范校验清单

用于检查一个 Skill 包是否符合当前简化协议。执行时必须逐项核对，不允许只口头说“已通过”。

> 本清单与同目录编号协议文档保持同步：核心总则见 `001_XGJK_SKILL_PROTOCOL.md`，详细规则见 `002`-`007`。如有冲突，以最新专题规范为准。

## A. 基础声明

- [ ] 存在 `SKILL.md`
- [ ] `SKILL.md` 的 YAML 头包含 `name`、`description`、`skillcode`、`github`
- [ ] `SKILL.md` 的 YAML 头包含 `dependencies: - cms-auth-skills`
- [ ] `name`、目录名、`skillcode` 保持一致
- [ ] `name` 和 `skillcode` 只使用小写字母、数字和连字符
- [ ] 全文不存在模板占位符残留（如 `<skill-name>`、`<module>`、`<action>`）

## B. 目录与路由

- [ ] 存在 `references/` 目录
- [ ] 存在 `scripts/` 目录
- [ ] 每个模块都有 `references/<module>/README.md`
- [ ] 每个模块都有 `scripts/<module>/README.md`
- [ ] 每个可执行动作都有对应的 `scripts/<module>/<action>.py`
- [ ] `SKILL.md` 的能力概览与实际模块目录一致
- [ ] `SKILL.md` 的模块路由表与实际脚本一致
- [ ] `SKILL.md` 的能力树与实际目录结构一致
- [ ] 不存在未在 `SKILL.md` 中声明的孤立脚本

## C. 文档完整性

- [ ] `SKILL.md` 包含能力概览
- [ ] `SKILL.md` 包含统一规范
- [ ] `SKILL.md` 包含授权依赖说明
- [ ] `SKILL.md` 包含输入完整性规则
- [ ] `SKILL.md` 包含建议工作流
- [ ] `SKILL.md` 包含脚本使用规则
- [ ] `SKILL.md` 包含路由与加载规则
- [ ] `SKILL.md` 包含宪章
- [ ] 每个模块说明包含适用场景、输入要求、输出说明和动作列表
- [ ] 每个脚本索引包含脚本清单、运行方式、鉴权前置条件和返回说明

## D. Python 脚本

- [ ] 所有业务脚本均为 Python 文件
- [ ] 每个脚本可在命令行独立执行
- [ ] 每个脚本包含 `main()` 函数
- [ ] 每个脚本包含 `if __name__ == '__main__'` 守卫
- [ ] 每个脚本的参数名与文档保持一致
- [ ] 每个脚本显式设置超时
- [ ] 如实现重试，重试间隔不少于 1 秒，最大次数不超过 3 次
- [ ] 不存在无限循环重试逻辑
- [ ] 脚本默认输出结构化 JSON 或明确可解析文本

## E. 鉴权与安全

- [ ] 需要鉴权时，明确依赖 `cms-auth-skills`
- [ ] 每个脚本都声明了明确的鉴权模式：`nologin`、`appKey` 或 `access-token`
- [ ] 需要 `appKey` 或 `access-token` 时，统一通过 `cms-auth-skills` 获取
- [ ] `nologin` 动作不依赖额外鉴权获取流程
- [ ] 目标 Skill 未实现本地登录流程
- [ ] 不向用户输出 token、appKey、cookie、authorization 等敏感值
- [ ] 写操作、发布操作、同步操作在执行前要求再次确认

## F. 输出、日志与运行时状态

- [ ] 对用户只输出最小必要信息
- [ ] 非必要场景不回显完整原始响应
- [ ] 如脚本输出日志，统一写入 `.cms-log/log/<skillcode>/`
- [ ] 如脚本记录状态，统一写入 `.cms-log/state/<skillcode>/`
- [ ] 运行时日志和状态不写回 Skill 包目录
- [ ] 日志中不出现敏感信息

## G. 交付前复核

- [ ] 已按 `007_XGJK_SKILL_CREATION_WORKFLOW.md` 走完生成流程
- [ ] 已逐项勾选本清单，并记录每项结论
- [ ] 已完成至少一次手工 smoke test
- [ ] 已确认文档、脚本、目录三者没有互相矛盾
