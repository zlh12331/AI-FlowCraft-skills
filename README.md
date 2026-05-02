<p align="center">
  <h1 align="center">AI-FlowCraft</h1>
  <p align="center">
    <strong>从一句话想法到可运行的全栈网站，28 个 AI 技能无缝衔接每一步</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/version-1.0.0-blue" alt="Version" />
    <img src="https://img.shields.io/badge/skills-28-green" alt="Skills" />
    <img src="https://img.shields.io/badge/templates-24-cyan" alt="Templates" />
    <img src="https://img.shields.io/badge/test_scripts-25-purple" alt="Test Scripts" />
    <img src="https://img.shields.io/badge/license-Apache_2.0-orange" alt="License" />
  </p>
  <p align="center">
    <a href="#why">为什么</a> ·
    <a href="#what">是什么</a> ·
    <a href="#features">核心特性</a> ·
    <a href="#skills-map">技能全景</a> ·
    <a href="#supported-stacks">技术栈</a> ·
    <a href="#quick-start">快速开始</a> ·
    <a href="#architecture">设计思路</a> ·
    <a href="#comparison">竞品对比</a> ·
    <a href="#faq">FAQ</a>
    <a href="#Star History">star history</a>
  </p>
  <p align="center">
    <a href="README.en.md">English</a> | 中文
  </p>
</p>

---

## Why · 为什么需要 AI-FlowCraft

用 AI 开发网站，失败的根本原因往往**不是 AI 不够强**，而是**缺乏系统规划**。

> 直接把需求丢给 AI，让它写代码——越往后越偏。需求没想清楚就动手，架构没定好就写实现，测试没规划就上线。每一步的"差不多"都在为后面的"大返工"埋雷。

**AI-FlowCraft 解决的核心问题：**

| 痛点 | 现状 | AI-FlowCraft 的解法 |
|------|------|-------------------|
| 🤷 需求模糊就开干 | AI 直接写代码，结果和预期差很远 | **Skill 1-2** 苏格拉底式提问，强制把需求想清楚再动手 |
| 🏗️ 设计文档缺失 | 跳过架构设计，代码结构混乱、难以维护 | **Skill 3-9** 系统化产出架构、数据库、API、交互等全套设计文档 |
| 📏 编码无规范 | AI 生成的代码风格不一致，质量参差不齐 | **Skill 13-15** 自动生成前后端开发规范，AI 编码时遵循统一标准 |
| 🧪 测试靠运气 | 写完代码才发现 bug，修复成本指数级增长 | **Skill 20** TDD 强制测试先行，**Skill 22-26** 五层测试金字塔兜底 |
| 🔄 跨文档不一致 | API 文档和实际代码对不上，前后端联调痛苦 | 自动化跨文档一致性校验，AC 从需求到测试全程可追溯 |
| 🤖 AI 越界操作 | 需求阶段就写代码、测试阶段改需求，流程混乱 | **边界守卫机制** 给每个 Skill 划硬线，防止 AI 在错误阶段做错误的事 |
| 🧠 AI 遗忘上下文 | 聊多了 AI 就忘了前面说的，反复返工 | **文档驱动编程**，每次讨论都产出文档记录，新窗口通过 PROJECT-CONTEXT 协议自动恢复上下文 |

---

## What · 是什么

**AI-FlowCraft** 是一套 **AI 辅助全栈网站开发的 Skills 工作流系统**。

它将网站开发从"模糊想法"到"测试交付"的全过程，拆解为 **28 个专业 Skill**，每个 Skill 都有明确的角色、职责、输入输出和质量底线。就像一个虚拟的软件开发团队——需求分析师、架构师、前端/后端工程师、测试工程师——各司其职，按流程协作。

**建议在 Trae MTC（内测中...）模式下使用，其他软件（Claude Code、Codex 等）未测试效果。**

```
一句话想法
  → Skill 1  需求讨论（苏格拉底式提问）
  → Skill 2  PRD 生成（验收标准 AC）
  → Skill 3-9  系统设计（架构/数据库/API/交互/视觉）
  → Skill 10-18  规范与初始化（编码规范/项目骨架）
  → Skill 19-21  功能开发（任务拆分/TDD 编码/阶段报告）
  → Skill 22-26  五层测试（单元→组件→集成→E2E→系统）
  → 可运行的全栈网站
```

---

## Features · 核心特性

### 🎯 文档驱动，想清楚再动手

不是上来就写代码。AI-FlowCraft 强制先产出完整的设计文档（PRD、架构、数据库、API、交互设计），每一份文档都经过**两阶段质量检查**——先确保内容足够深入，再确保没有错误。同时，文档也是 AI 的"外部记忆"——每次讨论都有文档记录，新窗口通过 PROJECT-CONTEXT 协议自动恢复上下文，**彻底解决 AI 遗忘上下文的问题**。

### 🔄 AC 贯穿全链路

验收标准（Acceptance Criteria）从需求文档诞生，一路贯穿 API 设计、技术方案、任务规划、TDD 编码、测试用例。每条 AC 都有唯一编号，全程可追溯，确保"需求说的"就是"代码做的"就是"测试验的"。

### 🛡️ 边界守卫

给每个 Skill 划硬线。需求阶段禁止写代码，测试阶段禁止改需求，编码阶段禁止改架构。AI 的"过度热心"是流程的最大敌人——在本系统中，**盲目满足 = 破坏流程**。

### 🧪 TDD 驱动开发

编码阶段强制 **Red → Green → Refactor** 循环。先写失败的测试，再写最少的代码通过测试，最后在测试保护下重构。UI 变化必须浏览器端验收，不靠"看起来差不多"蒙混过关。

### 📐 多技术栈适配

不绑定特定框架。同一套工作流适配 4 种前端框架、6 种后端语言、7 种 ORM、6 种数据库。Skill 中的技术栈特定规则通过 `（仅 XXX 项目适用）` 标注，AI 只执行与当前项目相关的规则。

### 🔍 自动化质量校验

内置 Python 脚本自动检查跨文档一致性——字段名、API 路径、页面清单、响应格式——任何不一致都会被捕获。

---

## Skills Map · 技能全景

28 个 Skill 按开发阶段分为 4 大类：

### 📋 项目启动（Skill 1-18，每个项目执行一次）

| # | Skill | 角色 | 产出 |
|---|-------|------|------|
| 1 | 需求讨论 | 需求分析师 | 需求讨论记录 |
| 2 | PRD 生成 | 产品规划师 | 产品需求文档 + 验收标准(AC) |
| 3 | 系统架构 | 系统架构师 | 技术栈 + 系统架构设计 |
| 4 | 信息架构 | 信息架构师 | 信息架构图（站点地图） |
| 5 | 数据模型约定 | 数据模型设计师 | 数据模型字段约定 |
| 6 | 交互设计 | 交互设计师 | 交互设计文档 |
| 7 | 数据库设计 | 数据库架构师 | ER 图 + 建表 SQL |
| 8 | API 设计 | API 设计师 | API 接口文档 |
| 9 | 设计规范 | 视觉设计师 | Design Token + 视觉规范 |
| 10 | 后端技术方案 | 后端架构师 | 功能级后端技术方案 |
| 11 | 前端技术方案 | 前端架构师 | 功能级前端技术方案 |
| 12 | 项目结构 | 项目结构工程师 | 目录结构定义 |
| 13 | 前端规范 | 前端规范工程师 | 前端开发规范 |
| 14 | 后端规范 | 后端规范工程师 | 后端开发规范 |
| 15 | 协作规范 | 协作规范工程师 | 前后端协作规范 |
| 16 | 环境配置 | 环境配置工程师 | 环境与配置文档 |
| 17 | 开发路线图 | 技术产品经理 | 里程碑 + 开发顺序 |
| 18 | 项目初始化 | 项目初始化工程师 | 项目骨架代码 |

### 💻 功能开发（Skill 19-21，每个功能重复执行）

| # | Skill | 角色 | 产出 |
|---|-------|------|------|
| 19 | 任务规划 | 任务规划工程师 | 垂直切片任务清单 |
| 20 | 编码实现 | 高级开发者 | 代码 + 测试（TDD） |
| 21 | 阶段报告 | 质量报告分析师 | 阶段完成报告 |

### 🧪 测试兜底（Skill 22-26，从内到外五层）

| # | Skill | 测试层级 | 覆盖范围 |
|---|-------|---------|---------|
| 22 | 单元测试 | 函数/方法 | 业务逻辑、工具函数、数据转换 |
| 23 | 组件测试 | UI 组件 | 渲染输出、用户交互、状态变化 |
| 24 | 集成测试 | API + 数据库 | 接口联调、数据一致性、事务 |
| 25 | E2E 测试 | 用户流程 | 核心业务流程、页面跳转 |
| 26 | 系统测试 | 全链路 | 安全扫描、性能测试、兼容性 |

### 🔧 随时可用（Skill 27-28，不限时机）

| # | Skill | 场景 | 说明 |
|---|-------|------|------|
| 27 | 功能变更 | 修改/扩展现有功能 | < 30% 增量更新，> 70% 建议重走流程 |
| 28 | Bug 修复 | 代码行为与需求不符 | 先判断是不是 bug，最小改动修复 |

---

## Supported Stacks · 支持的技术栈

AI-FlowCraft 通过"范围标注"机制适配多种技术栈。Skill 中的技术栈特定规则标注为 `（仅 XXX 项目适用）`，AI 只执行与当前项目匹配的规则。

### 前端

| 类别 | 支持的技术 |
|------|-----------|
| **框架** | React 18+、Vue 3+、Angular 17+、Svelte 4+、Next.js 14+、Nuxt 3+、Astro 4+ |
| **语言** | TypeScript 5+（强制严格模式） |
| **构建工具** | Vite 5+、Webpack 5+、Turbopack |
| **样式方案** | TailwindCSS 3+、CSS Modules、Styled Components、UnoCSS |
| **状态管理** | Zustand、Redux Toolkit、Pinia、NgRx、MobX |
| **测试框架** | Vitest、Jest、React Testing Library、Vue Test Utils |
| **E2E 框架** | Playwright、Cypress |

### 后端

| 类别 | 支持的技术 |
|------|-----------|
| **语言/框架** | Node.js (NestJS / Express / Fastify)、Python (Django / FastAPI)、Go (Gin / Echo)、Java (Spring Boot)、Rust (Actix-web / Axum)、C# (.NET 8+) |
| **ORM** | Prisma、TypeORM、Drizzle ORM、SQLAlchemy、GORM、Entity Framework Core |
| **数据库** | PostgreSQL、MySQL、SQLite、MongoDB、Redis、Elasticsearch |
| **认证方案** | JWT、Session、OAuth 2.0 |
| **API 风格** | REST、GraphQL、gRPC |
| **消息队列** | RabbitMQ、Kafka、Redis Streams |

### 项目类型适配

| 项目类型 | 可跳过的 Skill |
|---------|--------------|
| 纯后端 API | Skill 4, 6, 9, 11, 13 |
| 纯前端应用 | Skill 7, 8, 14 |
| 单功能项目 | 可合并 Skill 2-9 |

---

## Quick Start · 快速开始

### 前置条件

- 一个 AI 编程助手（Trae MTC）
- 将本仓库的 Skill 文件导入你的 AI 工作环境
- 项目开始时，`specs/` 文件夹及其下的 4 个文件（`GUARDRAILS.md`、`PROJECT-CONTEXT.md`、`validate_consistency.py`、`report_config.py`）必须存在

### 三步启动一个新项目

**第一步：梳理需求**

```
"使用 Skill 1 帮我梳理需求，我想做一个..."
```

AI 会通过苏格拉底式提问帮你把模糊想法变成清晰的项目描述。

**第二步：生成 PRD**

```
"使用 Skill 2 生成 PRD"
```

AI 会产出包含验收标准（AC）的产品需求文档。复杂项目会自动为每个功能生成独立文档。

**第三步：按流程推进**

```
"使用 Skill 3 设计系统架构"
```

之后按 Skill 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 17 → 18 顺序执行，完成全部设计和项目初始化。

### 功能开发循环

```
"使用 Skill 19 拆分任务" → "使用 Skill 20 编码实现" → "使用 Skill 21 生成报告"
```

每个功能重复这个循环。

### 测试兜底

```
"使用 Skill 22 开始单元测试"
```

按 22 → 23 → 24 → 25 → 26 从内到外执行五层测试。

> 💡 **建议**：项目启动阶段（Skill 1-18）尽量在同一个对话窗口中连续执行，避免上下文丢失。

---

## Architecture · 设计思路

### 五个核心机制

#### 1. 边界守卫（Guardrails）

每个 Skill 都有明确的职责边界。AI 在生成回复前必须自检：

- **Scope Check**：用户的请求是否在当前 Skill 的职责范围内？
- **Artifact Check**：我即将生成的是文档/计划，还是代码/操作？

如果当前是需求阶段但用户要求写代码，AI 会拒绝并引导回当前职责——不是"对不起我不能"，而是展现专业性："为了避免过早陷入技术细节导致返工，我们需要先在业务层面确认..."

#### 2. 项目上下文协议（Project Context Protocol）

强制 AI 在每个 Skill 执行前建立项目上下文。必读 6 个核心文档：PRD、技术栈、系统架构、信息架构、数据模型、项目结构。

> 花费 5 分钟读取文档，节省 2 小时返工时间。

#### 3. AC 贯穿全链路

```
Skill 2 PRD 产出 AC → Skill 8 API 映射 AC → Skill 10/11 技术方案映射 AC
→ Skill 19 任务承接 AC → Skill 20 TDD 验证 AC → Skill 22-26 测试兜底
```

AC 编号格式：`{功能缩写}-AC-{序号}`（如 `AUTH-AC-001`），覆盖三类场景：Happy Path / Edge & Error / Business Rules。

#### 4. 文档质量检查循环

每个文档产出后执行两阶段检查：

- **阶段 A（深度完善）**：逐章审视内容深度、完整性、可执行性，最少 2 次、最多 5 次循环
- **阶段 B（Bug 检查）**：检查内部一致性、跨文档一致性、AC 覆盖、占位符残留，最少 1 次、最多 3 次循环

先让内容足够好，再让内容没有错。

#### 5. TDD 驱动开发

编码阶段强制 Red-Green-Refactor 循环：

- **RED**：先写失败的测试
- **GREEN**：写最少代码通过测试
- **REFACTOR**：在测试保护下优化

TDD 通过 ≠ 任务完成。有 UI 变化的任务必须浏览器端验收。

### 项目结构

```text
ai-flowcraft/
├── README.md                                  ← 中文文档
├── README.en.md                               ← 英文文档
├── assets/                                    ← 项目资源
│   └── logo.jpg                               ← 项目 Logo
├── specs/                                     ← 全局协议 + 工具脚本
│   ├── GUARDRAILS.md                          ← 边界守卫规则
│   ├── PROJECT-CONTEXT.md                     ← 项目上下文协议
│   ├── validate_consistency.py                ← 跨文档一致性校验
│   └── report_config.py                       ← 测试报告配置
└── skills/                                    ← 28 个 Skill
    ├── project/                               ← 项目启动（Skill 1-18）
    │   ├── 1-project-requirements-clarification/
    │   ├── 2-project-prd-generation/
    │   ├── ...
    │   └── 18-project-initialization/
    ├── feature/                               ← 功能开发 + 测试（Skill 19-28）
    │   ├── 19-feature-task-planning/
    │   ├── 20-feature-implementation/
    │   ├── ...
    │   └── 28-bugfix-workflow/
```

### 文件统计

| 类型 | 数量 | 说明 |
|------|------|------|
| SKILL.md | 28 个 | 每个 Skill 的定义文件（角色、工作流程、底线规则） |
| 输出模板（assets/） | 24 个 | Skill 1-21、27-28 的输出文档模板 |
| 测试脚本（scripts/） | 25 个 | Skill 22-26 各含 5 个 Python 脚本 |
| 工具脚本（specs/） | 2 个 | 跨文档校验 + 报告配置 |
| 全局协议（specs/） | 2 个 | GUARDRAILS + PROJECT-CONTEXT |
| **合计** | **81 个文件** | |

### 运行时产出

使用 AI-FlowCraft 开发项目后，会产出以下文件结构：

```text
{你的项目}/
├── specs/                          ← 项目规划文档（19+ 份）
│   ├── 产品需求文档.md
│   ├── 系统架构设计.md、技术栈.md
│   ├── 信息架构图.md、数据模型字段约定.md
│   ├── 交互设计文档.md、数据库设计.md
│   ├── API接口文档.md、设计规范.md
│   ├── 项目结构.md、前端/后端开发规范.md
│   ├── 前后端协作规范.md、环境与配置文档.md
│   ├── 开发路线图.md
│   └── features/                   ← 功能级文档
│       ├── {功能名}.md
│       ├── {功能名}_后端技术方案.md
│       ├── {功能名}_前端技术方案.md
│       └── {功能名}_任务规划.md
├── src/                            ← 你的源代码
│   ├── frontend/                   ← 前端项目
│   └── backend/                    ← 后端项目
└── docs/                           ← 开发记录
    ├── 开发记录/                   ← 初始化记录、切片完成记录
    ├── 测试报告/                   ← 单元/组件/集成/E2E/系统测试报告
    └── BUG修复文档/                ← Bug 修复文档
```

---

## Comparison · 竞品对比

| 维度 | AI-FlowCraft | .cursorrules | .windsurfrules | CLAUDE.md |
|------|-------------|-------------|---------------|----------|
| **定位** | 完整开发工作流（28 个 Skill） | AI 编码行为约束 | AI 编码行为约束 | AI 编码行为约束 |
| **覆盖范围** | 需求 → 设计 → 编码 → 测试 | 仅编码 | 仅编码 | 仅编码 |
| **Skill 数量** | 28 个 | 1 个文件 | 1 个文件 | 1 个文件 |
| **文档产出** | 19+ 份设计文档 | 无 | 无 | 无 |
| **流程控制** | 边界守卫 + 阶段强制顺序 | 无 | 无 | 无 |
| **质量保证** | 两阶段文档检查 + AC 可追溯 + 自动化校验 | 无 | 无 | 无 |
| **测试策略** | 五层测试金字塔 | 无 | 无 | 无 |
| **跨文档一致性** | Python 脚本自动校验 | 无 | 无 | 无 |

> **一句话总结**：.cursorrules 告诉 AI "怎么写代码"，AI-FlowCraft 告诉 AI "怎么做一个项目"——从想清楚要做什么，到把每一行代码写对、测对。

---

## FAQ · 常见问题

### 支持中文项目吗？

完全支持。所有 Skill 的文档模板、交互话术、产出文件名均支持中文。你可以在需求讨论阶段指定项目文档使用中文，AI 会自动适配。

### 可以只执行部分 Skill 吗？

可以。AI-FlowCraft 的 28 个 Skill 是模块化设计的，你可以按需使用：

- 只想做需求分析？执行 Skill 1-2
- 只想生成设计文档？执行 Skill 3-9
- 只想用 TDD 编码？执行 Skill 19-20
- 只想补测试？执行 Skill 22-26

但建议首次使用时完整执行一次，体验完整流程的价值。

### 非全栈项目能用吗？

可以。系统内置了项目类型适配机制：

- **纯后端 API**：自动跳过前端相关 Skill（4, 6, 9, 11, 13）
- **纯前端应用**：自动跳过后端相关 Skill（7, 8, 14）
- **单功能项目**：可以合并 Skill 2-9，简化流程

### 必须按顺序执行吗？

项目启动阶段（Skill 1-18）建议按顺序执行，因为后续 Skill 依赖前面 Skill 的产出文档。功能开发阶段（Skill 19-21）和测试阶段（Skill 22-26）可以按需执行。

### 和 AI 编码工具（Cursor / Copilot）冲突吗？

不冲突。AI-FlowCraft 是工作流层面的规范，和具体的 AI 编码工具无关。你可以在 Cursor 中使用 Claude + AI-FlowCraft，也可以在 VS Code 中使用 Copilot + AI-FlowCraft。AI-FlowCraft 关注的是"做什么、按什么顺序做、做到什么标准"，而不是"用什么工具做"。

### 一个项目需要多久？

取决于项目复杂度：

- **简单项目**（单功能）：Skill 1-18 不到 1 小时对话，功能开发按实际代码量
- **中等项目**（5-10 个功能）：Skill 1-18 约 2-3 小时对话
- **复杂项目**（10+ 功能）：建议分多次会话完成，每次聚焦一个阶段

> 提示：项目启动阶段（Skill 1-18）是一次性投入，后续每个功能只需执行 Skill 19-21 循环。

### 如何处理 AI 上下文窗口限制？

- 项目启动阶段（Skill 1-18）尽量在**同一个对话窗口**中连续执行
- 功能开发阶段可以**按功能开新窗口**，AI 会通过 PROJECT-CONTEXT 协议自动读取项目文档建立上下文
- 每份设计文档都是独立可读的，新窗口不需要历史对话记录

## Star History

<p align="center">
  <img src="https://api.star-history.com/svg?repos=zlh12331/AI-FlowCraft&type=Date" alt="Star History Chart" width="600" />
</p>

---

## License

[Apache License 2.0](LICENSE)

---

<p align="center">
  用 AI-FlowCraft 构建你的下一个全栈项目 ⚡
</p>
