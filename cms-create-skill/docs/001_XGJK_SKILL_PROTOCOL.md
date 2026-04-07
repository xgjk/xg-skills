# XGJK Skill 协议总览 v2.0

本文档只保留总则、最小结构和交付边界；详细要求已拆分为同目录下的专题规范，避免单个协议文件过大、过杂。

## 0. 文档编号与命名规则

本套协议统一使用以下命名规则：

```text
NNN_XGJK_SKILL_<TOPIC>.md
```

说明：

- `NNN` 为三位数字编号，从 `001` 开始
- 编号同时代表推荐阅读顺序
- `XGJK_SKILL_` 为统一前缀
- `<TOPIC>` 为具体主题，使用全大写英文和下划线

## 1. 适用范围

- 面向按我方规范从零创建的新 Skill
- 面向以 `SKILL.md`、`references/`、`scripts/` 为核心的简化结构
- 面向需要统一鉴权、安全约束和交付校验的内部 Skill

## 2. 最小目录结构

一个合规的 Skill 包至少包含以下结构：

```text
<skill-name>/
├── SKILL.md
├── references/
│   └── <module>/
│       └── README.md
└── scripts/
    └── <module>/
        ├── README.md
        └── <action>.py
```

说明：

- `SKILL.md` 是总索引，负责能力边界、路由规则和能力树
- `references/<module>/README.md` 是模块说明，负责触发场景、输入输出和调用约束
- `scripts/<module>/<action>.py` 是唯一执行入口，负责真正完成业务动作
- `scripts/<module>/README.md` 是脚本索引，负责列出脚本、用途、入参与依赖

## 3. 核心强制规则

1. Skill 名称、目录名、`skillcode` 必须稳定且一致，统一使用小写加连字符格式。
2. 每个可执行动作都必须有对应的 Python 脚本，不允许“先留空后补”。
3. `SKILL.md` 只做索引和规则声明，不承载实现细节，不堆完整请求参数。
4. 模块说明写在 `references/`，脚本执行写在 `scripts/`，两者都必须和 `SKILL.md` 的路由表保持一致。
5. 所有鉴权统一依赖 `cms-auth-skills`，目标 Skill 不自行实现登录流程。
6. 运行时日志、缓存、状态不写回 Skill 包内部，统一放到工作区根目录的 `.cms-log/`。
7. 对用户有副作用的新增、修改、删除、发布、同步等动作，执行前必须再次确认。

## 4. 拆分后的专题文档

当前协议拆分为以下专题文档：

1. `002_XGJK_SKILL_NAMING_AND_DESCRIPTION_SPEC.md`
   说明命名规则、描述写法、YAML 基本字段。
2. `003_XGJK_SKILL_STRUCTURE_SPEC.md`
   说明目录结构、模块划分、文件职责和禁止项。
3. `004_XGJK_SKILL_INDEX_WRITING_SPEC.md`
   说明 `SKILL.md` 的标准写法、路由表格式和能力树要求。
4. `005_XGJK_SKILL_PYTHON_SCRIPT_SPEC.md`
   说明 Python 脚本的文件结构、参数约束、重试、输出和日志规则。
5. `006_XGJK_SKILL_AUTH_AND_SECURITY_SPEC.md`
   说明鉴权依赖、安全边界、敏感信息和危险操作处理方式。
6. `007_XGJK_SKILL_CREATION_WORKFLOW.md`
   给出从零创建 Skill 的 5 步流程。
7. `008_XGJK_SKILL_VALIDATION_CHECKLIST.md`
   用于交付前逐项核对。

## 5. 交付顺序

推荐按以下顺序完成交付：

1. 先阅读本总览，明确最小结构和强制规则。
2. 按专题文档分别完成命名、目录、`SKILL.md`、脚本和安全设计。
3. 按 `007_XGJK_SKILL_CREATION_WORKFLOW.md` 逐步生成目标 Skill。
4. 按 `008_XGJK_SKILL_VALIDATION_CHECKLIST.md` 逐项检查，不能只口头说“已通过”。
5. 完成手工 smoke test 后，再进入发布、同步或交付阶段。

## 6. 最终验收标准

满足以下条件，才算协议层面完成：

- 目录结构完整，且没有占位符残留
- `SKILL.md`、模块说明、脚本索引、Python 脚本四者一致
- 鉴权依赖、输出格式、危险操作确认规则清晰
- 脚本可独立执行，且能在命令行复现
- 校验清单逐项勾选完成，并保留检查结论
