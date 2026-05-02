---
name: "22-test-unit"
description: "单元测试技能。当用户提到"单元测试"、"unit test"、"函数测试"、"方法测试"、"代码质量"、"静态分析"、"代码覆盖率"、"写单测"、"生成测试用例"、"mock测试"、"参数化测试"、"变异测试"时使用此技能。支持 JavaScript/TypeScript、Python、Java、Go、Rust、C# 六大语言。AI 会阅读项目源码，自动编写并运行单元测试代码，生成覆盖率报告。"
allowed-tools: RunCommand, Read, Write, Grep, Glob, LS
metadata:
  author: AI
  version: "6.4.0"
  updated: "2026-04-19"
---

# 单元测试（Unit Test）

> AI 阅读项目源码，自动识别可测试的函数/方法，编写并运行单元测试代码，生成覆盖率报告。

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
| 2 | 项目类型已识别（必须） | 检查 package.json/pyproject.go.mod 等 | 报错并终止 |
| 3 | 测试框架已安装（必须） | 检查 vitest/jest/pytest | 报错并终止 |
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
6. **AC 覆盖**：如果功能需求文档存在，测试用例必须覆盖 AC 中与函数/方法行为和返回值相关的验收标准
7. **禁止弱断言**：禁止使用弱断言（如 Jest/Vitest 的 toBeTruthy/toBeFalsy；pytest 的 assertIsNone；Go 的 assert.Nil 等）作为唯一断言。必须断言具体的返回值（`toBe`、`toEqual`、`toMatchObject`、`assertEqual`）。异常测试必须验证异常类型和/或异常消息
8. **禁止复制源码逻辑**：测试中的预期值必须是独立确定的常量，不得复现被测函数的计算逻辑。例如测试 `add(a, b)` 时，预期值应写 `3` 而非 `a + b`
9. **测试必须可重复**：涉及时间的测试必须 Mock 时间（`jest.useFakeTimers`（JS/TS 项目）/ `freezegun`（Python 项目））；涉及随机的测试必须固定种子；涉及文件系统的测试必须使用临时目录（`tmp_path`（pytest 项目）/ `fs.mkdtemp`（Node.js 项目））
10. **禁止修改源码**：Write 工具仅用于创建测试文件，禁止修改任何非测试源码文件。测试失败时，只能修改测试代码。如果判断是源码 Bug，必须在测试中用注释标记 BUG（如 JS/TS: // BUG: 源码问题；Python: # BUG: 源码问题）并记录到报告中
11. **断言数值必须与源码一致**：测试断言中的数值（如数组长度、对象属性数量）必须与被测源码的实际值完全一致。生成测试前必须先读取被测源码文件，确认实际值后再编写断言。禁止凭记忆或估算编写数值断言
> 支持 **6 种语言**：JavaScript/TypeScript、Python、Java、Go、Rust、C#。
> 注意：TypeScript 项目会被归类为 `javascript` 或对应框架类型（如 `nextjs`、`react`）。

## 输出模板

> **输出文件路径**：`docs/测试报告/单元测试报告.md`
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

- 对项目（前端/后端/系统编程）进行单元测试
- 生成函数/方法级别的测试用例
- 自动生成 Mock 模板（jest.mock / pytest.fixture / @Mock / testify / Moq）
- 生成参数化测试（test.each / @pytest.mark.parametrize / @ParameterizedTest）
- 检查代码质量（静态分析）
- 生成代码覆盖率报告

## 辅助脚本

本 Skill 提供以下辅助脚本（位于 `scripts/` 目录）：

| 脚本 | 用途 | 用法 |
|------|------|------|
| `scan_source.py` | 扫描项目源码，识别可测试函数 | `python scripts/scan_source.py <项目路径> [输出JSON]` |
| `generate_tests.py` | 生成测试代码 + Mock 模板 + 参数化测试 | `python scripts/generate_tests.py <扫描结果JSON> <输出目录> [项目路径]` |
| `run_tests.py` | 运行测试并收集覆盖率数据 | `python scripts/run_tests.py <项目路径> [--coverage] [--output <JSON路径>]` |
| `generate_report.py` | 生成 Markdown 格式测试报告 | `python scripts/generate_report.py <测试结果JSON> <报告输出路径> [扫描结果JSON]` |

### 中间文件格式

脚本之间通过 JSON 文件传递数据。AI Agent 可直接读取这些文件获取结构化信息。

**scan_result.json**（`scan_source.py` 输出）：
```json
{
  "project_type": "string（nextjs/react/vue/python/java/go/rust/csharp/unknown）",
  "total_functions": "int",
  "testable_functions": "int",
  "functions": [{
    "name": "string（函数名）",
    "file": "string（相对路径）",
    "line": "int",
    "col": "int（仅 JS/TS）",
    "params": "string（参数列表）",
    "language": "string（js/ts/python/java/go/rust/csharp）",
    "return_type": "string",
    "exceptions": ["string"],
    "dependencies": ["string"],
    "docstring": "string",
    "branches": "int"
  }]
}
```

**test_result.json**（`run_tests.py --output` 输出）：
```json
{
  "framework": "string（jest/vitest/pytest/junit/go-test/cargo-test/xunit）",
  "passed": "int", "failed": "int", "skipped": "int", "total": "int",
  "pass_rate": "float（0-100）",
  "project_type": "string", "project_path": "string",
  "raw_output": "string（测试运行原始输出）",
  "errors": "int（可选，仅 Python，pytest 错误数）",
  "coverage": {
    "statement": "float（可选，0-100）",
    "branch": "float（可选）",
    "function": "float（可选）",
    "line": "float（可选）"
  },
  "error": "string（可选，运行出错时的错误信息）"
}
```

> **注意**：`duration`（执行时间）字段由 `generate_report` 从测试输出的原始文本中解析获取，而非 `run_tests` 直接提供。

> **注意**：辅助脚本用于预处理和批量操作，AI 仍需根据源码分析结果手动编写/完善测试代码中的具体测试值和断言。

---

## 七步流程

### 第一步：环境检测与准备

**1.1 识别项目类型**

> 运行 `scan_source.py` 会自动识别项目类型。以下为检测优先级参考：

```text
package.json → 读 dependencies 判断框架（Next.js/React/Vue/Nuxt/Angular/Svelte/纯JS）
pom.xml / build.gradle → Java
requirements.txt / pyproject.toml / setup.py → Python
go.mod → Go
Cargo.toml → Rust
*.csproj / *.sln → C#
以上均无 → 按文件扩展名回退推断（.py/.js/.ts/.java/.go/.rs/.cs）
```

**Monorepo 检测**（AI Agent 自行处理）：如发现 `pnpm-workspace.yaml`、`lerna.json`、`nx.json`、`turbo.json`，按子包逐个处理（脚本本身不自动检测 Monorepo）。

**1.2 检测已安装的测试框架**

> **优先级**：优先使用项目已安装的测试框架；如未安装，按下方推荐表安装；如已安装多个，使用配置最完整的一个。

主要通过检查项目配置文件中的依赖声明来检测（`package.json` 的 `devDependencies`、`requirements.txt`、`pom.xml` 等），而非运行 `--version` 命令。

> **主要方式**：检查项目配置文件中的依赖声明（`package.json` 的 `devDependencies`、`requirements.txt`、`pom.xml` 等）。

> **辅助验证**（可选）：运行以下命令确认框架是否可用：

```bash
# JavaScript/TypeScript
npx jest --version 2>/dev/null          # Jest
npx vitest --version 2>/dev/null         # Vitest

# Python
python -m pytest --version 2>/dev/null   # pytest

# Java
mvn test -v 2>/dev/null                  # Maven + JUnit

# Go / Rust / C#
go test ./... 2>/dev/null                # 内置 testing
cargo test --version 2>/dev/null         # 内置 cargo test
dotnet test --version 2>/dev/null        # .NET CLI
```

**1.3 安装测试框架（如未安装）**

> **Python 项目**：先检测是否在虚拟环境中（检查 `venv/`、`.venv/`、`conda` 环境变量）。如不在虚拟环境中，先创建：`python -m venv venv && source venv/bin/activate`。

> **Node.js 项目**：检查 `.nvmrc` / `.node-version` / `volta` 配置，确保使用项目要求的 Node.js 版本。

| 项目类型 | 推荐框架 | 安装命令 |
|---------|---------|---------|
| React/Next.js | Jest + RTL | `npm install -D jest @testing-library/react @testing-library/jest-dom ts-jest @types/jest` |
| Vue/Nuxt.js | Vitest + VTU | `npm install -D vitest @vue/test-utils happy-dom @testing-library/vue` |
| Angular | Jest | `ng test` (Angular CLI 内置) |
| Svelte | Vitest | `npm install -D vitest @testing-library/svelte jsdom` |
| Node.js | Jest | `npm install -D jest ts-jest @types/jest` |
| Python | pytest | `pip install pytest pytest-cov pytest-mock`（虚拟环境外加 `--break-system-packages`） |

> **Python 测试框架**：优先使用 `pytest`。如果未安装 pytest，自动回退到 `unittest`（但无法收集覆盖率数据）。

| Java (Maven) | JUnit 5 | 在 pom.xml 添加 `junit-jupiter` 依赖 |
| Java (Gradle) | JUnit 5 | 在 build.gradle 添加 `testImplementation 'org.junit.jupiter:junit-jupiter'` |
| Go | testing（内置） | Go 1.18+（使用了 `any` 类型和泛型），无需安装，仅创建 `_test.go` 文件 |
| Rust | cargo test（内置） | `cargo add --dev test-case mockall`（参数化测试和 Mock 支持） |
| C# | xUnit | `dotnet add package xunit` + `dotnet add package xunit.runner.visualstudio` |

> **Rust 依赖说明**：`generate_rust_tests` 生成的参数化测试依赖 `test-case = "3"` crate，Mock 模板依赖 `mockall = "0.11"` crate。如果不需要参数化测试或 Mock，可以只安装其中一个或不安装。

**1.4 配置测试环境**

```bash
# Jest 配置（如项目无 jest.config.js）
cat > jest.config.js << 'EOF'
module.exports = {
  testEnvironment: 'jsdom',        // 前端项目用 jsdom，后端用 node
  transform: {
    '^.+\\.tsx?$': 'ts-jest',     // TypeScript 支持
  },
  testMatch: ['**/__tests__/**/*.(test|spec).(ts|tsx|js|jsx)'],
  collectCoverageFrom: [
    'src/**/*.{ts,tsx,js,jsx}',
    '!src/**/*.d.ts',
    '!src/**/index.{ts,tsx,js,jsx}',
  ],
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 }
  }
};
EOF

# pytest 配置（如项目无 pytest.ini / pyproject.toml）
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short --cov=src --cov-report=term-missing --cov-report=html
EOF
```

---

### 第二步：源码分析

> **自动排除目录**：扫描时会自动跳过以下目录，无需手动排除：
> - **通用**：`.git`、`node_modules`
> - **JS/TS**：`.next`、`.nuxt`、`dist`、`build`、`coverage`、`__pycache__`
> - **Python**：`__pycache__`、`venv`、`.venv`、`env`、`dist`、`build`、`coverage`
> - **Java**：`target`、`build`、`.idea`
> - **Go**：`vendor`
> - **Rust**：`target`
> - **C#**：`bin`、`obj`、`.vs`、`TestResults`

**2.0 检查已有测试文件**

在分析源码之前，先扫描项目中是否已存在测试文件：

```text
已有测试？
  ├─ 有 → 分析已有测试覆盖了哪些函数
  │   ├─ 提取已有测试的函数名列表
  │   ├─ 与扫描结果对比，找出覆盖缺口
  │   └─ 仅对未覆盖的函数生成新测试（避免重复）
  └─ 无 → 对所有可测试函数生成测试
```

> **注意**：新测试的命名风格和导入路径应与已有测试保持一致。

**2.1 运行扫描脚本**

```bash
# 扫描项目，输出 JSON 结果
python scripts/scan_source.py <项目路径> /data/user/work/scan_result.json
```

扫描脚本会自动：
- 识别项目类型（JS/TS/Python/Java/Go/Rust/C#）
- 提取所有可测试的函数/方法（排除私有方法、getter/setter、生命周期方法）
- 分析每个函数的参数、返回类型、异常抛出、依赖关系、条件分支数
- Python 使用 AST 精确解析；JS/TS 支持多行函数声明；其他语言使用正则

**2.2 AI 补充分析（脚本无法自动完成的部分）**

对扫描结果中的每个函数，AI 需要阅读源码进行深度分析：

1. **读取函数源码**：使用 Read 工具读取函数所在文件，定位到函数体
2. **分析函数逻辑**：
   - 输入参数的类型约束（TypeScript 类型注解、Python 类型提示、Java 泛型、Rust 类型）
   - 返回值的具体结构和含义
   - 函数内部调用的其他函数（依赖关系）
   - 可能抛出的异常（`throw`、`raise`、`throws`、`Result::Err`）
   - 条件分支（if/else、switch、三元表达式、match）→ 每个分支至少一个测试
   - 循环逻辑 → 空集合、单元素、多元素各一个测试
3. **确定 Mock 需求**：
   - 外部 API 调用 → Mock fetch/axios/requests/reqwest
   - 数据库操作 → Mock ORM/DAO 层
   - 文件系统 → Mock fs 模块
   - 时间相关 → Mock Date/时间函数

**2.3 确定测试优先级**

| 优先级 | 函数类型 | 说明 |
|-------|---------|------|
| P0 | 核心业务逻辑 | 支付、认证、数据处理等关键函数 |
| P1 | 工具函数 | utils/helpers 中的通用函数 |
| P2 | 数据转换 | 格式化、序列化、类型转换函数 |
| P3 | 组件方法 | React/Vue/Svelte 组件中的业务方法 |

> 如函数数量过多（>50），优先测试 P0 和 P1 级别的函数。

---

### 第三步：编写测试用例

**3.1 生成测试代码框架**

```bash
# 基于扫描结果生成测试代码骨架（含 Mock 模板和参数化测试）
python scripts/generate_tests.py /data/user/work/scan_result.json /data/user/work/generated_tests/
```

> **⚠️ 重要：禁止直接使用脚本生成的 TODO 占位符！** AI 必须基于源码分析结果，自主填充每个测试的具体参数值和预期断言。脚本生成的测试代码仅作为结构模板，AI 需要手动完善每个测试用例的实际测试值和断言。

**3.2 AI 编写完整测试代码**

对每个函数，AI 需要编写以下测试用例：

| 测试类型 | 覆盖场景 | 示例 |
|---------|---------|------|
| 正向测试 | 正常输入 → 预期输出 | `addUser({name: "张三", age: 25})` → 返回用户对象 |
| 边界值测试 | 空值、极值、临界值 | `null`、`undefined`、`""`、`[]`、`0`、`Number.MAX_SAFE_INTEGER` |
| 类型错误测试 | 错误类型输入 → 抛异常 | 传数字给期望字符串的参数 |
| 等价类测试 | 有效等价类 + 无效等价类 | 年龄: 0-150(有效), -1/999(无效) |
| 分支覆盖 | 每个条件分支至少一次 | if-else 的 true 和 false 分支 |
| 异常路径 | 异常情况下的行为 | 网络超时、数据不存在、权限不足 |
| 参数化测试 | 多组输入-输出对 | `test.each([[1,2,3], [0,0,0], [-1,-2,-3]])` |

**3.3 测试命名规范（AAA 模式）**

所有测试用例遵循 **Arrange-Act-Assert (AAA)** 模式：

```javascript
// ✅ AAA 模式示例（Jest）
describe('calculatePrice', () => {
  it('应正确计算含税价格', () => {
    // Arrange（准备）
    const price = 100;
    const taxRate = 0.13;

    // Act（执行）
    const result = calculatePrice(price, taxRate);

    // Assert（断言）
    expect(result).toBeCloseTo(113, 2);
  });
});
```

```python
# ✅ AAA 模式示例（pytest）
class TestCalculatePrice:
    def test_should_calculate_price_with_tax(self):
        # Arrange（准备）
        price = 100
        tax_rate = 0.13

        # Act（执行）
        result = calculate_price(price, tax_rate)

        # Assert（断言）
        assert result == pytest.approx(113, abs=0.01)
```

**（Jest/Vitest 项目）describe/it 命名规范**：
- `describe('函数名', ...)` — 被测函数
- `it('should 期望行为 when 条件', ...)` — 测试场景
- 中文项目可用中文：`it('应返回正确结果 当输入合法时', ...)`

**3.4 Mock 指南**

当函数有外部依赖时，必须使用 Mock 隔离：

```javascript
// ✅ Jest Mock 示例
// 模块级别 Mock（文件顶部）
jest.mock('../api/userService', () => ({
  getUserById: jest.fn(),
  createUser: jest.fn(),
}));

import { getUserById } from '../api/userService';

describe('UserProfile', () => {
  it('应正确显示用户信息', async () => {
    // Arrange：设置 Mock 返回值
    getUserById.mockResolvedValue({ id: 1, name: '张三' });

    // Act
    const profile = await fetchUserProfile(1);

    // Assert
    expect(profile.name).toBe('张三');
    expect(getUserById).toHaveBeenCalledWith(1);
  });
});
```

```python
# ✅ pytest Mock 示例
from unittest.mock import patch, MagicMock

class TestUserService:
    @patch('services.user_service.requests.get')
    def test_should_fetch_user_successfully(self, mock_get):
        # Arrange：设置 Mock 返回值
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": 1, "name": "张三"}

        # Act
        user = get_user(1)

        # Assert
        assert user["name"] == "张三"
        mock_get.assert_called_once_with("https://api.example.com/users/1")
```

> **自动 Mock 模板**：`generate_tests.py` 会根据扫描结果中的 `dependencies` 字段自动生成 Mock 模板文件：
> - JS/TS → `__mocks__/<dep>.mock.ts`
> - Python → `conftest.py`（pytest fixture）
> - Java → `MockTemplates.java`
> - Go → `mock_<dep>.go`
> - Rust → `mock_<dep>.rs`
> - C# → `MockTemplates.cs`

**3.5 参数化测试指南**

使用参数化测试减少重复代码，覆盖多组输入：

```javascript
// ✅ Jest test.each 示例
describe('validateEmail', () => {
  it.each([
    ['user@example.com', true],
    ['user@mail.example.com', true],
    ['', false],
    ['not-an-email', false],
    ['user@', false],
  ])('应验证 %s → %s', (input, expected) => {
    expect(validateEmail(input)).toBe(expected);
  });
});
```

```python
# ✅ pytest @pytest.mark.parametrize 示例
@pytest.mark.parametrize("email, expected", [
    ("user@example.com", True),
    ("user@mail.example.com", True),
    ("", False),
    ("not-an-email", False),
    ("user@", False),
])
def test_validate_email(email, expected):
    assert validate_email(email) is expected
```

**3.6 测试代码规范**

```javascript
// ✅ 好的测试代码示例（Jest + React）
import { formatDate, calculatePrice } from '../utils/helpers';

describe('formatDate', () => {
  it('应将 ISO 日期字符串格式化为 YYYY-MM-DD', () => {
    // Arrange & Act
    const result = formatDate('2024-01-15T08:30:00Z');
    // Assert
    expect(result).toBe('2024-01-15');
  });

  it('空值输入应返回当前日期', () => {
    const today = new Date().toISOString().split('T')[0];
    expect(formatDate(null)).toBe(today);
  });

  it('无效日期应抛出 TypeError', () => {
    expect(() => formatDate('not-a-date')).toThrow(TypeError);
  });
});
```

```python
# ✅ 好的测试代码示例（pytest）
import pytest
from utils.validators import validate_email, validate_password

class TestValidateEmail:
    """邮箱验证函数测试"""

    def test_valid_email(self):
        """正向测试：合法邮箱应返回 True"""
        assert validate_email("user@example.com") is True

    def test_valid_email_with_subdomain(self):
        """正向测试：子域名邮箱也应通过"""
        assert validate_email("user@mail.example.com") is True

    def test_empty_email(self):
        """边界值测试：空字符串应返回 False"""
        assert validate_email("") is False

    def test_none_email(self):
        """边界值测试：None 应抛出 TypeError"""
        with pytest.raises(TypeError):
            validate_email(None)

    def test_email_without_at(self):
        """异常测试：缺少 @ 符号应返回 False"""
        assert validate_email("userexample.com") is False
```

```rust
// ✅ 好的测试代码示例（Rust）
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_should_calculate_sum() {
        // Arrange
        let numbers = vec![1, 2, 3, 4, 5];
        // Act
        let result = calculate_sum(&numbers);
        // Assert
        assert_eq!(result, 15);
    }

    #[test]
    fn test_should_return_zero_for_empty_input() {
        let result = calculate_sum(&[]);
        assert_eq!(result, 0);
    }

    #[test]
    #[should_panic(expected = "overflow")]
    fn test_should_panic_on_overflow() {
        let huge = vec![i32::MAX, 1];
        calculate_sum(&huge); // 应 panic
    }
}
```

```java
// ✅ 好的测试代码示例（Java JUnit 5）
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class UserServiceTest {
    private UserRepository mockRepo;
    private UserService userService;

    @BeforeEach
    void setUp() {
        mockRepo = mock(UserRepository.class);
        userService = new UserService(mockRepo);
    }

    @Test
    void should_return_user_when_found() {
        // Arrange
        User expected = new User(1L, "张三", "zhangsan@example.com");
        when(mockRepo.findById(1L)).thenReturn(Optional.of(expected));

        // Act
        User result = userService.getUserById(1L);

        // Assert
        assertEquals("张三", result.getName());
        verify(mockRepo).findById(1L);
    }

    @Test
    void should_throw_exception_when_user_not_found() {
        // Arrange
        when(mockRepo.findById(999L)).thenReturn(Optional.empty());

        // Act & Assert
        assertThrows(UserNotFoundException.class, () -> userService.getUserById(999L));
    }

    @ParameterizedTest
    @CsvSource({
        "user@example.com, true",
        "invalid-email, false",
        "'', false"
    })
    void should_validate_email(String email, boolean expected) {
        assertEquals(expected, userService.isValidEmail(email));
    }
}
```

```go
// ✅ 好的测试代码示例（Go testing + testify）
package service_test

import (
    "errors"
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "myapp/service"
)

// Mock 实现
type MockUserRepo struct {
    mock.Mock
}

func (m *MockUserRepo) FindByID(id int) (*service.User, error) {
    args := m.Called(id)
    if user := args.Get(0); user != nil {
        return user.(*service.User), nil
    }
    return nil, args.Error(1)
}

func TestUserService_GetUser_ShouldReturnUser(t *testing.T) {
    // Arrange
    mockRepo := new(MockUserRepo)
    svc := service.NewUserService(mockRepo)
    expected := &service.User{ID: 1, Name: "张三"}

    mockRepo.On("FindByID", 1).Return(expected, nil)

    // Act
    result, err := svc.GetUser(1)

    // Assert
    assert.NoError(t, err)
    assert.Equal(t, "张三", result.Name)
    mockRepo.AssertExpectations(t)
}

func TestUserService_GetUser_ShouldReturnError_WhenNotFound(t *testing.T) {
    // Arrange
    mockRepo := new(MockUserRepo)
    svc := service.NewUserService(mockRepo)

    mockRepo.On("FindByID", 999).Return(nil, errors.New("user not found"))

    // Act
    result, err := svc.GetUser(999)

    // Assert
    assert.Error(t, err)
    assert.Nil(t, result)
    assert.Contains(t, err.Error(), "user not found")
}
```

```csharp
// ✅ 好的测试代码示例（C# xUnit + FluentAssertions）
using FluentAssertions;
using Xunit;

public class CalculatorTests
{
    [Fact]
    public void Should_Add_Two_Numbers()
    {
        // Arrange
        var calculator = new Calculator();
        // Act
        var result = calculator.Add(3, 5);
        // Assert
        result.Should().Be(8);
    }

    [Theory]
    [InlineData(0, 0, 0)]
    [InlineData(-1, 1, 0)]
    [InlineData(100, 200, 300)]
    public void Should_Add_Various_Numbers(int a, int b, int expected)
    {
        var calculator = new Calculator();
        calculator.Add(a, b).Should().Be(expected);
    }
}
```

---

### 第四步：运行测试

**4.1 运行测试脚本**

```bash
# 运行测试并收集覆盖率（--output 保存结果为 JSON，供第六步生成报告）
python scripts/run_tests.py <项目路径> --coverage --output /data/user/work/test_result.json
```

或手动运行：

```bash
# JavaScript/TypeScript
npx jest --coverage --coverageDirectory=coverage

# Python
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

# Java (Maven)
mvn test -Djacoco.skip=false

# Java (Gradle)
gradle test jacocoTestReport

# Go
go test ./... -coverprofile=coverage.out && go tool cover -html=coverage.out

# Rust
cargo test
cargo tarpaulin --out Html  # 覆盖率（需安装 tarpaulin）

# C#
dotnet test --collect:"XPlat Code Coverage"
```

**4.2 处理测试失败**

当测试失败时，按以下流程处理：

```text
测试失败
  ├─ 分析失败信息（断言不匹配 / 异常抛出 / 超时）
  ├─ 读取失败测试的源码 + 被测函数源码
  ├─ 判断失败原因：
  │   ├─ 测试代码写错了（断言值不对、Mock 不完整）
  │   │   └─ 修复测试代码 → 重新运行
  │   ├─ 源码有 Bug（逻辑错误、边界未处理）
  │   │   └─ 记录为 Bug 报告（不修改源码）
  │   └─ 环境问题（依赖缺失、配置错误）
  │       └─ 修复环境 → 重新运行
  └─ 最多重试 3 次，仍失败则记录并继续下一个
```

**4.3 修复测试代码**

- AI 可以自动修复测试代码（修改断言值、补充 Mock、调整测试数据）
- **禁止修改源码**，除非用户明确要求
- 每次修复后重新运行测试，确认通过

---

### 第五步：代码质量检查

**5.1 运行静态分析**

```bash
# JavaScript/TypeScript
npx eslint src/ --format json --output-file /data/user/work/eslint_report.json

# Python
python -m pylint src/ --output-format=json > /data/user/work/pylint_report.json 2>/dev/null
# 或使用 flake8（更轻量）
python -m flake8 src/ --format=json --output-file /data/user/work/flake8_report.json

# Java
mvn checkstyle:check  # Maven
gradle checkstyleMain  # Gradle

# Go
go vet ./...
golangci-lint run

# Rust
cargo clippy           # Clippy lint
cargo check            # 编译检查

# C#
dotnet format --verify-no-changes  # 格式检查
```

**5.2 检查项目**

| 检查项 | 严重程度 | 说明 |
|-------|---------|------|
| 未使用变量/导入 | ⚠️ Warning | 清理无用代码 |
| 空指针/None 访问 | 🔴 Critical | 可能导致运行时崩溃 |
| 类型不匹配 | 🔴 Critical | TypeScript/Python/Rust 类型检查 |
| 硬编码密钥/密码 | 🔴 Critical | 安全风险 |
| SQL 拼接 | 🔴 Critical | SQL 注入风险 |
| 不安全的随机数 | ⚠️ Warning | 密码学相关需用 secrets 模块 |
| 圈复杂度 > 10 | ⚠️ Warning | 建议拆分函数 |
| 重复代码率 > 3% | ℹ️ Info | 建议提取公共函数 |
| 缺少错误处理 | ⚠️ Warning | try-catch/except/?/Result 覆盖 |

---

### 第六步：生成报告

**6.1 运行报告生成脚本**

```bash
python scripts/generate_report.py /data/user/work/test_result.json docs/测试报告/单元测试报告.md /data/user/work/scan_result.json
```

**6.2 报告内容**

生成的 Markdown 报告包含：

```markdown
# 单元测试报告

## 概览
| 指标 | 数值 |
|------|------|
| 项目类型 | React / Python / Java / Go / Rust / C# |
| 测试框架 | Jest / pytest / JUnit / Go testing / cargo test / xUnit |
| 扫描函数总数 | XX |
| 可测试函数 | XX |
| 测试用例总数 | XX |

## 测试结果
| 指标 | 数值 |
|------|------|
| 通过 | XX |
| 失败 | XX |
| 跳过 | XX |
| 通过率 | XX% |

## 执行时间分析
| 指标 | 数值 |
|------|------|
| 总执行时间 | X.Xs |
| 平均每个测试 | X.Xms |

## 代码覆盖率
| 类型 | 覆盖率 | 状态 |
|------|--------|------|
| 行覆盖率 | XX% | ✅/⚠️ |
| 分支覆盖率 | XX% | ✅/⚠️ |
| 函数覆盖率 | XX% | ✅/⚠️ |
| 语句覆盖率 | XX% | ✅/⚠️ |

## 函数测试覆盖情况
| 函数名 | 文件 | 行号 | 参数 | 返回类型 | 分支数 | 测试状态 |
|--------|------|------|------|----------|--------|---------|

## 未覆盖函数
（列出所有未被测试覆盖的函数）

## 失败详情
（如有失败测试，展示失败信息）

## 改进建议
（基于覆盖率、执行时间、未覆盖函数的智能建议）

## 通过标准
| 指标 | 标准 | 实际 | 状态 |
|------|------|------|------|
| 测试通过率 | 100% | XX% | ✅/❌ |
| 行覆盖率 | ≥ 80% | XX% | ✅/❌ |
| 分支覆盖率 | ≥ 70% | XX% | ✅/❌ |
| 函数覆盖率 | ≥ 80% | XX% | ✅/❌ |
| 总执行时间 | < 120s | Xs | ✅/❌ |
```

---

### 第七步：变异测试（可选进阶）

> 变异测试（Mutation Testing）用于评估测试套件的质量。它通过修改源码（引入"变异"），检查测试是否能检测到这些修改。

**7.1 运行变异测试**

```bash
# JavaScript (Stryker Mutator)
npx stryker run

# Python (mutmut)
pip install mutmut --break-system-packages
mutmut run

# Java (PITest)
mvn org.pitest:pitest-maven:mutationCoverage

# Rust (cargo-mutants)
cargo install cargo-mutants
cargo mutants
```

**7.2 变异测试通过标准**

| 指标 | 标准 |
|------|------|
| 变异得分（Mutation Score） | ≥ 80% |
| 被杀死的变异体 | ≥ 总变异体的 80% |

> 变异测试是可选的进阶步骤，仅在测试套件稳定后运行。

---

## 通过标准

| 指标 | 理想标准 | 最低可接受标准 |
|------|---------|-------------|
| 测试通过率 | 100% | ≥ 90%（源码缺陷已记录的除外） |
| 行覆盖率 | ≥ 80% | ≥ 60% |
| 分支覆盖率 | ≥ 70% | ≥ 50% |
| 函数覆盖率 | ≥ 80% | ≥ 60% |
| 总执行时间 | < 60s | < 120s（CI/CD 友好） |
| Critical 问题 | 0 个 | 0 个 |
| Warning 问题 | ≤ 3 个 | ≤ 5 个 |

> 大型遗留项目（>100 函数）可适用"最低可接受标准"。

## 注意事项

> **已知限制**：JS/TS/Java/Go/Rust/C# 的函数名匹配仅支持 ASCII 标识符（`[a-zA-Z0-9_]`），不支持 Unicode 函数名。Python 使用 AST 解析，支持 Unicode 函数名。

### Mock 策略决策

```text
依赖是外部服务（API/数据库/文件系统）？→ 全量 Mock（jest.mock（JS/TS 项目）/ patch（Python 项目）/ @Mock（Java/C# 项目））
依赖是内部模块？→ 部分 Spy（jest.spyOn（JS/TS 项目）/ patch.object（Python 项目））
依赖是非确定性（时间/随机数）？→ 专用 Fake（useFakeTimers（Jest 项目）/ freezegun.time_freezer（Python 项目） / seed（通用））
Mock 返回值应使用最小可用对象，而非完整真实对象
```

### 反模式（禁止）

```javascript
// ❌ 反模式：弱断言
expect(result).toBeDefined();
expect(result).toBeTruthy();
expect(func).not.toThrow();

// ❌ 反模式：测试实现细节
expect(internalHelper).toHaveBeenCalled();

// ❌ 反模式：无意义的测试
it('should work', () => { expect(func(1)).toBe(1); });

// ❌ 反模式：复制源码逻辑
expect(add(a, b)).toBe(a + b);  // 预期值复现了被测逻辑
```

### 其他规则

- 测试代码必须带注释，说明测试目的和预期行为
- 测试数据使用 Mock/Fixture，不依赖真实数据库或外部服务
- 如项目无源码访问权限，提示用户需要提供源码路径
- 如函数数量过多（>50），优先测试核心业务逻辑函数
- 测试文件命名遵循项目约定（`.test.ts` / `test_*.py` / `*Test.java` / `*_test.go` / `*_test.rs` / `*Tests.cs`）
- 使用 AAA（Arrange-Act-Assert）模式组织测试代码
- 优先使用参数化测试覆盖多组输入，减少重复代码。对于相同函数的不同输入组合测试，应使用 `it.each` / `describe.each`（JS/TS 项目）/ `@pytest.mark.parametrize`（Python 项目）进行参数化，而非编写多个结构相同的独立测试用例

### 错误处理指引

| 错误场景 | 处理方式 |
|---------|---------|
| 脚本执行失败（报错退出） | 查看错误信息，修复后重试。常见原因：缺少依赖、路径不存在、权限不足 |
| JSON 文件缺失 | 确认上一步是否成功执行。`scan_result.json` 由第二步生成，`test_result.json` 由第四步 `--output` 生成 |
| JSON 文件格式损坏 | 删除后重新执行上一步 |
| 项目路径不存在 | 确认用户提供的路径正确，提示用户重新指定 |
| 权限不足（无法读/写文件） | 检查文件/目录权限，必要时提示用户 |
| 测试超时（>300s） | 检查是否有死循环或外部依赖未 Mock，增加超时时间或优化测试 |

> **超时配置**：默认测试超时为 300 秒（5 分钟），编译型语言（Java、Rust）使用 600 秒（10 分钟）超时。
