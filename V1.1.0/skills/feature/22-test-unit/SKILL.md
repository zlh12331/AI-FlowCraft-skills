---
name: "22-test-unit"
description: "扫描项目源码，自动识别可测试的函数/方法，编写并运行单元测试代码，生成覆盖率报告。当用户提到「单元测试」、「unit test」、「写单测」、「代码覆盖率」时使用。支持 JS/TS、Python、Java、Go、Rust、C# 六大语言。"
---

# 单元测试（Unit Test）

> AI 阅读项目源码，自动识别可测试的函数/方法，编写并运行单元测试代码，生成覆盖率报告。

## 描述

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
| 3 | 测试框架已安装（必须） | 检查 vitest/jest/pytest | 报错并终止 |
| 4 | specs 目录存在（建议） | `ls specs/` | [降级执行] 不读取 specs，仅基于源码分析 |
| 5 | 功能需求文档存在（建议） | `ls specs/features/` | [降级执行] 不关联 AC，仅基于源码分析 |
| 6 | 阶段完成报告（建议） | `docs/开发记录/{功能名}_阶段完成报告.md` 存在，用于了解当前代码状态和已知问题 | [降级执行] 不读取阶段报告，仅基于源码分析 |

## 使用场景

- 对项目（前端/后端/系统编程）进行单元测试
- 生成函数/方法级别的测试用例
- 自动生成 Mock 模板（jest.mock / pytest.fixture / @Mock / testify / Moq）
- 生成参数化测试（test.each / @pytest.mark.parametrize / @ParameterizedTest）
- 检查代码质量（静态分析）
- 生成代码覆盖率报告

### 不适用场景
- **组件测试**：请引导至 `23-test-component` Skill
- **集成测试**：请引导至 `24-test-integration` Skill
- **E2E 测试**：请引导至 `25-test-e2e` Skill
- **系统测试**：请引导至 `26-test-system` Skill

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
6. **AC 覆盖**：如果功能需求文档存在，测试用例必须覆盖 AC 中与函数/方法行为和返回值相关的验收标准
7. **禁止弱断言**：禁止使用弱断言（如 Jest/Vitest 的 toBeTruthy/toBeFalsy；pytest 的 assertIsNone；Go 的 assert.Nil 等）作为唯一断言。必须断言具体的返回值（`toBe`、`toEqual`、`toMatchObject`、`assertEqual`）。异常测试必须验证异常类型和/或异常消息
8. **禁止复制源码逻辑**：测试中的预期值必须是独立确定的常量，不得复现被测函数的计算逻辑。例如测试 `add(a, b)` 时，预期值应写 `3` 而非 `a + b`
9. **测试必须可重复**：涉及时间的测试必须 Mock 时间（`jest.useFakeTimers`（JS/TS 项目）/ `freezegun`（Python 项目））；涉及随机的测试必须固定种子；涉及文件系统的测试必须使用临时目录（`tmp_path`（pytest 项目）/ `fs.mkdtemp`（Node.js 项目））
10. **禁止修改源码**：Write 工具仅用于创建测试文件，禁止修改任何非测试源码文件。测试失败时，只能修改测试代码。如果判断是源码 Bug，必须在测试中用注释标记 BUG（如 JS/TS: `// BUG: 源码问题`；Python: `# BUG: 源码问题`）并记录到报告中
11. **断言数值必须与源码一致**：测试断言中的数值（如数组长度、对象属性数量）必须与被测源码的实际值完全一致。生成测试前必须先读取被测源码文件，确认实际值后再编写断言。禁止凭记忆或估算编写数值断言
12. **设计文档驱动的业务规则覆盖**：如果后端技术方案（Skill 10 产出）中包含"Service 层业务规则"章节，单元测试必须覆盖清单中定义的每条业务规则。具体要求：(1) 在第二步（源码分析）之前，先读取 `specs/features/{功能名}_后端技术方案.md`，提取"Service 层业务规则"章节中的所有规则项；(2) 为每条业务规则编写至少一个正向测试和一个异常/边界测试；(3) 在测试报告中增加"业务规则覆盖"章节，逐项列出每条规则的测试覆盖状态。

> 支持 **6 种语言**：JavaScript/TypeScript、Python、Java、Go、Rust、C#。
> 注意：TypeScript 项目会被归类为 `javascript` 或对应框架类型（如 `nextjs`、`react`）。

**推荐**：TypeScript + Jest（生态成熟、类型安全）。其他选项参见 `examples/test-examples.md`。

### 交互准则

1. **主动分析，不要被动询问**：不要问用户"需要测试什么"，你应该主动分析项目源码和 specs 文档，推荐测试策略
2. **保持务实**：小项目不需要追求 100% 覆盖率，优先测试核心业务逻辑和关键路径
3. **结果导向**：测试报告中的"改进建议"必须具体可操作（如"为 UserService.login() 添加密码强度校验的边界值测试"），不要写泛泛建议（如"提高覆盖率"）
4. **失败即信息**：测试失败不是坏事，每个失败都提供了改进代码质量的机会。报告中必须分析失败根因，而非仅记录失败现象

### 输出模板

> **输出文件路径**：`docs/测试报告/单元测试报告.md`
> **报告格式**：Markdown，由辅助脚本 `generate_report.py` 自动生成
> **占位符规则**：`{{}}` 标记的占位符必须替换为实际值，不得保留占位符

测试报告必须包含以下章节：
1. 测试概览（项目信息、测试框架、扫描/编写统计）
2. 测试结果（通过/失败/跳过/通过率）
3. 覆盖情况（函数/组件/端点覆盖详情）
4. 失败详情（失败测试的错误信息和修复建议）
5. 改进建议（基于测试结果的具体改进建议）

### 辅助脚本

本 Skill 提供以下辅助脚本（位于 `resources/` 目录）：

| 脚本 | 用途 | 用法 |
|------|------|------|
| `scan_source.py` | 扫描项目源码，识别可测试函数 | `python resources/scan_source.py <项目路径> [输出JSON]` |
| `generate_tests.py` | 生成测试代码 + Mock 模板 + 参数化测试 | `python resources/generate_tests.py <扫描结果JSON> <输出目录> [项目路径]` |
| `run_tests.py` | 运行测试并收集覆盖率数据 | `python resources/run_tests.py <项目路径> [--coverage] [--output <JSON路径>]` |
| `generate_report.py` | 生成 Markdown 格式测试报告 | `python resources/generate_report.py <测试结果JSON> <报告输出路径> [扫描结果JSON]` |

#### 中间文件格式

脚本之间通过 JSON 文件传递数据。AI Agent 可直接读取这些文件获取结构化信息。详细格式定义见 `examples/test-examples.md` 附录。

- **scan_result.json**（`scan_source.py` 输出）：包含 `project_type`、`total_functions`、`testable_functions`、`functions` 数组（每个函数含 name/file/line/params/language/return_type/exceptions/dependencies/docstring/branches）
- **test_result.json**（`run_tests.py --output` 输出）：包含 framework/passed/failed/skipped/total/pass_rate/coverage/error 等字段

> **注意**：`duration`（执行时间）字段由 `generate_report` 从测试输出的原始文本中解析获取，而非 `run_tests` 直接提供。

> **注意**：辅助脚本用于预处理和批量操作，AI 仍需根据源码分析结果手动编写/完善测试代码中的具体测试值和断言。

---

### 七步流程

#### 第一步：环境检测与准备

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

> **辅助验证**（可选）：运行 `npx jest --version` / `npx vitest --version` / `python -m pytest --version` / `mvn test -v` / `go test ./...` / `cargo test --version` / `dotnet test --version` 确认框架是否可用。

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

如项目无测试配置文件，需创建。Jest 项目创建 `jest.config.js`（设置 testEnvironment、transform、testMatch、collectCoverageFrom、coverageThreshold）；pytest 项目创建 `pytest.ini`（设置 testpaths、python_files、addopts 含 `--cov`）。

---

#### 第二步：源码分析

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
python resources/scan_source.py <项目路径> ./scan_result.json
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

#### 第三步：编写测试用例

**3.1 生成测试代码框架**

```bash
# 基于扫描结果生成测试代码骨架（含 Mock 模板和参数化测试）
python resources/generate_tests.py ./scan_result.json ./generated_tests/
```

> **重要：禁止直接使用脚本生成的 TODO 占位符！** AI 必须基于源码分析结果，自主填充每个测试的具体参数值和预期断言。脚本生成的测试代码仅作为结构模板，AI 需要手动完善每个测试用例的实际测试值和断言。

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

所有测试用例遵循 **Arrange-Act-Assert (AAA)** 模式。代码示例见「示例」章节。

**（Jest/Vitest 项目）describe/it 命名规范**：
- `describe('函数名', ...)` — 被测函数
- `it('should 期望行为 when 条件', ...)` — 测试场景
- 中文项目可用中文：`it('应返回正确结果 当输入合法时', ...)`

**3.4 Mock 指南**

当函数有外部依赖时，必须使用 Mock 隔离。代码示例见「示例」章节。

> **自动 Mock 模板**：`generate_tests.py` 会根据扫描结果中的 `dependencies` 字段自动生成 Mock 模板文件：
> - JS/TS → `__mocks__/<dep>.mock.ts`
> - Python → `conftest.py`（pytest fixture）
> - Java → `MockTemplates.java`
> - Go → `mock_<dep>.go`
> - Rust → `mock_<dep>.rs`
> - C# → `MockTemplates.cs`

**3.5 参数化测试指南**

使用参数化测试减少重复代码，覆盖多组输入。代码示例见「示例」章节。

**3.6 测试代码规范**

各语言测试代码示例见「示例」章节。

---

#### 第四步：运行测试

**4.1 运行测试脚本**

```bash
# 运行测试并收集覆盖率（--output 保存结果为 JSON，供第六步生成报告）
python resources/run_tests.py <项目路径> --coverage --output ./test_result.json
```

或手动运行各语言测试命令：JS/TS（`npx jest --coverage`）、Python（`pytest tests/ -v --cov=src`）、Java（`mvn test` / `gradle test`）、Go（`go test ./... -coverprofile=coverage.out`）、Rust（`cargo test`）、C#（`dotnet test --collect:"XPlat Code Coverage"`）。

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

#### 第五步：代码质量检查

**5.1 运行静态分析**

各语言静态分析工具：JS/TS（`eslint`）、Python（`pylint` / `flake8`）、Java（`checkstyle`）、Go（`go vet` / `golangci-lint`）、Rust（`cargo clippy`）、C#（`dotnet format --verify-no-changes`）。

**5.2 检查项目**

| 检查项 | 严重程度 | 说明 |
|-------|---------|------|
| 未使用变量/导入 | Warning | 清理无用代码 |
| 空指针/None 访问 | Critical | 可能导致运行时崩溃 |
| 类型不匹配 | Critical | TypeScript/Python/Rust 类型检查 |
| 硬编码密钥/密码 | Critical | 安全风险 |
| SQL 拼接 | Critical | SQL 注入风险 |
| 不安全的随机数 | Warning | 密码学相关需用 secrets 模块 |
| 圈复杂度 > 10 | Warning | 建议拆分函数 |
| 重复代码率 > 3% | Info | 建议提取公共函数 |
| 缺少错误处理 | Warning | try-catch/except/?/Result 覆盖 |

---

#### 第六步：生成报告

**6.1 运行报告生成脚本**

```bash
python resources/generate_report.py ./test_result.json docs/测试报告/单元测试报告.md ./scan_result.json
```

**6.2 报告内容**

生成的 Markdown 报告包含以下章节：测试概览（项目信息、框架、扫描/编写统计）、测试结果（通过/失败/跳过/通过率）、执行时间分析、代码覆盖率（行/分支/函数/语句）、函数测试覆盖情况、未覆盖函数、失败详情、改进建议、通过标准（通过率 100%、行覆盖率 >= 80%、分支覆盖率 >= 70%、函数覆盖率 >= 80%、执行时间 < 120s）。

---

#### 第七步：变异测试（可选进阶）

> 变异测试（Mutation Testing）用于评估测试套件的质量。它通过修改源码（引入"变异"），检查测试是否能检测到这些修改。

> 变异测试是可选的进阶步骤，仅在测试套件稳定后运行。各语言工具：JS（Stryker）、Python（mutmut）、Java（PITest）、Rust（cargo-mutants）。

---

### 通过标准

| 指标 | 理想标准 | 最低可接受标准 |
|------|---------|-------------|
| 测试通过率 | 100% | >= 90%（源码缺陷已记录的除外） |
| 行覆盖率 | >= 80% | >= 60% |
| 分支覆盖率 | >= 70% | >= 50% |
| 函数覆盖率 | >= 80% | >= 60% |
| 总执行时间 | < 60s | < 120s（CI/CD 友好） |
| Critical 问题 | 0 个 | 0 个 |
| Warning 问题 | <= 3 个 | <= 5 个 |

> 大型遗留项目（>100 函数）可适用"最低可接受标准"。

### 注意事项

> **已知限制**：JS/TS/Java/Go/Rust/C# 的函数名匹配仅支持 ASCII 标识符（`[a-zA-Z0-9_]`），不支持 Unicode 函数名。Python 使用 AST 解析，支持 Unicode 函数名。

#### Mock 策略决策

```text
依赖是外部服务（API/数据库/文件系统）？→ 全量 Mock（jest.mock（JS/TS 项目）/ patch（Python 项目）/ @Mock（Java/C# 项目））
依赖是内部模块？→ 部分 Spy（jest.spyOn（JS/TS 项目）/ patch.object（Python 项目））
依赖是非确定性（时间/随机数）？→ 专用 Fake（useFakeTimers（Jest 项目）/ freezegun.time_freezer（Python 项目） / seed（通用））
Mock 返回值应使用最小可用对象，而非完整真实对象
```

#### 反模式（禁止）

- **弱断言**：`expect(result).toBeDefined()` / `toBeTruthy()` / `not.toThrow()` 作为唯一断言
- **测试实现细节**：`expect(internalHelper).toHaveBeenCalled()`
- **无意义的测试**：`it('should work', () => { expect(func(1)).toBe(1); })`
- **复制源码逻辑**：`expect(add(a, b)).toBe(a + b)` -- 预期值复现了被测逻辑

#### 其他规则

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

### 失败处理

> 遵循 GUARDRAILS.md 中的全局失败处理规则。

## 示例

### TypeScript/Jest 快速示例（AAA 模式 + Mock + 参数化）

```typescript
import { formatDate, validateEmail } from '../utils/helpers';

// AAA 模式 + 参数化测试
describe('formatDate', () => {
  it('应将 ISO 日期字符串格式化为 YYYY-MM-DD', () => {
    // Arrange & Act
    const result = formatDate('2024-01-15T08:30:00Z');
    // Assert
    expect(result).toBe('2024-01-15');
  });

  it('无效日期应抛出 TypeError', () => {
    expect(() => formatDate('not-a-date')).toThrow(TypeError);
  });
});

// 参数化测试（test.each）
describe('validateEmail', () => {
  it.each([
    ['user@example.com', true],
    ['', false],
    ['not-an-email', false],
  ])('应验证 %s → %s', (input, expected) => {
    expect(validateEmail(input)).toBe(expected);
  });
});
```

> 更多语言的测试示例（Python、Java、Go、Rust、C#、Mock 指南、参数化测试等）请参见 `examples/test-examples.md`。
