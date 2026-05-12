# 技术栈选型

> **文档版本**：1.0
> **创建日期**：{{YYYY-MM-DD}}
> **最后更新**：{{YYYY-MM-DD}}

## 1. 项目类型
<!-- 填写指引：选择项目类型，决定哪些技术栈章节需要填写 -->
*   **项目类型**：{{全栈 / 纯前端 / 纯后端}}
*   **说明**：纯后端项目将前端章节标注为"不适用"；纯前端项目将后端章节标注为"不适用"

## 2. 核心决策 (Key Decisions)

| 决策领域 | 选定方案 | 备选方案 | 选择理由 |
|---------|---------|---------|---------|
| {{决策领域}} | {{选定方案}} | {{备选方案}} | {{为什么选它}} |

## 3. 前端 (Frontend)
*   **框架**：{{例如: React / Vue / Next.js}}
*   **样式方案**：{{例如: TailwindCSS}}
*   **状态管理**：{{例如: Zustand / Redux}}

## 4. 后端 (Backend)
*   **运行时/语言**：{{例如: Node.js / Go / Python}}
*   **Web 框架**：{{例如: Express / Gin / FastAPI}}
*   **API 协议**：{{例如: REST / GraphQL / gRPC}}

## 5. 数据存储 (Database)
*   **主数据库**：{{例如: PostgreSQL / MySQL}}
*   **缓存 (可选)**：{{例如: Redis}}
<!-- 填写指引：如项目暂不需要此能力，填写'暂不需要。原因：[说明]。后续扩展路径：[说明]'。 -->

## 6. 基础设施 & 工具 (Infra & Tools)

*   **部署**：{{例如: Vercel / Docker / AWS}}
*   **包管理**：{{例如: pnpm / go mod / poetry}}
*   **CI/CD**：{{例如: GitHub Actions / GitLab CI / Jenkins}}
    *   *选择理由*: {{例如：GitHub Actions 与仓库深度集成，配置简单，免费额度充足}}

## 7. 测试工具链 (Testing Tools)
*单元测试、组件测试、E2E 测试和 Mock 工具的选型。*

*   **单元测试框架**：{{例如: Vitest / Jest / pytest}}
    *   *选择理由*: {{例如：Vitest 与 Vite 深度集成，速度快}}
*   **组件测试**：{{例如: Testing Library / Storybook}}
    *   *选择理由*: {{例如：Testing Library 关注用户行为而非实现细节}}
*   **E2E 测试**：{{例如: Playwright / Cypress}}
    *   *选择理由*: {{例如：Playwright 支持多浏览器，CI 集成方便}}
*   **Mock 工具**：{{例如: MSW (Mock Service Worker) / pytest-mock}}
    *   *选择理由*: {{例如：MSW 可在浏览器和网络层同时拦截请求}}

## 8. 监控工具链 (Monitoring Tools)
*日志、APM 和错误追踪工具的选型（可选，根据项目复杂度决定）。*
<!-- 填写指引：如项目暂不需要此能力，填写'暂不需要。原因：[说明]。后续扩展路径：[说明]'。 -->

*   **日志 (Logging)**：{{例如: Pino / Winston / Loguru}}
    *   *选择理由*: {{例如：Pino 性能优异，JSON 格式便于后续分析}}
*   **APM (应用性能监控)**：{{例如: OpenTelemetry + Grafana / Datadog}}
    *   *选择理由*: {{例如：OpenTelemetry 为开放标准，避免厂商锁定}}
*   **错误追踪 (Error Tracking)**：{{例如: Sentry / Rollbar}}
    *   *选择理由*: {{例如：Sentry 支持自动捕获未处理异常，提供丰富的上下文信息}}

---

## 9. 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| {{YYYY-MM-DD}} | 1.0 | 初始版本 | {{作者}} |
