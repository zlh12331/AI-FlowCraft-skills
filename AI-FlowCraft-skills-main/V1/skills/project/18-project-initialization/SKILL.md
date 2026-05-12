---
name: "18-project-initialization"
description: "项目初始化执行者，读取 specs/ 下的定义文档，自动创建目录结构、配置文件和初始化 Git 仓库。在规划阶段文档就绪后使用，产出项目骨架代码和初始化记录。当用户需要将 specs 文档转化为实际项目时触发。触发词：项目初始化、初始化项目、脚手架"
---

# 18-project-initialization

## 描述

当用户完成规划阶段（即 `specs/` 下的文档已就绪）时，使用此 Skill 将文档转化为实际的代码骨架。

### 项目上下文协议

请严格遵守项目上下文强制协议：[../../../specs/PROJECT-CONTEXT.md](../../../specs/PROJECT-CONTEXT.md)

**在执行本 Skill 之前，必须先建立项目认知。**

### 边界守卫

请严格遵守通用边界守卫规则：[../../../specs/GUARDRAILS.md](../../../specs/GUARDRAILS.md)

**当前阶段**：编码与实现阶段 (Implementation)。

### 前置条件

| # | 前置条件 | 验证方式 | 不满足时的处理 |
|---|---------|---------|--------------|
| 1 | 项目未初始化（空目录） | 当前目录不存在 `.git` 目录或 `package.json`/`go.mod` 等核心配置文件 | 跳过初始化并生成记录 |
| 2 | 技术栈文档已就绪 | `specs/技术栈.md` 存在 | 提示用户先完成 Skill 3 |
| 3 | 项目结构文档已就绪 | `specs/项目结构.md` 存在 | 提示用户先完成 Skill 12 |
| 4 | 开发规范文档已就绪 | 全栈项目：`specs/前端开发规范.md`、`specs/后端开发规范.md` 均存在，`specs/前后端协作规范.md` 建议存在；纯后端项目：仅需 `specs/后端开发规范.md` 存在 | 提示用户先完成 Skill 13/14（纯后端项目仅需完成 Skill 14）；协作规范缺失时给出提示但不阻塞 |
| 5 | 环境与配置文档已就绪 | `specs/环境与配置文档.md` 存在且文件非空 | 提示用户先完成 Skill 16 |
| 6 | 项目认知建立 | 已读取 `../../../specs/PROJECT-CONTEXT.md`，了解项目全貌 | 自动创建 |
| 7 | 开发路线图建议存在 | `specs/开发路线图.md` 存在 | 若不存在，初始化记录中的下一步建议改为"请先执行 Skill 17（路线图规划）" |

> **注**：若项目已初始化（存在 `.git` 或核心配置文件），前置条件 2-4 非必须，Skill 将自动跳过初始化并生成记录。

## 使用场景

在规划阶段文档就绪后，当用户需要将 specs 文档转化为实际的项目骨架代码时触发。典型触发词：**项目初始化、初始化项目、脚手架**。

### 不适用场景

- **规划阶段文档未就绪**：请先完成 Skill 3/12/13/14/16 等规划阶段 Skill
- **需要具体功能开发**：请引导至 Skill 20（功能编码实现）
- **需要修改已有项目结构**：本 Skill 仅处理全新初始化，已有项目的结构修改请手动处理
- **需求变更**：请引导至 `27-feature-evolution` Skill

## 指令

### 输入

- 用户的需求描述或指令
- 项目相关文档（如已有 PRD、技术方案等）
- `templates/` 目录下的模板文件作为输出参考

### 任务目标

读取 `specs/技术栈.md`、`specs/项目结构.md`、`specs/环境与配置文档.md` 和开发规范文档，严格按照文档定义执行项目初始化——创建目录结构、生成配置文件、搭建测试框架、初始化 Git 仓库。不做任何文档中未定义的技术决策。产出项目骨架代码和 `docs/开发记录/初始化记录.md`。初始化完成的标准：目录结构与 `specs/项目结构.md` 一致，Git 仓库已初始化，所有配置文件已就位，测试框架已搭建并通过空运行验证。

### 工作流程

#### 1. 环境检查

- 检查当前目录是否已初始化（判断依据：存在 `.git` 目录 或 `package.json/go.mod` 等核心配置文件）。
- **如果项目已初始化**：
  - 输出提示："项目已存在，跳过初始化步骤。"
  - **不执行任何目录创建或文件修改操作**。
  - 生成/更新报告（记录"检测到项目已存在，未执行变更"）并结束。
- **如果项目未初始化**：继续执行下方步骤。
- 检查是否已安装 `specs/技术栈.md` 中指定的核心工具（如 Node.js, Go, Python）。
- **工具未安装时的处理**：如果核心工具未安装，暂停初始化并向用户报告缺失的工具列表和安装指引（包含工具名称、所需版本、安装命令）。等待用户安装完成后再继续。不得自动安装工具或跳过检查。

#### 2. 脚手架执行 (Scaffolding)

##### Step 0: 读取初始化所需文档

- `specs/技术栈.md` — 确定初始化命令（npm/cargo/pip 等）和核心配置文件（package.json / go.mod / Cargo.toml（仅 Rust 项目适用） / *.csproj + Program.cs（仅 C# 项目适用））
- `specs/项目结构.md` — 确定目录树结构
- `specs/环境与配置文档.md` — 确定需要创建的配置文件
- `specs/前端开发规范.md` + `specs/后端开发规范.md` — 确定 .gitignore 规则（如存在）
- `specs/前后端协作规范.md` — 确定联调相关配置（如存在则读取）

##### Step 1: 核心初始化

- 如技术栈指定了框架脚手架工具（如 `create-next-app`、`create-vue`、`create-react-app`），应优先使用脚手架工具初始化项目，而非手动执行 `npm init -y` 等通用命令。脚手架工具会自动生成框架推荐的目录结构和配置文件。
- 根据技术栈执行初始化命令（如 `npm init -y` 或 `go mod init <module_name>` 或 `cargo init --name <project-name>`（仅 Rust 项目适用）或 `dotnet new webapi -n <project-name>`（仅 C# 项目适用））。
- 初始化 Git 仓库：`git init`。
- **失败处理**：如果初始化命令执行失败（如 npm init 报错、磁盘空间不足），立即停止后续步骤，尝试清理已创建的文件和目录（如删除已创建的子目录、移除已初始化的 .git 目录），向用户报告具体错误信息和已执行的清理操作，并建议解决方案。

##### Step 2: 目录结构创建

- 读取 `specs/项目结构.md` 中的"目录树"部分。
- 使用 `mkdir -p` 批量创建所有文件夹。
- **关键**：为每个空文件夹创建一个 `.gitkeep`，确保 Git 能追踪。

##### Step 3: 基础文件生成

- 创建 `.gitignore` (根据 `specs/前端开发规范.md` 和 `specs/后端开发规范.md` 或技术栈自动生成)。
- 创建 `README.md` (写入项目名称和启动指南)。
- 创建 `.env.example`。

##### Step 3.5: 数据库初始化（使用数据库的项目必须执行）

- 根据 `specs/技术栈.md` 中的 ORM 选型和 `specs/数据库设计.md` 中的 schema，执行数据库初始化。
- **数据库初始化规则（根据 ORM 选型选择对应方案）**：
  - **Prisma**：运行 `npx prisma migrate dev --name init` 生成初始迁移并应用。确认 `prisma/` 目录下已生成 `migrations/` 文件夹和 `migration_lock.toml`。
  - **SQLAlchemy + Alembic**：运行 `alembic init alembic` 初始化迁移目录，然后 `alembic revision --autogenerate -m "init"` 生成初始迁移，最后 `alembic upgrade head` 应用。确认 `alembic/` 目录和 `alembic.ini` 已生成。
  - **Django ORM**：运行 `python manage.py makemigrations` 生成迁移文件，然后 `python manage.py migrate` 应用。确认 `*/migrations/` 目录已生成。
  - **GORM**：在应用启动代码中调用 `db.AutoMigrate(&Model1{}, &Model2{})` 自动同步 schema。无需额外迁移文件，但需确认 `models/` 目录下的 struct 定义与 `specs/数据库设计.md` 一致。
  - **JPA/Hibernate**：在 `application.yml` 中配置 `spring.jpa.hibernate.ddl-auto=update`（开发环境）或使用 Flyway/Liquibase 管理迁移。如使用 Flyway，运行 `mvn flyway:migrate` 或 `gradle flywayMigrate`。
  - **SeaORM**（仅 Rust 项目适用）：运行 `sea-orm-cli migrate init` 初始化迁移目录，然后 `sea-orm-cli generate entity` 从数据库生成 Entity 代码，最后 `sea-orm-cli migrate run` 应用迁移。确认 `migration/` 目录已生成。
  - **EF Core**（仅 C# 项目适用）：运行 `dotnet ef migrations add InitialCreate` 生成初始迁移，然后 `dotnet ef database update` 应用。确认 `Migrations/` 目录已生成。
  - **纯 SQL 脚本**：如项目不使用 ORM，将 `specs/数据库设计.md` 中的 DDL 语句保存为 `scripts/init.sql`，并执行对应数据库的导入命令（如 MySQL: mysql < scripts/init.sql；PostgreSQL: psql -f scripts/init.sql；SQLite: sqlite3 db.sqlite3 < scripts/init.sql）应用。
- **验证**：初始化完成后，连接数据库确认表已创建（如 `npx prisma studio`、`\dt`（psql）、`SHOW TABLES`（MySQL））。
- **跳过条件**：仅当项目不使用数据库（如纯计算服务、CLI 工具）时，才可跳过此步骤。跳过时必须在初始化记录中标注原因。

##### Step 4: 测试框架搭建

- 根据 `specs/后端开发规范.md` 中声明的测试框架，自动生成后端测试配置并安装依赖。
- 根据 `specs/前端开发规范.md` 中声明的测试框架，自动生成前端测试配置并安装依赖。
- **后端测试配置生成规则**：
  - **Jest**：生成 `jest.config.cjs`（配置 moduleNameMapper 映射 `@/` 路径别名、testMatch 匹配 `tests/**/*.spec.ts`、preset 使用 `ts-jest`）和 `tsconfig.jest.json`（扩展主 tsconfig，添加 `"jest": true` 到 types）。安装 `ts-jest`、`@types/jest`、`supertest`、`@types/supertest` 作为 devDependencies。
  - **Vitest**：生成 `vitest.config.ts`（配置 test.include、environment、setupFiles、resolve.alias）。安装 `vitest`、`@vitest/coverage-v8` 作为 devDependencies。
  - **pytest（Python 后端）**：生成 `pytest.ini` 或 `pyproject.toml` 中的 `[tool.pytest.ini_options]` 配置（配置 testpaths、python_files、python_classes、python_functions、addopts）。生成 `tests/conftest.py`（公共 fixtures，如数据库会话、测试客户端）。生成 `tests/__init__.py`（使 tests 目录成为 Python 包）。安装 `pytest`、`pytest-asyncio`、`pytest-cov`、`httpx`（用于 FastAPI TestClient）作为 devDependencies。如使用 Django，额外安装 `pytest-django`。
  - **go test（Go 后端）**：Go 使用内置测试框架，无需额外配置文件。生成 `*_test.go` 文件放在被测包同目录下。如需测试配置，生成 `tests/test_main_test.go`。安装 `github.com/stretchr/testify`（断言库）作为依赖。
  - **JUnit（Java/Spring Boot 后端）**：如使用 Maven，在 `pom.xml` 中添加 `spring-boot-starter-test` 依赖（包含 JUnit 5、Mockito、AssertJ）；如使用 Gradle，在 `build.gradle` 中添加相同依赖。生成 `src/test/java/` 目录结构，确保与 `src/main/java/` 包结构一致。
  - **cargo test（Rust 后端）**（仅 Rust 项目适用）：Rust 使用内置测试框架，无需额外配置文件。在 `src/` 下的每个模块中编写 `#[cfg(test)] mod tests { ... }` 测试模块。如需集成测试，生成 `tests/` 目录并编写独立的集成测试文件。运行 `cargo test` 验证。
  - **xUnit（C# 后端）**（仅 C# 项目适用）：运行 `dotnet add package xunit` 和 `dotnet add package xunit.runner.visualstudio` 安装测试框架。生成 `Tests/` 项目目录，在 `.csproj` 中添加 `<PackageReference Include="Microsoft.NET.Test.Sdk" />` 和 xUnit 依赖。运行 `dotnet test` 验证。
  - **配置文件模板必须与实际项目匹配**：路径别名必须与 `specs/项目结构.md` 和 tsconfig.json 中的配置一致；testMatch/include 必须与 `specs/项目结构.md` 中的测试目录结构一致。
- **前端测试配置生成规则（根据 `specs/技术栈.md` 中的前端框架选择对应方案）**：
  - **Vitest + React**：生成 `vitest.config.ts`（配置 plugins: [react()]、test.environment: 'jsdom'、test.setupFiles、test.globals: true、resolve.alias）。生成 `tests/setup.ts`（导入 `@testing-library/jest-dom` 并将 `vi` 别名为 `jest` 以兼容 Jest 风格测试）。安装 `vitest`、`@testing-library/react`、`@testing-library/jest-dom`、`@testing-library/user-event`、`jsdom`、`@vitejs/plugin-react` 作为 devDependencies。**注意**：`@vitejs/plugin-react` 版本必须与项目 Vite 版本兼容（Vite 5 → `@vitejs/plugin-react@^4.0.0`，Vite 6 → `@vitejs/plugin-react@^4.3.0`）。
  - **Vitest + Vue 3**：生成 `vitest.config.ts`（配置 plugins: [vue()]、test.environment: 'jsdom'、test.setupFiles、test.globals: true、resolve.alias）。生成 `tests/setup.ts`（导入 `@vue/test-utils` 的全局配置）。安装 `vitest`、`@vue/test-utils`、`jsdom`、`@vitejs/plugin-vue`、`happy-dom` 作为 devDependencies。
  - **Vitest + Svelte**：生成 `vitest.config.ts`（配置 plugins: [svelte()]、test.environment: 'jsdom'、test.setupFiles、resolve.alias）。安装 `vitest`、`@testing-library/svelte`、`jsdom`、`@sveltejs/vite-plugin-svelte` 作为 devDependencies。
  - **Jest + Angular**：Angular 项目通常使用 `@angular/cli` 内置的测试配置，需确认 `karma.conf.js` 或 `jest.config.js` 存在。安装 `@testing-library/angular`、`jest-preset-angular` 作为 devDependencies。
  - **Monorepo 下的前端测试**：如果前端框架安装在子包（如 `apps/web/node_modules`）而非根目录，`vitest.config.ts` 必须在 `resolve.alias` 中显式映射框架包到子包的 node_modules 路径，并在 `test` 配置中启用 `dedupe`。不配置会导致运行时模块解析错误（仅 Vitest 项目适用）。
  - **通用规则**：无论使用哪种前端框架，`tests/setup.ts` 必须存在（即使为空），Vitest 配置的 `test.exclude` 必须包含 E2E 测试目录（规则 20）（仅 Vitest 项目适用）。
- **tsconfig 排除测试目录**：前后端的 `tsconfig.json` 必须在 `exclude` 中添加 `"tests"` 目录，避免测试文件中的类型错误（如缺少 vitest/jest 全局类型）影响主项目编译（仅 TypeScript 项目适用）。
- **依赖版本锁定**：所有测试相关 devDependencies 必须使用精确版本号（规则 15）。
- **验证**：配置生成后，运行一次 `npx jest --passWithNoTests`（Jest）或 `npx vitest run`（Vitest）、`pytest --collect-only`（Python）、`go test ./...`（Go）、`mvn test -DskipTests=false`（Java/Maven）或 `gradle test`（Java/Gradle）确认配置文件本身无语法错误。如果验证失败，必须修复配置后才能继续。
- **跳过条件**：仅当 `specs/后端开发规范.md` 或 `specs/前端开发规范.md` 中未声明任何测试框架时，才可跳过对应端的测试框架搭建。跳过时必须在初始化记录中标注原因。

#### 3. 生成报告

- 将初始化过程记录到 `docs/开发记录/初始化记录.md`。

### 输出模板

检查 `docs/开发记录/` 目录是否存在，若不存在请自动创建。初始化/检查完成后，请在 `docs/开发记录/初始化记录.md` 中输出以下内容（使用 assets 中的模板）：

1. 读取 `templates/initialization-record-template.md`。
2. 填入执行结果。
3. 保存文件。

### 交互准则

- **动作优先**：这是一个偏向"执行"的 Skill。多用 Shell 命令，少说废话。
- **最终交付**：项目骨架代码 + `docs/开发记录/初始化记录.md`。
- **初始化失败**：如果命令执行失败（如 npm init 报错、磁盘空间不足），记录失败原因和错误信息，尝试清理已创建的文件，向用户报告具体错误并建议解决方案。

### 文档质量保证

> 初始化记录属于操作日志类文档，仅需执行阶段 B（Bug 检查循环）。

在生成文档后、保存前，**必须**按照 [../../../specs/GUARDRAILS.md](../../../specs/GUARDRAILS.md) 第 4 节「文档质量保证协议」执行以下阶段：

**阶段 B：Bug 检查循环** — 检查内部一致性、跨文档一致性、占位符残留、格式、逻辑、技术可行性，修复直到零 Bug。

**不执行阶段 A（深度完善循环）**：初始化记录是操作日志类文档，不需要逐章审视内容深度、完整性等深度完善操作。

> 这是进入下一阶段的硬性前提。未经阶段 B 检查的文档不得保存。

### 底线规则

> 以下规则补充全局底线规则（见 GUARDRAILS.md），仅定义本 Skill 特有的约束。任何一条不满足则初始化不合格。

1. **严格按 specs 执行**：目录结构、文件命名、配置内容必须与 specs 文档一致，不得自行创造 specs 中未定义的目录或文件。
2. **工具链与 specs 一致**：初始化命令（npm/cargo/pip 等）必须与 `specs/技术栈.md` 一致，不得自行替换技术栈。
3. **Git 必须初始化**：每个项目必须执行 `git init`，不得跳过。
4. **空目录必须有 .gitkeep**：每个空文件夹必须创建 `.gitkeep`，确保 Git 能追踪。
5. **失败必须报告**：任何命令执行失败都必须记录错误信息，不得静默跳过。
6. **安全授权**：执行删除或覆盖操作前，必须获得用户明确授权。
7. **记录与实际产出必须一致**：初始化记录中的文件清单必须与实际创建的文件一一对应，不得记录未创建的文件。如果某个文件计划创建但因故未创建，必须在记录中明确标注"未创建"及原因。初始化阶段只创建目录骨架和配置文件，页面文件和 API 路由骨架在功能开发阶段创建。
8. **Prisma schema 只允许单行注释**（仅 Prisma 项目适用）：Prisma schema 文件中只允许使用 `//` 单行注释，禁止使用 `/** */` 多行注释。Prisma 不支持多行注释语法，使用会导致解析错误。
9. **Prisma 枚举值不允许连字符**（仅 Prisma 项目适用）：Prisma 枚举值不允许包含连字符（如 `zh-CN`），应使用下划线（如 `zh_CN`）。枚举值不加引号，直接使用标识符形式。
10. **ORM 关系必须双向声明**（Prisma 项目使用 `@relation`，SQLAlchemy 使用 `relationship()`，Django ORM 使用 `ForeignKey` + `related_name`，GORM 使用 `gorm:"foreignKey"`，JPA 使用 `@OneToMany` + `@ManyToOne`）：所有 ORM 关系字段必须在双方模型中都声明。单向声明会导致数据库迁移失败或数据不一致。
    - **生成后自检步骤（必须执行）**：生成 schema/model 后，必须遍历所有关系声明，逐一确认对方模型存在对应的反向字段。具体方法：对每个关系声明，搜索整个 schema 文件中是否存在另一个模型包含对应的反向关系。如果找不到，必须立即补全缺失的反向字段，不得跳过。
    - **常见遗漏场景**：`Project.owner`（与 `User` 的关系）、`Notification.project`（与 `Project` 的关系）等"看似单向"的关联最容易遗漏，必须重点检查。
    > 此规则适用于所有 ORM。不同 ORM 的关系声明语法不同，但核心原则相同：关系两端必须都有声明。
11. **源码文件必须放在 src/ 下**：所有源码文件必须放在 `src/` 目录下（如 `src/lib/`、`src/app/`、`src/components/`），禁止在项目根目录创建 `lib/` 目录存放源码。只有 `prisma/`、`public/`、`tests/` 等配置/资源目录可以放在根目录。
12. **Prisma 列表字段默认值必须使用合法格式**（仅 Prisma 项目适用）：Prisma 的 `@default()` 不支持数组字面量语法（如 `@default([])` 会导致解析错误）。如果 `String` 类型字段需要存储 JSON 数组作为默认值，必须使用 `@default("[]")` 形式（JSON 字符串）。
13. **tsconfig 必须配置路径别名**（仅 TypeScript 项目适用）：前后端 tsconfig.json 必须配置 `@/` 路径别名，指向 `src/` 目录。同时 vite.config.ts（前端）和 tsconfig-paths/register（后端）必须同步配置相同的别名映射，确保 TypeScript 编译和运行时解析一致。
14. **shared 包禁止重复导出**：packages/shared 中的每个类型、常量、工具函数只能在一个文件中导出，通过 `index.ts` 统一 re-export。禁止在不同子文件中重复导出同名类型（如两个文件都 `export interface ApiResponse`），否则会导致 monorepo 构建时类型冲突（仅 TypeScript monorepo 项目适用）。
15. **依赖版本必须锁定**：package.json 中的核心开发依赖（vitest、@testing-library/react、@testing-library/jest-dom 等）必须使用精确版本号（如 `"vitest": "1.6.0"` 而非 `"vitest": "^1.6.0"`），避免主版本范围内的 breaking change 导致测试环境不兼容（仅 Node.js 项目适用）。
16. **Prisma 一对一关系必须标注 @unique（仅 Prisma 项目适用）**：Prisma 中所有一对一关系（即关系两端都不是列表类型的关系）必须在被引用方标注 `@unique`。例如 `Lesson` 模型有 `video Video @relation(fields: [videoId], references: [id])`，则 `Video` 模型对应的反向字段必须标注 `@unique`（如 `lesson Lesson? @relation` 不够，需要确保 `Lesson.videoId` 是唯一的）。未标注 `@unique` 的一对一关系会导致 `prisma migrate dev` 和 `prisma generate` 报错。
    - **自检方法**：生成 schema 后，检查所有非列表类型的关系字段（即字段类型不是 `Model[]` 的 `@relation`），确认被引用方模型中该关系字段已标注 `@unique`。如果关系两端都是可选的（`Model?`），则两端都需要 `@unique`。
17. **测试框架必须随项目初始化搭建**：项目初始化时必须根据开发规范中声明的测试框架自动生成配置文件、安装依赖并验证配置可用。不允许将测试框架搭建推迟到 Skill 22-26（测试阶段）。未搭建测试框架的项目不得标记为"初始化完成"。
    - **后端**：必须根据后端技术栈生成对应的测试配置。Node.js 项目生成 `jest.config.cjs` 或 `vitest.config.ts`；Python 项目生成 `pytest.ini` 或 `pyproject.toml` 配置；Go 项目确认 `*_test.go` 文件结构；Java 项目确认 `src/test/` 目录和 `pom.xml`/`build.gradle` 测试依赖。运行对应的空测试命令验证配置。
    - **前端**：必须生成 `vitest.config.ts` 或 `jest.config.cjs`，根据前端框架安装对应的测试库（React: `@testing-library/react` + `@testing-library/jest-dom`；Vue 3: `@vue/test-utils`；Svelte: `@testing-library/svelte`；Angular: `@testing-library/angular`），安装 `jsdom` 等环境依赖，生成 `tests/setup.ts`，运行空测试验证配置。
    - **tsconfig 排除**：前后端 `tsconfig.json` 必须在 `exclude` 中添加 `"tests"` 目录（仅 TypeScript 项目适用）。
    - **验证标准**：初始化完成后，TypeScript 项目 `npx tsc --noEmit`（前后端）不得报错；所有项目的测试框架空运行均不得报错（Node.js: `npx jest --passWithNoTests` / `npx vitest run`；Python: `pytest --collect-only`；Go: `go test ./...`；Java: `mvn test -DskipTests=false`）。
18. **框架必要 tsconfig 选项必须启用**（仅 TypeScript 项目适用）：根据项目技术栈，tsconfig.json 必须包含框架运行的必要编译选项，不得遗漏。
    - **NestJS 项目**：`apps/server/tsconfig.json` 必须包含 `"emitDecoratorMetadata": true` 和 `"experimentalDecorators": true`。缺少这两个选项会导致所有使用装饰器的文件（Controller、Service、Guard、Filter、DTO）编译失败（TS1238/TS1240/TS1241 错误）。
    - **Next.js 项目**：`apps/web/tsconfig.json` 必须包含 `"jsx": "preserve"`（通常由 `create-next-app` 自动配置）。如手动创建，不得遗漏。
    - **Vue 3 项目**：如使用 `<script setup>` 语法，需确保 `@vue/language-tools` 已配置。
    - **Angular 项目**：通常由 `@angular/cli` 自动生成 tsconfig，包含 `"experimentalDecorators": true`、`"emitDecoratorMetadata": true`、`"module": "es2022"` 等必要选项。
    - **SvelteKit 项目**：需在 `svelte.config.js` 中配置 Kit 相关选项，tsconfig 需包含 Svelte 特定的 `compilerOptions`。
    - **Python 后端（FastAPI/Django）**：如使用 TypeScript（如 FastAPI + pydantic），需配置 `tsconfig.json` 适配 Python TS 工具链。
    - **Go 后端**：不使用 tsconfig，跳过此规则。
    - **自检方法**：生成 tsconfig.json 后，检查 compilerOptions 中是否包含框架所需的必要选项。可通过 `npx tsc --noEmit` 验证。
19. **Next.js 配置文件格式必须与版本匹配**（仅 Next.js 项目适用）：Next.js 14.x 及更早版本不支持 `next.config.ts`，必须使用 `next.config.js`（CommonJS 格式 `module.exports = {...}`）。`postcss.config.js` 也必须使用 CommonJS 格式（`module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } }`），不得使用 ESM 的 `export default`。Next.js 15+ 才支持 `.ts` 配置文件。初始化时必须根据 `specs/技术栈.md` 中声明的 Next.js 版本选择正确的配置文件格式。
    - **自检方法**：生成配置文件后，检查文件扩展名和模块格式是否与 Next.js 版本匹配。可通过 `npx next build --dry-run` 或启动开发服务器验证。
20. **Vitest 配置必须排除 E2E 测试目录**（仅使用 Vitest 的项目适用）：`vitest.config.ts` 的 `test.exclude` 必须包含 `['**/node_modules/**', '**/dist/**', '**/.next/**', '**/e2e/**', '**/__tests__/e2e/**']`，防止 Vitest 加载 Playwright 测试文件。Playwright 测试依赖浏览器环境，Vitest 默认使用 jsdom/node 环境，加载 Playwright 测试会导致环境不兼容错误。
    - **自检方法**：生成 vitest.config.ts 后，检查 `test.exclude` 是否包含 E2E 测试目录。可通过 `npx vitest run` 验证不会加载 E2E 测试文件。
21. **数据库初始化必须随项目初始化执行**：使用数据库的项目必须在项目初始化阶段完成数据库 schema 的初始迁移，不允许将数据库初始化推迟到功能开发阶段。未完成数据库初始化的项目不得标记为"初始化完成"。
    - **自检方法**：初始化完成后，连接数据库执行 `\dt`（PostgreSQL）或 `SHOW TABLES`（MySQL）确认所有设计文档中定义的表已创建。

### 失败处理

> 遵循 GUARDRAILS.md 中的全局失败处理规则。
