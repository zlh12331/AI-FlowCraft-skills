# 系统测试完整示例

> 从 `SKILL.md` 的 `## 示例` 章节提取的完整代码示例，供参考。

## 功能性系统测试

验证核心业务流程的端到端正确性：

```typescript
// ✅ 完整业务流程测试示例
import { test, expect } from '@playwright/test';

test.describe('系统测试：核心业务全链路', () => {
  test.beforeEach(async ({ page }) => {
    // 登录测试账号
    await page.goto('/login');
    await page.getByLabel('邮箱').fill('test@example.com');  // 优先使用语义化选择器（与 Skill 25 底线规则 8 对齐）
    await page.fill('[name="password"]', 'TestPass123!');
    await page.getByRole('button', { name: '提交' }).click();
    await expect(page).toHaveURL('/dashboard');
  });

  test('完整业务流程应端到端成功', async ({ page, request }) => {
    // 步骤 1：访问核心页面
    await page.goto('/orders/new');
    await expect(page.locator('h1')).toContainText('创建订单');

    // 步骤 2：填写并提交表单
    await page.getByLabel('商品名称').fill('新商品');  // 优先使用语义化选择器（与 Skill 25 底线规则 8 对齐）
    await page.fill('[name="quantity"]', '10');
    await page.getByRole('button', { name: '提交' }).click();

    // 步骤 3：验证前端显示成功
    await expect(page.locator('.success-message')).toBeVisible();

    // 步骤 4：通过 API 验证后端数据持久化
    const response = await request.get('/api/orders');
    expect(response.ok()).toBeTruthy();
    const orders = await response.json();
    expect(orders).toHaveLengthGreaterThan(0);
    expect(orders[orders.length - 1].product).toBe('测试商品');
  });

  test('前端显示应与后端数据一致', async ({ page, request }) => {
    // 通过 API 获取数据
    const apiResponse = await request.get('/api/dashboard/stats');
    const apiData = await apiResponse.json();

    // 在页面上获取相同数据
    await page.goto('/dashboard');
    const pageValue = await page.locator('[data-testid="total-orders"]').textContent();

    // 对比两者
    expect(Number(pageValue)).toBe(apiData.totalOrders);
  });
});
```

## 性能测试（k6）

使用 k6 进行负载测试：

```javascript
// ✅ k6 负载测试示例
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },    // 预热：20 用户
    { duration: '60s', target: 50 },    // 峰值：50 用户
    { duration: '30s', target: 0 },     // 冷却
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],  // P95<500ms, P99<1s
    http_req_failed: ['rate<0.01'],                   // 失败率 < 1%
  },
};

export default function () {
  const BASE_URL = 'http://localhost:8080';

  // 健康检查
  const health = http.get(`${BASE_URL}/api/health`);
  check(health, { '健康检查 200': (r) => r.status === 200 });

  // 核心 API 性能测试
  const listRes = http.get(`${BASE_URL}/api/items`);
  check(listRes, { '列表接口 200': (r) => r.status === 200 });

  const createRes = http.post(`${BASE_URL}/api/items`,
    JSON.stringify({ name: 'perf-test', quantity: 1 }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(createRes, { '创建接口 201': (r) => r.status === 201 });

  sleep(1);
}
```

## 安全测试

```typescript
// ✅ 安全测试示例
import { test, expect } from '@playwright/test';

test.describe('系统安全基线测试', () => {
  test('应包含安全响应头', async ({ request }) => {
    const response = await request.get('https://staging.example.com');
    const headers = response.headers();

    // 验证关键安全头
    expect(headers['x-frame-options']).toBeDefined();
    expect(headers['x-content-type-options']).toBe('nosniff');
    expect(headers['x-xss-protection']).toBeDefined();
    expect(headers['strict-transport-security']).toBeDefined();
  });

  test('应防止 XSS 攻击', async ({ page }) => {
    await page.goto('/search');
    await page.fill('[name="query"]', '<script>alert("xss")</script>');
    await page.click('button[type="submit"]');

    // 验证脚本不被执行（输入被转义）
    const pageContent = await page.content();
    expect(pageContent).not.toContain('<script>alert("xss")</script>');
    // 验证转义后的显示
    await expect(page.locator('.search-results')).toContainText('&lt;script&gt;');
  });

  test('应防止 SQL 注入', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="email"] = "' OR 1=1 --");
    await page.fill('[name="password"]', 'anything');
    await page.click('button[type="submit"]');

    // 应显示错误信息而非登录成功
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page).not.toHaveURL('/dashboard');
  });
});
```

## 兼容性测试

```typescript
// ✅ 跨浏览器兼容性测试示例
import { test, expect } from '@playwright/test';

test.describe('跨浏览器兼容性', () => {
  // 移动端设备测试
  const devices = [
    { name: 'iPhone 14', viewport: { width: 390, height: 844 } },
    { name: 'iPad Pro', viewport: { width: 1024, height: 1366 } },
    { name: 'Desktop 1920', viewport: { width: 1920, height: 1080 } },
  ];

  for (const device of devices) {
    test(`${device.name}: 响应式布局应正确`, async ({ browser }) => {
      const context = await browser.newContext({
        viewport: device.viewport,
      });
      const page = await context.newPage();
      await page.goto('/');

      // 验证无水平滚动条（响应式基本要求）
      const hasHorizontalScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      expect(hasHorizontalScroll).toBeFalsy();

      // 验证关键元素可见
      await expect(page.locator('header')).toBeVisible();
      await expect(page.locator('main')).toBeVisible();

      await context.close();
    });
  }
});
```

## 数据备份恢复测试

```typescript
// ✅ 数据备份恢复测试示例
import { test, expect } from '@playwright/test';

test.describe('数据备份与恢复', () => {
  test('数据库备份应成功创建', async ({ request }) => {
    const response = await request.post('/api/admin/backup', {
      data: { database: 'PostgreSQL' }
    });
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.backupId).toBeDefined();
    expect(body.status).toBe('success');
  });

  test('备份后数据应与源数据一致', async ({ request }) => {
    // 获取当前数据快照
    const before = await request.get('/api/data/snapshot');
    const beforeData = await before.json();

    // 创建备份
    const backup = await request.post('/api/admin/backup');
    const backupId = (await backup.json()).backupId;

    // 从备份恢复
    await request.post(`/api/admin/restore/${backupId}`);

    // 验证恢复后数据一致
    const after = await request.get('/api/data/snapshot');
    const afterData = await after.json();
    expect(afterData).toEqual(beforeData);
  });
});
```

## CI/CD 集成示例

### GitHub Actions

```yaml
name: System Tests
on: [push, pull_request]

jobs:
  system-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: testdb
          POSTGRES_PASSWORD: testpass
        ports: ["5432:5432"]
      redis:
        image: redis:7
        ports: ["6379:6379"]

    steps:
      - uses: actions/checkout@v4
      - name: 安装依赖
        run: npm ci
      - name: 启动服务
        run: |
          npm run build
          npm run start &
          sleep 10
      - name: 运行系统测试
        run: npx playwright test system-tests/ --workers=1
      - name: 安全审计
        run: npm audit --audit-level=high
      - name: 上传报告
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: system-test-report
          path: system-test-report.md
```

### GitLab CI

```yaml
system_test:
  stage: test
  image: mcr.microsoft.com/playwright:v1.40.0-jammy
  services:
    - postgres:15
    - redis:7
  script:
    - npm ci
    - npx playwright install --with-deps
    - npx playwright test system-tests/ --workers=1
    - npm audit --audit-level=high
  artifacts:
    paths:
      - system-test-report.md
    when: always
```
