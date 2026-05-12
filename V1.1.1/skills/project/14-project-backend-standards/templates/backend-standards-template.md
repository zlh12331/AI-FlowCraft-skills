# 后端开发规范

> 本文档由 `14-project-backend-standards` Skill 自动生成。
> **文档版本**：1.0
> **创建日期**：{{YYYY-MM-DD}}
> **最后更新**：{{YYYY-MM-DD}}
> **基于技术栈**：{{技术栈概要}}

---

<!-- 填写指引：以下代码示例默认使用 Java 语法，并在每个关键章节的 Java 代码块后提供了 Node.js/TypeScript（Next.js App Router + Prisma Client）、Python (FastAPI/Django)、Go (Gin) 的等效写法注释。Rust (Axum) 和 C# (ASP.NET) 的等效写法待后续补充。如项目使用其他语言，请替换为对应语言的等效写法。分层架构概念（Controller/Service/Repository）在不同语言中可能有不同命名习惯。 -->

## 1. 语言与运行时要求

<!-- 填写指引：明确后端开发所需的运行时版本和编译目标，确保团队环境一致 -->

### 1.1 语言版本

<!-- 填写指引：指定后端语言的版本要求，建议使用版本管理工具 -->

- **语言**：{{例如：Java 21 LTS / Go 1.22 / Python 3.12 / Node.js 20 LTS / Rust 1.75}}
- **版本管理**：{{例如：sdkman / gvm / pyenv / nvm}}
- **包管理器**：{{例如：Gradle / Go Modules / Poetry / pnpm}}

```bash
# 版本文件示例（根据语言选择）
{{例如：.tool-versions 或 .python-version 或 go.mod 中的 go 版本}}
```

### 1.2 运行时环境

<!-- 填写指引：定义开发和运行时的环境要求 -->

- **操作系统**：{{例如：Linux (Ubuntu 22.04+) / macOS / 不限制}}
- **容器化**：{{例如：Docker + Docker Compose，指定基础镜像版本}}
- **JDK/运行时版本**：{{例如：Eclipse Temurin 21 / 指定发行版}}

```dockerfile
# Dockerfile 基础镜像示例
FROM {{例如：openjdk:21-jdk-slim}}
```

### 1.3 编译与构建

<!-- 填写指引：定义编译选项、构建命令和产物管理 -->

- **编译命令**：{{例如：gradle build / go build / python -m build}}
- **构建产物**：{{例如：JAR / 二进制文件 / Wheel}}
- **产物目录**：{{例如：build/libs/ / bin/ / dist/}}

---

## 2. 代码风格与 Lint 规则

<!-- 填写指引：定义后端代码的 Linter 和 Formatter 配置，确保代码风格统一 -->

### 2.1 Linter 配置

<!-- 填写指引：根据语言选择合适的 Linter 工具，列出关键规则 -->

- **Linter 工具**：{{例如：Checkstyle (Java) / golangci-lint (Go) / Ruff (Python) / ESLint (Node.js)}}
- **配置文件**：{{例如：.golangci.yml / ruff.toml / .eslintrc.js}}
- **运行命令**：{{例如：gradle check / golangci-lint run / ruff check}}

#### 关键规则说明

| 规则 | 值 | 原因 |
|------|-----|------|
| {{例如：errcheck}} | {{例如：enabled}} | {{例如：强制检查错误返回值，避免静默失败}} |
| {{例如：unused}} | {{例如：error}} | {{例如：禁止未使用的变量和导入}} |

### 2.2 Formatter 配置

<!-- 填写指引：定义代码格式化工具和配置 -->

- **Formatter 工具**：{{例如：google-java-format / gofmt / Black / Prettier}}
- **配置文件**：{{例如：无配置（使用默认） / .prettierrc}}
- **运行命令**：{{例如：gradle format / gofmt -w . / black .}}

### 2.3 静态分析（如适用）

<!-- 填写指引：如果使用静态分析工具（如 SonarQube），列出配置 -->

- **工具**：{{例如：SonarQube / Semgrep}}
- **扫描范围**：{{例如：仅 src/ 目录，排除测试和生成代码}}
- **质量门禁**：{{例如：新代码覆盖率 > 80%，零 Critical 问题}}

---

## 3. 命名约定

<!-- 填写指引：后端命名约定需要覆盖文件、包、类、函数、变量、常量、数据库对象等多个维度 -->

### 3.1 文件与目录命名

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| 源文件 | {{例如：PascalCase.java / snake_case.go / snake_case.py}} | {{例如：UserService.java / user_service.go / user_service.py}} |
| 测试文件 | {{例如：与源文件同名 + Test 后缀}} | {{例如：UserServiceTest.java / user_service_test.go}} |
| 配置文件 | {{例如：kebab-case.yml}} | {{例如：application-dev.yml}} |
| 迁移文件 | {{例如：时间戳_描述.sql}} | {{例如：20240115_001_create_users_table.sql}} |

### 3.2 包/模块命名

<!-- 填写指引：包名使用全小写，避免下划线和连字符 -->

```text
# ✅ 正确
com.example.project.user
internal/service
api/v1

# ❌ 错误
com.example.project.UserService
internal/user_service
api/v-1
```

### 3.3 类/结构体命名

<!-- 填写指引：类名使用 PascalCase，接口与实现分离命名 -->

```java
// ✅ 正确（Java 示例）
public class UserService { ... }
public interface UserRepository { ... }
public class JpaUserRepository implements UserRepository { ... }

// ❌ 错误
public class userService { ... }  // 类名不应使用 camelCase
public class UserServiceImpl { ... }  // 避免无意义的 Impl 后缀，应使用具体技术前缀
```

### 3.4 函数/方法命名

<!-- 填写指引：函数使用 camelCase，遵循动词+名词模式 -->

```java
// ✅ 正确
public User findById(Long id) { ... }
public List<User> findActiveUsers() { ... }
public void createUser(CreateUserRequest request) { ... }
public boolean isUserExists(String email) { ... }

// ❌ 错误
public User get(Long id) { ... }  // 过于简短
public List<User> data() { ... }  // 缺少动词
public void process() { ... }  // 过于笼统
```

### 3.5 常量命名

<!-- 填写指引：常量使用 UPPER_SNAKE_CASE，枚举使用 PascalCase -->

```java
// ✅ 正确
public static final int MAX_RETRY_COUNT = 3;
public static final String API_VERSION = "v1";

public enum UserStatus {
    ACTIVE,
    INACTIVE,
    BANNED
}

// ❌ 错误
public static final int maxRetry = 3;  // 常量不应使用 camelCase
public static final String api_version = "v1";  // 常量不应使用 snake_case
```

### 3.6 数据库对象命名

<!-- 填写指引：数据库表名、字段名、索引名的命名规则 -->

| 对象 | 命名规则 | 示例 |
|------|---------|------|
| 表名 | {{例如：snake_case 复数}} | {{例如：users, order_items}} |
| 字段名 | {{例如：snake_case 单数}} | {{例如：user_id, created_at}} |
| 主键 | {{例如：id}} | {{例如：id}} |
| 外键 | {{例如：关联表_id}} | {{例如：user_id, order_id}} |
| 索引 | {{例如：idx_表名_字段名}} | {{例如：idx_users_email}} |
| 唯一索引 | {{例如：uk_表名_字段名}} | {{例如：uk_users_email}} |

---

## 4. 分层规范

<!-- 填写指引：定义后端代码的分层架构，明确每一层的职责边界和交互规则 -->

### 4.1 分层架构概览

<!-- 填写指引：根据项目架构定义分层，常见为 Controller → Service → Repository 三层 -->

```text
{{例如：
Controller 层（接口层）
    ↓ 调用
Service 层（业务逻辑层）
    ↓ 调用
Repository 层（数据访问层）
    ↓ 操作
Database
}}
```

### 4.2 Controller 层规范

<!-- 填写指引：Controller 只负责参数校验、调用 Service、返回响应，不包含业务逻辑 -->

- **职责**：{{例如：接收请求、参数校验、调用 Service、格式化响应}}
- **禁止**：{{例如：直接操作数据库、包含业务逻辑、处理事务}}
- **返回值**：{{例如：统一使用 ApiResponse 包装}}

```java
// ✅ 正确：Controller 只做参数转发和响应包装
@RestController
@RequestMapping("/api/v1/users")
public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{id}")
    public ApiResponse<UserDTO> getUser(@PathVariable Long id) {
        return ApiResponse.ok(userService.findById(id));
    }
}

// ❌ 错误：Controller 中包含业务逻辑
@GetMapping("/{id}")
public ApiResponse<UserDTO> getUser(@PathVariable Long id) {
    User user = userRepository.findById(id);
    if (user == null) {
        throw new RuntimeException("用户不存在");  // 业务判断应在 Service 层
    }
    return ApiResponse.ok(convertToDTO(user));  // 转换逻辑应在 Service 层
}
```

<!-- Node.js/TypeScript 等效写法（Next.js App Router + Prisma Client）：
// ✅ 正确：Route Handler 只做参数校验、调用 Service、返回响应
// app/api/v1/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { userService } from '@/services/user.service';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await userService.findById(Number(params.id));
  return NextResponse.json({ code: 0, data: user });
}

// ❌ 错误：Route Handler 中包含业务逻辑
export async function GET(request: NextRequest, { params }) {
  const user = await prisma.user.findUnique({ where: { id: Number(params.id) } });
  if (!user) throw new Error('用户不存在');  // 业务判断应在 Service 层
  return NextResponse.json({ code: 0, data: user });
}
-->

<!-- Python (FastAPI) 等效写法 -->
```python
from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_current_user
from ..dtos.user_dto import UserCreateRequest, UserResponse
from ..services.user_service import UserService

router = APIRouter(prefix="/users", tags=["用户"])

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    data: UserCreateRequest,
    service: UserService = Depends(),
    current_user = Depends(get_current_user),
):
    """创建用户"""
    return await service.create(data)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(),
):
    """获取用户详情"""
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
```

<!-- Go (Gin) 等效写法 -->
```go
package controller

import (
    "net/http"
    "strconv"
    "github.com/gin-gonic/gin"
    "{{project}}/internal/service"
    "{{project}}/internal/dto"
)

type UserController struct {
    service *service.UserService
}

func NewUserController(svc *service.UserService) *UserController {
    return &UserController{service: svc}
}

func (c *UserController) Create(ctx *gin.Context) {
    var req dto.UserCreateRequest
    if err := ctx.ShouldBindJSON(&req); err != nil {
        ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }
    user, err := c.service.Create(ctx.Request.Context(), &req)
    if err != nil {
        ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
        return
    }
    ctx.JSON(http.StatusCreated, user)
}

func (c *UserController) GetByID(ctx *gin.Context) {
    id, _ := strconv.Atoi(ctx.Param("id"))
    user, err := c.service.GetByID(ctx.Request.Context(), id)
    if err != nil {
        ctx.JSON(http.StatusNotFound, gin.H{"error": "用户不存在"})
        return
    }
    ctx.JSON(http.StatusOK, user)
}
```

### 4.3 Service 层规范

<!-- 填写指引：Service 层包含所有业务逻辑，是事务管理的主要场所 -->

- **职责**：{{例如：业务逻辑编排、事务管理、数据转换、调用外部服务}}
- **禁止**：{{例如：直接操作 HTTP 请求/响应对象、包含数据访问细节}}
- **事务管理**：{{例如：在 Service 方法上声明事务边界}}

```java
// ✅ 正确：Service 层包含业务逻辑和事务管理
@Service
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;

    @Transactional
    public UserDTO createUser(CreateUserRequest request) {
        // 业务校验
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException(ErrorCode.USER_EMAIL_EXISTS);
        }
        // 创建用户
        User user = new User(request.getName(), request.getEmail());
        userRepository.save(user);
        // 发送欢迎邮件
        emailService.sendWelcomeEmail(user);
        return UserDTO.from(user);
    }
}
```

<!-- Node.js/TypeScript 等效写法（Service 层 + Prisma Client）：
// ✅ 正确：Service 层包含业务逻辑和事务管理
// services/user.service.ts
import { prisma } from '@/lib/prisma';
import { BusinessError } from '@/errors/business-error';
import { emailService } from '@/services/email.service';

export const userService = {
  async createUser(data: CreateUserRequest): Promise<UserDTO> {
    // 业务校验
    const existing = await prisma.user.findUnique({ where: { email: data.email } });
    if (existing) {
      throw new BusinessError('USER_EMAIL_EXISTS', '邮箱已被注册');
    }
    // 创建用户（Prisma 事务）
    const user = await prisma.$transaction(async (tx) => {
      const newUser = await tx.user.create({
        data: { name: data.name, email: data.email },
      });
      // 发送欢迎邮件
      await emailService.sendWelcomeEmail(newUser);
      return newUser;
    });
    return UserDTO.from(user);
  },
};
-->

<!-- Python (FastAPI) 等效写法 -->
```python
from ..repositories.user_repository import UserRepository
from ..models.user import User
from ..dtos.user_dto import UserCreateRequest, UserResponse
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create(self, data: UserCreateRequest) -> UserResponse:
        """创建用户，检查用户名唯一性"""
        existing = await self.repo.get_by_username(data.username)
        if existing:
            raise ValueError(f"用户名 '{data.username}' 已存在")
        user = await self.repo.create(data)
        logger.info(f"用户创建成功: id={user.id}, username={user.username}")
        return UserResponse.model_validate(user)

    async def get_by_id(self, user_id: int) -> UserResponse | None:
        """根据 ID 获取用户"""
        user = await self.repo.get_by_id(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)
```

<!-- Go (Gin) 等效写法 -->
```go
package service

import (
    "context"
    "errors"
    "{{project}}/internal/repository"
    "{{project}}/internal/dto"
    "go.uber.org/zap"
)

var ErrUserNotFound = errors.New("用户不存在")
var ErrUsernameExists = errors.New("用户名已存在")

type UserService struct {
    repo   *repository.UserRepository
    logger *zap.Logger
}

func NewUserService(repo *repository.UserRepository, logger *zap.Logger) *UserService {
    return &UserService{repo: repo, logger: logger}
}

func (s *UserService) Create(ctx context.Context, req *dto.UserCreateRequest) (*dto.UserResponse, error) {
    if _, err := s.repo.GetByUsername(ctx, req.Username); err == nil {
        return nil, ErrUsernameExists
    }
    user, err := s.repo.Create(ctx, req)
    if err != nil {
        return nil, err
    }
    s.logger.Info("用户创建成功", zap.Int("id", user.ID), zap.String("username", user.Username))
    return user, nil
}
```

### 4.4 Repository 层规范

<!-- 填写指引：Repository 层只负责数据访问，不包含业务逻辑 -->

- **职责**：{{例如：数据 CRUD、复杂查询封装、数据库操作}}
- **禁止**：{{例如：包含业务判断、调用其他 Service、事务管理}}
- **查询方法**：{{例如：使用 ORM 提供的方法命名约定或自定义查询}}

```java
// ✅ 正确：Repository 只做数据访问
public interface UserRepository {
    Optional<User> findById(Long id);
    Optional<User> findByEmail(String email);
    boolean existsByEmail(String email);
    void save(User user);
    Page<User> findAll(Pageable pageable);
}

// ❌ 错误：Repository 中包含业务逻辑
public interface UserRepository {
    User findActiveUser(Long id);  // "活跃"是业务概念，不应出现在 Repository
    void registerUser(User user);  // "注册"是业务操作，不应出现在 Repository
}
```

<!-- Node.js/TypeScript 等效写法（Repository 层 + Prisma Client）：
// ✅ 正确：Repository 只做数据访问
// repositories/user.repository.ts
import { prisma } from '@/lib/prisma';

export const userRepository = {
  findById(id: number) {
    return prisma.user.findUnique({ where: { id } });
  },
  findByEmail(email: string) {
    return prisma.user.findUnique({ where: { email } });
  },
  existsByEmail(email: string) {
    return prisma.user.count({ where: { email } }).then((c) => c > 0);
  },
  findAll(page: number, pageSize: number) {
    return prisma.user.findMany({
      skip: (page - 1) * pageSize,
      take: pageSize,
    });
  },
};

// ❌ 错误：Repository 中包含业务逻辑
export const userRepository = {
  findActiveUser(id: number) {  // "活跃"是业务概念，不应出现在 Repository
    return prisma.user.findFirst({ where: { id, status: 'ACTIVE' } });
  },
  registerUser(data: CreateUserInput) {  // "注册"是业务操作，不应出现在 Repository
    return prisma.user.create({ data });
  },
};
-->

> **其他 ORM 参考**：Python FastAPI 项目使用 SQLAlchemy（`Base = declarative_base()` + `sessionmaker`）；Django 项目使用 Django ORM（`models.Model` 子类）；Go 项目使用 GORM（`gorm.Model` 嵌入）；Java Spring Boot 项目使用 JPA/Hibernate（`@Entity` + `@Repository`）。

### 4.5 层间数据传输

<!-- 填写指引：定义层间数据传输对象（DTO）的使用规范 -->

| 层间 | 传输对象 | 命名规则 |
|------|---------|---------|
| Controller → Service | {{例如：Request DTO}} | {{例如：CreateUserRequest}} |
| Service → Controller | {{例如：Response DTO}} | {{例如：UserDTO / UserResponse}} |
| Service → Repository | {{例如：Entity / Model}} | {{例如：User}} |
| Repository → Service | {{例如：Entity / Model}} | {{例如：User}} |

---

## 5. 异常处理规范

<!-- 填写指引：定义统一的异常处理体系，确保错误信息格式一致、便于排查 -->

### 5.1 异常体系设计

<!-- 填写指引：设计异常类的继承层次，区分业务异常和系统异常 -->

```text
{{例如：
RuntimeException
├── BusinessException          // 业务异常（可预期）
│   ├── ResourceNotFoundException  // 资源不存在
│   ├── ValidationException        // 参数校验失败
│   └── PermissionDeniedException  // 权限不足
└── SystemException             // 系统异常（不可预期）
    ├── DatabaseException          // 数据库异常
    └── ExternalServiceException   // 外部服务异常
}}
```

### 5.2 统一异常响应格式

<!-- 填写指引：定义所有异常的 HTTP 响应格式，必须与 API 规范中的错误格式一致 -->

```json
{
  "code": "{{例如：USER_NOT_FOUND}}",
  "message": "{{例如：用户不存在}}",
  "details": {{例如：null 或具体错误详情数组}},
  "timestamp": "{{例如：2024-01-15T10:30:00Z}}"
}
```

### 5.3 异常处理示例

```java
// ✅ 正确：使用自定义异常 + 全局异常处理器
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException ex) {
        return ResponseEntity
            .status(ex.getHttpStatus())
            .body(ErrorResponse.from(ex));
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleUnexpectedException(Exception ex) {
        log.error("未预期的异常", ex);  // 记录完整堆栈
        return ResponseEntity
            .status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(new ErrorResponse("INTERNAL_ERROR", "服务器内部错误", null));
    }
}

// ❌ 错误：在 Controller 中逐个 try-catch
@GetMapping("/{id}")
public ResponseEntity<?> getUser(@PathVariable Long id) {
    try {
        User user = userService.findById(id);
        return ResponseEntity.ok(user);
    } catch (Exception e) {
        return ResponseEntity.badRequest().body("出错了");  // 错误信息不结构化
    }
}
```

<!-- Node.js/TypeScript 等效写法（Next.js error handler + 自定义错误类）：
// ✅ 正确：使用自定义错误类 + 统一错误处理中间件
// errors/business-error.ts
export class BusinessError extends Error {
  constructor(
    public code: string,
    public message: string,
    public statusCode: number = 400
  ) {
    super(message);
    this.name = 'BusinessError';
  }
}

// errors/global-handler.ts（Next.js middleware 或 utils/catch-error）
export function handleError(error: unknown): { code: string; message: string; statusCode: number } {
  if (error instanceof BusinessError) {
    return { code: error.code, message: error.message, statusCode: error.statusCode };
  }
  console.error('未预期的异常', error);  // 记录完整堆栈
  return { code: 'INTERNAL_ERROR', message: '服务器内部错误', statusCode: 500 };
}

// app/api/v1/users/[id]/route.ts 中使用
export async function GET(request: NextRequest, { params }) {
  try {
    const user = await userService.findById(Number(params.id));
    return NextResponse.json({ code: 0, data: user });
  } catch (error) {
    const { code, message, statusCode } = handleError(error);
    return NextResponse.json({ code, message }, { status: statusCode });
  }
}

// ❌ 错误：在 Route Handler 中吞掉异常
export async function GET(request: NextRequest, { params }) {
  try {
    const user = await userService.findById(Number(params.id));
    return NextResponse.json({ code: 0, data: user });
  } catch (e) {
    return NextResponse.json({ message: '出错了' }, { status: 400 });  // 错误信息不结构化
  }
}
-->

<!-- Python (FastAPI) 等效写法 -->
```python
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class AppException(Exception):
    """业务异常基类"""
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """统一业务异常处理"""
    logger.warning(f"业务异常: code={exc.code}, message={exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """未捕获异常处理"""
    logger.error(f"未捕获异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_ERROR", "message": "服务器内部错误"},
    )
```

<!-- Go (Gin) 等效写法 -->
```go
package middleware

import (
    "log/slog"
    "net/http"
    "github.com/gin-gonic/gin"
)

type AppError struct {
    Code    string `json:"code"`
    Message string `json:"message"`
}

func ErrorHandler() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()
        for _, err := range c.Errors {
            switch e := err.Err.(type) {
            case *AppError:
                slog.Warn("业务异常", "code", e.Code, "message", e.Message)
                c.JSON(e.StatusCode(), e)
            default:
                slog.Error("未捕获异常", "error", err.Error())
                c.JSON(http.StatusInternalServerError, gin.H{
                    "code":    "INTERNAL_ERROR",
                    "message": "服务器内部错误",
                })
            }
            return
        }
    }
}
```

### 5.4 异常处理禁止事项

| 禁止事项 | 原因 | 替代方案 |
|---------|------|---------|
| {{例如：吞掉异常（空 catch）}} | {{例如：问题被隐藏，无法排查}} | {{例如：至少记录日志}} |
| {{例如：在 Controller 中 try-catch}} | {{例如：应使用全局异常处理器}} | {{例如：抛出异常，由 GlobalHandler 统一处理}} |
| {{例如：向前端暴露堆栈信息}} | {{例如：安全风险}} | {{例如：生产环境只返回错误码和友好提示}} |

---

## 6. 日志规范

<!-- 填写指引：定义日志的格式、级别、输出目标和脱敏规则，确保日志可用于问题排查 -->

### 6.1 日志格式

<!-- 填写指引：定义统一的日志输出格式，便于日志采集和分析 -->

```text
{{例如：
[时间] [级别] [TraceID] [类名.方法名] - 日志内容

2024-01-15 10:30:00.123 [INFO] [abc123] [UserService.createUser] - 用户创建成功, userId=123
}}
```

### 6.2 日志级别使用

<!-- 填写指引：明确每个日志级别的使用场景 -->

| 级别 | 使用场景 | 示例 |
|------|---------|------|
| ERROR | 系统错误，需要立即处理 | {{例如：数据库连接失败、外部服务调用超时}} |
| WARN | 潜在问题，不影响主流程 | {{例如：请求参数接近上限、缓存未命中率过高}} |
| INFO | 关键业务流程节点 | {{例如：用户注册成功、订单创建完成}} |
| DEBUG | 开发调试信息 | {{例如：SQL 查询语句、方法入参出参}} |

### 6.3 日志编写规范

```java
// ✅ 正确：日志包含关键上下文信息
log.info("用户登录成功, userId={}, ip={}, device={}", userId, ip, deviceType);

// ✅ 正确：异常日志记录完整堆栈
log.error("支付回调处理失败, orderId={}", orderId, exception);

// ❌ 错误：日志信息不足
log.info("登录成功");  // 缺少用户标识
log.error("出错了", e);  // 缺少业务上下文

// ❌ 错误：使用字符串拼接（性能问题）
log.info("用户 " + userId + " 登录成功");  // 应使用占位符
```

### 6.4 敏感信息脱敏

<!-- 填写指引：定义哪些信息属于敏感信息，日志中必须脱敏处理 -->

| 敏感信息 | 脱敏规则 | 示例 |
|---------|---------|------|
| {{例如：手机号}} | {{例如：保留前3后4，中间用 * 替代}} | {{例如：138****1234}} |
| {{例如：邮箱}} | {{例如：保留首字母和域名}} | {{例如：z***@example.com}} |
| {{例如：身份证号}} | {{例如：保留前3后4}} | {{例如：110***********1234}} |
| {{例如：密码}} | {{例如：绝不记录}} | {{例如：[REDACTED]}} |
| {{例如：Token}} | {{例如：只记录前8位}} | {{例如：eyJhbGci...}} |

---

## 7. SQL 编写规范

<!-- 填写指引：定义 SQL 编写的最佳实践，覆盖查询优化、索引使用和禁止写法 -->

### 7.1 查询编写规范

<!-- 填写指引：SQL 查询的基本编写规则 -->

```sql
-- ✅ 正确：明确列出需要的字段，不使用 SELECT *
SELECT id, name, email, created_at
FROM users
WHERE status = 'active'
  AND created_at > '2024-01-01'
ORDER BY created_at DESC
LIMIT 20;

-- ❌ 错误：使用 SELECT *
SELECT * FROM users WHERE status = 'active';
```

<!-- Node.js/TypeScript 等效写法（Prisma ORM 查询）：
// ✅ 正确：明确指定 select 字段，不使用 include 拉取不需要的关联
const users = await prisma.user.findMany({
  select: {
    id: true,
    name: true,
    email: true,
    createdAt: true,
  },
  where: {
    status: 'active',
    createdAt: { gt: new Date('2024-01-01') },
  },
  orderBy: { createdAt: 'desc' },
  take: 20,
});

// ❌ 错误：不指定 select，拉取所有字段（包括敏感字段如 password）
const users = await prisma.user.findMany({
  where: { status: 'active' },
});
-->

### 7.2 索引使用规范

<!-- 填写指引：定义索引的设计原则和使用规范 -->

- **索引原则**：{{例如：WHERE 条件字段、JOIN 关联字段、ORDER BY 排序字段应建立索引}}
- **复合索引**：{{例如：遵循最左前缀原则，高选择性字段放前面}}
- **禁止**：{{例如：在低选择性字段（如性别）上单独建索引}}

```sql
-- ✅ 正确：利用索引的查询
SELECT id, name FROM users WHERE email = 'user@example.com';

-- ❌ 错误：对索引字段使用函数，导致索引失效
SELECT id, name FROM users WHERE LOWER(email) = 'user@example.com';
-- 替代方案：存储时就统一为小写
```

### 7.3 禁止写法

| 禁止写法 | 原因 | 替代方案 |
|---------|------|---------|
| {{例如：SELECT *}} | {{例如：浪费 IO 和内存，破坏索引覆盖}} | {{例如：明确列出字段}} |
| {{例如：在 WHERE 中对索引字段使用函数}} | {{例如：导致索引失效}} | {{例如：使用函数式索引或存储计算值}} |
| {{例如：大表无 LIMIT 的查询}} | {{例如：可能导致 OOM}} | {{例如：必须加 LIMIT 或使用分页}} |
| {{例如：隐式类型转换}} | {{例如：导致索引失效}} | {{例如：保持类型一致}} |
| {{例如：OR 条件连接不同字段}} | {{例如：优化器可能放弃索引}} | {{例如：使用 UNION ALL 替代}} |

### 7.4 慢查询规范

<!-- 填写指引：定义慢查询的阈值和处理流程 -->

- **慢查询阈值**：{{例如：> 200ms}}
- **监控方式**：{{例如：数据库慢查询日志 / APM 工具}}
- **处理流程**：{{例如：每日检查慢查询日志 → 分析执行计划 → 优化或添加索引}}

---

## 8. 安全编码规范

<!-- 填写指引：定义后端安全编码的基本规则，覆盖 OWASP Top 10 中的常见风险 -->

### 8.1 输入校验

<!-- 填写指引：所有外部输入必须校验，使用白名单而非黑名单策略 -->

```java
// ✅ 正确：使用注解进行参数校验
public class CreateUserRequest {
    @NotBlank(message = "用户名不能为空")
    @Size(min = 2, max = 50, message = "用户名长度必须在 2-50 之间")
    private String name;

    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    private String email;

    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;
}

// ❌ 错误：不校验直接使用
public void createUser(String name, String email) {
    userRepository.save(new User(name, email));  // 没有任何校验
}
```

<!-- Node.js/TypeScript 等效写法（Zod schema validation）：
// ✅ 正确：使用 Zod 定义校验 schema
// schemas/user.schema.ts
import { z } from 'zod';

export const createUserSchema = z.object({
  name: z.string().min(2, '用户名不能为空').max(50, '用户名长度必须在 2-50 之间'),
  email: z.string().email('邮箱格式不正确'),
  phone: z.string().regex(/^1[3-9]\d{9}$/, '手机号格式不正确').optional(),
});

export type CreateUserInput = z.infer<typeof createUserSchema>;

// 在 Route Handler 中使用
export async function POST(request: NextRequest) {
  const body = await request.json();
  const result = createUserSchema.safeParse(body);
  if (!result.success) {
    return NextResponse.json(
      { code: 'VALIDATION_ERROR', message: result.error.flatten() },
      { status: 400 }
    );
  }
  const user = await userService.createUser(result.data);
  return NextResponse.json({ code: 0, data: user });
}

// ❌ 错误：不校验直接使用
export async function POST(request: NextRequest) {
  const { name, email } = await request.json();
  await prisma.user.create({ data: { name, email } });  // 没有任何校验
}
-->

### 8.2 SQL 注入防护

<!-- 填写指引：使用参数化查询，禁止字符串拼接 SQL -->

```java
// ✅ 正确：使用参数化查询
@Query("SELECT u FROM User u WHERE u.email = :email")
Optional<User> findByEmail(@Param("email") String email);

// ❌ 错误：字符串拼接 SQL
@Query("SELECT u FROM User u WHERE u.email = '" + email + "'")  // SQL 注入风险！
```

### 8.3 XSS 防护

<!-- 填写指引：对所有用户输入进行 HTML 转义，设置正确的 Content-Type -->

- **输入处理**：{{例如：存储前进行 HTML 转义或使用富文本白名单}}
- **输出处理**：{{例如：API 响应设置 Content-Type: application/json}}
- **CSP**：{{例如：配置 Content-Security-Policy 头}}

### 8.4 认证与授权

<!-- 填写指引：定义认证和授权的基本规范 -->

- **密码存储**：{{例如：使用 bcrypt/argon2 哈希，禁止明文存储}}
- **Token 管理**：{{例如：使用 JWT，设置合理的过期时间}}
- **权限校验**：{{例如：在 Controller 或拦截器中进行权限校验，默认拒绝}}

### 8.5 其他安全规范

| 规范 | 要求 |
|------|------|
| {{例如：HTTPS}} | {{例如：所有接口必须使用 HTTPS}} |
| {{例如：CORS}} | {{例如：明确配置允许的域名，不使用 *}} |
| {{例如：速率限制}} | {{例如：对敏感接口（登录/注册）进行速率限制}} |
| {{例如：敏感数据}} | {{例如：日志和响应中不得包含密码、密钥等敏感信息}} |

---

## 9. AI 协作协议

<!-- 填写指引：本章节定义 AI 辅助编码时的行为准则，确保 AI 生成的代码符合项目规范 -->

### 9.1 必读文档清单

<!-- 填写指引：AI 在为本项目写代码前必须读取的文档列表 -->

AI 在为本项目编写或修改后端代码前，必须先读取以下文档：

1. `../../../specs/PROJECT-CONTEXT.md` — 项目全景上下文
2. `specs/后端开发规范.md` — 本文档
3. `specs/技术栈.md` — 技术栈决策
4. `specs/项目结构.md` — 目录结构约定
5. `specs/API接口文档.md` — 接口设计规范
6. `specs/数据模型字段约定.md` — 数据模型定义
7. `../../../specs/GUARDRAILS.md` — 项目边界守卫

### 9.2 写代码规则

<!-- 填写指引：AI 编写代码时必须遵守的规则 -->

1. **分层约束**：{{例如：Controller 不写业务逻辑，Repository 不写业务判断}}
2. **异常处理**：{{例如：使用自定义异常，不使用 RuntimeException}}
3. **参数校验**：{{例如：所有外部输入必须校验}}
4. **日志记录**：{{例如：关键操作必须记录日志，包含业务上下文}}
5. **SQL 安全**：{{例如：使用参数化查询，禁止字符串拼接}}
6. **敏感信息**：{{例如：日志中必须脱敏处理}}

### 9.3 自检清单

<!-- 填写指引：AI 提交代码前必须逐项检查的清单 -->

- [ ] 代码是否遵循分层规范（Controller/Service/Repository 职责清晰）
- [ ] 是否使用了自定义异常而非通用异常
- [ ] 所有外部输入是否进行了校验
- [ ] 关键操作是否记录了日志（包含上下文信息）
- [ ] SQL 是否使用参数化查询
- [ ] 日志中是否包含敏感信息（需要脱敏）
- [ ] 是否有未处理的异常（空 catch 块）
- [ ] 命名是否符合第 3 节的约定

### 9.4 错题本

<!-- 填写指引：记录 AI 常见的后端编码错误和正确做法，持续更新 -->

| 错误模式 | 正确做法 | 备注 |
|---------|---------|------|
| {{例如：在 Controller 中写业务逻辑}} | {{例如：业务逻辑放在 Service 层}} | {{例如：违反分层架构}} |
| {{例如：使用 SELECT * 查询}} | {{例如：明确列出需要的字段}} | {{例如：性能和安全问题}} |
| {{例如：密码明文存储}} | {{例如：使用 bcrypt 哈希存储}} | {{例如：严重安全漏洞}} |
| {{例如：空 catch 块吞掉异常}} | {{例如：至少记录日志并抛出/包装异常}} | {{例如：问题被隐藏}} |

---

> 本文档基于项目技术栈定制生成，所有规则均针对本项目优化。
> 如有疑问或需要调整，请在团队内部讨论后更新本文档。

---

## 10. 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| {{YYYY-MM-DD}} | 1.0 | 初始版本 | {{作者}} |
