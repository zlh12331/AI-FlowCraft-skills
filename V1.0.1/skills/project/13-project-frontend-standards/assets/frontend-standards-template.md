# 前端开发规范

> 本文档由 `13-project-frontend-standards` Skill 自动生成。
> **文档版本**：1.0
> **创建日期**：{{YYYY-MM-DD}}
> **最后更新**：{{YYYY-MM-DD}}
> **基于技术栈**：{{技术栈概要}}

---

> **说明**：本模板默认以 React + TypeScript 为例。Vue / Angular / Svelte 项目请将代码示例替换为对应框架的等效写法，规范原则保持不变。

## 1. 语言与运行时要求

<!-- 填写指引：明确前端开发所需的运行时版本和编译目标，确保团队环境一致 -->

### 1.1 Node.js 版本

<!-- 填写指引：指定项目要求的 Node.js 版本范围，建议使用 .nvmrc 或 .node-version 文件管理 -->

- **要求版本**：{{Node.js 版本，例如 v20.x LTS}}
- **版本管理**：{{版本管理方式，例如 .nvmrc / volta / fnm}}
- **包管理器**：{{pnpm / npm / yarn，指定版本}}

```bash
# .nvmrc 示例
{{例如：20.11.0}}
```

### 1.2 浏览器兼容性

<!-- 填写指引：根据产品目标用户确定需要支持的浏览器范围 -->

- **目标浏览器**：{{例如：Chrome >= 90, Firefox >= 88, Safari >= 14, Edge >= 90}}
- **兼容性策略**：{{例如：Browserslist 配置 / core-js 按需引入}}
- **IE 支持**：{{是否需要支持 IE，通常为"不支持"}}

```jsonc
// package.json 中的 browserslist 配置示例
{
  "browserslist": [
    "{{例如：'> 1%', 'last 2 versions', 'not dead'}}"
  ]
}
```

### 1.3 TypeScript 配置

<!-- 填写指引：定义 TypeScript 编译选项，严格模式是推荐默认开启的 -->

- **TS 版本**：{{TypeScript 版本，例如 ~5.3.0}}
- **严格模式**：{{是否开启 strict: true，强烈建议开启}}
- **目标模块**：{{module / moduleResolution 配置}}
- **路径别名**：{{baseUrl / paths 配置，与目录结构保持一致}}

```jsonc
// tsconfig.json 核心配置示例
{
  "compilerOptions": {
    "target": "{{例如：ES2020}}",
    "module": "{{例如：ESNext}}",
    "moduleResolution": "{{例如：bundler}}",
    "strict": {{true}},
    "jsx": "{{例如：react-jsx}}",
    "baseUrl": "{{例如：'.'}}",
    "paths": {
      "{{例如：'@/*': ['src/*']}}"
    }
  }
}
```

---

## 2. 代码风格与 Lint 规则

<!-- 填写指引：定义 ESLint、Prettier、Stylelint 的配置策略和关键规则，确保代码风格统一 -->

### 2.1 ESLint 配置

<!-- 填写指引：列出 ESLint 使用的扩展/插件，以及需要特别说明的规则 -->

- **配置方案**：{{例如：eslint.config.js (flat config) / .eslintrc.js}}
- **核心扩展**：{{例如：@typescript-eslint/recommended, eslint-plugin-react-hooks, eslint-plugin-import}}
- **运行命令**：{{例如：pnpm lint}}

```javascript
// eslint.config.js 示例框架
export default [
  {{根据项目技术栈列出 ESLint 配置}}
];
```

#### 关键规则说明

<!-- 填写指引：只列出需要特别说明的规则（与默认值不同的、容易踩坑的），不要列出所有规则 -->

| 规则 | 值 | 原因 |
|------|-----|------|
| {{例如：no-console}} | {{例如：'warn'}} | {{例如：开发阶段允许 console，生产构建时由构建工具移除}} |
| {{例如：no-unused-vars}} | {{例如：'off'}} | {{例如：由 @typescript-eslint/no-unused-vars 替代}} |
| {{例如：@typescript-eslint/no-explicit-any}} | {{例如：'error'}} | {{例如：禁止 any，强制类型安全}} |

### 2.2 Prettier 配置

<!-- 填写指引：定义代码格式化规则，确保与 ESLint 不冲突 -->

- **配置文件**：{{例如：.prettierrc}}
- **运行命令**：{{例如：pnpm format}}

```jsonc
// .prettierrc 示例
{
  "semi": {{例如：false}},
  "singleQuote": {{例如：true}},
  "tabWidth": {{例如：2}},
  "trailingComma": {{例如：'all'}},
  "printWidth": {{例如：100}},
  "arrowParens": {{例如：'always'}}
}
```

### 2.3 Stylelint 配置（如适用）

<!-- 填写指引：如果项目使用 CSS/SCSS/Less，配置 Stylelint；如果使用 Tailwind 且不写自定义 CSS，可标注"不适用" -->

- **是否启用**：{{是 / 否，及原因}}
- **配置方案**：{{例如：stylelint-config-standard-scss}}

---

## 3. 命名约定

<!-- 填写指引：命名约定是代码可读性的基础，必须具体到每个场景，并配以正确/错误示例 -->

### 3.1 文件命名

<!-- 填写指引：根据框架约定定义文件命名规则 -->

| 文件类型 | 命名规则 | 示例 |
|---------|---------|------|
| 组件文件 | {{例如：PascalCase.tsx}} | {{例如：UserProfile.tsx}} |
| 工具函数 | {{例如：camelCase.ts}} | {{例如：formatDate.ts}} |
| 类型定义 | {{例如：camelCase.types.ts}} | {{例如：user.types.ts}} |
| 样式文件 | {{例如：camelCase.module.css}} | {{例如：button.module.css}} |
| 测试文件 | {{例如：xxx.test.ts(x)}} | {{例如：utils.test.ts}} |
| 常量文件 | {{例如：camelCase.constants.ts}} | {{例如：api.constants.ts}} |
| Hook 文件 | {{例如：useXxx.ts}} | {{例如：useAuth.ts}} |

### 3.2 组件命名

<!-- 填写指引：组件命名必须与文件名一致，使用 PascalCase -->

```tsx
// ✅ 正确：组件名与文件名一致，PascalCase
export default function UserProfile() { ... }

// ❌ 错误：组件名与文件名不一致
export default function UserCard() { ... } // 文件名是 UserProfile.tsx
```

### 3.3 函数命名

<!-- 填写指引：函数使用 camelCase，事件处理函数以 handle 开头，布尔判断以 is/has/should 开头 -->

```typescript
// ✅ 正确
const handleClick = () => { ... };
const isValidEmail = (email: string) => { ... };
const fetchUserList = async () => { ... };

// ❌ 错误
const click_handler = () => { ... };  // 不使用 snake_case
const valid = (email: string) => { ... };  // 布尔函数缺少 is 前缀
const getData = async () => { ... };  // 过于笼统
```

### 3.4 变量命名

<!-- 填写指引：变量使用 camelCase，常量使用 UPPER_SNAKE_CASE，私有变量以 _ 开头（如团队有此约定） -->

```typescript
// ✅ 正确
const maxRetryCount = 3;
const API_BASE_URL = 'https://api.example.com';

// ❌ 错误
const MaxRetryCount = 3;  // 变量不应使用 PascalCase
const api_base_url = 'https://api.example.com';  // 不使用 snake_case
```

### 3.5 类型命名

<!-- 填写指引：接口使用 PascalCase，类型别名使用 PascalCase，泛型参数使用有意义的名称 -->

```typescript
// ✅ 正确
interface UserProfile { ... }
type ApiResponse<T> = { data: T; code: number };
type UserStatus = 'active' | 'inactive';

// ❌ 错误
interface userProfile { ... }  // 接口不应使用 camelCase
type api_response = { ... };   // 类型不应使用 snake_case
type T = { ... };              // 泛型参数不应使用单字母（简单场景除外）
```

---

## 4. 语言特定规范（TypeScript）

<!-- 填写指引：本章节专门针对 TypeScript 的使用规范，确保类型安全性和代码质量 -->

### 4.1 类型定义规范

<!-- 填写指引：优先使用 interface 而非 type，明确区分类型导出和值导出 -->

```typescript
// ✅ 正确：使用 interface 定义对象类型
interface User {
  id: string;
  name: string;
  email: string;
}

// ✅ 正确：使用 type 定义联合类型和工具类型
type UserStatus = 'active' | 'inactive' | 'banned';
type Nullable<T> = T | null;

// ❌ 错误：用 type 定义普通对象类型（项目中约定优先使用 interface）
type User = {
  id: string;
  name: string;
};
```

### 4.2 禁止 any

<!-- 填写指引：明确禁止使用 any 的策略，以及 any 的替代方案 -->

```typescript
// ✅ 正确：使用 unknown 替代 any，强制调用方进行类型检查
function parseJSON(input: string): unknown {
  return JSON.parse(input);
}

// ✅ 正确：使用泛型保持类型安全
function getData<T>(url: string): Promise<T> {
  return fetch(url).then(res => res.json());
}

// ❌ 错误：使用 any 逃避类型检查
function getData(url: string): Promise<any> {
  return fetch(url).then(res => res.json());
}
```

### 4.3 类型导入导出

<!-- 填写指引：使用 `import type` 语法导入纯类型，避免运行时副作用 -->

```typescript
// ✅ 正确：使用 type 关键字导入类型
import type { User, UserProfile } from '@/types/user';

// ❌ 错误：将类型作为值导入（可能导致循环依赖和打包问题）
import { User, UserProfile } from '@/types/user';
```

### 4.4 泛型使用规范

<!-- 填写指引：泛型参数命名要有意义，避免过度泛型化 -->

```typescript
// ✅ 正确：泛型参数名称有意义
interface ApiResponse<TData> {
  code: number;
  data: TData;
  message: string;
}

// ❌ 错误：单字母泛型参数（除简单场景外）
interface ApiResponse<T> {
  code: number;
  data: T;
  message: string;
}
```

---

## 5. 框架特定规范

<!-- 填写指引：根据项目使用的框架（React / Vue / Angular / Svelte / 其他）定制组件设计、状态管理、路由等规范 -->

### 5.1 组件设计原则

<!-- 填写指引：定义组件的拆分粒度、Props 设计规范、组件通信方式 -->

- **组件粒度**：{{例如：单个组件文件不超过 300 行，超过则拆分}}
- **Props 设计**：{{例如：必须定义 Props interface，禁止使用 any}}
- **组件通信**：{{例如：Props 向下传递，回调向上冒泡，跨层级使用 Context}}

```tsx
// ✅ 正确：Props 使用独立 interface 定义
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}

export function Button({ label, onClick, variant = 'primary', disabled }: ButtonProps) {
  return (
    <button onClick={onClick} disabled={disabled} className={`btn btn-${variant}`}>
      {label}
    </button>
  );
}

// ❌ 错误：Props 内联定义，缺少类型约束
export function Button({ label, onClick, variant, disabled }) {
  return (
    <button onClick={onClick} disabled={disabled}>
      {label}
    </button>
  );
}
```

### 5.2 Hooks 使用规范

<!-- 填写指引：自定义 Hook 的命名、封装原则和常见陷阱 -->

- **命名规则**：{{例如：以 use 开头，camelCase}}
- **封装原则**：{{例如：只封装可复用的逻辑，不封装一次性逻辑}}
- **依赖数组**：{{例如：必须完整声明依赖，使用 eslint-plugin-react-hooks 自动检查}}

```typescript
// ✅ 正确：自定义 Hook 封装可复用逻辑
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}

// ❌ 错误：Hook 内部有条件调用
function useAuth() {
  if (isLoggedIn) {  // ❌ 不能在条件语句中调用 Hook
    useEffect(() => { ... }, []);
  }
}
```

### 5.3 导入排序

<!-- 填写指引：定义 import 语句的排序规则，建议使用自动排序工具 -->

<!-- 填写指引：按以下顺序排列导入语句 -->

1. {{例如：React / 框架核心库}}
2. {{例如：第三方库}}
3. {{例如：项目内部模块（@/ 别名）}}
4. {{例如：同目录模块（./ 相对路径）}}
5. {{例如：类型导入（import type）}}
6. {{例如：样式文件}}

```typescript
// ✅ 正确：按分组排序，组间空行分隔
import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';  // Next.js App Router
// import { useNavigate } from 'react-router-dom';  // React Router（非 Next.js 项目）
import { Button, Modal } from 'antd';

import { useAuth } from '@/hooks/useAuth';
import { formatDate } from '@/utils/formatDate';

import type { User } from '@/types/user';

import styles from './UserProfile.module.css';

// ❌ 错误：导入顺序混乱
import styles from './UserProfile.module.css';
import { Button } from 'antd';
import { useState } from 'react';
import type { User } from '@/types/user';
```

---

## 6. 样式规范

<!-- 填写指引：明确项目使用的唯一样式方案，列出禁止使用的写法，避免样式方案混用 -->

### 6.1 样式方案

<!-- 填写指引：根据技术选型确定唯一样式方案，不允许混用多种方案 -->

- **唯一方案**：{{例如：CSS Modules / Tailwind CSS / Styled Components}}
- **禁止使用**：{{例如：内联 style 属性（除动态计算值外）/ 全局 CSS 类名 / 其他方案}}
- **原因**：{{例如：保持样式方案一致性，降低维护成本}}

### 6.2 样式编写规范

<!-- 填写指引：定义样式文件的组织方式、命名规则和常见约定 -->

```css
/* ✅ 正确：使用 BEM 命名（如项目约定 BEM） */
.userProfile { ... }
.userProfile__avatar { ... }
.userProfile--active { ... }

/* ❌ 错误：使用无语义的缩写 */
.up { ... }
.up-av { ... }
```

### 6.3 响应式设计

<!-- 填写指引：定义断点系统、响应式布局策略 -->

- **断点系统**：{{例如：sm: 640px, md: 768px, lg: 1024px, xl: 1280px}}
- **布局策略**：{{例如：Mobile First / Desktop First}}
- **单位选择**：{{例如：间距使用 rem，字体使用 px，布局使用 % 或 flex/grid}}

### 6.4 禁止写法

<!-- 填写指引：列出所有明确禁止的样式写法 -->

| 禁止写法 | 原因 | 替代方案 |
|---------|------|---------|
| {{例如：!important}} | {{例如：破坏样式优先级}} | {{例如：提高选择器特异性}} |
| {{例如：内联 style（静态值）}} | {{例如：无法复用和覆盖}} | {{例如：使用 CSS Modules 类名}} |
| {{例如：* 通配符选择器}} | {{例如：性能问题}} | {{例如：具体选择器}} |

---

## 7. Git 工作流

<!-- 填写指引：定义分支策略、提交信息规范和协作流程，根据团队规模调整严格程度 -->

### 7.1 分支策略

<!-- 填写指引：根据团队规模选择合适的分支模型 -->

- **分支模型**：{{例如：GitHub Flow / Git Flow / Trunk-Based}}
- **主分支**：{{例如：main（生产）/ develop（开发）}}
- **功能分支命名**：{{例如：feature/xxx / fix/xxx / chore/xxx}}

```bash
# ✅ 正确
git checkout -b feature/user-profile-page
git checkout -b fix/login-error-handling
git checkout -b chore/update-dependencies

# ❌ 错误
git checkout -b my-branch
git checkout -b test
git checkout -b fix
```

### 7.2 提交信息规范

<!-- 填写指引：使用 Conventional Commits 规范，确保提交历史可追溯 -->

- **规范**：{{例如：Conventional Commits}}
- **格式**：`<type>(<scope>): <description>`
- **类型**：{{例如：feat / fix / docs / style / refactor / perf / test / chore}}

```text
# ✅ 正确
feat(auth): 添加用户登录功能
fix(cart): 修复购物车数量计算错误
refactor(utils): 重构日期格式化工具函数

# ❌ 错误
update code
fix bug
修改了一些东西
```

### 7.3 Code Review 流程（如适用）

<!-- 填写指引：根据团队规模定义 Code Review 要求，1-3 人团队可简化 -->

- **是否强制**：{{例如：2 人以上团队强制 CR}}
- **审查重点**：{{例如：类型安全、性能影响、安全性、可读性}}
- **合并条件**：{{例如：至少 1 人 approve，CI 全部通过}}

---

## 8. 代码注释规范

<!-- 填写指引：定义注释的使用场景和格式，避免过度注释或注释不足 -->

### 8.1 注释原则

<!-- 填写指引：好的代码是自解释的，注释用于解释"为什么"而不是"做什么" -->

- **注释语言**：{{例如：中文（与团队沟通语言一致）}}
- **注释场景**：{{例如：复杂业务逻辑、非显而易见的设计决策、临时方案（TODO）}}
- **不需要注释**：{{例如：简单的 getter/setter、显而易见的逻辑}}

### 8.2 JSDoc 规范

<!-- 填写指引：公共 API（导出的函数、类、类型）必须使用 JSDoc -->

```typescript
/**
 * 格式化日期为中文显示格式
 * @param date - 需要格式化的日期对象或时间戳
 * @param format - 格式模板，默认 'YYYY-MM-DD'
 * @returns 格式化后的日期字符串
 * @throws {Error} 当 date 参数无效时抛出错误
 *
 * @example
 * formatDate(new Date(), 'YYYY-MM-DD') // => '2024-01-15'
 * formatDate(1705276800000) // => '2024-01-15'
 */
export function formatDate(date: Date | number, format = 'YYYY-MM-DD'): string {
  // ...
}
```

### 8.3 TODO / FIXME 格式

<!-- 填写指引：统一临时标记的格式，便于后续搜索和跟踪 -->

```typescript
// ✅ 正确：TODO 附带作者和原因
// TODO(zhangsan): 这里的分页逻辑需要优化，当前在大数据量下有性能问题

// ✅ 正确：FIXME 标记已知问题
// FIXME(2024-01-15): 并发请求时偶发竞态条件，需要加锁

// ❌ 错误：无上下文的 TODO
// TODO: 修复
// fixme
```

---

## 9. AI 协作协议

<!-- 填写指引：本章节定义 AI 辅助编码时的行为准则，确保 AI 生成的代码符合项目规范 -->

### 9.1 必读文档清单

<!-- 填写指引：AI 在为本项目写代码前必须读取的文档列表 -->

AI 在为本项目编写或修改前端代码前，必须先读取以下文档：

1. `../../../specs/PROJECT-CONTEXT.md` — 项目全景上下文
2. `specs/前端开发规范.md` — 本文档
3. `specs/技术栈.md` — 技术栈决策
4. `specs/项目结构.md` — 目录结构约定
5. `specs/API接口文档.md` — 接口设计规范
6. `../../../specs/GUARDRAILS.md` — 项目边界守卫

### 9.2 写代码规则

<!-- 填写指引：AI 编写代码时必须遵守的规则 -->

1. **类型安全**：{{例如：所有函数参数和返回值必须有类型标注，禁止使用 any}}
2. **导入排序**：{{例如：必须按照第 5.3 节的排序规则组织 import 语句}}
3. **组件拆分**：{{例如：单个组件文件不超过 300 行}}
4. **错误处理**：{{例如：所有 async 函数必须有 try-catch 或 .catch()}}
5. **样式方案**：{{例如：只使用第 6 节规定的唯一样式方案}}
6. **命名规范**：{{例如：严格遵循第 3 节的命名约定}}

### 9.3 自检清单

<!-- 填写指引：AI 提交代码前必须逐项检查的清单 -->

- [ ] 所有 TypeScript 类型是否正确，无 any 类型
- [ ] 所有 import 是否按规范排序
- [ ] 组件 Props 是否有 interface 定义
- [ ] 是否使用了项目规定的样式方案
- [ ] 是否有未处理的 Promise（缺少 await 或 .catch）
- [ ] 是否有硬编码的字符串（应提取为常量）
- [ ] 是否有 console.log 残留（生产代码中）
- [ ] 文件命名是否符合第 3.1 节的约定

### 9.4 错题本

<!-- 填写指引：记录 AI 常见的编码错误和正确做法，持续更新 -->

| 错误模式 | 正确做法 | 备注 |
|---------|---------|------|
| {{例如：使用 any 绕过类型检查}} | {{例如：使用 unknown 或具体类型}} | {{例如：TypeScript 严格模式下 any 会导致类型安全漏洞}} |
| {{例如：在 useEffect 中直接修改 state 而不检查依赖}} | {{例如：使用 useRef 或正确声明依赖数组}} | {{例如：常见闭包陷阱}} |
| {{例如：导入整个库而非按需导入}} | {{例如：使用具名导入减少包体积}} | {{例如：Tree-shaking 优化}} |

---

> 本文档基于项目技术栈定制生成，所有规则均针对本项目优化。
> 如有疑问或需要调整，请在团队内部讨论后更新本文档。

---

## 10. 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| {{YYYY-MM-DD}} | 1.0 | 初始版本 | {{作者}} |
