# 环境与配置文档

> 本文档由 `16-project-environment-config` Skill 自动生成。
> **文档版本**：1.0
> **创建日期**：{{YYYY-MM-DD}}
> **最后更新**：{{YYYY-MM-DD}}
> **基于技术栈**：{{技术栈概要}}

---

## 1. 环境列表

<!-- 填写指引：定义项目的所有环境，包括用途、访问方式和负责人 -->

### 1.1 环境概览

<!-- 填写指引：根据项目规模定义环境数量，MVP 阶段通常只需要 dev + prod -->

| 环境 | 用途 | 部署方式 | 数据来源 | 负责人 |
|------|------|---------|---------|--------|
| {{例如：开发环境 (dev)}} | {{例如：开发者日常开发和自测}} | {{例如：本地 Docker Compose}} | {{例如：独立数据库，可随意修改}} | {{例如：各开发者}} |
| {{例如：测试环境 (test)}} | {{例如：QA 功能测试和回归测试}} | {{例如：云服务器 / 容器服务}} | {{例如：测试数据，定期重置}} | {{例如：QA 团队}} |
| {{例如：预发环境 (staging)}} | {{例如：上线前验证，数据与生产一致}} | {{例如：与生产相同配置}} | {{例如：生产数据脱敏副本}} | {{例如：Tech Lead}} |
| {{例如：生产环境 (prod)}} | {{例如：正式对外服务}} | {{例如：云服务器 / 容器服务 / K8s}} | {{例如：真实用户数据}} | {{例如：运维团队}} |

### 1.2 环境差异说明

<!-- 填写指引：明确各环境之间的关键差异 -->

| 配置项 | 开发环境 | 测试环境 | 预发环境 | 生产环境 |
|--------|---------|---------|---------|---------|
| {{例如：日志级别}} | {{例如：DEBUG}} | {{例如：INFO}} | {{例如：INFO}} | {{例如：WARN}} |
| {{例如：热重载}} | {{例如：开启}} | {{例如：关闭}} | {{例如：关闭}} | {{例如：关闭}} |
| {{例如：数据量}} | {{例如：少量种子数据}} | {{例如：模拟数据}} | {{例如：生产脱敏}} | {{例如：真实数据}} |
| {{例如：缓存}} | {{例如：可选}} | {{例如：开启}} | {{例如：开启}} | {{例如：开启}} |
| {{例如：CDN}} | {{例如：不使用}} | {{例如：不使用}} | {{例如：使用}} | {{例如：使用}} |
| {{例如：限流}} | {{例如：不限制}} | {{例如：不限制}} | {{例如：与生产一致}} | {{例如：开启}} |

---

## 2. 环境变量清单

<!-- 填写指引：列出所有环境变量，按分类组织，标注每个环境的具体值或获取方式 -->

### 2.1 应用配置

<!-- 填写指引：应用自身运行所需的配置变量 -->

| 变量名 | 说明 | 开发环境 | 测试环境 | 预发环境 | 生产环境 |
|--------|------|---------|---------|---------|---------|
| {{例如：NODE_ENV}} | {{例如：运行环境标识}} | {{例如：development}} | {{例如：test}} | {{例如：staging}} | {{例如：production}} |
| {{例如：APP_PORT}} | {{例如：应用监听端口}} | {{例如：3000}} | {{例如：3000}} | {{例如：3000}} | {{例如：3000}} |
| {{例如：APP_SECRET}} | {{例如：应用密钥（JWT 签名等）}} | {{例如：dev-secret}} | {{例如：test-secret}} | {{例如：从密钥管理获取}} | {{例如：从密钥管理获取}} |
| {{例如：LOG_LEVEL}} | {{例如：日志级别}} | {{例如：debug}} | {{例如：info}} | {{例如：info}} | {{例如：warn}} |

#### Next.js 特有变量（如使用 Next.js 框架）

<!-- 填写指引：Next.js 中只有 NEXT_PUBLIC_ 前缀的环境变量会暴露给浏览器端，其余仅在服务端可用 -->

| 变量名 | 说明 | 开发环境 | 测试环境 | 预发环境 | 生产环境 |
|--------|------|---------|---------|---------|---------|
| {{例如：NEXT_PUBLIC_API_URL}} | {{例如：浏览器端可访问的 API 地址}} | {{例如：http://localhost:8080}} | {{例如：https://api-test.example.com}} | {{例如：https://api-staging.example.com}} | {{例如：https://api.example.com}} |
| {{例如：NEXT_PUBLIC_APP_NAME}} | {{例如：应用名称（浏览器端可见）}} | {{例如：MyApp (Dev)}} | {{例如：MyApp (Test)}} | {{例如：MyApp (Staging)}} | {{例如：MyApp}} |

```bash
# .env.example 中 Next.js 特有变量示例
# 注意：只有 NEXT_PUBLIC_ 前缀的变量会暴露给浏览器端
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_APP_NAME=MyApp
```

#### Python 特有变量（如使用 Python 框架）

<!-- 填写指引：Python 项目中常用环境变量，容器环境下必须设置 PYTHONUNBUFFERED -->

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `PYTHONPATH` | Python 模块搜索路径 | `/app/src` |
| `PYTHONUNBUFFERED` | 禁用输出缓冲（容器环境必须） | `1` |
| `FLASK_ENV` | Flask 运行环境 | `development` |
| `DJANGO_SETTINGS_MODULE` | Django 配置模块 | `myproject.settings.dev` |
| `PYTHONDONTWRITEBYTECODE` | 禁止生成 .pyc 文件 | `1` |

#### Java/Spring Boot 特有变量（如使用 Java/Spring Boot 框架）

<!-- 填写指引：Spring Boot 使用 SPRING_PROFILES_ACTIVE 区分环境，JVM 参数通过 JAVA_OPTS 传入 -->

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `JAVA_OPTS` | JVM 启动参数 | `-Xmx512m -Xms256m` |
| `SPRING_PROFILES_ACTIVE` | Spring 活跃配置 | `dev` |
| `SPRING_DATASOURCE_URL` | 数据库连接 URL | `jdbc:postgresql://localhost:5432/mydb` |

#### Go 特有变量（如使用 Go 框架）

<!-- 填写指引：Go 项目通过环境变量控制运行时行为，GOGC 和 GOMAXPROCS 影响性能 -->

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `GOGC` | GC 触发百分比 | `100` |
| `GOMAXPROCS` | 最大 CPU 核数 | `4` |
| `GO_ENV` | 应用运行环境 | `development` |

### 2.2 数据库配置

<!-- 填写指引：数据库连接相关变量 -->

| 变量名 | 说明 | 开发环境 | 测试环境 | 预发环境 | 生产环境 |
|--------|------|---------|---------|---------|---------|
| {{例如：DB_HOST}} | {{例如：数据库主机地址}} | {{例如：localhost}} | {{例如：test-db.internal}} | {{例如：staging-db.internal}} | {{例如：prod-db.internal}} |
| {{例如：DB_PORT}} | {{例如：数据库端口}} | {{例如：5432}} | {{例如：5432}} | {{例如：5432}} | {{例如：5432}} |
| {{例如：DB_NAME}} | {{例如：数据库名称}} | {{例如：app_dev}} | {{例如：app_test}} | {{例如：app_staging}} | {{例如：app_prod}} |
| {{例如：DB_USER}} | {{例如：数据库用户名}} | {{例如：postgres}} | {{例如：app_test}} | {{例如：app_staging}} | {{例如：app_prod}} |
| {{例如：DB_PASSWORD}} | {{例如：数据库密码}} | {{例如：postgres}} | {{例如：从密钥管理获取}} | {{例如：从密钥管理获取}} | {{例如：从密钥管理获取}} |
| {{例如：DB_POOL_SIZE}} | {{例如：连接池大小}} | {{例如：5}} | {{例如：10}} | {{例如：20}} | {{例如：50}} |

#### Prisma 连接字符串格式（如使用 Prisma ORM）

<!-- 填写指引：Prisma 使用 DATABASE_URL 连接字符串，格式为 postgresql://用户名:密码@主机:端口/数据库名 -->

| 变量名 | 说明 | 格式示例 |
|--------|------|---------|
| DATABASE_URL | Prisma 数据库连接字符串 | `postgresql://postgres:password@localhost:5432/app_dev` |

```bash
# .env.example 中 Prisma 连接字符串示例
DATABASE_URL="postgresql://postgres:your-password@localhost:5432/app_dev?schema=public"
```

#### SQLAlchemy 连接字符串格式（如使用 Python SQLAlchemy）

<!-- 填写指引：SQLAlchemy 使用标准连接字符串格式，不同数据库使用不同的驱动前缀 -->

| 数据库 | 格式 | 示例 |
|--------|------|------|
| PostgreSQL | `postgresql+psycopg2://` | `postgresql+psycopg2://user:pass@localhost:5432/mydb` |
| MySQL | `mysql+pymysql://` | `mysql+pymysql://user:pass@localhost:3306/mydb` |
| SQLite | `sqlite:///` | `sqlite:///./dev.db` |

#### Django DATABASES 配置格式（如使用 Django）

<!-- 填写指引：Django 使用 settings.py 中的 DATABASES 字典配置，而非连接字符串 -->

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### GORM 连接字符串格式（如使用 Go GORM）

<!-- 填写指引：GORM 使用 DSN（Data Source Name）格式连接数据库 -->

| 数据库 | 格式 | 示例 |
|--------|------|------|
| PostgreSQL | `host=%s port=%s user=%s password=%s dbname=%s sslmode=disable` | `host=localhost port=5432 user=user password=pass dbname=mydb sslmode=disable` |
| MySQL | `%s:%s@tcp(%s:%s)/%s?charset=utf8mb4&parseTime=True` | `user:pass@tcp(localhost:3306)/mydb?charset=utf8mb4&parseTime=True` |

#### JPA/Hibernate 连接字符串格式（如使用 Java/Spring Boot）

<!-- 填写指引：JPA 使用 JDBC 连接字符串，通过 spring.datasource.url 配置 -->

| 数据库 | 格式 | 示例 |
|--------|------|------|
| PostgreSQL | `jdbc:postgresql://` | `jdbc:postgresql://localhost:5432/mydb` |
| MySQL | `jdbc:mysql://` | `jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=UTC` |
| H2 (测试) | `jdbc:h2:mem:` | `jdbc:h2:mem:testdb` |

### 2.3 缓存配置（如适用）

<!-- 填写指引：Redis 或其他缓存服务的连接配置 -->

| 变量名 | 说明 | 开发环境 | 测试环境 | 预发环境 | 生产环境 |
|--------|------|---------|---------|---------|---------|
| {{例如：REDIS_HOST}} | {{例如：Redis 主机地址}} | {{例如：localhost}} | {{例如：test-redis.internal}} | {{例如：staging-redis.internal}} | {{例如：prod-redis.internal}} |
| {{例如：REDIS_PORT}} | {{例如：Redis 端口}} | {{例如：6379}} | {{例如：6379}} | {{例如：6379}} | {{例如：6379}} |
| {{例如：REDIS_PASSWORD}} | {{例如：Redis 密码}} | {{例如：（空）}} | {{例如：从密钥管理获取}} | {{例如：从密钥管理获取}} | {{例如：从密钥管理获取}} |
| {{例如：REDIS_DB}} | {{例如：Redis 数据库编号}} | {{例如：0}} | {{例如：1}} | {{例如：2}} | {{例如：3}} |

### 2.4 外部服务配置（如适用）

<!-- 填写指引：第三方服务的 API Key 和配置 -->

| 变量名 | 说明 | 开发环境 | 测试环境 | 预发环境 | 生产环境 |
|--------|------|---------|---------|---------|---------|
| {{例如：SMTP_HOST}} | {{例如：邮件服务地址}} | {{例如：smtp.example.com}} | {{例如：smtp.example.com}} | {{例如：smtp.example.com}} | {{例如：smtp.example.com}} |
| {{例如：SMTP_USER}} | {{例如：邮件服务用户名}} | {{例如：noreply@example.com}} | {{例如：noreply@example.com}} | {{例如：从密钥管理获取}} | {{例如：从密钥管理获取}} |
| {{例如：OSS_ACCESS_KEY}} | {{例如：对象存储 AccessKey}} | {{例如：测试 Key}} | {{例如：测试 Key}} | {{例如：从密钥管理获取}} | {{例如：从密钥管理获取}} |
| {{例如：OSS_BUCKET}} | {{例如：对象存储桶名称}} | {{例如：dev-assets}} | {{例如：test-assets}} | {{例如：staging-assets}} | {{例如：prod-assets}} |

### 2.5 安全相关配置

<!-- 填写指引：与安全相关的配置变量，生产环境必须从密钥管理服务获取 -->

| 变量名 | 说明 | 开发环境 | 测试环境 | 预发环境 | 生产环境 |
|--------|------|---------|---------|---------|---------|
| {{例如：JWT_SECRET}} | {{例如：JWT 签名密钥}} | {{例如：dev-jwt-secret}} | {{例如：test-jwt-secret}} | {{例如：从密钥管理获取}} | {{例如：从密钥管理获取}} |
| {{例如：JWT_EXPIRES_IN}} | {{例如：JWT 过期时间}} | {{例如：7d}} | {{例如：1h}} | {{例如：2h}} | {{例如：2h}} |
| {{例如：CORS_ORIGINS}} | {{例如：允许的跨域来源}} | {{例如：*}} | {{例如：https://test.example.com}} | {{例如：https://staging.example.com}} | {{例如：https://example.com}} |

---

## 3. .env.example 模板

<!-- 填写指引：生成标准的 .env.example 文件，供新开发者参考。所有敏感值使用占位符 -->

```bash
# ============================================
# 应用配置
# ============================================
NODE_ENV=development
APP_PORT=3000
APP_SECRET=your-app-secret-here
LOG_LEVEL=debug

# ============================================
# 数据库配置
# ============================================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=app_dev
DB_USER=postgres
DB_PASSWORD=your-db-password-here
DB_POOL_SIZE=5

# ============================================
# 缓存配置（如适用）
# ============================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# ============================================
# 外部服务配置（如适用）
# ============================================
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=your-smtp-password-here

# OSS 配置（如适用）
OSS_ACCESS_KEY=your-oss-access-key-here
OSS_SECRET_KEY=your-oss-secret-key-here
OSS_BUCKET=dev-assets
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com

# ============================================
# 安全配置
# ============================================
JWT_SECRET=your-jwt-secret-here
JWT_EXPIRES_IN=2h
JWT_REFRESH_EXPIRES_IN=7d
CORS_ORIGINS=http://localhost:3000
```

> **非 Node.js 项目的 .env.example 参考**：
> - **Python (FastAPI)**：使用 `python-dotenv` 加载 `.env`，变量命名使用 `PROJECT_` 前缀（如 `PROJECT_DATABASE_URL`）
> - **Java (Spring Boot)**：使用 `application-{profile}.yml` 或 `.env` + `spring-dotenv`，变量命名遵循 `SPRING_` 前缀
> - **Go**：使用 `os.Getenv()` 读取环境变量，或使用 `godotenv` 加载 `.env` 文件

### .env 文件管理规则

<!-- 填写指引：定义 .env 文件的管理规范 -->

1. **版本控制**：{{例如：.env.example 提交到 Git，.env 加入 .gitignore}}
2. **密钥管理**：{{例如：生产环境密钥使用云密钥管理服务（如 AWS Secrets Manager / 阿里云 KMS）}}
3. **密钥轮换**：{{例如：每 90 天轮换一次 JWT_SECRET}}
4. **新成员接入**：{{例如：新开发者复制 .env.example 为 .env，填写本地开发值}}

---

## 4. 域名规划

<!-- 填写指引：定义各环境的域名分配和 SSL 证书管理策略 -->

### 4.1 域名分配

<!-- 填写指引：根据环境规划域名，使用子域名区分环境 -->

| 环境 | 前端域名 | 后端 API 域名 | 管理后台域名 |
|------|---------|-------------|------------|
| {{例如：开发环境}} | {{例如：localhost:3000}} | {{例如：localhost:8080}} | {{例如：localhost:3001}} |
| {{例如：测试环境}} | {{例如：test.example.com}} | {{例如：api-test.example.com}} | {{例如：admin-test.example.com}} |
| {{例如：预发环境}} | {{例如：staging.example.com}} | {{例如：api-staging.example.com}} | {{例如：admin-staging.example.com}} |
| {{例如：生产环境}} | {{例如：www.example.com}} | {{例如：api.example.com}} | {{例如：admin.example.com}} |

### 4.2 DNS 配置

<!-- 填写指引：定义 DNS 解析记录 -->

| 记录类型 | 主机记录 | 记录值 | 说明 |
|---------|---------|--------|------|
| {{例如：A}} | {{例如：@}} | {{例如：1.2.3.4}} | {{例如：主域名指向生产服务器}} |
| {{例如：A}} | {{例如：api}} | {{例如：1.2.3.4}} | {{例如：API 子域名}} |
| {{例如：CNAME}} | {{例如：www}} | {{例如：example.com}} | {{例如：www 子域名}} |

### 4.3 SSL 证书管理

<!-- 填写指引：定义 SSL 证书的申请、续期和管理方式 -->

- **证书类型**：{{例如：Let's Encrypt 免费证书 / 商业证书}}
- **申请方式**：{{例如：Certbot 自动申请 / 云服务商免费证书}}
- **自动续期**：{{例如：Certbot 自动续期 / 云服务商自动续期}}
- **证书覆盖范围**：{{例如：泛域名证书 *.example.com 或单域名证书}}

```bash
# Certbot 申请证书示例（如使用 Let's Encrypt）
certbot certonly --nginx -d example.com -d www.example.com -d api.example.com
```

---

## 5. 构建命令与 CI/CD

<!-- 填写指引：定义项目的构建、测试和部署命令，以及 CI/CD 自动化流程 -->

### 5.1 本地开发命令

<!-- 填写指引：定义开发者日常使用的命令 -->

```bash
# 安装依赖
{{例如：pnpm install}}

# 启动开发环境（前端 + 后端 + 数据库）
{{例如：docker compose up -d && pnpm dev}}

# 运行数据库迁移
{{例如：pnpm db:migrate}}

# 填充种子数据
{{例如：pnpm db:seed}}

# 代码检查
{{例如：pnpm lint}}

# 运行测试
{{例如：pnpm test}}

# 运行测试（带覆盖率）
{{例如：pnpm test:coverage}}
```

### 5.2 构建命令

<!-- 填写指引：定义各环境的构建命令 -->

```bash
# 前端构建
{{例如：pnpm --filter frontend build}}

# 后端构建
{{例如：pnpm --filter backend build}}

# 生产构建（带优化）
{{例如：NODE_ENV=production pnpm build}}

# Docker 镜像构建
{{例如：docker build -t example-app:latest .}}
```

### 5.3 CI/CD 流程

<!-- 填写指引：定义 CI/CD 流水线的各个阶段和触发条件 -->

#### 流水线概览

```text
{{例如：
代码提交 → 代码检查 → 单元测试 → 构建 → 部署到测试环境 → 人工验证 → 部署到生产环境
}}
```

#### 触发条件

| 环境 | 触发条件 | 部署方式 |
|------|---------|---------|
| {{例如：测试环境}} | {{例如：推送到 develop 分支自动触发}} | {{例如：自动部署}} |
| {{例如：预发环境}} | {{例如：创建 Release PR 或手动触发}} | {{例如：手动确认后自动部署}} |
| {{例如：生产环境}} | {{例如：合并到 main 分支 + 手动确认}} | {{例如：手动确认后自动部署}} |

#### CI 配置示例

<!-- 填写指引：根据 CI/CD 工具提供配置示例 -->

```yaml
# .github/workflows/ci.yml 示例
name: CI/CD Pipeline

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  # 代码检查
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm type-check

  # 单元测试
  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - run: pnpm install --frozen-lockfile
      - run: pnpm test:coverage

  # 构建并部署到测试环境
  deploy-test:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4
      - name: Build and Deploy
        run: |
          {{构建和部署到测试环境的命令}}

  # 部署到生产环境
  deploy-prod:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    environment: production  # 需要手动确认
    steps:
      - uses: actions/checkout@v4
      - name: Build and Deploy
        run: |
          {{构建和部署到生产环境的命令}}
```

#### 其他技术栈的构建命令参考

<!-- 填写指引：不同技术栈的 CI/CD 构建命令对照表，替换上方 YAML 中的对应命令即可 -->

| 技术栈 | 安装依赖 | 代码检查 | 测试 | 构建 |
|--------|---------|---------|------|------|
| Python (FastAPI) | `pip install -r requirements.txt` | `ruff check .` 或 `flake8` | `pytest` | `pip install .` |
| Python (Django) | `pip install -r requirements.txt` | `ruff check .` | `pytest` | `python manage.py collectstatic` |
| Go | `go mod download` | `go vet ./...` | `go test ./...` | `go build -o bin/app ./cmd/app` |
| Java (Maven) | `mvn dependency:resolve` | `mvn checkstyle:check` | `mvn test` | `mvn package -DskipTests` |
| Java (Gradle) | `gradle dependencies` | `gradle checkstyleMain` | `gradle test` | `gradle build -x test` |

### 5.4 部署检查清单

<!-- 填写指引：部署前必须确认的检查项 -->

- [ ] {{例如：所有测试通过}}
- [ ] {{例如：代码已合并到目标分支}}
- [ ] {{例如：环境变量已配置（与第 2 节清单一致）}}
- [ ] {{例如：数据库迁移已执行}}
- [ ] {{例如：SSL 证书有效}}
- [ ] {{例如：健康检查接口正常}}
- [ ] {{例如：日志收集正常}}
- [ ] {{例如：告警规则已配置}}

### 5.5 回滚方案

<!-- 填写指引：定义部署失败时的回滚策略 -->

- **回滚触发条件**：{{例如：健康检查失败 / 错误率超过阈值 / 人工判断}}
- **回滚方式**：{{例如：回退到上一个 Docker 镜像版本 / 回退代码分支}}
- **回滚命令**：

```bash
# 回滚到上一个版本示例
{{例如：docker pull example-app:previous && docker compose up -d}}
```

---

> 本文档基于项目技术栈定制生成，所有配置均针对本项目优化。
> 如有疑问或需要调整，请在团队内部讨论后更新本文档。

---

## 6. 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| {{YYYY-MM-DD}} | 1.0 | 初始版本 | {{作者}} |
