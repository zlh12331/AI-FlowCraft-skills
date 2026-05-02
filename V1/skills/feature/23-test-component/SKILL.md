---
name: "23-test-component"
description: "网站组件测试技能。当用户提到"组件测试"、"component test"、"UI测试"、"组件渲染测试"、"交互测试"、"快照测试"、"snapshot test"、"React Testing Library"、"Vue Test Utils"、"测试组件"、"写组件测试"时使用此技能。AI 会阅读项目组件源码，自动编写并运行组件测试代码，生成覆盖率报告。"
allowed-tools: RunCommand, Read, Write, Grep, Glob, LS
metadata:
  author: AI
  version: "2.1.0"
---

# 组件测试（Component Test）

> AI 阅读项目组件源码，自动识别可测试的 UI 组件，编写并运行组件测试代码（渲染、交互、状态、快照），生成覆盖率报告。

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
| 3 | 测试框架已安装（必须） | 检查 vitest/jest | 报错并终止 |
| 4 | specs 目录存在（建议） | `ls specs/` | [降级执行] 不读取 specs，仅基于源码分析 |
| 5 | 功能需求文档存在（建议） | `ls specs/features/` | [降级执行] 不关联 AC，仅基于源码分析 |
| 6 | 阶段完成报告（建议） | `docs/开发记录/{功能名}_阶段完成报告.md` 存在，用于了解当前代码状态和已知问题 | [降级执行] 不读取阶段报告，仅基于源码分析 |

## 底线规则

> 以下规则补充全局底线规则（见 GUARDRAILS.md），仅定义本 Skill 特有的约束。任何一条不满足则执行不合格。

1. **测试文件必须保存在项目目录**：测试文件必须保存在项目的 `tests/` 目录下，不得保存在临时目录
2. **每个测试必须有注释**：每个测试用例必须有注释说明测试目的和预期行为
3. **禁止硬编码敏感信息**：测试代码中不得包含真实的密码、Token、API Key
4. **Mock 必须有清理**：每个使用 Mock 的测试必须在 afterEach/afterAll 中清理 Mock 状态
5. **失败测试必须有原因分析**：报告中每个失败的测试必须包含失败原因分析和修复建议
6. **组件 Props 必须测试**：每个组件的所有 Props 组合必须有对应的测试用例
7. **JSX 文件必须导入 React**（仅 React/TypeScript 项目适用；Vue/Svelte 项目不涉及 JSX 导入）：所有使用 JSX 语法的测试文件（.tsx）必须在文件顶部显式导入 `import React from 'react'`，即使 TypeScript 配置了 `jsx: "preserve"` 或 `jsx: "react-jsx"`。这是因为 Vitest 的 jsdom 环境不会自动注入 React JSX 转换
8. **组件测试必须基于实际组件源码编写**：编写组件测试前，必须先读取被测组件的完整源码（包括其依赖的 hooks、stores、services），确认以下信息后再编写测试：
    1. 组件的错误处理逻辑（catch 块如何区分错误类型）
    2. 组件使用的 store 导出方式和 API
    3. 组件的 props 接口定义
    4. 组件的异步操作流程
    禁止凭记忆或上游文档描述编写测试断言，必须以实际源码为准。
9. **AC 覆盖**：如果功能需求文档存在，组件测试用例必须覆盖 AC 中与 UI 渲染和交互相关的验收标准

## 适用场景

- 对网站前端项目进行组件级测试
- 测试组件的渲染输出、用户交互、状态管理
- 生成组件快照测试（Snapshot Test）
- 检查组件的可访问性（Accessibility）
- 测试组件的 Props 验证和事件回调

## 与单元测试的区别

| 维度 | 单元测试 (test-unit) | 组件测试 (test-component) |
|------|---------------------|--------------------------|
| 测试对象 | 纯函数、工具函数、方法 | UI 组件（React/Vue/Angular） |
| 运行环境 | Node.js | jsdom / 浏览器环境 |
| 是否渲染 | 不渲染 DOM | 渲染 DOM / Virtual DOM |
| 依赖 | Mock 外部依赖 | Mock 子组件、API、路由 |
| 测试内容 | 输入→输出 | 渲染→交互→状态变化 |

## 辅助脚本

本 Skill 提供以下辅助脚本（位于 `scripts/` 目录）：

| 脚本 | 用途 | 用法 |
|------|------|------|
| `scan_components.py` | 扫描项目组件，识别可测试组件 | `python scripts/scan_components.py <项目路径> [输出JSON]` |
| `generate_component_tests.py` | 根据扫描结果生成组件测试代码 | `python scripts/generate_component_tests.py <扫描结果JSON> <输出目录>` |
| `run_component_tests.py` | 运行组件测试并收集覆盖率 | `python scripts/run_component_tests.py <项目路径> [--coverage]` |
| `generate_report.py` | 生成 Markdown 格式测试报告 | `python scripts/generate_report.py <测试结果JSON> <报告路径> [扫描结果JSON]` |

> **注意**：辅助脚本用于预处理和批量操作，AI 仍需根据组件源码分析结果手动完善测试代码中的具体测试值和断言。

---

## 执行流程

### 第一步：环境检测与准备

**1.1 识别前端框架**

```bash
# 检查 package.json 中的依赖
cat package.json | grep -E '"(react|vue|angular|next|nuxt|svelte)"'
```

| 框架标识 | 前端框架 | 推荐测试库 |
|---------|---------|-----------|
| `react` + `next` | Next.js | Jest + React Testing Library |
| `react` | React | Jest + React Testing Library |
| `vue` + `nuxt` | Nuxt.js | Vitest + Vue Test Utils |
| `vue` | Vue | Vitest + Vue Test Utils |
| `angular` | Angular | Jest + Angular Testing Library |
| `svelte` | Svelte | Vitest + @testing-library/svelte |

**1.2 检测已安装的测试库**

```bash
# React Testing Library
npx @testing-library/react --version 2>/dev/null

# Vue Test Utils
npx @vue/test-utils --version 2>/dev/null

# 检查 package.json devDependencies
cat package.json | grep -E '"@testing-library|vitest|jest|@vue/test-utils"'
```

**1.3 安装测试框架（如未安装）**

| 前端框架 | 测试框架 | 安装命令 |
|---------|---------|---------|
| React/Next.js | Jest + RTL | `npm install -D jest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom ts-jest @types/jest` |
| Vue 3/Nuxt.js | Vitest + VTU | `npm install -D vitest @vue/test-utils happy-dom @testing-library/vue @testing-library/user-event` |
| Vue 2 | Jest + VTU | `npm install -D jest @vue/test-utils vue-jest babel-jest @testing-library/vue` |
| Angular | Jest + ATL | `ng add @testing-library/angular` |
| Svelte | Vitest | `npm install -D vitest @testing-library/svelte happy-dom jsdom` |

**1.4 配置测试环境**

```bash
# Jest 配置（React 项目）
cat > jest.config.js << 'EOF'
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterSetup: ['<rootDir>/jest.setup.js'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js',
  },
  testPathIgnorePatterns: ['/node_modules/', '/.next/', '/dist/'],
  collectCoverageFrom: [
    'src/components/**/*.{ts,tsx,js,jsx}',
    '!src/components/**/*.d.ts',
    '!src/components/**/index.{ts,tsx,js,jsx}',
  ],
};
EOF

# Jest setup 文件（全局匹配器）
cat > jest.setup.js << 'EOF'
import '@testing-library/jest-dom';
EOF

# Vitest 配置（Vue 项目）
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
  },
});
EOF
```

---

### 第二步：组件扫描与分析

**2.1 运行扫描脚本**

```bash
# 扫描项目组件
python scripts/scan_components.py <项目路径> /data/user/work/component_scan_result.json
```

扫描脚本会自动：
- 识别前端框架（React/Vue/Angular/Svelte）
- 提取所有组件（排除页面级组件、布局组件）
- 分析每个组件的 Props、Events、Slots、状态管理

**2.2 AI 补充分析（脚本无法自动完成的部分）**

对扫描结果中的每个组件，AI 需要阅读源码进行深度分析：

1. **读取组件源码**：使用 Read 工具读取组件文件
2. **分析组件结构**：
   - **Props**：类型、是否必填、默认值、验证规则
   - **Events/Emits**：事件名称、回调参数
   - **Slots**：具名插槽、默认插槽
   - **State**：内部状态（useState/ref/reactive）、派生状态
   - **生命周期**：useEffect/mounted/watch 等副作用
   - **条件渲染**：v-if/v-show/三元表达式 → 每个分支至少一个测试
   - **列表渲染**：v-for/map → 空列表、单元素、多元素
3. **确定 Mock 需求**：
   - 子组件 → Mock 或浅渲染（Shallow Render）
   - API 调用 → Mock fetch/axios
   - 路由 → Mock useRouter/useRoute
   - 状态管理 → Mock Redux Store / Pinia / Vuex
   - 国际化 → Mock i18n

**2.3 确定测试优先级**

| 优先级 | 组件类型 | 说明 |
|-------|---------|------|
| P0 | 表单组件 | 登录表单、注册表单、支付表单等关键交互 |
| P1 | 数据展示组件 | 表格、列表、卡片、图表 |
| P2 | 交互组件 | 模态框、下拉菜单、标签页、手风琴 |
| P3 | 基础 UI 组件 | 按钮、输入框、标签、徽章 |

> 如组件数量过多（>30），优先测试 P0 和 P1 级别的组件。

---

### 第三步：编写组件测试

**3.1 生成测试代码骨架**

```bash
# 基于扫描结果生成测试代码骨架
python scripts/generate_component_tests.py /data/user/work/component_scan_result.json /data/user/work/generated_component_tests/
```

> **重要**：生成的测试代码仅是骨架，AI 必须根据第二步的源码分析结果，手动填充每个测试的具体 Props 值、交互步骤和预期断言。

**3.2 AI 编写完整测试代码**

对每个组件，AI 需要编写以下测试用例：

| 测试类型 | 覆盖场景 | 示例 |
|---------|---------|------|
| 渲染测试 | 正常 Props → 正确渲染 | 传入 `title="Hello"` → 屏幕上显示 "Hello" |
| Props 验证 | 必填 Props 缺失 → 警告/默认值 | 不传 `required` prop → 控制台警告 |
| 交互测试 | 用户操作 → 状态变化/事件触发 | 点击按钮 → 调用 `onClick` 回调 |
| 条件渲染 | 不同 Props → 显示/隐藏不同内容 | `isLoading=true` → 显示加载动画 |
| 列表渲染 | 空数据/单条/多条 → 正确渲染 | `items=[]` → 显示"暂无数据" |
| 快照测试 | 组件渲染输出 → 与快照匹配 | 首次生成快照，后续比对 |
| 可访问性 | 语义化标签、ARIA 属性 | 按钮有 `aria-label`，图片有 `alt` |
| 事件测试 | 触发事件 → 回调被正确调用 | 表单提交 → 调用 `onSubmit(data)` |

**3.3 测试代码规范**

```tsx
// ✅ 好的组件测试示例（React + RTL）
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

```vue
<!-- ✅ 好的组件测试示例（Vue 3 + VTU） -->
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

```typescript
// ✅ 好的组件测试示例（Angular + Angular Testing Library）
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

```svelte
<!-- ✅ 好的组件测试示例（Svelte + @testing-library/svelte） -->
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

---

### 第四步：运行测试

**4.1 运行测试脚本**

```bash
# 运行组件测试并收集覆盖率
python scripts/run_component_tests.py <项目路径> --coverage
```

或手动运行：

```bash
# React (Jest)
npx jest --coverage --coverageDirectory=coverage --testPathPattern="components"

# Vue (Vitest)
npx vitest run --coverage --coverage.include="src/components/**/*.{vue,ts,tsx}"

# Angular
ng test --code-coverage --watch=false
```

**4.2 处理测试失败**

```
测试失败
  ├─ 分析失败信息（渲染错误 / 断言不匹配 / 事件未触发）
  ├─ 读取失败测试的源码 + 被测组件源码
  ├─ 判断失败原因：
  │   ├─ 测试代码写错了（选择器不对、等待不足、Mock 不完整）
  │   │   └─ 修复测试代码 → 重新运行
  │   ├─ 组件有 Bug（渲染错误、事件未绑定、状态异常）
  │   │   └─ 记录为 Bug 报告（不修改源码）
  │   └─ 环境问题（jsdom 限制、CSS 模块、SVG 支持）
  │       └─ 调整配置或 Mock → 重新运行
  └─ 最多重试 3 次，仍失败则记录并继续下一个
```

**4.3 常见问题处理**

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `findBy` 查询超时 | 异步渲染未完成 | 使用 `waitFor` 或增加超时时间 |
| `act` 警告 | 状态更新未包裹在 act 中 | 使用 `waitFor` 或 `act()` 包裹 |
| CSS 样式不生效 | jsdom 不支持真实 CSS | 使用 `@testing-library/jest-dom` 匹配器 |
| 图片/字体加载失败 | jsdom 不支持网络请求 | Mock 静态资源文件 |
| 路由相关报错 | 未 Mock 路由 | `jest.mock('next/navigation')`（仅 Next.js 项目） |
| 路由相关报错 | 未 Mock 路由 | `vi.mock('vue-router')`（Vue/Nuxt 项目） |
| 路由相关报错 | 未 Mock 路由 | `vi.mock('$app/navigation')`（SvelteKit 项目） |

---

### 第五步：生成报告

**5.1 运行报告生成脚本**

```bash
python scripts/generate_report.py /data/user/work/component_test_result.json docs/测试报告/组件测试报告.md /data/user/work/component_scan_result.json
```

**5.2 报告内容**

生成的 Markdown 报告包含：

```markdown
# 组件测试报告

## 概览
| 指标 | 数值 |
|------|------|
| 前端框架 | React / Vue / Angular / Svelte |
| 测试框架 | Jest + RTL / Vitest + VTU |
| 扫描组件总数 | XX |
| 编写测试组件数 | XX |
| 测试用例总数 | XX |

## 测试结果
| 指标 | 数值 |
|------|------|
| 通过 | XX |
| 失败 | XX |
| 跳过 | XX |
| 通过率 | XX% |

## 代码覆盖率
| 类型 | 覆盖率 |
|------|--------|
| 行覆盖率 | XX% |
| 分支覆盖率 | XX% |
| 函数覆盖率 | XX% |
| 语句覆盖率 | XX% |

## 组件测试覆盖情况
| 组件名 | 文件 | Props | Events | 测试用例数 | 状态 |
|--------|------|-------|--------|-----------|------|

## 发现的缺陷
（如有组件 Bug，在此列出）

## 改进建议
（重构建议、可访问性改进建议）
```

---

## 输出模板

> 本节定义报告的输出路径、格式和占位符规则。

**报告路径**：`docs/测试报告/组件测试报告.md`

**报告格式**：

```markdown
# 组件测试报告

## 概览
| 指标 | 数值 |
|------|------|
| 前端框架 | {{React / Vue / Angular / Svelte}} |
| 测试框架 | {{Jest + RTL / Vitest + VTU}} |
| 扫描组件总数 | {{XX}} |
| 编写测试组件数 | {{XX}} |
| 测试用例总数 | {{XX}} |

## 测试结果
| 指标 | 数值 |
|------|------|
| 通过 | {{XX}} |
| 失败 | {{XX}} |
| 跳过 | {{XX}} |
| 通过率 | {{XX%}} |

## 代码覆盖率
| 类型 | 覆盖率 |
|------|--------|
| 行覆盖率 | {{XX%}} |
| 分支覆盖率 | {{XX%}} |
| 函数覆盖率 | {{XX%}} |
| 语句覆盖率 | {{XX%}} |

## 组件测试覆盖情况
| 组件名 | 文件 | Props | Events | 测试用例数 | 状态 |
|--------|------|-------|--------|-----------|------|

## 发现的缺陷
（如有组件 Bug，在此列出）

## 改进建议
（重构建议、可访问性改进建议）
```

## 通过标准

| 指标 | 标准 |
|------|------|
| 测试通过率 | 100%（组件缺陷已记录的除外） |
| 行覆盖率 | ≥ 80% |
| 分支覆盖率 | ≥ 70% |
| 函数覆盖率 | ≥ 80% |
| P0/P1 组件覆盖率 | 100% |

## 注意事项

- 测试代码必须带注释，说明测试目的和预期行为
- **不要修改组件源码**，仅生成测试代码（除非用户明确要求修复 Bug）
- 优先使用用户事件库（`@testing-library/user-event`）而非 `fireEvent`
- 查询优先级：`getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByTestId`
- 不要测试实现细节（内部 state、私有方法），只测试行为和渲染输出
- 每个测试用例应独立运行，不依赖其他测试的状态
- Mock 子组件时使用 `jest.mock()（仅 Jest 项目；Vitest 项目使用 vi.mock()）` 或浅渲染，避免测试子组件逻辑
- 测试文件命名遵循项目约定（`.test.tsx` / `.spec.tsx`）
