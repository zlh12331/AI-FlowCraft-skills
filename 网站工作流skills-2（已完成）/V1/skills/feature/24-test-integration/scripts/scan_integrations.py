#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试辅助脚本 - 集成点扫描器
功能：扫描项目中的 API 路由、数据库模型、中间件、服务连接等集成点
用法：python scan_integrations.py <项目路径> [输出JSON路径]
"""

import sys
import re
from pathlib import Path
from typing import Dict, List
from itertools import chain

from common import detect_tech_stack, save_json, validate_project_path


def _iter_js_ts_files(project_path: Path) -> list:
    """遍历项目中的 .js/.jsx/.ts/.tsx 文件（排除 .d.ts）"""
    return chain(
        project_path.rglob("*.js"),
        project_path.rglob("*.jsx"),
        project_path.rglob("*.ts"),
        project_path.rglob("*.tsx"),
    )


def scan_project(project_path: str) -> Dict:
    """
    扫描项目目录，识别技术栈和集成点

    Args:
        project_path: 项目根目录路径

    Returns:
        dict: 项目信息和集成点列表
    """
    try:
        project_path = validate_project_path(project_path)
    except ValueError as e:
        print(f"错误：{e}")
        return {}

    # 识别技术栈（使用 common.py 中的统一实现）
    tech_stack = detect_tech_stack(project_path)
    print(f"技术栈: {', '.join(tech_stack)}")

    # 扫描各类集成点
    api_routes: List[Dict] = []
    db_models: List[Dict] = []
    middleware: List[Dict] = []
    external_services: List[Dict] = []

    # API 路由
    if any(t in tech_stack for t in ["express", "koa", "fastify", "nestjs", "flask", "django", "fastapi", "gin", "echo", "spring"]):
        api_routes = scan_api_routes(project_path, tech_stack)

    # 数据库模型
    if any(t in tech_stack for t in ["prisma", "sequelize", "mongoose", "sqlalchemy", "django-orm", "gorm", "jpa", "mybatis"]):
        db_models = scan_db_models(project_path, tech_stack)

    # 中间件
    middleware = scan_middleware(project_path, tech_stack)

    # 外部服务调用
    external_services = scan_external_services(project_path, tech_stack)

    # 合并所有集成点
    all_points: List[Dict] = []
    for point in api_routes:
        point["category"] = "api"
        all_points.append(point)
    for point in db_models:
        point["category"] = "database"
        all_points.append(point)
    for point in middleware:
        point["category"] = "middleware"
        all_points.append(point)
    for point in external_services:
        point["category"] = "external_service"
        all_points.append(point)

    result = {
        "tech_stack": tech_stack,
        "api_routes_count": len(api_routes),
        "db_models_count": len(db_models),
        "middleware_count": len(middleware),
        "external_services_count": len(external_services),
        "total_integration_points": len(all_points),
        "integration_points": all_points
    }

    # 输出结果
    print(f"\n扫描结果:")
    print(f"  API 路由: {len(api_routes)}")
    print(f"  数据库模型: {len(db_models)}")
    print(f"  中间件: {len(middleware)}")
    print(f"  外部服务: {len(external_services)}")
    print(f"  总集成点: {len(all_points)}")

    if api_routes:
        print(f"\nAPI 路由列表:")
        for route in api_routes[:20]:
            print(f"  {route['method']:6s} {route['path']} ({route['file']}:{route['line']})")
        if len(api_routes) > 20:
            print(f"  ... 还有 {len(api_routes) - 20} 个路由")

    if db_models:
        print(f"\n数据库模型列表:")
        for model in db_models[:15]:
            print(f"  {model['name']} ({model['file']}:{model['line']}) 字段: {model.get('fields', [])[:5]}")
        if len(db_models) > 15:
            print(f"  ... 还有 {len(db_models) - 15} 个模型")

    return result


def scan_api_routes(project_path: Path, tech_stack: List[str]) -> List[Dict]:
    """
    扫描项目中的 API 路由

    Args:
        project_path: 项目根目录
        tech_stack: 技术栈列表

    Returns:
        list: API 路由信息列表
    """
    routes: List[Dict] = []
    skip_dirs = {"node_modules", ".next", "dist", "build", "coverage", ".git", "__pycache__", "venv", ".venv", "target"}

    # === Node.js / Express / NestJS 路由 ===
    if any(t in tech_stack for t in ["express", "koa", "fastify", "nestjs"]):
        for file_path in _iter_js_ts_files(project_path):
            if file_path.suffix == ".d.ts":
                continue
            if any(skip in file_path.parts for skip in skip_dirs):
                continue
            if any(kw in file_path.name for kw in [".test.", ".spec.", "config.", "node_modules"]):
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # Express: app.get('/path', ...)
            # Router: router.post('/path', ...)
            # NestJS: @Get('/path')
            patterns = [
                (r"(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)", "express"),
                (r"@(Get|Post|Put|Delete|Patch)\s*\(\s*['\"]([^'\"]+)", "nestjs"),
            ]

            for line_num, line in enumerate(content.split("\n"), 1):
                for pattern, framework in patterns:
                    match = re.search(pattern, line)
                    if match:
                        method = match.group(1).upper()
                        path = match.group(2)
                        routes.append({
                            "name": f"{method} {path}",
                            "method": method,
                            "path": path,
                            "file": str(file_path.relative_to(project_path)),
                            "line": line_num,
                            "framework": framework,
                            "auth_required": _guess_auth_required(content, line_num),
                        })
                        break

    # === Python / Flask / FastAPI 路由 ===
    if any(t in tech_stack for t in ["flask", "fastapi", "django"]):
        for file_path in project_path.rglob("*.py"):
            if any(skip in file_path.parts for skip in skip_dirs):
                continue
            if "test_" in file_path.name or "_test.py" in file_path.name:
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # Flask: @app.route('/path', methods=['GET', 'POST'])
            # FastAPI: @router.get('/path')
            # Django: path('api/users/', views.user_list)
            patterns = [
                (r"@(?:app|router)\.route\s*\(\s*['\"]([^'\"]+)[^)]*methods\s*=\s*\[([^\]]+)\]", "flask"),
                (r"@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)", "fastapi"),
                (r"path\s*\(\s*['\"]([^'\"]+)", "django"),
            ]

            for line_num, line in enumerate(content.split("\n"), 1):
                for pattern, framework in patterns:
                    match = re.search(pattern, line)
                    if match:
                        if framework == "flask":
                            path = match.group(1)
                            methods_str = match.group(2)
                            methods = re.findall(r"'(GET|POST|PUT|DELETE|PATCH)'", methods_str)
                            for method in methods:
                                routes.append({
                                    "name": f"{method} {path}",
                                    "method": method,
                                    "path": path,
                                    "file": str(file_path.relative_to(project_path)),
                                    "line": line_num,
                                    "framework": framework,
                                    "auth_required": _guess_auth_required(content, line_num),
                                })
                        elif framework == "fastapi":
                            method = match.group(1).upper()
                            path = match.group(2)
                            routes.append({
                                "name": f"{method} {path}",
                                "method": method,
                                "path": path,
                                "file": str(file_path.relative_to(project_path)),
                                "line": line_num,
                                "framework": framework,
                                "auth_required": _guess_auth_required(content, line_num),
                            })
                        elif framework == "django":
                            path = match.group(1)
                            routes.append({
                                "name": f"GET {path}",
                                "method": "GET",
                                "path": path,
                                "file": str(file_path.relative_to(project_path)),
                                "line": line_num,
                                "framework": framework,
                                "auth_required": False,
                            })
                        break

    # === Go / Gin / Echo 路由 ===
    if any(t in tech_stack for t in ["gin", "echo"]):
        for file_path in project_path.rglob("*.go"):
            if any(skip in file_path.parts for skip in skip_dirs):
                continue
            if file_path.name.endswith("_test.go"):
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # Gin: r.GET("/path", handler)
            # Echo: e.GET("/path", handler)
            patterns = [
                r"(?:r|e|group)\.(GET|POST|PUT|DELETE|PATCH)\s*\(\s*['\"]([^'\"]+)",
            ]

            for line_num, line in enumerate(content.split("\n"), 1):
                for pattern in patterns:
                    match = re.search(pattern, line)
                    if match:
                        method = match.group(1)
                        path = match.group(2)
                        routes.append({
                            "name": f"{method} {path}",
                            "method": method,
                            "path": path,
                            "file": str(file_path.relative_to(project_path)),
                            "line": line_num,
                            "framework": "go",
                            "auth_required": _guess_auth_required(content, line_num),
                        })
                        break

    return routes


def _guess_auth_required(content: str, route_line: int) -> bool:
    """
    猜测路由是否需要认证（简单启发式）

    Args:
        content: 文件内容
        route_line: 路由所在行号

    Returns:
        bool: 是否可能需要认证
    """
    # 检查路由附近是否有认证相关装饰器/中间件
    lines = content.split("\n")
    # 检查路由上方 5 行
    start = max(0, route_line - 6)
    context = "\n".join(lines[start:route_line])

    auth_keywords = [
        "requireAuth", "authenticate", "login_required", "permission_required",
        "@UseGuards", "jwt", "authMiddleware", "protected", "@LoginRequired",
    ]
    return any(kw.lower() in context.lower() for kw in auth_keywords)


def scan_db_models(project_path: Path, tech_stack: List[str]) -> List[Dict]:
    """
    扫描项目中的数据库模型

    Args:
        project_path: 项目根目录
        tech_stack: 技术栈列表

    Returns:
        list: 数据库模型信息列表
    """
    models: List[Dict] = []
    skip_dirs = {"node_modules", ".next", "dist", "build", "coverage", ".git", "__pycache__", "venv", ".venv", "target", "migrations"}

    # === Prisma 模型 ===
    if "prisma" in tech_stack:
        schema = project_path / "prisma" / "schema.prisma"
        if schema.exists():
            content = schema.read_text(encoding="utf-8", errors="ignore")
            # 匹配 model Name { ... }
            model_blocks = re.findall(r"model\s+(\w+)\s*\{([^}]+)\}", content)
            for model_name, body in model_blocks:
                fields = re.findall(r"(\w+)\s+\w+", body)
                models.append({
                    "name": model_name,
                    "file": "prisma/schema.prisma",
                    "line": 1,
                    "fields": fields[:10],
                    "orm": "prisma",
                })

    # === Sequelize 模型 ===
    if "sequelize" in tech_stack:
        for file_path in _iter_js_ts_files(project_path):
            if file_path.suffix == ".d.ts":
                continue
            if any(skip in file_path.parts for skip in skip_dirs):
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            # 匹配: modelName.init({ ... })
            match = re.search(r"(\w+)\.init\s*\(\s*\{", content)
            if match:
                model_name = match.group(1)
                # 提取字段
                fields = re.findall(r"(\w+)\s*:\s*DataTypes\.\w+", content)
                models.append({
                    "name": model_name,
                    "file": str(file_path.relative_to(project_path)),
                    "line": match.start(),
                    "fields": fields[:10],
                    "orm": "sequelize",
                })

    # === SQLAlchemy / Django 模型 ===
    if any(t in tech_stack for t in ["sqlalchemy", "django"]):
        for file_path in project_path.rglob("*.py"):
            if any(skip in file_path.parts for skip in skip_dirs):
                continue
            if "test_" in file_path.name:
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # SQLAlchemy: class User(Base):
            # Django: class User(models.Model):
            patterns = [
                r"class\s+(\w+)\s*\(\s*(?:Base|AbstractBaseUser|Model)\s*\)",
                r"class\s+(\w+)\s*\(\s*models\.Model\s*\)",
            ]
            for line_num, line in enumerate(content.split("\n"), 1):
                for pattern in patterns:
                    match = re.search(pattern, line)
                    if match:
                        model_name = match.group(1)
                        # 提取字段（Column / models.CharField 等）
                        fields = re.findall(r"(\w+)\s*=\s*(?:Column|models\.\w+)", content)
                        models.append({
                            "name": model_name,
                            "file": str(file_path.relative_to(project_path)),
                            "line": line_num,
                            "fields": fields[:10],
                            "orm": "sqlalchemy" if "Base" in line else "django",
                        })
                        break

    # === GORM 模型 ===
    if "gorm" in tech_stack:
        for file_path in project_path.rglob("*.go"):
            if any(skip in file_path.parts for skip in skip_dirs):
                continue
            if file_path.name.endswith("_test.go"):
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            # 匹配: type User struct { ... }
            struct_matches = re.findall(r"type\s+(\w+)\s+struct\s*\{([^}]+)\}", content)
            for struct_name, body in struct_matches:
                # 只取包含 gorm 标签的结构体
                if "gorm:" in body:
                    fields = re.findall(r"(\w+)\s+\w+", body)
                    models.append({
                        "name": struct_name,
                        "file": str(file_path.relative_to(project_path)),
                        "line": 1,
                        "fields": fields[:10],
                        "orm": "gorm",
                    })

    return models


def scan_middleware(project_path: Path, tech_stack: List[str]) -> List[Dict]:
    """
    扫描项目中的中间件

    Args:
        project_path: 项目根目录
        tech_stack: 技术栈列表

    Returns:
        list: 中间件信息列表
    """
    middleware_list: List[Dict] = []
    skip_dirs = {"node_modules", ".next", "dist", "build", "coverage", ".git", "__pycache__", "venv"}

    # 搜索中间件关键词
    middleware_keywords = [
        "auth", "cors", "logger", "errorHandler", "rateLimit", "validate",
        "compress", "helmet", "csrf", "session", "cookie", "bodyParser",
    ]

    # Node.js 中间件
    if any(t in tech_stack for t in ["express", "koa", "fastify", "nestjs"]):
        for file_path in _iter_js_ts_files(project_path):
            if file_path.suffix == ".d.ts":
                continue
            if any(skip in file_path.parts for skip in skip_dirs):
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # app.use(authMiddleware)
            matches = re.findall(r"(?:app|router)\.use\s*\(\s*(\w+)", content)
            for match in matches:
                if any(kw.lower() in match.lower() for kw in middleware_keywords):
                    middleware_list.append({
                        "name": match,
                        "file": str(file_path.relative_to(project_path)),
                        "line": 1,
                        "type": "node-middleware",
                    })

    # Python 中间件
    if any(t in tech_stack for t in ["flask", "django", "fastapi"]):
        for file_path in project_path.rglob("*.py"):
            if any(skip in file_path.parts for skip in skip_dirs):
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # @app.middleware("http")
            # MIDDLEWARE = [...]
            if "@app.middleware" in content or "MIDDLEWARE" in content:
                for kw in middleware_keywords:
                    if kw.lower() in content.lower():
                        middleware_list.append({
                            "name": kw,
                            "file": str(file_path.relative_to(project_path)),
                            "line": 1,
                            "type": "python-middleware",
                        })
                        break

    return middleware_list


def scan_external_services(project_path: Path, tech_stack: List[str]) -> List[Dict]:
    """
    扫描项目中的外部服务调用

    Args:
        project_path: 项目根目录
        tech_stack: 技术栈列表

    Returns:
        list: 外部服务信息列表
    """
    services: List[Dict] = []
    skip_dirs = {"node_modules", ".next", "dist", "build", "coverage", ".git", "__pycache__", "venv"}

    # 外部服务关键词
    service_patterns = {
        "axios": r"axios\.(get|post|put|delete)\s*\(\s*['\"]([^'\"]+)",
        "fetch": r"fetch\s*\(\s*['\"]([^'\"]+)",
        "requests": r"requests\.(get|post|put|delete)\s*\(\s*['\"]([^'\"]+)",
        "httpx": r"(?:client|httpx)\.(get|post|put|delete)\s*\(\s*['\"]([^'\"]+)",
        "redis": r"redis\.(get|set|hset|expire|del)",
        "s3": r"s3\.(upload|download|getObject|putObject)",
        "email": r"(?:sendMail|send_email|smtp|nodemailer)",
        "sms": r"(?:sendSms|send_sms|twilio)",
        "payment": r"(?:stripe|paypal|alipay|wechatpay)",
    }

    # 扫描 Node.js 文件
    for file_path in _iter_js_ts_files(project_path):
        if file_path.suffix == ".d.ts":
            continue
        if any(skip in file_path.parts for skip in skip_dirs):
            continue
        if any(kw in file_path.name for kw in [".test.", ".spec.", "config."]):
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for service_name, pattern in service_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                # 提取 URL（如果有）
                urls: List[str] = []
                for match in matches:
                    if isinstance(match, tuple) and len(match) > 1:
                        urls.append(match[1])
                services.append({
                    "name": service_name,
                    "file": str(file_path.relative_to(project_path)),
                    "line": 1,
                    "urls": urls[:3],
                    "type": "external-service",
                })

    # 扫描 Python 文件
    for file_path in project_path.rglob("*.py"):
        if any(skip in file_path.parts for skip in skip_dirs):
            continue
        if "test_" in file_path.name:
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for service_name, pattern in service_patterns.items():
            if service_name in ["axios", "fetch"]:
                continue  # 跳过 Node.js 专用的
            matches = re.findall(pattern, content)
            if matches:
                urls: List[str] = []
                for match in matches:
                    if isinstance(match, tuple) and len(match) > 1:
                        urls.append(match[1])
                services.append({
                    "name": service_name,
                    "file": str(file_path.relative_to(project_path)),
                    "line": 1,
                    "urls": urls[:3],
                    "type": "external-service",
                })

    # 去重（同一文件中同一服务只保留一个）
    seen: set = set()
    unique_services: List[Dict] = []
    for svc in services:
        key = f"{svc['name']}:{svc['file']}"
        if key not in seen:
            seen.add(key)
            unique_services.append(svc)

    return unique_services


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scan_integrations.py <项目路径> [输出JSON路径]")
        print("示例: python scan_integrations.py /path/to/project result.json")
        sys.exit(1)

    project = sys.argv[1]
    result = scan_project(project)

    if result and len(sys.argv) >= 3:
        save_json(result, sys.argv[2])
        print(f"\n扫描结果已导出到: {sys.argv[2]}")
