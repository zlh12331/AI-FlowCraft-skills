---
name: "25-test-e2e"
description: "网站端到端测试技能。当用户提到"E2E测试"、"end-to-end test"、"端到端测试"、"用户流程测试"、"UI自动化测试"、"浏览器自动化测试"、"Playwright测试"、"Cypress测试"、"Selenium测试"、"验收测试"、"写E2E测试"、"自动化测试"时使用此技能。AI 会阅读项目源码，自动识别可测试的页面和用户流程，编写并运行 E2E 测试代码，生成测试报告。"
allowed-tools: RunCommand, Read, Write, Grep, Glob, LS
metadata:
  author: AI
  version: "2.1.0"
---

# E2E 测试（End-to-End Test）

> AI 阅读项目源码，自动识别可测试的页面和用户流程，编写并运行 E2E 测试代码（Playwright），模拟真实用户在浏览器中的完整操作流程。

## 项目上下文协议 (Project Context Protocol) - CRITICAL

> **本节定义 AI 如何获取项目上下文。每次执行前必须先读取项目上下文。**

读取项目上下文文件：`cat specs/PROJECT-CONTEXT.md`

如果文件不存在，向用户询问以下信息并创建该文件：
- 项目名称、技术栈、项目路径
- 已完成的功能列表和对应的 specs 文档路径
- 当前开发阶段

## 边界守卫 (Guardrails) - CRITICAL

> **本节定义 AI 的行为边界。违反任何一条守卫则执行不合格。**

读取全局守卫规则：`cat specs/GUARDRAILS.md`

核心守卫：
1. **禁止修改源码**：测试代码不得修改被测源码，只能读取和验证
2. **禁止跳过失败测试**：不得将失败测试标记为 skip，必须记录失败原因
3. **测试必须独立**：每个测试用例必须独立运行，不依赖其他测试的执行顺序或状态

## 前置条件

| # | 前置条件 | 验证方式 | 不满足时的处理 |
|---|---------|---------|--------------|
| 1 | 源码可访问（必须） | `ls src/` | 报错并终止 |
| 2 | 项目类型已识别（必须） | 检查 package.json | 报错并终止 |
| 3 | 浏览器环境可用（必须） | 检查 playwright 安装 | 报错并终止 |
| 4 | specs 目录存在（建议） | `ls specs/` | [降级执行] 不读取 specs，仅基于源码分析 |
| 5 | 功能需求文档存在（建议） | `ls specs/features/` | [降级执行] 不关联 AC，仅基于源码分析 |
| 6 | 阶段完成报告（建议） | `docs/开发记录/{功能名}_阶段完成报告.md` 存在，用于了解当前代码状态和已知问题 | [降级执行] 不读取阶段报告，仅基于源码分析 |

## 底线规则

> 以下规则补充全局底线规则（见 GUARDRAILS.md），仅定义本 Skill 特有的约束。任何一条不满足则执行不合格。

1. **测试文件必须保存在项目目录**：测试文件必须保存在项目的 `tests/` 目录下，不得保存在临时目录。
2. **每个测试必须有注释**：每个测试用例必须有注释说明测试目的和预期行为。
3. **禁止硬编码敏感信息**：测试代码中不得包含真实的密码、Token、API Key。
4. **Mock 必须有清理**：每个使用 Mock 的测试必须在 afterEach/afterAll 中清理 Mock 状态。
5. **失败测试必须有原因分析**：报告中每个失败的测试必须包含失败原因分析和修复建议。
6. **核心流程必须覆盖**：PRD 中定义的核心用户流程必须有 E2E 测试。
7. **测试数据必须唯一且可清理**：每个测试用例必须使用唯一的测试数据（如使用时间戳生成唯一邮箱 `test${Date.now()}@example.com`），测试结束后必须清理创建的数据（如删除测试账号、测试订单），不得在数据库中残留测试数据。
8. **必须优先使用语义化选择器**：选择器优先级为 `getByRole` > `getByLabel` > `getByText` > `getByTestId` > CSS 选择器。禁止使用脆弱的 CSS 类名选择器（如 `.btn-primary`）或 XPath。如需使用 `getByTestId`，被测组件中必须已添加对应的 `data-testid` 属性。
9. **禁止硬编码等待时间**：不得使用 `page.waitForTimeout(3000)` 等固定等待。必须使用 Playwright 的自动等待机制（`waitFor`、`waitForSelector`、`waitForLoadState`）或 `expect` 的自动重试。如确实需要等待特定条件，必须使用 `page.waitForResponse()` 等条件等待。
10. **Playwright 配置必须已存在**：执行 E2E 测试前，必须确认 `playwright.config.ts` 已在 Skill 18（项目初始化）中创建。如未创建，不得直接运行 `npm init playwright@latest`（会覆盖项目配置），必须手动创建配置文件或提示用户先完成项目初始化。（仅 Node.js/TypeScript 项目适用）
11. **E2E 测试与单元测试必须隔离**：E2E 测试文件（Playwright）必须保存在 `__tests__/e2e/` 或 `e2e/` 目录下，与单元/集成测试文件分开。项目的 Vitest 配置（`vitest.config.ts`）的 `test.exclude` 必须排除 E2E 测试目录，避免 Vitest 尝试加载 Playwright 测试文件导致环境不兼容错误（Playwright 测试依赖浏览器环境，Vitest 默认使用 jsdom/node 环境）。（仅使用 Vitest 的项目适用）
12. **页面结构变更时必须同步更新 E2E 测试**：当功能开发阶段（Skill 20）修改了页面结构（组件拆分、元素层级变化、路由变更等），必须同步检查并更新受影响的 E2E 测试用例。E2E 测试的选择器应优先使用 `getByRole` 和 `getByTestId`（需在被测组件中添加 `data-testid`），而非依赖 CSS 类名或 DOM 结构，以降低页面重构对测试的影响。
13. **AC 覆盖**：如果功能需求文档存在，E2E 测试必须覆盖 AC 中定义的核心用户流程

## 输出模板

> **输出文件路径**：`docs/测试报告/E2E测试报告.md`
> **报告格式**：Markdown，由辅助脚本 `generate_report.py` 自动生成
> **占位符规则**：`{{}}` 标记的占位符必须替换为实际值，不得保留占位符

测试报告必须包含以下章节：
1. 测试概览（项目信息、测试框架、扫描/编写统计）
2. 测试结果（通过/失败/跳过/通过率）
3. 覆盖情况（函数/组件/端点覆盖详情）
4. 失败详情（失败测试的错误信息和修复建议）
5. 改进建议（基于测试结果的具体改进建议）

## 交互准则

1. **主动分析，不要被动询问**：不要问用户"需要测试什么"，你应该主动分析项目源码和 specs 文档，推荐测试策略
2. **保持务实**：小项目不需要追求 100% 覆盖率，优先测试核心业务逻辑和关键路径
3. **结果导向**：测试报告中的"改进建议"必须具体可操作（如"为 UserService.login() 添加密码强度校验的边界值测试"），不要写泛泛建议（如"提高覆盖率"）
4. **失败即信息**：测试失败不是坏事，每个失败都提供了改进代码质量的机会。报告中必须分析失败根因，而非仅记录失败现象

## 适用场景

- 模拟真实用户的完整操作流程（注册→登录→浏览→下单→支付）
- 验证前端页面与后端 API 的完整链路
- 跨页面导航和数据流转测试
- 表单提交流程测试（多步骤表单）
- 响应式布局测试（不同屏幕尺寸）
- 视觉回归测试（截图对比）

## 与其他测试层级的区别

| 维度 | 集成测试 | **E2E 测试** |
|------|---------|-------------|
| 测试对象 | API 接口、数据库 | **真实用户操作流程** |
| 运行环境 | Node.js / Python | **真实浏览器（Chromium/Firefox/WebKit）** |
| 测试方式 | 发送 HTTP 请求 | **模拟点击、输入、滚动** |
| 速度 | 快（毫秒级） | **慢（秒级）** |
| 覆盖范围 | 单个接口 | **完整业务流程** |
| 脆弱性 | 低 | **高（依赖 UI、网络、环境）** |

## 辅助脚本

本 Skill 提供以下辅助脚本（位于 `scripts/` 目录）：

| 脚本 | 用途 | 用法 |
|------|------|------|
| `scan_pages.py` | 扫描项目中的可测试页面和用户流程 | `python scripts/scan_pages.py <项目路径> [输出JSON]` |
| `generate_e2e_tests.py` | 根据扫描结果生成 E2E 测试代码 | `python scripts/generate_e2e_tests.py <扫描结果JSON> <输出目录>` |
| `run_e2e_tests.py` | 运行 E2E 测试并收集结果 | `python scripts/run_e2e_tests.py <项目路径> [--headed]` |
| `generate_report.py` | 生成 Markdown 格式测试报告 | `python scripts/generate_report.py <测试结果JSON> <报告路径> [扫描结果JSON]` |

> **注意**：辅助脚本用于预处理和批量操作，AI 仍需根据页面源码分析结果手动完善测试代码中的具体操作步骤和断言。

---

## 执行流程

### 第一步：环境检测与准备

**1.1 识别前端框架**

```bash
cat package.json | grep -E '"(react|vue|angular|next|nuxt|svelte)"'
```

**1.2 检测已安装的 E2E 测试框架**

```bash
# Playwright
npx playwright --version 2>/dev/null

# Cypress
npx cypress --version 2>/dev/null

# Selenium（较少用于现代前端项目）
# 检查 package.json 中的 webdriverio / selenium-webdriver
```

**1.3 安装 E2E 测试框架（推荐 Playwright）**

| 框架 | 安装命令 | 说明 |
|------|---------|------|
| **Playwright**（推荐） | `npm install -D @playwright/test && npx playwright install chromium` | 支持多浏览器、自动等待、截图/视频、网络拦截 |
| Cypress | `npm install -D cypress` | 适合 React 项目，但只支持 Chromium |
| Selenium | `npm install -D selenium-webdriver` | 老牌工具，配置复杂，不推荐新项目 |

```bash
# 安装 Playwright（推荐）
npm install -D @playwright/test && npx playwright install chromium
```

**1.4 配置 Playwright**

```bash
# playwright.config.ts
cat > playwright.config.ts << 'EOF'
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,         // E2E 测试建议串行，避免数据冲突
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 1,
  reporter: 'html',             // 生成 HTML 报告
  timeout: 60000,               // 每个测试超时 60 秒

  use: {
    baseURL: 'http://localhost:3000',  // 被测网站地址
    trace: 'retain-on-failure',        // 失败时保留 trace
    screenshot: 'only-on-failure',     // 失败时截图
    video: 'retain-on-failure',        // 失败时录制视频
  },

  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    // 移动端
    { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
    { name: 'mobile-safari', use: { ...devices['iPhone 13'] } },
  ],
});
EOF
```

**1.5 确保被测网站可访问**

```bash
# 检查网站是否在运行
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000

# 如未运行，启动开发服务器
npm run dev &

# 等待服务就绪
npx wait-on http://localhost:3000 --timeout 30000
```

---

### 第二步：页面扫描与流程分析

**2.1 运行扫描脚本**

```bash
python scripts/scan_pages.py <项目路径> /data/user/work/e2e_scan_result.json
```

扫描脚本会自动：
- 识别前端框架和路由配置
- 提取所有页面路由（Next.js pages/app、Vue Router、React Router）
- 识别表单页面、需要认证的页面、公开页面

**2.2 AI 补充分析（脚本无法自动完成的部分）**

对扫描结果中的每个页面，AI 需要阅读源码进行深度分析：

1. **读取页面源码**：使用 Read 工具读取页面组件文件
2. **分析页面结构**：
   - 页面标题和描述（`<title>`、meta）
   - 表单字段（输入框、下拉框、复选框、单选框）
   - 按钮和链接（提交按钮、导航链接）
   - 条件渲染内容（登录前/后显示不同内容）
   - 异步加载内容（骨架屏、加载动画）
3. **识别用户流程**：
   - 注册流程：首页→注册页→填写信息→提交→验证邮箱→登录
   - 登录流程：登录页→输入凭据→提交→跳转首页
   - 搜索流程：首页→搜索框→输入关键词→查看结果→点击详情
   - 购物流程：商品列表→商品详情→加入购物车→结算→支付→订单确认
4. **确定测试数据**：
   - 测试账号（已有账号 / 每次创建新账号）
   - 测试数据（商品、文章等）
   - 清理策略（测试后删除创建的数据）

**2.3 确定测试优先级**

| 优先级 | 用户流程 | 说明 |
|-------|---------|------|
| P0 | 核心业务流程 | 注册、登录、支付、下单 |
| P1 | 主要功能流程 | 搜索、筛选、数据提交 |
| P2 | 辅助功能流程 | 个人资料编辑、密码重置 |
| P3 | 边缘场景 | 错误页面、空状态、权限不足 |

> E2E 测试数量应控制在 **10-30 个核心流程**，不要试图覆盖所有页面。

---

### 第三步：编写 E2E 测试

**3.1 生成测试代码骨架**

```bash
python scripts/generate_e2e_tests.py /data/user/work/e2e_scan_result.json /data/user/work/generated_e2e_tests/
```

> **重要**：生成的测试代码仅是骨架，AI 必须根据页面源码分析结果填充具体的操作步骤和断言。

**3.2 AI 编写完整测试代码**

对每个用户流程，AI 需要编写以下测试用例：

| 测试类型 | 覆盖场景 | 示例 |
|---------|---------|------|
| 正向流程 | 完整操作流程→预期结果 | 注册→填写信息→提交→跳转首页 |
| 表单验证 | 空提交/格式错误→错误提示 | 密码太短→"密码至少8位" |
| 导航测试 | 点击链接→跳转正确页面 | 点击"关于"→显示关于页面 |
| 登录态测试 | 未登录→重定向登录页 | 访问个人中心→跳转登录 |
| 响应式测试 | 不同屏幕尺寸→布局正确 | 移动端→汉堡菜单可见 |
| 空状态测试 | 无数据→显示空状态提示 | 无订单→"暂无订单" |
| 错误处理 | 网络错误/服务器错误→友好提示 | 断网→"网络连接失败" |

**3.3 测试代码规范**

```typescript
// ✅ 好的 E2E 测试示例（Playwright）
import { test, expect } from '@playwright/test';

// === 登录流程 ===
test.describe('用户登录流程', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试前：打开登录页
    await page.goto('/login');
  });

  test('合法凭据应成功登录并跳转首页', async ({ page }) => {
    // 填写表单
    await page.getByLabel('邮箱').fill('test@example.com');
    await page.getByLabel('密码').fill('SecurePass123!');
    await page.getByRole('button', { name: '登录' }).click();

    // 验证跳转
    await expect(page).toHaveURL('/dashboard');
    // 验证页面内容
    await expect(page.getByText('欢迎回来')).toBeVisible();
  });

  test('错误密码应显示错误提示', async ({ page }) => {
    await page.getByLabel('邮箱').fill('test@example.com');
    await page.getByLabel('密码').fill('WrongPassword');
    await page.getByRole('button', { name: '登录' }).click();

    // 验证错误提示（不跳转）
    await expect(page.getByText('邮箱或密码错误')).toBeVisible();
    await expect(page).toHaveURL('/login');
  });

  test('空表单提交应显示验证错误', async ({ page }) => {
    await page.getByRole('button', { name: '登录' }).click();

    // 验证每个字段的错误提示
    await expect(page.getByText('请输入邮箱')).toBeVisible();
    await expect(page.getByText('请输入密码')).toBeVisible();
  });
});

// === 注册流程 ===
test.describe('用户注册流程', () => {
  test('完整注册流程应成功创建账号', async ({ page }) => {
    await page.goto('/register');

    // 填写注册表单
    await page.getByLabel('用户名').fill('newuser');
    await page.getByLabel('邮箱').fill(`test${Date.now()}@example.com`);  // 唯一邮箱
    await page.getByLabel('密码').fill('SecurePass123!');
    await page.getByLabel('确认密码').fill('SecurePass123!');
    await page.getByLabel('同意条款').check();
    await page.getByRole('button', { name: '注册' }).click();

    // 验证注册成功
    await expect(page.getByText('注册成功')).toBeVisible();
    // 验证跳转到登录页或自动登录
    await expect(page).toHaveURL(/\/(login|dashboard)/);
  });
});

// === 搜索流程 ===
test.describe('搜索功能', () => {
  test('搜索关键词应显示匹配结果', async ({ page }) => {
    await page.goto('/');

    // 输入搜索关键词
    await page.getByPlaceholder('搜索商品...').fill('iPhone');
    await page.getByRole('button', { name: '搜索' }).click();

    // 验证搜索结果页
    await expect(page).toHaveURL(/\/search\?q=iPhone/);
    // 验证结果列表不为空
    const results = page.getByTestId('search-result');
    await expect(results.first()).toBeVisible();
    // 验证结果包含关键词
    await expect(page.getByText(/iPhone/i).first()).toBeVisible();
  });

  test('空搜索应显示提示', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: '搜索' }).click();
    await expect(page.getByText('请输入搜索关键词')).toBeVisible();
  });
});

// === 响应式测试 ===
test.describe('响应式布局', () => {
  test('移动端应显示汉堡菜单', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // 验证汉堡菜单可见
    await expect(page.getByRole('button', { name: '菜单' })).toBeVisible();
    // 验证桌面导航不可见
    await expect(page.getByRole('navigation').getByRole('link')).not.toBeVisible();
  });
});
```

---

### 第四步：运行测试

**4.1 运行测试脚本**

```bash
python scripts/run_e2e_tests.py <项目路径> [--headed] [--browser chromium]
```

或手动运行：

```bash
# 运行所有 E2E 测试（无头模式）
npx playwright test

# 有头模式（可视化调试）
npx playwright test --headed

# 指定浏览器
npx playwright test --project=chromium
npx playwright test --project=firefox

# 指定测试文件
npx playwright test e2e/login.spec.ts

# 调试模式（逐步执行）
npx playwright test --debug

# 查看测试报告
npx playwright show-report
```

**4.2 处理测试失败**

```
E2E 测试失败
  ├─ 查看失败截图和视频（playwright-report/）
  ├─ 查看 trace（npx playwright show-trace trace.zip）
  ├─ 分析失败原因：
  │   ├─ 选择器失效（UI 改动导致元素找不到）
  │   │   └─ 更新选择器 → 重新运行
  │   ├─ 等待不足（异步加载未完成就操作）
  │   │   └─ 增加等待时间或使用 waitFor → 重新运行
  │   ├─ 测试数据问题（账号被禁用、数据冲突）
  │   │   └─ 更新测试数据 → 重新运行
  │   ├─ 环境问题（服务未启动、端口错误）
  │   │   └─ 修复环境 → 重新运行
  │   └─ 网站有 Bug（功能异常、显示错误）
  │       └─ 记录为 Bug 报告（不修改源码）
  └─ 最多重试 2 次，仍失败则记录并继续下一个
```

**4.3 常见问题处理**

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 元素找不到 | 选择器不正确 | 使用 `getByRole`/`getByLabel`/`getByTestId` |
| 操作超时 | 页面加载慢 | `await page.waitForLoadState('networkidle')` |
| 测试间数据冲突 | 测试未独立 | 每个测试使用唯一数据 / 测试前清理 |
| 弹窗遮挡操作 | Cookie 同意弹窗等 | `beforeEach` 中关闭弹窗 |
| 截图对比失败 | 视觉回归 | 更新基准截图或调查 UI 变更 |

---

### 第五步：生成报告

**5.1 运行报告生成脚本**

```bash
python scripts/generate_report.py /data/user/work/e2e_test_result.json docs/测试报告/E2E测试报告.md /data/user/work/e2e_scan_result.json
```

**5.2 报告内容**

生成的 Markdown 报告包含：

```markdown
# E2E 测试报告

## 概览
| 指标 | 数值 |
|------|------|
| 前端框架 | React / Vue / Next.js |
| 测试框架 | Playwright |
| 扫描页面总数 | XX |
| 测试流程数 | XX |
| 测试用例总数 | XX |

## 测试结果
| 指标 | 数值 |
|------|------|
| 通过 | XX |
| 失败 | XX |
| 跳过 | XX |
| 通过率 | XX% |

## 用户流程覆盖情况
| 流程名称 | 测试用例数 | 状态 |
|----------|-----------|------|

## 发现的缺陷
（如有网站 Bug，在此列出）

## 改进建议
```

---

## 通过标准

| 指标 | 标准 |
|------|------|
| 测试通过率 | 100%（网站缺陷已记录的除外） |
| P0 核心流程覆盖率 | 100% |
| 每个测试独立运行 | 是（不依赖其他测试的状态） |
| 失败时有截图/trace | 是 |
| 测试运行时间 | < 10 分钟 |

## 注意事项

- 测试代码必须带注释，说明每个操作步骤的目的
- **不要修改网站源码**，仅生成测试代码（除非用户明确要求修复 Bug）
- 优先使用语义化选择器（`getByRole` > `getByLabel` > `getByText` > `getByTestId` > CSS 选择器）
- 每个测试用例必须独立，使用唯一测试数据
- 使用 `test.describe` 按用户流程分组
- 避免硬编码等待时间（`page.waitForTimeout`），使用 `waitFor` / `waitForSelector`
- 测试前确保被测网站正在运行
- 敏感数据（密码、Token）使用环境变量，不出现在代码中
- E2E 测试数量控制在 10-30 个核心流程，不要过度测试
- 测试文件命名遵循项目约定（`.spec.ts`）
- **E2E 测试应包含视觉回归测试**：至少 1 个关键页面应使用 `await expect(page).toHaveScreenshot()` 进行截图对比，用于检测 UI 回归问题。首次运行生成基线截图，后续运行自动对比
