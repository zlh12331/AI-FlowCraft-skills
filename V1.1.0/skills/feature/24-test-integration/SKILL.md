---
name: "24-test-integration"
description: "扫描项目源码，自动识别 API 路由、数据库模型、服务连接等集成点，编写并运行集成测试代码，验证模块间的协作是否正确，生成测试报告。当用户提到"集成测试"、"API测试"、"接口测试"、"端到端API测试"、"数据库集成测试"、"服务间测试"、"集成验证"、"写集成测试"时使用。"
---

# 集成测试（Integration Test）

## 描述

AI 阅读项目源码，自动识别 API 路由、数据库模型、服务连接等集成点，编写并运行集成测试代码，验证模块间的协作是否正确。

### 项目上下文协议

> **本节定义 AI 如何获取项目上下文。每次执行前必须先读取项目上下文。**

读取项目上下文文件：`cat specs/PROJECT-CONTEXT.md`

如果文件不存在，向用户询问以下信息并创建该文件：
- 项目名称、技术栈、项目路径
- 已完成的功能列表和对应的 specs 文档路径
- 当前开发阶段

### 边界守卫

> **本节定义 AI 的行为边界。违反任何一条守卫则执行不合格。**

读取全局守卫规则：`cat specs/GUARDRAILS.md`

核心守卫：
1. **禁止修改源码**：测试代码不得修改被测源码，只能读取和验证
2. **禁止跳过失败测试**：不得将失败测试标记为 skip，必须记录失败原因
3. **测试必须独立**：每个测试用例必须独立运行，不依赖其他测试的执行顺序或状态

### 前置条件

| # | 前置条件 | 验证方式 | 不满足时的处理 |
|---|---------|---------|--------------|
| 1 | 源码可访问（必须） | `ls src/` | 报错并终止 |
| 2 | 项目类型已识别（必须） | 检查 package.json/pyproject.go.mod 等 | 报错并终止 |
| 3 | API 服务可启动（建议） | 检查 package.json scripts | [降级执行] 使用 Mock |
| 4 | specs 目录存在（建议） | `ls specs/` | [降级执行] 不读取 specs，仅基于源码分析 |
| 5 | 功能需求文档存在（建议） | `ls specs/features/` | [降级执行] 不关联 AC，仅基于源码分析 |
| 6 | 阶段完成报告（建议） | `docs/开发记录/{功能名}_阶段完成报告.md` 存在，用于了解当前代码状态和已知问题 | [降级执行] 不读取阶段报告，仅基于源码分析 |

### 与其他测试层级的区别

| 维度 | 单元测试 | 组件测试 | **集成测试** |
|------|---------|---------|-------------|
| 测试对象 | 单个函数 | 单个 UI 组件 | **多个模块协作** |
| 运行环境 | Node.js / Python | jsdom | **真实/模拟服务器** |
| 外部依赖 | 全部 Mock | Mock 子组件 | **使用真实数据库/缓存** |
| 测试内容 | 输入→输出 | 渲染→交互 | **请求→处理→响应→持久化** |

- **与单元测试的区别**：单元测试（Skill 22）可以 mock 所有外部依赖（数据库、第三方服务）。集成测试（本 Skill）至少要连接一个真实的数据库，验证 SQL 查询、事务、索引等数据库层面的行为。

## 使用场景

- 测试 API 接口的请求/响应（REST / GraphQL）
- 测试数据库 CRUD 操作（增删改查）
- 测试前端与后端的接口对接
- 测试服务间调用（微服务通信）
- 测试缓存、消息队列等中间件集成
- 测试认证/授权流程的完整链路

### 不适用场景
- **单元测试**：请引导至 `22-test-unit` Skill
- **组件测试**：请引导至 `23-test-component` Skill
- **E2E 测试**：请引导至 `25-test-e2e` Skill
- **系统测试**：请引导至 `26-test-system` Skill

## 指令

### 输入
- 项目源码目录路径
- `resources/` 目录下的辅助脚本
- `examples/` 目录下的测试示例作为参考

### 底线规则

> 以下规则补充全局底线规则（见 GUARDRAILS.md），仅定义本 Skill 特有的约束。任何一条不满足则执行不合格。

1. **测试文件必须保存在项目目录**：测试文件必须保存在项目的 `tests/` 目录下，不得保存在临时目录。
2. **每个测试必须有注释**：每个测试用例必须有注释说明测试目的和预期行为。
3. **禁止硬编码敏感信息**：测试代码中不得包含真实的密码、Token、API Key。
4. **Mock 必须有清理**：每个使用 Mock 的测试必须在 afterEach/afterAll 中清理 Mock 状态。
5. **失败测试必须有原因分析**：报告中每个失败的测试必须包含失败原因分析和修复建议。
6. **API 端点必须覆盖**：所有 API 端点（包括认证、CRUD、错误处理）必须有集成测试。
7. **测试数据必须隔离**：每个测试用例必须独立准备和清理测试数据，不得依赖其他测试创建的数据。推荐使用事务回滚（`BEGIN` → `ROLLBACK`）或 `TRUNCATE` 清理方式（仅关系型数据库适用；MongoDB 可使用 `deleteMany()` 或 `dropDatabase()`；Redis 可使用 `FLUSHDB`）。禁止测试用例之间存在数据依赖（如"测试 B 依赖测试 A 创建的用户"）。
8. **外部 API 必须使用 Mock**：不得在集成测试中调用真实的第三方 API（如支付网关、短信服务、邮件服务）。必须使用 Mock Server 或 Nock/MSW（Node.js 项目）、responses（Python 项目）、WireMock（Java 项目）等工具模拟外部依赖，Mock 响应必须与真实 API 的响应格式一致。
9. **断言值必须基于实际源码**：编写测试前必须先读取被测 API 的源码（Controller + Service），断言中的状态码、响应字段名、错误消息必须与源码中的实际实现一致，不得凭记忆或猜测编写断言。此规则与 Skill 22 规则 11 对齐。
10. **测试配置必须已存在**：执行集成测试前，必须确认测试框架配置文件（jest.config.ts/vitest.config.ts）（TypeScript/JavaScript 项目）；Python 项目对应 pytest.ini 或 pyproject.toml，Java 项目对应 pom.xml 中的 surefire 配置。如未创建，不得直接安装和配置，必须提示用户先完成项目初始化。
11. **AC 覆盖**：如果功能需求文档存在，集成测试用例必须覆盖 AC 中与 API 接口和数据一致性相关的验收标准
12. **真实数据库测试**：集成测试必须使用测试数据库（推荐 SQLite in-memory 或 Docker PostgreSQL test container），验证真实的数据库读写操作。完全 mock 数据库客户端（如 `jest.mock` Prisma）的测试属于路由层单元测试，应归入 Skill 22（单元测试），不得归入本 Skill。
13. **设计文档驱动的数据一致性测试**：如果后端技术方案（Skill 10 产出）中包含"Service 层业务规则"章节，集成测试必须覆盖涉及数据一致性和并发控制的规则。具体要求：(1) 在第二步（扫描集成点）之前，先读取 `specs/features/{功能名}_后端技术方案.md`，提取"Service 层业务规则"章节中涉及数据一致性、级联操作、并发控制的规则项；(2) 为乐观锁校验编写并发更新冲突测试（模拟两个请求同时更新同一资源）；(3) 为级联删除/更新编写数据状态验证测试（删除父资源后验证子资源的实际状态）；(4) 在测试报告中增加"业务规则覆盖"章节，逐项列出每条规则的集成测试覆盖状态。

**推荐**：Node.js + Supertest（轻量、易配置）。其他选项参见 `examples/integration-test-examples.md`。

### 交互准则

1. **主动分析，不要被动询问**：不要问用户"需要测试什么"，你应该主动分析项目源码和 specs 文档，推荐测试策略
2. **保持务实**：小项目不需要追求 100% 覆盖率，优先测试核心业务逻辑和关键路径
3. **结果导向**：测试报告中的"改进建议"必须具体可操作（如"为 UserService.login() 添加密码强度校验的边界值测试"），不要写泛泛建议（如"提高覆盖率"）
4. **失败即信息**：测试失败不是坏事，每个失败都提供了改进代码质量的机会。报告中必须分析失败根因，而非仅记录失败现象

### 辅助脚本

本 Skill 提供以下辅助脚本（位于 `resources/` 目录）：

| 脚本 | 用途 | 用法 |
|------|------|------|
| `scan_integrations.py` | 扫描项目中的集成点（API/DB/服务） | `python resources/scan_integrations.py <项目路径> [输出JSON]` |
| `generate_integration_tests.py` | 根据扫描结果生成集成测试代码 | `python resources/generate_integration_tests.py <扫描结果JSON> <输出目录>` |
| `run_integration_tests.py` | 运行集成测试并收集结果 | `python resources/run_integration_tests.py <项目路径> [--coverage]` |
| `generate_report.py` | 生成 Markdown 格式测试报告 | `python resources/generate_report.py <测试结果JSON> <报告路径> [扫描结果JSON]` |

> **注意**：辅助脚本用于预处理和批量操作，AI 仍需根据源码分析结果手动完善测试代码中的具体测试值和断言。

### 执行流程

#### 第一步：环境检测与准备

**1.1 识别项目类型和技术栈**

```bash
# 前端项目
cat package.json | grep -E '"(react|vue|angular|next|nuxt|axios|fetch)"'

# 后端项目
# Node.js
cat package.json | grep -E '"(express|koa|fastify|nestjs|prisma|sequelize|mongoose)"'
# Python
cat requirements.txt 2>/dev/null | grep -E "(flask|django|fastapi|sqlalchemy|pymongo|redis)"
cat pyproject.toml 2>/dev/null | grep -E "(flask|django|fastapi|sqlalchemy)"
# Java
cat pom.xml 2>/dev/null | grep -E "(spring-boot|mybatis|hibernate|jpa)"
# Go
cat go.mod 2>/dev/null | grep -E "(gin|echo|gorm|sqlx)"
# Rust（仅 Rust 项目适用）
cat Cargo.toml 2>/dev/null | grep -E "(actix|axum|tokio|serde)"
# C#（仅 C# 项目适用）
cat *.csproj 2>/dev/null | grep -E "(Microsoft.AspNetCore|EntityFramework)" || cat *.sln 2>/dev/null
```

**1.2 检测已安装的测试框架**

```bash
# Node.js 后端
npx jest --version 2>/dev/null
npx vitest --version 2>/dev/null  # Vitest（仅 Node.js 项目适用，作为 Jest 的替代方案）
npx supertest --version 2>/dev/null

# Python
python -m pytest --version 2>/dev/null

# Java
mvn test -v 2>/dev/null

# Go
go test ./... 2>/dev/null

# Rust（仅 Rust 项目适用）
cargo test --version 2>/dev/null

# C#（仅 C# 项目适用）
dotnet test --version 2>/dev/null
```

**1.3 安装测试框架（如未安装）**

| 技术栈 | 测试框架 | 安装命令 |
|--------|---------|---------|
| Express/Koa (Node.js) | Jest + Supertest | `npm install -D jest supertest @types/supertest ts-jest` |
| Express/Koa (Node.js) | Vitest + Supertest（仅 Node.js 项目适用，作为 Jest 的替代方案） | `npm install -D vitest supertest @types/supertest` |
| NestJS | Jest (内置) | 已内置，无需额外安装 |
| Flask/Django/FastAPI (Python) | pytest + httpx | `pip install pytest pytest-asyncio httpx pytest-cov --break-system-packages` |
| Spring Boot (Java) | JUnit 5 + MockMvc | Maven/Gradle 已内置 |
| Gin/Echo (Go) | testing + httptest | Go 标准库，无需安装 |
| Actix-web/Axum (Rust) | testing + reqwest | Rust 标准库 testing 模块 + reqwest crate（HTTP 客户端） |
| ASP.NET Core (C#) | xUnit + WebApplicationFactory | `dotnet add package Microsoft.AspNetCore.Mvc.Testing` |

**1.4 配置测试环境**

```bash
# Node.js - Jest 配置（API 测试）
cat > jest.config.js << 'EOF'
module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/__tests__/integration/**/*.test.ts'],
  setupFilesAfterSetup: ['<rootDir>/jest.setup.ts'],
  testTimeout: 30000,  // API 测试超时 30 秒
};
EOF

# Python - pytest 配置（API 测试）
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests/integration
python_files = test_*.py
addopts = -v --tb=short --timeout=30
EOF
```

**1.5 准备测试基础设施**

集成测试需要真实的或模拟的外部依赖：

```bash
# 检查是否有 Docker（用于启动测试数据库）
docker --version 2>/dev/null

# 检查是否有测试数据库配置
cat .env.test 2>/dev/null
cat docker-compose.test.yml 2>/dev/null
```

| 依赖类型 | 推荐方案 | 说明 |
|---------|---------|------|
| 数据库 | SQLite（内存） / Docker PostgreSQL | 轻量用 SQLite，生产一致用 Docker |
| MySQL（仅 MySQL 项目适用） | Docker MySQL 或测试环境 MySQL 实例 | 与生产环境 MySQL 版本一致 |
| Elasticsearch（仅 Elasticsearch 项目适用） | Docker Elasticsearch 或 Testcontainers | 全文搜索/日志分析场景使用 |
| Redis | Docker Redis / fakeredis | Python 用 fakeredis，其他用 Docker |
| 消息队列 | Docker RabbitMQ / Mock | 集成测试通常 Mock |
| 外部 API | Mock Server / Nock | 不依赖真实外部服务 |
| 文件存储 | 临时目录 / MinIO | 使用 tmpdir |

#### 第二步：扫描集成点

**2.1 运行扫描脚本**

```bash
# 扫描项目中的集成点
python resources/scan_integrations.py <项目路径> ./integration_scan_result.json
```

扫描脚本会自动识别：
- **API 路由**：REST 端点（GET/POST/PUT/DELETE）、GraphQL resolver
- **数据库模型**：ORM 模型定义（Prisma/Sequelize/SQLAlchemy/Django Model/GORM）
- **中间件**：认证、日志、错误处理等
- **服务连接**：外部 API 调用、消息队列、缓存

**2.2 AI 补充分析（脚本无法自动完成的部分）**

对扫描结果中的每个集成点，AI 需要阅读源码进行深度分析：

1. **API 路由分析**：
   - HTTP 方法（GET/POST/PUT/DELETE/PATCH）
   - 请求参数（Path 参数、Query 参数、Request Body）
   - 请求体格式（JSON Schema、FormData）
   - 响应格式（状态码、响应体结构）
   - 认证要求（是否需要 Token、权限级别）
   - 依赖的服务（数据库操作、外部 API 调用）

2. **数据库模型分析**：
   - 表结构（字段、类型、约束）
   - 关联关系（一对一、一对多、多对多）
   - 索引和唯一约束
   - 钩子/触发器（beforeSave、afterCreate）

3. **确定测试策略**：
   - 是否需要真实数据库（SQLite 内存 vs Docker PostgreSQL）
   - 是否需要 Mock 外部服务
   - 是否需要测试认证流程
   - 测试数据如何准备（Fixture / Factory / Seed）

**2.3 确定测试优先级**

| 优先级 | 集成点类型 | 说明 |
|-------|-----------|------|
| P0 | 认证/授权 API | 登录、注册、Token 刷新、权限验证 |
| P0 | 核心业务 API | 支付、订单、数据提交 |
| P1 | CRUD API | 增删改查接口 |
| P1 | 数据库模型 | 核心表的操作和约束 |
| P2 | 文件上传/下载 | 文件处理接口 |
| P2 | 搜索/过滤 | 复杂查询接口 |
| P3 | WebSocket/实时通信 | 实时功能 |
| P3 | 第三方集成 | 支付网关、短信、邮件 |

#### 第三步：编写集成测试

**3.1 生成测试代码骨架**

```bash
python resources/generate_integration_tests.py ./integration_scan_result.json ./generated_integration_tests/
```

> **重要**：生成的测试代码仅是骨架，AI 必须根据源码分析结果填充具体的测试数据、请求参数和预期响应。

**3.2 AI 编写完整测试代码**

对每个集成点，AI 需要编写以下测试用例：

| 测试类型 | 覆盖场景 | 示例 |
|---------|---------|------|
| 正向测试 | 合法请求 → 预期响应 | POST /api/users + 合法数据 → 201 + 用户对象 |
| 参数验证 | 缺少必填字段 → 400 | POST /api/users + 无用户名 → 400 + 错误信息 |
| 认证测试 | 无 Token / 过期 Token → 401 | GET /api/profile + 无 Token → 401 |
| 权限测试 | 普通用户访问管理员接口 → 403 | DELETE /api/users/1 + 普通用户 → 403 |
| 数据一致性 | 创建后数据库中存在对应记录 | POST /api/users → 查询数据库验证记录存在 |
| 边界值 | 分页边界、数据量边界 | GET /api/users?page=999 → 空数组 |
| 并发测试 | 重复提交 / 竞态条件 | POST /api/orders 同一订单两次 → 幂等处理 |
| 错误处理 | 服务不可用 / 超时 → 友好错误 | Mock 外部 API 超时 → 503 + 错误信息 |

**3.3 测试代码规范**

参见下方"示例"章节中各语言的集成测试代码示例。

#### 第四步：运行测试

**4.1 运行测试脚本**

```bash
python resources/run_integration_tests.py <项目路径> --coverage
```

或手动运行：

```bash
# Node.js
npx jest --testPathPattern="integration" --verbose --runInBand
# Node.js - Vitest（仅 Node.js 项目适用，作为 Jest 的替代方案）
npx vitest run --dir tests/integration --reporter verbose

# Python
python -m pytest tests/integration/ -v --tb=short

# Java
mvn test -Dtest="*IntegrationTest"

# Go
go test ./tests/integration/... -v

# Rust（仅 Rust 项目适用）
cargo test --test integration -- --nocapture

# C#（仅 C# 项目适用）
dotnet test --filter "Category=Integration" --verbosity normal
```

**4.2 处理测试失败**

```
集成测试失败
  ├─ 分析失败信息（HTTP 状态码不匹配 / 响应体不一致 / 数据库断言失败）
  ├─ 读取失败测试的源码 + 被测 API 源码
  ├─ 判断失败原因：
  │   ├─ 测试数据问题（Fixture 数据过期、依赖顺序错误）
  │   │   └─ 更新测试数据 → 重新运行
  │   ├─ 测试代码写错了（断言值不对、请求参数错误）
  │   │   └─ 修复测试代码 → 重新运行
  │   ├─ 环境问题（数据库未启动、端口冲突、环境变量缺失）
  │   │   └─ 修复环境配置 → 重新运行
  │   └─ 源码有 Bug（API 逻辑错误、数据库约束问题）
  │       └─ 记录为 Bug 报告（不修改源码）
  └─ 最多重试 3 次，仍失败则记录并继续下一个
```

**4.3 集成测试注意事项**

| 问题 | 解决方案 |
|------|---------|
| 测试数据污染 | 每个测试用例前后清空数据库 / 使用事务回滚 |
| 测试顺序依赖 | 每个测试独立准备数据，不依赖其他测试 |
| 外部服务不可用 | Mock 外部 API / 使用 Docker Compose 启动依赖 |
| 端口冲突 | 使用随机端口 / 配置 test 环境专用端口 |
| 测试速度慢 | 并行运行（注意数据库隔离）/ 使用 SQLite 内存模式 |

#### 第五步：生成报告

**5.1 运行报告生成脚本**

```bash
python resources/generate_report.py ./integration_test_result.json docs/测试报告/集成测试报告.md ./integration_scan_result.json
```

**5.2 输出模板**

> **输出文件路径**：`docs/测试报告/集成测试报告.md`
> **报告格式**：Markdown，由辅助脚本 `generate_report.py` 自动生成
> **占位符规则**：`{{}}` 标记的占位符必须替换为实际值，不得保留占位符

测试报告必须包含以下章节：
1. 测试概览（项目信息、测试框架、扫描/编写统计）
2. 测试结果（通过/失败/跳过/通过率）
3. 覆盖情况（函数/组件/端点覆盖详情）
4. 失败详情（失败测试的错误信息和修复建议）
5. 改进建议（基于测试结果的具体改进建议）

**5.3 报告内容**

生成的 Markdown 报告包含：

```markdown
# 集成测试报告

## 概览
| 指标 | 数值 |
|------|------|
| 项目类型 | Node.js / Python / Java / Go / Rust / C# |
| 测试框架 | Jest + Supertest / pytest + httpx |
| 扫描集成点总数 | XX |
| 编写测试集成点数 | XX |
| 测试用例总数 | XX |

## 测试结果
| 指标 | 数值 |
|------|------|
| 通过 | XX |
| 失败 | XX |
| 跳过 | XX |
| 通过率 | XX% |

## 集成点覆盖情况
| 集成点 | 类型 | 方法 | 测试用例数 | 状态 |
|--------|------|------|-----------|------|

## 发现的缺陷
（如有 API Bug，在此列出）

## 改进建议
（API 设计改进、错误处理改进建议）
```

### 通过标准

| 指标 | 标准 |
|------|------|
| 测试通过率 | 100%（源码缺陷已记录的除外） |
| P0/P1 API 覆盖率 | 100% |
| 所有 API 端点至少 1 个正向测试 | 是 |
| 认证/授权相关测试 | 全部覆盖 |
| 错误响应格式一致 | 是（统一的错误格式） |

### 注意事项

- 测试代码必须带注释，说明测试目的和预期行为
- **不要修改源码**，仅生成测试代码（除非用户明确要求修复 Bug）
- 集成测试使用真实数据库（SQLite 内存或 Docker），不 Mock 数据库操作
- 外部 API 调用必须 Mock（不依赖真实外部服务）
- 每个测试用例必须独立，不依赖其他测试的状态
- 测试数据在每个测试前准备，测试后清理
- API 响应格式验证（状态码 + Content-Type + 响应体结构）
- 敏感数据（密码、Token）不出现在测试日志中

### 失败处理

> 遵循 GUARDRAILS.md 中的全局失败处理规则。

## 示例

### Node.js + Supertest（推荐）

```typescript
import request from 'supertest';
import app from '../src/app';
import { setupTestDB, teardownTestDB } from '../test/helpers/database';

describe('用户 API 集成测试', () => {
  beforeAll(async () => { await setupTestDB(); });
  afterAll(async () => { await teardownTestDB(); });

  it('合法数据应创建用户并返回 201', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ username: 'testuser', email: 'test@example.com', password: 'SecurePass123!' })
      .expect('Content-Type', /json/)
      .expect(201);
    expect(res.body.username).toBe('testuser');
    expect(res.body).not.toHaveProperty('password');
  });

  it('缺少必填字段应返回 400', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ username: 'testuser' })
      .expect(400);
    expect(res.body.error).toBeDefined();
  });

  it('不存在的用户 ID 应返回 404', async () => {
    await request(app).get('/api/users/99999').expect(404);
  });
});
```

> **更多语言示例**：Python + FastAPI、Java + Spring Boot、Go、Rust、C# 的完整集成测试示例请参阅 [`examples/integration-test-examples.md`](examples/integration-test-examples.md)。
