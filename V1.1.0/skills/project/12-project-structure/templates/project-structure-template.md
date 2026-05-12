# 项目结构

> **文档版本**：1.0
> **创建日期**：{{YYYY-MM-DD}}
> **最后更新**：{{YYYY-MM-DD}}

<!-- 填写指引：根据技术栈和项目需求，展开每个目录下的文件结构。参考 Skill 3 系统架构设计中的分层方案。 -->

## 1. 目录树 (Directory Tree)

```text
/
├── specs/                  # 项目核心定义 (产品/技术/结构/规范)
├── docs/                   # 项目文档
├── src/                    # 源代码
│   ├── modules/            # {{基于 PRD 核心板块生成的模块}}
│   │   ├── {{模块A}}/
│   │   └── {{模块B}}/
│   ├── shared/             # 共享代码 (Utils, Components)
│   └── {{框架特定目录}}       # (如 app/, pages/, cmd/)
├── tests/                  # 测试代码
├── .gitignore
├── README.md
└── {{配置文件}}               # (package.json, go.mod 等)
```

### 各目录用途说明

| 目录 | 用途 | 包含内容示例 |
|------|------|------------|
| {{目录名}} | {{用途说明}} | {{文件示例}} |

## 2. 文件命名规范

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| 组件/页面文件 | PascalCase | `UserProfile.tsx` / `UserProfile.vue` / `user_profile.go` |
| 工具函数 | camelCase / snake_case | `formatDate.ts` / `format_date.py` / `format_date.go` |
| 样式文件 | 由前端开发规范定义 | {{按 Skill 13 规范填写}} |
| 测试文件 | 与源文件同名 + `.test` / `_test` / `_test.go` | `UserProfile.test.tsx` / `test_user_profile.py` / `user_service_test.go` |
| 类型/模型定义 | PascalCase | `User.types.ts` / `models/user.py` / `user.go` |

## 3. 关键文件说明 (Key Files)
*   **package.json / go.mod**：项目依赖管理文件。
*   **.env.example**：环境变量示例（禁止上传敏感信息）。
*   **README.md**：项目入口文档，必须包含"如何启动"说明。

## 4. 模块说明 (Module Description)
*   **src/modules/**：业务逻辑的核心。
    *   `{{模块A}}`: {{描述}}
    *   `{{模块B}}`: {{描述}}
*   **src/shared/**：通用工具，不包含具体业务逻辑。

<!-- 填写指引：根据技术栈展开以下目录结构。后端项目参考分层架构示例，前端项目参考组件化架构示例 -->

<!-- 后端分层示例（如 Controller/Service/Repository/DTO） -->
<!-- 前端分层示例（如 pages/components/hooks/stores/api） -->

## 5. 文件放置规则 (Placement Rules)
*   **页面/路由**：放在 `{{框架特定路由目录}}`。
*   **业务逻辑**：放在 `src/modules/{{对应模块}}`，禁止直接写在 UI 组件中。
*   **通用组件**：放在 `src/shared/components`。

---

## 6. 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| {{YYYY-MM-DD}} | 1.0 | 初始版本 | {{作者}} |
