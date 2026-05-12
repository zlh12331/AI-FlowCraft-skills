# 组件测试代码示例

> 本文件包含各前端框架的完整组件测试代码示例，供 AI 编写测试时参考。
> SKILL.md 中仅保留推荐框架的简短示例，完整示例见此处。

---

## React + React Testing Library

```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginForm from '../components/LoginForm';

// Mock 依赖
jest.mock('next/router', () => ({
  useRouter: () => ({ push: jest.fn() }),
}));

describe('LoginForm', () => {
  // === 渲染测试 ===
  it('应渲染用户名和密码输入框', () => {
    render(<LoginForm onSubmit={jest.fn()} />);
    expect(screen.getByLabelText('用户名')).toBeInTheDocument();
    expect(screen.getByLabelText('密码')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '登录' })).toBeInTheDocument();
  });

  // === 交互测试 ===
  it('输入用户名和密码后点击登录应调用 onSubmit', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText('用户名'), 'testuser');
    await user.type(screen.getByLabelText('密码'), 'password123');
    await user.click(screen.getByRole('button', { name: '登录' }));

    expect(onSubmit).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123',
    });
  });

  // === 验证测试 ===
  it('空表单提交应显示验证错误', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={jest.fn()} />);

    await user.click(screen.getByRole('button', { name: '登录' }));

    expect(screen.getByText('请输入用户名')).toBeInTheDocument();
    expect(screen.getByText('请输入密码')).toBeInTheDocument();
  });

  // === 条件渲染 ===
  it('isLoading 为 true 时应显示加载状态并禁用按钮', () => {
    render(<LoginForm onSubmit={jest.fn()} isLoading />);
    expect(screen.getByText('登录中...')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();
  });

  // === 错误提示 ===
  it('error prop 有值时应显示错误信息', () => {
    render(<LoginForm onSubmit={jest.fn()} error="用户名或密码错误" />);
    expect(screen.getByText('用户名或密码错误')).toBeInTheDocument();
  });
});
```

---

## Vue 3 + Vue Test Utils

```vue
<script setup>
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import UserCard from '@/components/UserCard.vue';

describe('UserCard', () => {
  // === 渲染测试 ===
  it('应正确渲染用户信息', () => {
    const wrapper = mount(UserCard, {
      props: {
        name: '张三',
        email: 'zhangsan@example.com',
        avatar: '/avatar.jpg',
      },
    });
    expect(wrapper.text()).toContain('张三');
    expect(wrapper.text()).toContain('zhangsan@example.com');
  });

  // === 事件测试 ===
  it('点击删除按钮应触发 delete 事件', async () => {
    const wrapper = mount(UserCard, {
      props: { name: '张三', email: 'test@test.com' },
    });
    await wrapper.find('[data-testid="delete-btn"]').trigger('click');
    expect(wrapper.emitted('delete')).toBeTruthy();
    expect(wrapper.emitted('delete')[0]).toEqual([]);
  });

  // === 条件渲染 ===
  it('isAdmin 为 true 时应显示管理员标签', () => {
    const wrapper = mount(UserCard, {
      props: { name: '张三', email: 'test@test.com', isAdmin: true },
    });
    expect(wrapper.find('.admin-badge').exists()).toBe(true);
  });

  // === 插槽测试 ===
  it('应渲染默认插槽内容', () => {
    const wrapper = mount(UserCard, {
      props: { name: '张三', email: 'test@test.com' },
      slots: { default: '<span class="custom">自定义内容</span>' },
    });
    expect(wrapper.find('.custom').exists()).toBe(true);
  });
});
</script>
```

---

## Angular + Angular Testing Library

```typescript
import { render, screen, fireEvent } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { LoginFormComponent } from './login-form.component';
import { AuthService } from './auth.service';
import { of, throwError } from 'rxjs';

// Mock AuthService
const mockAuthService = {
  login: jest.fn(),
};

describe('LoginFormComponent', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // === 渲染测试 ===
  it('应渲染用户名和密码输入框及登录按钮', async () => {
    await render(LoginFormComponent, {
      providers: [{ provide: AuthService, useValue: mockAuthService }],
    });

    expect(screen.getByLabelText('用户名')).toBeInTheDocument();
    expect(screen.getByLabelText('密码')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '登录' })).toBeInTheDocument();
  });

  // === 交互测试 ===
  it('输入凭据并提交应调用 AuthService.login', async () => {
    const user = userEvent.setup();
    mockAuthService.login.mockReturnValue(of({ token: 'fake-token' }));

    await render(LoginFormComponent, {
      providers: [{ provide: AuthService, useValue: mockAuthService }],
    });

    await user.type(screen.getByLabelText('用户名'), 'testuser');
    await user.type(screen.getByLabelText('密码'), 'password123');
    await user.click(screen.getByRole('button', { name: '登录' }));

    expect(mockAuthService.login).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123',
    });
  });

  // === 验证测试 ===
  it('空表单提交应显示验证错误', async () => {
    const user = userEvent.setup();

    await render(LoginFormComponent, {
      providers: [{ provide: AuthService, useValue: mockAuthService }],
    });

    await user.click(screen.getByRole('button', { name: '登录' }));

    expect(screen.getByText('请输入用户名')).toBeInTheDocument();
    expect(screen.getByText('请输入密码')).toBeInTheDocument();
  });

  // === 条件渲染 ===
  it('isLoading 为 true 时应显示加载状态', async () => {
    await render(LoginFormComponent, {
      componentInputs: { isLoading: true },
      providers: [{ provide: AuthService, useValue: mockAuthService }],
    });

    expect(screen.getByText('登录中...')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();
  });

  // === 错误提示 ===
  it('error 有值时应显示错误信息', async () => {
    await render(LoginFormComponent, {
      componentInputs: { error: '用户名或密码错误' },
      providers: [{ provide: AuthService, useValue: mockAuthService }],
    });

    expect(screen.getByText('用户名或密码错误')).toBeInTheDocument();
  });
});
```

---

## Svelte + @testing-library/svelte

```svelte
<script>
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import Counter from '../components/Counter.svelte';

describe('Counter', () => {
  // === 渲染测试 ===
  it('应正确渲染初始值', () => {
    render(Counter, { props: { initialCount: 5 } });
    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '增加' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '减少' })).toBeInTheDocument();
  });

  // === 交互测试 ===
  it('点击增加按钮应使计数加 1', async () => {
    const user = userEvent.setup();
    render(Counter, { props: { initialCount: 0 } });

    await user.click(screen.getByRole('button', { name: '增加' }));

    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('点击减少按钮应使计数减 1', async () => {
    const user = userEvent.setup();
    render(Counter, { props: { initialCount: 5 } });

    await user.click(screen.getByRole('button', { name: '减少' }));

    expect(screen.getByText('4')).toBeInTheDocument();
  });

  // === 边界值测试 ===
  it('计数为 0 时点击减少不应变为负数', async () => {
    const user = userEvent.setup();
    render(Counter, { props: { initialCount: 0, min: 0 } });

    await user.click(screen.getByRole('button', { name: '减少' }));

    expect(screen.getByText('0')).toBeInTheDocument();
  });

  // === 事件测试 ===
  it('计数变化时应触发 change 事件', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(Counter, { props: { initialCount: 0, onChange } });

    await user.click(screen.getByRole('button', { name: '增加' }));

    expect(onChange).toHaveBeenCalledWith(1);
  });
});
</script>
```
