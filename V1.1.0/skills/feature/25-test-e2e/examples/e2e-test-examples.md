# Playwright E2E 测试完整示例

> 从 `SKILL.md` 的 `## 示例` 章节提取的完整代码示例，供参考。

## 登录流程

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
```

## 注册流程

```typescript
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
```

## 搜索流程

```typescript
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
```

## 响应式测试

```typescript
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
