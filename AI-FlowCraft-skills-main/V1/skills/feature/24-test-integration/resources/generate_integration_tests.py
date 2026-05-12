#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试辅助脚本 - 测试代码生成器
功能：根据扫描结果，自动生成集成测试代码骨架
支持：Node.js (Supertest)、Python (httpx/pytest)、Go (httptest)
用法：python generate_integration_tests.py <扫描结果JSON> <输出目录> [项目路径]
"""

import sys
import re
from pathlib import Path
from typing import Dict, List

from common import load_json


def generate_nodejs_tests(integration_points: List[Dict], output_dir: str, project_path: str = "") -> None:
    """
    生成 Node.js 集成测试代码（Jest + Supertest）

    Args:
        integration_points: 集成点列表
        output_dir: 测试文件输出目录
        project_path: 项目根目录
    """
    # 按 API 路由分组
    api_routes = [p for p in integration_points if p.get("category") == "api"]

    if not api_routes:
        print("  未发现 API 路由，跳过 Node.js 测试生成")
        return

    # 按文件分组
    file_groups: Dict[str, List[Dict]] = {}
    for route in api_routes:
        file_key = route["file"]
        if file_key not in file_groups:
            file_groups[file_key] = []
        file_groups[file_key].append(route)

    for file_path, routes in file_groups.items():
        # 生成测试文件路径
        test_file = Path(output_dir) / file_path.replace(".ts", ".test.ts").replace(".js", ".test.js")
        test_file = test_file.with_name(f"{test_file.stem}.integration{test_file.suffix}")
        test_file.parent.mkdir(parents=True, exist_ok=True)

        # 计算导入路径
        import_path = file_path.replace(".ts", "").replace(".js", "")
        depth = file_path.count("/")
        prefix = "../" * depth

        lines: List[str] = []
        lines.append(f"// 自动生成的集成测试 - {file_path}")
        lines.append(f"// 测试框架: Jest + Supertest")
        lines.append(f"// 注意：以下测试代码为骨架，AI 需根据源码分析结果填充具体测试值和断言")
        lines.append("")
        lines.append(f"import request from 'supertest';")
        lines.append(f"import {{ setupTestDB, teardownTestDB }} from '{prefix}test/helpers/database';")
        lines.append(f"// TODO: 根据实际项目调整 app 导入路径")
        lines.append(f"import app from '{prefix}{import_path}';")
        lines.append("")

        # 按路径分组路由
        path_groups: Dict[str, List[Dict]] = {}
        for route in routes:
            path_key = route["path"]
            if path_key not in path_groups:
                path_groups[path_key] = []
            path_groups[path_key].append(route)

        for path, path_routes in path_groups.items():
            # 使用第一个路由的方法作为 describe 名称
            method = path_routes[0]["method"]
            safe_name = path.replace("/", "_").replace(":", "").replace("-", "_").strip("_")
            if not safe_name:
                safe_name = "root"

            lines.append(f"describe('{method} {path}', () => {{")
            lines.append(f"  // 路由文件: {file_path}")
            auth = path_routes[0].get("auth_required", False)
            if auth:
                lines.append(f"  // 此路由需要认证")
            lines.append("")

            # === 正向测试 ===
            lines.append(f"  describe('正向测试', () => {{")
            lines.append(f"    it('合法请求应返回正确响应', async () => {{")
            lines.append(f"      // TODO: 准备请求数据 - 替换 {{}} 中的字段为实际合法数据")
            if auth:
                lines.append(f"      // const token = await getTestToken();")
                lines.append(f"      const response = await request(app)")
                lines.append(f"        .{method.lower()}('{path}')")
                lines.append(f"        .set('Authorization', 'Bearer ' + token)")
                lines.append(f"        .send({{ /* TODO: 替换为实际合法请求数据 */ }});")
            else:
                lines.append(f"      const response = await request(app)")
                lines.append(f"        .{method.lower()}('{path}')")
                lines.append(f"        .send({{ /* TODO: 替换为实际合法请求数据 */ }});")
            lines.append(f"      expect(response.status).toBe(200);")
            lines.append(f"      expect(response.body).toBeDefined();")
            lines.append(f"      // TODO: 替换为实际业务字段断言，如 expect(response.body.data.id).toBeDefined();")
            lines.append(f"    }});")
            lines.append(f"  }});")
            lines.append("")

            # === 参数验证测试 ===
            if method in ("POST", "PUT", "PATCH"):
                lines.append(f"  describe('参数验证测试', () => {{")
                lines.append(f"    it('缺少必填字段应返回 400', async () => {{")
                lines.append(f"      const response = await request(app)")
                lines.append(f"        .{method.lower()}('{path}')")
                lines.append(f"        .send({{}});  // 空请求体")
                lines.append(f"      expect(response.status).toBe(400);")
                lines.append(f"    }});")
                lines.append("")
                lines.append(f"    it('字段类型错误应返回 400', async () => {{")
                lines.append(f"      // TODO: 替换 'field' 为实际的字符串类型必填字段名")
                lines.append(f"      const response = await request(app)")
                lines.append(f"        .{method.lower()}('{path}')")
                lines.append(f"        .send({{ field: 123 }});  // 应为字符串")
                lines.append(f"      expect(response.status).toBe(400);")
                lines.append(f"    }});")
                lines.append(f"  }});")
                lines.append("")

            # === 认证测试 ===
            if auth:
                lines.append(f"  describe('认证测试', () => {{")
                lines.append(f"    it('无 Token 应返回 401', async () => {{")
                lines.append(f"      const response = await request(app)")
                lines.append(f"        .{method.lower()}('{path}');")
                lines.append(f"      expect(response.status).toBe(401);")
                lines.append(f"    }});")
                lines.append("")
                lines.append(f"    it('过期 Token 应返回 401', async () => {{")
                lines.append(f"      const response = await request(app)")
                lines.append(f"        .{method.lower()}('{path}')")
                lines.append(f"        .set('Authorization', 'Bearer expired_token');")
                lines.append(f"      expect(response.status).toBe(401);")
                lines.append(f"    }});")
                lines.append(f"  }});")
                lines.append("")

            # === 数据一致性测试 ===
            if method == "POST":
                lines.append(f"  describe('数据一致性测试', () => {{")
                lines.append(f"    it('创建后数据库中应存在对应记录', async () => {{")
                lines.append(f"      // TODO: 替换 {{}} 中的字段为实际合法创建数据")
                lines.append(f"      const response = await request(app)")
                lines.append(f"        .post('{path}')")
                lines.append(f"        .send({{ /* 合法数据 */ }});")
                lines.append(f"      expect(response.status).toBe(201);")
                lines.append(f"      // TODO: 查询数据库验证记录存在 - 替换 SQL 和字段为实际表名/列名")
                lines.append(f"      // const record = await db.query('SELECT * FROM <表名> WHERE id = ?', [response.body.id]);")
                lines.append(f"      // expect(record).toBeDefined();")
                lines.append(f"    }});")
                lines.append(f"  }});")
                lines.append("")

            # === 错误处理测试 ===
            lines.append(f"  describe('错误处理测试', () => {{")
            if method == "GET":
                lines.append(f"    it('不存在的资源应返回 404', async () => {{")
                lines.append(f"      const response = await request(app)")
                lines.append(f"        .get('{path}/nonexistent_id');")
                lines.append(f"      expect(response.status).toBe(404);")
                lines.append(f"    }});")
            else:
                lines.append(f"    it('服务异常应返回 500', async () => {{")
                lines.append(f"      // TODO: Mock 内部服务抛出异常 - 根据实际依赖的服务设置 Mock")
                lines.append(f"      const response = await request(app)")
                lines.append(f"        .{method.lower()}('{path}')")
                lines.append(f"        .send({{ /* TODO: 替换为触发异常的数据 */ }});")
                lines.append(f"      expect(response.status).toBe(500);")
                lines.append(f"    }});")
            lines.append(f"  }});")
            lines.append("")

            lines.append("});")
            lines.append("")

        try:
            test_file.write_text("\n".join(lines), encoding="utf-8")
            print(f"  已生成: {test_file}")
        except OSError as e:
            print(f"  写入失败: {test_file} - {e}")


def generate_python_tests(integration_points: List[Dict], output_dir: str, project_path: str = "") -> None:
    """
    生成 Python 集成测试代码（pytest + httpx）

    Args:
        integration_points: 集成点列表
        output_dir: 测试文件输出目录
        project_path: 项目根目录
    """
    api_routes = [p for p in integration_points if p.get("category") == "api"]

    if not api_routes:
        print("  未发现 API 路由，跳过 Python 测试生成")
        return

    # 按文件分组
    file_groups: Dict[str, List[Dict]] = {}
    for route in api_routes:
        file_key = route["file"]
        if file_key not in file_groups:
            file_groups[file_key] = []
        file_groups[file_key].append(route)

    for file_path, routes in file_groups.items():
        # 生成测试文件路径
        stem = Path(file_path).stem
        test_file = Path(output_dir) / f"test_{stem}.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)

        # 计算导入路径
        module_path = file_path.replace(".py", "").replace("/", ".")

        lines: List[str] = []
        lines.append(f"# 自动生成的集成测试 - {file_path}")
        lines.append(f"# 测试框架: pytest + httpx")
        lines.append(f"# 注意：以下测试代码为骨架，AI 需根据源码分析结果填充具体测试值和断言")
        lines.append("")
        lines.append(f"import pytest")
        lines.append(f"from httpx import AsyncClient, ASGITransport")
        lines.append(f"# TODO: 根据实际项目调整 app 导入路径")
        lines.append(f"from {module_path} import app")
        lines.append("")

        # Fixtures
        lines.append(f"@pytest.fixture")
        lines.append(f"async def client():")
        lines.append(f"    \"\"\"创建测试客户端\"\"\"")
        lines.append(f"    transport = ASGITransport(app=app)")
        lines.append(f"    async with AsyncClient(transport=transport, base_url='http://test') as ac:")
        lines.append(f"        yield ac")
        lines.append("")
        lines.append(f"@pytest.fixture(autouse=True)")
        lines.append(f"async def setup_db():")
        lines.append(f"    \"\"\"每个测试前重建数据库\"\"\"")
        lines.append(f"    # TODO: 初始化测试数据库")
        lines.append(f"    yield")
        lines.append(f"    # TODO: 清理测试数据库")
        lines.append("")

        # 按路径分组
        path_groups: Dict[str, List[Dict]] = {}
        for route in routes:
            path_key = route["path"]
            if path_key not in path_groups:
                path_groups[path_key] = []
            path_groups[path_key].append(route)

        for path, path_routes in path_groups.items():
            method = path_routes[0]["method"]
            safe_name = path.replace("/", "_").replace(":", "").replace("-", "_").strip("_")
            if not safe_name:
                safe_name = "root"
            auth = path_routes[0].get("auth_required", False)

            lines.append(f"class Test{method}{safe_name.capitalize()}:")
            lines.append(f"    # 路由: {method} {path}")
            if auth:
                lines.append(f"    # 此路由需要认证")
            lines.append("")

            # 正向测试
            lines.append(f"    async def test_success(self, client: AsyncClient):")
            lines.append(f"        \"\"\"正向测试：合法请求应返回正确响应\"\"\"")
            if auth:
                lines.append(f"        # TODO: 获取测试 Token - 根据实际认证机制生成")
                lines.append(f"        # headers = {{'Authorization': 'Bearer test_token'}}")
                lines.append(f"        response = await client.{method.lower()}('{path}', headers=headers, json={{}})")
            else:
                lines.append(f"        # TODO: 替换 {{}} 中的字段为实际合法请求数据")
                lines.append(f"        response = await client.{method.lower()}('{path}', json={{}})")
            lines.append(f"        assert response.status_code == 200")
            lines.append(f"        assert response.json() is not None")
            lines.append(f"        # TODO: 替换为实际业务字段断言，如 assert 'id' in response.json().get('data', {{}})")
            lines.append("")

            # 参数验证
            if method in ("POST", "PUT", "PATCH"):
                lines.append(f"    async def test_missing_required_fields(self, client: AsyncClient):")
                lines.append(f"        \"\"\"参数验证：缺少必填字段应返回 422\"\"\"")
                lines.append(f"        response = await client.{method.lower()}('{path}', json={{}})")
                lines.append(f"        assert response.status_code == 422")
                lines.append(f"        # TODO: 可补充验证错误消息中包含具体字段名")
                lines.append("")

            # 认证测试
            if auth:
                lines.append(f"    async def test_unauthorized(self, client: AsyncClient):")
                lines.append(f"        \"\"\"认证测试：无 Token 应返回 401\"\"\"")
                lines.append(f"        response = await client.{method.lower()}('{path}')")
                lines.append(f"        assert response.status_code == 401")
                lines.append(f"        # TODO: 可补充验证错误消息，如 assert 'Unauthorized' in response.text")
                lines.append("")

            # 404 测试
            if method == "GET":
                lines.append(f"    async def test_not_found(self, client: AsyncClient):")
                lines.append(f"        \"\"\"异常测试：不存在的资源应返回 404\"\"\"")
                lines.append(f"        response = await client.get('{path}/nonexistent')")
                lines.append(f"        assert response.status_code == 404")
                lines.append(f"        # TODO: 可补充验证错误消息，如 assert 'not found' in response.text.lower()")
                lines.append("")

            lines.append("")

        try:
            test_file.write_text("\n".join(lines), encoding="utf-8")
            print(f"  已生成: {test_file}")
        except OSError as e:
            print(f"  写入失败: {test_file} - {e}")


def generate_go_tests(integration_points: List[Dict], output_dir: str, project_path: str = "") -> None:
    """
    生成 Go 集成测试代码（testing + httptest）

    Args:
        integration_points: 集成点列表
        output_dir: 测试文件输出目录
        project_path: 项目根目录
    """
    api_routes = [p for p in integration_points if p.get("category") == "api"]

    if not api_routes:
        print("  未发现 API 路由，跳过 Go 测试生成")
        return

    # 按文件分组
    file_groups: Dict[str, List[Dict]] = {}
    for route in api_routes:
        file_key = route["file"]
        if file_key not in file_groups:
            file_groups[file_key] = []
        file_groups[file_key].append(route)

    for file_path, routes in file_groups.items():
        test_file = Path(output_dir) / file_path.replace(".go", "_test.go")
        test_file.parent.mkdir(parents=True, exist_ok=True)

        # 提取包名
        package = "main"
        try:
            content = ""
            if project_path:
                src_file = Path(project_path) / file_path
                if src_file.exists():
                    content = src_file.read_text(encoding="utf-8", errors="ignore")
            pkg_match = re.search(r"package\s+(\w+)", content)
            if pkg_match:
                package = pkg_match.group(1)
        except Exception:
            pass

        lines: List[str] = []
        lines.append(f"// 自动生成的集成测试 - {file_path}")
        lines.append(f"// 测试框架: Go testing + httptest")
        lines.append(f"// 注意：以下测试代码为骨架，AI 需根据源码分析结果填充具体测试值和断言")
        lines.append("")
        lines.append(f"package {package}")
        lines.append("")
        lines.append(f'import (')
        lines.append(f'    "bytes"')
        lines.append(f'    "encoding/json"')
        lines.append(f'    "net/http"')
        lines.append(f'    "net/http/httptest"')
        lines.append(f'    "testing"')
        lines.append(f'    "github.com/stretchr/testify/assert"')
        lines.append(f'    "github.com/stretchr/testify/require"')
        lines.append(f')')
        lines.append("")

        # 按路径分组
        path_groups: Dict[str, List[Dict]] = {}
        for route in routes:
            path_key = route["path"]
            if path_key not in path_groups:
                path_groups[path_key] = []
            path_groups[path_key].append(route)

        for path, path_routes in path_groups.items():
            method = path_routes[0]["method"]
            safe_name = path.replace("/", "_").replace(":", "").replace("-", "_").strip("_")
            if not safe_name:
                safe_name = "root"
            auth = path_routes[0].get("auth_required", False)

            lines.append(f"func Test{method}{safe_name.capitalize()}_Success(t *testing.T) {{")
            lines.append(f"    // 正向测试: {method} {path}")
            if auth:
                lines.append(f"    // 此路由需要认证")
            lines.append(f"    // TODO: 设置测试服务器和请求")
            lines.append(f"    req, _ := http.NewRequest(\"{method}\", \"{path}\", nil)")
            lines.append(f"    w := httptest.NewRecorder()")
            lines.append(f"    // TODO: 替换 router 为实际路由实例")
            lines.append(f"    router.ServeHTTP(w, req)")
            lines.append(f"    assert.Equal(t, http.StatusOK, w.Code)")
            lines.append(f"    assert.NotNil(t, w.Body)")
            lines.append(f"}}")
            lines.append("")

            if method in ("POST", "PUT", "PATCH"):
                lines.append(f"func Test{method}{safe_name.capitalize()}_MissingFields(t *testing.T) {{")
                lines.append(f"    // 参数验证: 缺少必填字段应返回 400")
                lines.append(f"    // TODO: 发送空请求体 - 替换为实际请求构造代码")
                lines.append(f"    body, _ := json.Marshal(map[string]interface{{}}{{}})")
                lines.append(f"    req, _ := http.NewRequest(\"{method}\", \"{path}\", bytes.NewBuffer(body))")
                lines.append(f"    req.Header.Set(\"Content-Type\", \"application/json\")")
                lines.append(f"    w := httptest.NewRecorder()")
                lines.append(f"    router.ServeHTTP(w, req)")
                lines.append(f"    assert.Equal(t, http.StatusBadRequest, w.Code)")
                lines.append(f"}}")
                lines.append("")

            if auth:
                lines.append(f"func Test{method}{safe_name.capitalize()}_Unauthorized(t *testing.T) {{")
                lines.append(f"    // 认证测试: 无 Token 应返回 401")
                lines.append(f"    // TODO: 发送无认证的请求 - 替换为实际请求构造代码")
                lines.append(f"    req, _ := http.NewRequest(\"{method}\", \"{path}\", nil)")
                lines.append(f"    w := httptest.NewRecorder()")
                lines.append(f"    router.ServeHTTP(w, req)")
                lines.append(f"    assert.Equal(t, http.StatusUnauthorized, w.Code)")
                lines.append(f"}}")
                lines.append("")

        try:
            test_file.write_text("\n".join(lines), encoding="utf-8")
            print(f"  已生成: {test_file}")
        except OSError as e:
            print(f"  写入失败: {test_file} - {e}")


def generate_integration_tests(scan_result_path: str, output_dir: str, project_path: str = "") -> None:
    """
    根据扫描结果生成对应语言的集成测试代码

    Args:
        scan_result_path: 扫描结果 JSON 文件路径
        output_dir: 测试文件输出目录
        project_path: 项目根目录
    """
    # 读取扫描结果（使用 common.py 的 load_json）
    try:
        data = load_json(scan_result_path)
    except FileNotFoundError:
        print(f"错误：扫描结果文件不存在 - {scan_result_path}")
        return
    except json.JSONDecodeError as e:
        print(f"错误：扫描结果 JSON 格式无效 - {e}")
        return

    points = data.get("integration_points", [])
    if not points:
        print("没有集成点")
        return

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    tech_stack = data.get("tech_stack", [])
    print(f"\n技术栈: {', '.join(tech_stack)}")

    # 根据技术栈选择生成器
    if any(t in tech_stack for t in ["express", "koa", "fastify", "nestjs"]):
        generate_nodejs_tests(points, output_dir, project_path)
    elif any(t in tech_stack for t in ["flask", "django", "fastapi", "sqlalchemy"]):
        generate_python_tests(points, output_dir, project_path)
    elif any(t in tech_stack for t in ["gin", "echo", "gorm"]):
        generate_go_tests(points, output_dir, project_path)
    else:
        # 尝试根据文件扩展名推断
        print("  无法确定技术栈，尝试根据文件类型生成...")
        if project_path and list(Path(project_path).rglob("*.py")):
            generate_python_tests(points, output_dir, project_path)
        elif project_path and list(Path(project_path).rglob("*.[jt]s")):
            generate_nodejs_tests(points, output_dir, project_path)
        else:
            print(f"  暂不支持的技术栈: {tech_stack}")

    print(f"\n测试文件已生成到: {output_dir}")
    print(f"\n注意：生成的测试代码为骨架，包含 TODO 占位符")
    print(f"   AI 需要读取源码分析结果，填充具体的测试值和断言")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python generate_integration_tests.py <扫描结果JSON> <输出目录> [项目路径]")
        print("示例: python generate_integration_tests.py scan_result.json ./tests/ /path/to/project")
        sys.exit(1)

    project = sys.argv[3] if len(sys.argv) >= 4 else ""
    generate_integration_tests(sys.argv[1], sys.argv[2], project)
