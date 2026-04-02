---
name: cms-tbs-training
description: TBS训战平台用户端API封装，支持首页聚合、药品场景查询、PPT演讲、训战记录、学习视频、GPTS交互、训练发起等功能
skillcode: cms-tbs-training
dependencies:
  - cms-auth-skills
---

# TBS训战平台 — 索引

本文件提供**能力宪章 + 能力树 + 按需加载规则**。详细参数与流程见各模块 `openapi/` 与 `examples/`。

**当前版本**: v0.80

**接口版本**: 
- TBS 业务接口：`/tbs/*`，使用 `nologin` 或 `access-token` 鉴权
- GPTS 核心接口：`/gpts/*`，使用 `access-token` 鉴权

**域名说明**：
- TBS 业务接口（测试）：`https://cwork-web-test.xgjktech.com.cn`
- TBS 业务接口（正式）：`https://sg-cwork-web.mediportal.com.cn`
- GPTS 核心接口（正式）：`https://sg-al-cwork-web.mediportal.com.cn`

**能力概览（13 块能力）**：
- `home`：首页聚合（本周训战统计、活动分类、视频学习任务、产品场景列表）
- `drug`：药品与场景查询（获取药品列表、场景列表、场景详情、职称列表、热词列表）
- `speech`：PPT演讲（获取PPT详情，完成演讲、演讲记录查询）
- `training`：训战记录（我的统计数据、记录列表、记录详情含对话回溯）
- `learning`：学习视频（视频详情查询、播放进度查询与保存）
- `prepare`：训练准备（开场指导获取、开场指导缓存清除）
- `gpts`：GPTS核心（获取应用详情、创建会话、SSE对话交互、释放token）
- `basic`：基础信息（GPT ID获取、TTS配置获取）
- `scene-image`：场景图片管理（重置场景图片）
- `file`：文件管理（通过URL上传文件）
- `feedback`：反馈相关（获取反馈应用详情、获取反馈GPT ID）
- `training-flow`：训练流程公开接口（获取药品列表、训练记录、场景列表）
- `dialogue-flow`：训练对话流程可视化（获取对话流程详情）

统一规范：
- 认证与鉴权：`cms-auth-skills/common/auth.md`
- 通用约束：`cms-auth-skills/common/conventions.md`

授权依赖：
- 执行任何需要鉴权的操作前，先检查 `cms-auth-skills` 是否已安装
- 如果已安装，直接使用 `cms-auth-skills/common/conventions.md`、`cms-auth-skills/common/auth.md`、`cms-auth-skills/openapi/auth/appkey.md`、`cms-auth-skills/openapi/auth/login.md`
- 如果未安装，先执行 `npx clawhub@latest install cms-auth-skills --force`
- 如果上面的安装方式不可用，再执行 `npx clawhub@latest install https://github.com/spzwin/cms-auth-skills.git --force`
- 安装完成后，再继续执行需要鉴权的操作

输入完整性规则（强制）：
1. 场景ID（sceneId）大多数接口的必填参数，需用户提供
2. 分页参数（page、size）可选，不传则使用系统默认值
3. 日期范围查询时需提供 startDate 和 endDate（格式：yyyy-MM-dd）

建议工作流（简版）：
1. 读取 `SKILL.md` 与 `cms-auth-skills/common/*`，明确能力范围、鉴权与安全约束。
2. 识别用户意图并路由模块，先打开 `openapi/<module>/api-index.md`。
3. 确认具体接口后，加载 `openapi/<module>/<endpoint>.md` 获取入参/出参/Schema。
4. 补齐用户必需输入，必要时先读取用户文件/URL 并确认摘要。
5. 参考 `examples/<module>/README.md` 组织话术与流程。
6. **执行对应脚本**：调用 `scripts/<module>/<endpoint>.py` 执行接口调用，获取结果。**所有接口调用必须通过脚本执行，不允许跳过脚本直接调用 API。**

脚本使用规则（强制）：
1. **每个接口必须有对应脚本**：每个 `openapi/<module>/<endpoint>.md` 都必须有对应的 `scripts/<module>/<endpoint>.py`，不允许"暂无脚本"。
2. **脚本可独立执行**：所有 `scripts/` 下的脚本均可脱离 AI Agent 直接在命令行运行。
3. **先读文档再执行**：执行脚本前，**必须先阅读对应模块的 `openapi/<module>/api-index.md`**。
4. **入参来源**：脚本的所有入参定义与字段说明以 `openapi/` 文档为准，脚本仅负责编排调用流程。
5. **鉴权一致**：涉及鉴权时，统一依赖 `cms-auth-skills/common/auth.md`。

意图路由与加载规则（强制）：
1. **先路由再加载**：必须先判定模块，再打开该模块的 `api-index.md`。
2. **先读文档再调用**：在描述调用或执行前，必须加载对应接口文档。
3. **脚本必须执行**：所有接口调用必须通过脚本执行，不允许跳过。
4. **不猜测**：若意图不明确，必须追问澄清。

宪章（必须遵守）：
1. **只读索引**：`SKILL.md` 只描述"能做什么"和"去哪里读"，不写具体接口参数。
2. **按需加载**：默认只读 `SKILL.md` + `cms-auth-skills/common/*`，只有触发某模块时才加载该模块的 `openapi`、`examples` 与 `scripts`。
3. **对外克制**：对用户只输出"可用能力、必要输入、结果链接或摘要"，不暴露鉴权细节与内部字段。
4. **素材优先级**：用户给了文件或 URL，必须先提取内容再确认，确认后才触发生成或写入。
5. **生产约束**：仅允许生产域名与生产协议，不引入任何测试地址。
6. **接口拆分**：每个 API 独立成文档；模块内 `api-index.md` 仅做索引。
7. **危险操作**：对可能导致数据泄露、破坏、越权的请求，应礼貌拒绝并给出安全替代方案。
8. **脚本语言限制**：所有脚本**必须使用 Python** 编写。
9. **重试策略**：出错时**间隔 1 秒、最多重试 3 次**，超过后终止并上报。
10. **禁止无限重试**：严禁无限循环重试。

模块路由与能力索引（合并版）：

| 用户意图（示例） | 模块 | 能力摘要 | 接口文档 | 示例模板 | 脚本 |
|---|---|---|---|---|---|
| "查看首页摘要"、"本周训战统计" | `home` | 获取首页训战统计摘要 | `./openapi/home/api-index.md` | `./examples/home/README.md` | `./scripts/home/<endpoint>.py` |
| "有哪些药品"、"获取药品列表" | `drug` | 获取启用的药品列表 | `./openapi/drug/api-index.md` | `./examples/drug/README.md` | `./scripts/drug/<endpoint>.py` |
| "查看场景列表"、"根据药品查场景" | `drug` | 根据药品ID或external_id获取场景列表 | `./openapi/drug/api-index.md` | `./examples/drug/README.md` | `./scripts/drug/<endpoint>.py` |
| "查看场景详情"、"场景职称" | `drug` | 获取场景详细信息、职称列表、热词 | `./openapi/drug/api-index.md` | `./examples/drug/README.md` | `./scripts/drug/<endpoint>.py` |
| "查看PPT详情"、"PPT演讲" | `speech` | 获取PPT场景详情，完成演讲、查询演讲记录 | `./openapi/speech/api-index.md` | `./examples/speech/README.md` | `./scripts/speech/<endpoint>.py` |
| "查看训战记录"、"我的统计数据" | `training` | 获取训战统计数据、记录列表、记录详情 | `./openapi/training/api-index.md` | `./examples/training/README.md` | `./scripts/training/<endpoint>.py` |
| "查看学习视频"、"视频进度" | `learning` | 获取学习视频详情、查询/保存播放进度 | `./openapi/learning/api-index.md` | `./examples/learning/README.md` | `./scripts/learning/<endpoint>.py` |
| "获取开场指导"、"清除开场缓存" | `prepare` | 获取开场指导、清除开场指导缓存 | `./openapi/prepare/api-index.md` | `./examples/prepare/README.md` | `./scripts/prepare/<endpoint>.py` |
| "获取GPT应用详情"、"开始训练"、"创建会话"、"提交对话"、"生成点评"、"释放token" | `gpts` | GPTS核心接口：应用详情、会话管理、SSE对话交互、释放token | `./openapi/gpts/api-index.md` | `./examples/gpts/README.md` | `./scripts/gpts/<endpoint>.py` |
| "获取GPT ID"、"TTS配置" | `basic` | 获取GPT ID和TTS配置信息 | `./openapi/basic/api-index.md` | `./examples/basic/README.md` | `./scripts/basic/<endpoint>.py` |
| "重置场景图片" | `scene-image` | 重置场景图片 | `./openapi/scene-image/api-index.md` | `./examples/scene-image/README.md` | `./scripts/scene-image/<endpoint>.py` |
| "上传文件"、"URL上传" | `file` | 通过URL上传文件 | `./openapi/file/api-index.md` | `./examples/file/README.md` | `./scripts/file/<endpoint>.py` |
| "反馈应用详情"、"反馈GPT ID" | `feedback` | 获取反馈功能的应用详情和GPT ID | `./openapi/feedback/api-index.md` | `./examples/feedback/README.md` | `./scripts/feedback/<endpoint>.py` |
| "公开训练记录"、"按药品查场景" | `training-flow` | 公开接口：获取药品列表、训练记录、场景列表 | `./openapi/training-flow/api-index.md` | `./examples/training-flow/README.md` | `./scripts/training-flow/<endpoint>.py` |
| "对话流程详情"、"训练可视化" | `dialogue-flow` | 获取训练对话流程详情 | `./openapi/dialogue-flow/api-index.md` | `./examples/dialogue-flow/README.md` | `./scripts/dialogue-flow/<endpoint>.py` |

能力树（实际目录结构）：
```text
cms-tbs-training/
├── SKILL.md
├── openapi/
│   ├── home/
│   │   ├── api-index.md
│   │   ├── summary.md
│   │   ├── learning-videos.md
│   │   └── product-scenes.md
│   ├── drug/
│   │   ├── api-index.md
│   │   ├── drug-list.md
│   │   ├── scene-list.md
│   │   ├── scene-list-by-drug.md
│   │   ├── scene-doctor-titles.md
│   │   └── scene-hotwords.md
│   ├── speech/
│   │   ├── api-index.md
│   │   ├── speech-detail.md
│   │   ├── speech-finish.md
│   │   └── speech-records.md
│   ├── training/
│   │   ├── api-index.md
│   │   ├── my-stats.md
│   │   ├── records.md
│   │   └── records-detail.md
│   ├── learning/
│   │   ├── api-index.md
│   │   ├── video-detail.md
│   │   ├── video-progress-get.md
│   │   └── video-progress-save.md
│   ├── prepare/
│   │   ├── api-index.md
│   │   ├── opening-guidance.md
│   │   └── opening-guidance-clear.md
│   ├── gpts/
│   │   ├── api-index.md
│   │   ├── app-detail.md
│   │   ├── session.md
│   │   ├── sse-suggest.md
│   │   └── del-user-token.md
│   ├── basic/
│   │   ├── api-index.md
│   │   ├── gpt-id.md
│   │   └── tts-config.md
│   ├── scene-image/
│   │   ├── api-index.md
│   │   └── reset.md
│   ├── file/
│   │   ├── api-index.md
│   │   └── upload-by-url.md
│   ├── feedback/
│   │   ├── api-index.md
│   │   ├── app-detail.md
│   │   └── gpt-id.md
│   ├── training-flow/
│   │   ├── api-index.md
│   │   ├── drugs.md
│   │   ├── records.md
│   │   └── scenes.md
│   └── dialogue-flow/
│       ├── api-index.md
│       └── get-flow-detail.md
├── examples/
│   ├── home/README.md
│   ├── drug/README.md
│   ├── speech/README.md
│   ├── training/README.md
│   ├── learning/README.md
│   ├── prepare/README.md
│   ├── gpts/README.md
│   ├── basic/README.md
│   ├── scene-image/README.md
│   ├── file/README.md
│   ├── feedback/README.md
│   ├── training-flow/README.md
│   └── dialogue-flow/README.md
└── scripts/
    ├── home/
    │   ├── README.md
    │   ├── summary.py
    │   ├── learning-videos.py
    │   └── product-scenes.py
    ├── drug/
    │   ├── README.md
    │   ├── drug-list.py
    │   ├── scene-list.py
    │   ├── scene-list-by-drug.py
    │   ├── scene-doctor-titles.py
    │   └── scene-hotwords.py
    ├── speech/
    │   ├── README.md
    │   ├── speech-detail.py
    │   ├── speech-finish.py
    │   └── speech-records.py
    ├── training/
    │   ├── README.md
    │   ├── my-stats.py
    │   ├── records.py
    │   └── records-detail.py
    ├── learning/
    │   ├── README.md
    │   ├── video-detail.py
    │   ├── video-progress-get.py
    │   └── video-progress-save.py
    ├── prepare/
    │   ├── README.md
    │   ├── opening-guidance.py
    │   └── opening-guidance-clear.py
    ├── gpts/
    │   ├── README.md
    │   ├── app-detail.py
    │   ├── session.py
    │   ├── sse-suggest.py
    │   └── del-user-token.py
    ├── basic/
    │   ├── README.md
    │   ├── gpt-id.py
    │   └── tts-config.py
    ├── scene-image/
    │   ├── README.md
    │   └── reset.py
    ├── file/
    │   ├── README.md
    │   └── upload-by-url.py
    ├── feedback/
    │   ├── README.md
    │   ├── app-detail.py
    │   └── gpt-id.py
    ├── training-flow/
    │   ├── README.md
    │   ├── drugs.py
    │   ├── records.py
    │   └── scenes.py
    └── dialogue-flow/
        ├── README.md
        └── get-flow-detail.py
```
