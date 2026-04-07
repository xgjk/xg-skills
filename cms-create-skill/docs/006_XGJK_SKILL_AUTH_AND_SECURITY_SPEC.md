# 鉴权与安全规范

本规范只定义一条核心原则：所有需要鉴权的 Skill，统一通过 `cms-auth-skills` 获取并使用具体的 `appKey` 或 `access-token`。

## 1. 统一依赖

所有需要鉴权的 Skill 都统一依赖：

```yaml
dependencies:
  - cms-auth-skills
```

## 2. 统一规则

1. 目标 Skill 不自己实现登录流程。
2. 目标 Skill 不自己维护鉴权方案说明。
3. 目标 Skill 只声明当前动作属于哪一种鉴权模式：`nologin`、`appKey`、`access-token`。
4. 当动作需要 `appKey` 或 `access-token` 时，统一通过 `cms-auth-skills` 获取。

## 3. 禁止事项

- 不在目标 Skill 中重复编写 token、appKey 的获取方式
- 不在目标 Skill 中实现本地登录、换 token、鉴权兜底逻辑

## 4. 交付要求

- 文档中明确写出动作的鉴权模式
- 需要鉴权时，统一指向 `cms-auth-skills`
- 除此之外，不再展开具体鉴权实现细节
