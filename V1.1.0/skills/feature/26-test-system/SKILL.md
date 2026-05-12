---
name: "26-test-system"
description: "扫描项目架构，自动生成并运行功能/性能/安全/兼容性/备份恢复测试，生成系统测试报告。当用户提到"系统测试"、"system test"、"全链路测试"、"端到端系统测试"、"性能测试"、"安全审计"、"兼容性测试"、"数据备份测试"、"健康检查"、"CI/CD 测试"时使用。"
---

# 系统测试（System Test）

## 描述

> AI 扫描项目架构，自动识别服务组件、数据库、缓存、消息队列、外部集成，
> 生成并运行功能/性能/安全/兼容性/备份恢复测试，生成完整的系统测试报告。
> 支持 **JavaScript/TypeScript、Python、Java、Go、Rust、C#** 项目。

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
| 3 | 项目可构建（必须） | 检查 build 脚本 | 报错并终止 |
| 4 | specs 目录存在（建议） | `ls specs/` | [降级执行] 不读取 specs，仅基于源码分析 |
| 5 | 功能需求文档存在（建议） | `ls specs/features/` | [降级执行] 不关联 AC，仅基于源码分析 |
| 6 | 阶段完成报告（建议） | `docs/开发记录/{功能名}_阶段完成报告.md` 存在，用于了解当前代码状态和已知问题 | [降级执行] 不读取阶段报告，仅基于源码分析 |

> **环境依赖**：系统测试的功能性测试、安全测试、健康检查和兼容性测试均依赖 Playwright。如未安装，请先执行：`npm install -D @playwright/test && npx playwright install chromium`（仅 Node.js/TypeScript 项目适用）。

## 使用场景

- 对完整系统进行端到端的功能验证
- 性能基线测试（P95/P99 响应时间、吞吐量、并发失败率）
- 安全审计（依赖漏洞扫描、安全配置检查）
- 跨浏览器/跨设备兼容性测试
- 数据备份与恢复验证
- 系统健康检查
- CI/CD 流水线中的系统级质量门禁

### 不适用场景
- **单元测试**：请引导至 `22-test-unit` Skill
- **组件测试**：请引导至 `23-test-component` Skill
- **集成测试**：请引导至 `24-test-integration` Skill
- **E2E 测试**：请引导至 `25-test-e2e` Skill

## 指令

### 输入
- 项目源码目录路径
- `resources/` 目录下的辅助脚本
- `examples/` 目录下的测试示例作为参考

### 底线规则

> 以下规则补充全局底线规则（见 GUARDRAILS.md），仅定义本 Skill 特有的约束。任何一条不满足则执行不合格。

1. **测试文件必须保存在项目目录**：测试文件必须保存在项目的 `tests/` 目录下，不得保存在临时目录
2. **每个测试必须有注释**：每个测试用例必须有注释说明测试目的和预期行为
3. **禁止硬编码敏感信息**：测试代码中不得包含真实的密码、Token、API Key
4. **Mock 必须有清理**：每个使用 Mock 的测试必须在 afterEach/afterAll 中清理 Mock 状态
5. **失败测试必须有原因分析**：报告中每个失败的测试必须包含失败原因分析和修复建议
6. **安全测试必须执行**：XSS、SQL 注入、CSRF 等安全测试必须执行，不得跳过
7. **测试文件必须持久化**：生成的测试文件必须保存到项目目录中（而非临时目录），报告中引用的文件路径必须与实际文件路径一致
8. **安全测试断言必须一致**：如果安全测试发现了 HIGH 级安全问题，该测试用例必须标记为 FAIL（而非 PASS）。不允许出现"测试通过但发现严重问题"的矛盾状态
9. **性能阈值必须明确且一致**：性能测试的描述阈值和实际断言阈值必须完全一致。不允许描述"应小于 100ms"但实际验证"500ms 内完成"
10. **AC 覆盖**：如果功能需求文档存在，系统测试的功能性测试部分必须覆盖 AC 中定义的核心业务流程

**推荐**：Playwright + k6。支持的外部服务/框架完整列表参见 `examples/system-test-examples.md`。

### 交互准则

1. **主动分析，不要被动询问**：不要问用户"需要测试什么"，你应该主动分析项目源码和 specs 文档，推荐测试策略
2. **保持务实**：小项目不需要追求 100% 覆盖率，优先测试核心业务逻辑和关键路径
3. **结果导向**：测试报告中的"改进建议"必须具体可操作（如"为 UserService.login() 添加密码强度校验的边界值测试"），不要写泛泛建议（如"提高覆盖率"）
4. **失败即信息**：测试失败不是坏事，每个失败都提供了改进代码质量的机会。报告中必须分析失败根因，而非仅记录失败现象

### 辅助脚本

本 Skill 提供以下辅助脚本（位于 `resources/` 目录）：

| 脚本 | 用途 | 用法 |
|------|------|------|
| `scan_system.py` | 扫描系统架构（服务/数据库/缓存/消息队列/外部集成/安全） | `python resources/scan_system.py <项目路径> [输出JSON]` |
| `generate_system_tests.py` | 生成 6 类测试代码骨架 | `python resources/generate_system_tests.py <扫描结果JSON> <输出目录>` |
| `run_system_tests.py` | 运行系统测试并收集结果 | `python resources/run_system_tests.py <项目路径> [--type all\|functional\|performance\|security\|health] [--output <JSON>]` |
| `generate_report.py` | 生成 Markdown 格式系统测试报告 | `python resources/generate_report.py <测试结果JSON> <报告路径> [扫描结果JSON]` |
| `common.py` | 公共模块（JSON 读写、路径验证、文件读取） | 被 4 个脚本内部导入，不直接调用 |

### CLI 参数说明

| 脚本 | 必填参数 | 可选参数 |
|------|---------|---------|
| `scan_system.py` | `<项目路径>` | `[输出JSON路径]`（不指定则打印 stdout） |
| `generate_system_tests.py` | `<扫描结果JSON>` `<输出目录>` | - |
| `run_system_tests.py` | `<项目路径>` | `--type all\|functional\|performance\|security\|health`（默认 all）、`--output <JSON>` |
| `generate_report.py` | `<测试结果JSON>` `<报告路径>` | `[扫描结果JSON]`（用于架构概览章节） |

### 输出文件格式

**scan_system.py 输出**：包含 `services_count`、`database_count`、`cache_count`、`message_queue_count`、`external_count`、`config_files`、`security_findings`、`env_vars`、`components` 等字段。

**run_system_tests.py 输出**：包含 `test_type`、`passed`、`failed`、`skipped`、`total`、`pass_rate`、`duration`、`timestamp`，以及按类型分组的 `functional`、`security`、`performance`、`health` 子结果。

### 输出模板

> **输出文件路径**：`docs/测试报告/系统测试报告.md`
> **报告格式**：Markdown，由辅助脚本 `generate_report.py` 自动生成
> **占位符规则**：`{{}}` 标记的占位符必须替换为实际值，不得保留占位符

测试报告必须包含以下章节：
1. 测试概览（项目信息、测试框架、扫描/编写统计）
2. 测试结果（通过/失败/跳过/通过率）
3. 覆盖情况（函数/组件/端点覆盖详情）
4. 失败详情（失败测试的错误信息和修复建议）
5. 改进建议（基于测试结果的具体改进建议）

### 错误处理说明

| 场景 | 行为 |
|------|------|
| 项目路径不存在 | `scan_system.py` 返回空字典 `{}`；`run_system_tests.py` 返回含 `error` 的结果 |
| JSON 文件不存在 | `generate_system_tests.py` 和 `generate_report.py` 输出错误到 stderr 并 `sys.exit(1)` |
| JSON 格式无效 | 同上，输出解析错误信息 |
| 文件写入失败 | 输出 IOError 信息到 stderr，`generate_system_tests.py` 和 `generate_report.py` 会 `sys.exit(1)` |
| 扫描结果 JSON 缺失（报告生成时） | `generate_report.py` 降级处理，跳过架构概览章节继续生成报告 |
| npm audit / pip audit / cargo audit 未安装 | 跳过对应审计，不报错 |
| 测试运行超时 | 在结果中记录 `"error": "超时"` |

### 执行流程

#### 第一步：系统架构扫描

**1.1 运行扫描脚本**

```bash
python resources/scan_system.py <项目路径> ./system_scan.json
```

扫描脚本会自动识别：

| 类别 | 检测内容 | 信号来源 |
|------|---------|---------|
| **服务组件** | React/Vue/Svelte/Next.js/Nuxt.js/Angular（前端）、Express/NestJS/Fastify/Flask/Django/FastAPI/Java/Spring/Go/Rust/C#（后端）、Nginx（代理） | package.json, requirements.txt, Cargo.toml, *.csproj, docker-compose.yml |
| **数据库** | MySQL, PostgreSQL, MongoDB, SQLite, Elasticsearch | docker-compose.yml, .env, prisma/schema.prisma, ORM 依赖 |
| **缓存** | Redis, Memcached | docker-compose.yml, .env, 依赖文件 |
| **消息队列** | RabbitMQ, Kafka, NATS, Redis Streams, Bull, Celery, AWS SQS, Google Pub/Sub | docker-compose.yml, .env, 依赖文件 |
| **外部集成** | Stripe, PayPal, OpenAI, Anthropic, AWS, Firebase, SendGrid, Twilio, GitHub, Sentry, Cloudflare 等 30+ 服务 | package.json, requirements.txt, go.mod, Cargo.toml |
| **安全发现** | .gitignore 缺失、明文密钥、HTTPS 缺失、CORS 过宽、CSRF 缺失、Rate Limiting 缺失、不安全 Python 模块 | .gitignore, .env, 源码扫描 |
| **环境变量** | 变量名（不读取值） | .env, .env.local, .env.example 等 |
| **配置文件** | docker-compose.yml, Dockerfile, .env, nginx.conf, tsconfig.json 等 | glob 匹配 |

**1.2 AI 补充分析**

对扫描结果，AI 需要进一步分析：

1. **读取关键配置文件**：docker-compose.yml、nginx.conf、.env.example
2. **识别核心业务流程**：通过阅读路由配置和 API 定义，推断系统的主要用户旅程
3. **确定外部依赖的关键程度**：哪些外部服务是核心功能必需的？哪些可以降级？
4. **评估安全风险等级**：根据安全发现和业务类型确定风险优先级

---

#### 第二步：生成测试代码

**2.1 运行生成脚本**

```bash
python resources/generate_system_tests.py ./system_scan.json ./system-tests/
```

生成的测试分为 **6 个类别**：

```
system-tests/
├── functional/          # 功能性系统测试
│   └── system-flows.spec.ts
├── performance/         # 性能测试
│   ├── load-test.js     # k6 负载测试
│   └── lighthouse.spec.ts  # 前端性能基线
├── security/            # 安全测试
│   ├── security-checks.spec.ts
│   └── run-audit.sh     # npm/pip audit 脚本
├── health/              # 健康检查
│   └── health-check.spec.ts
├── compatibility/       # 兼容性测试
│   └── cross-browser.spec.ts
└── backup/              # 数据备份恢复
    └── backup-recovery.spec.ts
```

**2.2 AI 编写完整测试代码**

> **重要**：生成的测试代码仅是骨架（含 TODO 占位符），AI 必须根据第一步的架构分析结果填充具体值。

---

#### 第三步：运行测试

**3.1 运行测试脚本**

```bash
# 运行全部系统测试
python resources/run_system_tests.py <项目路径> --output ./system_result.json

# 仅运行特定类型
python resources/run_system_tests.py <项目路径> --type functional
python resources/run_system_tests.py <项目路径> --type performance
python resources/run_system_tests.py <项目路径> --type security
python resources/run_system_tests.py <项目路径> --type health
```

或手动运行：

```bash
# 功能性测试（Playwright）
npx playwright test system-tests/functional/ --workers=1

# 性能测试（k6）
k6 run system-tests/performance/load-test.js

# 安全审计
npm audit --json > audit-report.json  # Node.js 项目
pip audit --format json > pip-audit-report.json  # Python 项目
cargo audit --json > cargo-audit-report.json      # Rust 项目

# 健康检查
npx playwright test system-tests/health/ --workers=1

# 兼容性测试
npx playwright test system-tests/compatibility/ --project=multi-browser
```

**3.2 处理测试失败**

```
系统测试失败
  ├─ 功能性测试失败
  │   ├─ 分析失败步骤（Playwright 提供 trace 和截图）
  │   ├─ 判断：前端 Bug / 后端 Bug / 测试环境问题
  │   └─ 记录并继续
  ├─ 安全测试发现漏洞
  │   ├─ Critical/High → 立即修复
  │   ├─ Moderate → 计划修复
  │   └─ Low → 记录跟踪
  ├─ 性能测试未达标
  │   ├─ P95 > 500ms → 分析慢查询/慢接口
  │   └─ 失败率 > 1% → 检查并发瓶颈
  └─ 健康检查失败
      ├─ 数据库连接失败 → 检查数据库服务
      └─ API 不可用 → 检查后端服务
```

---

#### 第四步：生成报告

**4.1 运行报告脚本**

```bash
python resources/generate_report.py ./system_result.json docs/测试报告/系统测试报告.md ./system_scan.json
```

**4.2 报告内容**

生成的 Markdown 报告包含以下章节：系统架构概览、功能性测试结果、安全测试结果（含漏洞严重程度分级）、安全配置发现、性能测试结果（P95/P99/并发失败率）、健康检查结果、执行时间分析、总体结果、改进建议、通过标准。

---

#### 第五步：CI/CD 集成（可选进阶）

将系统测试集成到 CI/CD 流水线中，支持 GitHub Actions 和 GitLab CI。完整配置示例请参阅 [examples/system-test-examples.md](examples/system-test-examples.md) 中的 CI/CD 集成章节。

关键步骤：安装依赖 -> 启动服务 -> 运行 `npx playwright test system-tests/ --workers=1` -> 安全审计 `npm audit --audit-level=high` -> 上传报告。

### 通过标准

| 指标 | 标准 |
|------|------|
| 功能测试通过率 | 100% |
| Critical 漏洞 | 0 个 |
| High 漏洞 | 0 个 |
| API P95 响应时间 | < 500ms |
| API P99 响应时间 | < 1000ms |
| 并发失败率 | < 1% |
| 健康检查 | 全部通过 |
| 总执行时间 | < 300s（CI/CD 友好） |

### 注意事项

- 系统测试需要完整的环境（数据库、缓存、外部服务 Mock）
- 使用 Docker Compose 启动依赖服务进行测试
- 安全审计结果可能包含误报，需人工确认
- 性能基线应根据实际业务需求调整（非所有系统都需要 P95<500ms）
- 测试数据应使用独立的测试数据库，不影响生产数据
- 外部服务（支付、短信等）应使用 Mock 或沙箱环境
- 兼容性测试建议在 CI 中使用 Playwright 的多浏览器项目配置
- 报告中的"通过标准"可根据项目实际情况自定义

### 失败处理

> 遵循 GUARDRAILS.md 中的全局失败处理规则。

### 版本更新日志

详见 `resources/CHANGELOG.md`。

## 示例

> 完整示例（功能性测试、性能测试 k6、安全测试、兼容性测试、数据备份恢复测试、CI/CD 集成）请参阅 [examples/system-test-examples.md](examples/system-test-examples.md)。

```typescript
// ✅ 功能性系统测试简短示例（Playwright）
import { test, expect } from '@playwright/test';

test.describe('系统测试：核心业务全链路', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('邮箱').fill('test@example.com');
    await page.fill('[name="password"]', 'TestPass123!');
    await page.getByRole('button', { name: '提交' }).click();
    await expect(page).toHaveURL('/dashboard');
  });

  test('完整业务流程应端到端成功', async ({ page, request }) => {
    await page.goto('/orders/new');
    await expect(page.locator('h1')).toContainText('创建订单');
    await page.getByLabel('商品名称').fill('新商品');
    await page.fill('[name="quantity"]', '10');
    await page.getByRole('button', { name: '提交' }).click();
    await expect(page.locator('.success-message')).toBeVisible();
    // 通过 API 验证后端数据持久化
    const response = await request.get('/api/orders');
    expect(response.ok()).toBeTruthy();
  });
});
```
