# 集成测试代码示例

> 本文件包含各语言/框架的完整集成测试代码示例，供 AI 编写测试时参考。
> SKILL.md 中仅保留推荐框架的简短示例，完整示例见此处。

---

## Node.js + Supertest

```typescript
// Node.js + Express + Supertest
import request from 'supertest';
import app from '../src/app';
import { setupTestDB, teardownTestDB } from '../test/helpers/database';

describe('用户 API 集成测试', () => {
  // 每个测试套件前：初始化测试数据库
  beforeAll(async () => {
    await setupTestDB();
  });

  afterAll(async () => {
    await teardownTestDB();
  });

  describe('POST /api/users', () => {
    it('合法数据应创建用户并返回 201', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({
          username: 'testuser',
          email: 'test@example.com',
          password: 'SecurePass123!',
        })
        .expect('Content-Type', /json/)
        .expect(201);

      // 验证响应体
      expect(response.body.username).toBe('testuser');
      expect(response.body.email).toBe('test@example.com');
      expect(response.body).not.toHaveProperty('password');  // 不返回密码

      // 验证数据库中存在该记录
      // await verifyUserInDB(response.body.id);
    });

    it('缺少必填字段应返回 400', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({ username: 'testuser' })  // 缺少 email 和 password
        .expect(400);

      expect(response.body.error).toBeDefined();
    });

    it('重复邮箱应返回 409', async () => {
      // 先创建一个用户
      await request(app)
        .post('/api/users')
        .send({ username: 'user1', email: 'dup@example.com', password: 'Pass123!' });

      // 再用相同邮箱创建
      const response = await request(app)
        .post('/api/users')
        .send({ username: 'user2', email: 'dup@example.com', password: 'Pass123!' })
        .expect(409);

      expect(response.body.error).toContain('已存在');
    });
  });

  describe('GET /api/users/:id', () => {
    it('存在的用户 ID 应返回用户信息', async () => {
      // 先创建用户
      const created = await request(app)
        .post('/api/users')
        .send({ username: 'findme', email: 'find@example.com', password: 'Pass123!' });

      const response = await request(app)
        .get(`/api/users/${created.body.id}`)
        .expect(200);

      expect(response.body.username).toBe('findme');
    });

    it('不存在的用户 ID 应返回 404', async () => {
      await request(app)
        .get('/api/users/99999')
        .expect(404);
    });
  });
});
```

---

## Python + FastAPI

```python
# Python + FastAPI + httpx
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def client():
    """创建测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(autouse=True)
async def setup_db():
    """每个测试前清空并重建数据库"""
    from app.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class TestUserAPI:
    """用户 API 集成测试"""

    async def test_create_user_success(self, client: AsyncClient):
        """正向测试：合法数据应创建用户"""
        response = await client.post("/api/users", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert "password" not in data  # 不返回密码

    async def test_create_user_duplicate_email(self, client: AsyncClient):
        """边界测试：重复邮箱应返回 409"""
        # 先创建
        await client.post("/api/users", json={
            "username": "user1", "email": "dup@example.com", "password": "Pass123!"
        })
        # 重复创建
        response = await client.post("/api/users", json={
            "username": "user2", "email": "dup@example.com", "password": "Pass123!"
        })
        assert response.status_code == 409

    async def test_get_user_not_found(self, client: AsyncClient):
        """异常测试：不存在的用户应返回 404"""
        response = await client.get("/api/users/99999")
        assert response.status_code == 404

    async def test_unauthorized_access(self, client: AsyncClient):
        """认证测试：未认证访问受保护接口应返回 401"""
        response = await client.get("/api/profile")
        assert response.status_code == 401
```

---

## Java

```java
// Java (Spring Boot + JUnit 5 + MockMvc)
@SpringBootTest
@AutoConfigureMockMvc
class OrderIntegrationTest {
    @Autowired private MockMvc mockMvc;
    @Test void createOrder() throws Exception {
        mockMvc.perform(post("/api/orders")
            .contentType(MediaType.APPLICATION_JSON)
            .content("{\"productId\": 1, \"quantity\": 2}"))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").exists());
    }
}
```

---

## Go

```go
// Go (Gin/Echo + httptest)
func TestCreateOrder(t *testing.T) {
    w := httptest.NewRecorder()
    req, _ := http.NewRequest("POST", "/api/orders", bytes.NewBufferString(`{"product_id":1,"quantity":2}`))
    req.Header.Set("Content-Type", "application/json")
    router.ServeHTTP(w, req)
    assert.Equal(t, http.StatusCreated, w.Code)
}
```

---

## Rust

```rust
// Rust (Actix-web/Axum + reqwest)
#[cfg(test)]
mod tests {
    use super::*;
    #[actix_web::test]
    async fn test_create_order() {
        let app = test::init_service(App::new().configure(init_routes)).await;
        let req = TestRequest::post().uri("/api/orders")
            .set_json(&serde_json::json!({"product_id": 1, "quantity": 2}))
            .to_request();
        let resp = test::call_service(&app, req).await;
        assert_eq!(resp.status(), StatusCode::CREATED);
    }
}
```

---

## C#

```csharp
// C# (ASP.NET Core + xUnit + WebApplicationFactory)
public class OrderIntegrationTests : IClassFixture<WebApplicationFactory<Program>> {
    private readonly HttpClient _client;
    public OrderIntegrationTests(WebApplicationFactory<Program> factory) => _client = factory.CreateClient();
    [Fact] public async Task CreateOrder_ReturnsCreated() {
        var resp = await _client.PostAsJsonAsync("/api/orders", new { ProductId = 1, Quantity = 2 });
        Assert.Equal(HttpStatusCode.Created, resp.StatusCode);
    }
}
```
