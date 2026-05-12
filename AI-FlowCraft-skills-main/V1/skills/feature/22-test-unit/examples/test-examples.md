# 单元测试代码示例

> 本文件包含各语言的单元测试代码示例及参考配置，从 SKILL.md 中提取，便于独立查阅。

## AAA 模式示例

### JavaScript/TypeScript（Jest）

```javascript
// AAA 模式示例（Jest）
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

### Python（pytest）

```python
# AAA 模式示例（pytest）
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

## Mock 示例

### JavaScript/TypeScript（Jest）

```javascript
// Jest Mock 示例
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

### Python（pytest）

```python
# pytest Mock 示例
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

## 参数化测试示例

### JavaScript/TypeScript（Jest test.each）

```javascript
// Jest test.each 示例
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

### Python（pytest @pytest.mark.parametrize）

```python
# pytest @pytest.mark.parametrize 示例
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

## 各语言完整测试代码示例

### JavaScript/TypeScript（Jest + React）

```javascript
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

### Python（pytest）

```python
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

### Rust（cargo test）

```rust
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

### Java（JUnit 5）

```java
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

### Go（testing + testify）

```go
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

### C#（xUnit + FluentAssertions）

```csharp
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

## 附录

### 附录 A：中间文件 JSON 格式定义

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

### 附录 B：测试环境配置模板

**Jest 配置**（`jest.config.js`）：
```javascript
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
```

**pytest 配置**（`pytest.ini`）：
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short --cov=src --cov-report=term-missing --cov-report=html
```

### 附录 C：各语言手动运行测试命令

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

### 附录 D：静态分析命令

```bash
# JavaScript/TypeScript
npx eslint src/ --format json --output-file ./eslint_report.json

# Python
python -m pylint src/ --output-format=json > ./pylint_report.json 2>/dev/null
# 或使用 flake8（更轻量）
python -m flake8 src/ --format=json --output-file ./flake8_report.json

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

### 附录 E：变异测试命令

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

变异测试通过标准：变异得分（Mutation Score）>= 80%，被杀死的变异体 >= 总变异体的 80%。

### 附录 F：测试报告模板

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
| 行覆盖率 | XX% | OK/Warning |
| 分支覆盖率 | XX% | OK/Warning |
| 函数覆盖率 | XX% | OK/Warning |
| 语句覆盖率 | XX% | OK/Warning |

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
| 测试通过率 | 100% | XX% | Pass/Fail |
| 行覆盖率 | >= 80% | XX% | Pass/Fail |
| 分支覆盖率 | >= 70% | XX% | Pass/Fail |
| 函数覆盖率 | >= 80% | XX% | Pass/Fail |
| 总执行时间 | < 120s | Xs | Pass/Fail |
```
