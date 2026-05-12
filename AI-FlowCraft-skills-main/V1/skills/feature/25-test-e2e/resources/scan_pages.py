#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E 测试辅助脚本 - 页面扫描器
功能：扫描前端项目，识别可测试的页面路由、表单页面、认证页面
用法：python scan_pages.py <项目路径> [输出JSON路径]
"""

import os
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import detect_framework, save_json


def scan_project(project_path: str) -> dict:
    """
    扫描项目目录，识别前端框架和可测试的页面

    Args:
        project_path: 项目根目录路径

    Returns:
        dict: 项目信息和页面列表；路径不存在时返回空字典
    """
    project_path = Path(project_path)
    if not project_path.exists():
        print(f"错误：路径不存在 - {project_path}")
        return {}

    # 识别前端框架
    framework = detect_framework(project_path)
    print(f"前端框架: {framework}")

    # 扫描页面路由
    pages: List[Dict[str, Any]] = []
    if framework in ("react", "nextjs"):
        pages = scan_nextjs_pages(project_path) if framework == "nextjs" else scan_react_pages(project_path)
    elif framework in ("vue", "nuxtjs"):
        pages = scan_vue_pages(project_path)
    elif framework == "angular":
        pages = scan_angular_pages(project_path)

    # 分析每个页面
    analyzed: List[Dict[str, Any]] = []
    for page in pages:
        file_full_path = project_path / page["file"]
        if file_full_path.exists():
            analysis = analyze_page(file_full_path, page, framework)
            page.update(analysis)
        analyzed.append(page)

    # 推断用户流程
    flows = infer_user_flows(analyzed)

    result: Dict[str, Any] = {
        "framework": framework,
        "total_pages": len(pages),
        "pages": analyzed,
        "user_flows": flows,
    }

    # 输出结果
    print(f"\n扫描结果:")
    print(f"  页面总数: {len(pages)}")
    print(f"  用户流程: {len(flows)}")
    print(f"\n页面列表:")
    for page in analyzed:
        page_type = page.get("page_type", "普通页面")
        has_form = "📝" if page.get("has_form") else ""
        needs_auth = "🔒" if page.get("needs_auth") else ""
        print(f"  {has_form}{needs_auth} {page['route']} ({page['file']}) [{page_type}]")

    if flows:
        print(f"\n推荐的用户流程:")
        for flow in flows:
            print(f"  🔄 {flow['name']}: {' → '.join(flow['steps'])}")

    return result


def scan_nextjs_pages(project_path: Path) -> list:
    """
    扫描 Next.js 项目中的页面路由（支持 App Router 和 Pages Router）

    Args:
        project_path: 项目根目录

    Returns:
        list: 页面信息列表
    """
    pages: List[Dict[str, Any]] = []
    skip_dirs = {"node_modules", ".next", "dist", "build", "coverage", ".git", "api", "components", "lib", "utils", "hooks"}

    # App Router: app/ 或 src/app/ 目录
    app_dir = project_path / "app"
    src_app_dir = project_path / "src" / "app"
    for base_dir in [app_dir, src_app_dir]:
        if base_dir.exists():
            for file_path in base_dir.rglob("page.tsx"):
                if any(skip in file_path.parts for skip in skip_dirs):
                    continue

                # 从文件路径推导路由（使用 base_dir 作为基准，兼容 app/ 和 src/app/）
                rel = file_path.relative_to(base_dir)
                # app/(auth)/login/page.tsx → /login（路由组括号忽略）
                parts = list(rel.parts)
                parts = [p for p in parts if not p.startswith("(") and p != "page.tsx"]
                route = "/" + "/".join(parts).replace("page.tsx", "").strip("/")
                if route == "/":
                    route = "/"

                pages.append({
                    "route": route,
                    "file": str(file_path.relative_to(project_path)),
                    "line": 1,
                    "router_type": "app-router",
                })

    # Pages Router: pages/ 或 src/pages/ 目录
    pages_dir = project_path / "pages"
    src_pages_dir = project_path / "src" / "pages"
    for base_dir in [pages_dir, src_pages_dir]:
        if base_dir.exists():
            for file_path in base_dir.rglob("*.[jt]sx*"):
                if any(skip in file_path.parts for skip in skip_dirs):
                    continue
                if file_path.name.startswith("_"):
                    continue

                rel = file_path.relative_to(base_dir)
                # pages/index.tsx → /
                # pages/blog/[id].tsx → /blog/:id
                route = "/" + str(rel.with_suffix("")).replace("index", "").strip("/")
                # 动态路由 [param] → :param
                route = re.sub(r"\[([^\]]+)\]", r":\1", route)
                if route == "/":
                    route = "/"

                pages.append({
                    "route": route,
                    "file": str(file_path.relative_to(project_path)),
                    "line": 1,
                    "router_type": "pages-router",
                })

    return pages


def scan_react_pages(project_path: Path) -> list:
    """
    扫描 React SPA 项目中的页面路由（从 React Router 配置提取）

    Args:
        project_path: 项目根目录

    Returns:
        list: 页面信息列表
    """
    pages: List[Dict[str, Any]] = []
    skip_dirs = {"node_modules", "dist", "build", "coverage", ".git"}

    # 从路由配置文件提取
    for file_path in project_path.rglob("*.[jt]sx*"):
        if any(skip in file_path.parts for skip in skip_dirs):
            continue
        if any(kw in file_path.name for kw in ["route", "router", "app", "App"]):
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            # 匹配 React Router 路由定义
            # <Route path="/login" element={<LoginPage />} />
            # createBrowserRouter([{ path: "/login", element: <LoginPage /> }])
            patterns = [
                r'<Route\s+path=["\']([^"\']+)["\']',
                r'path:\s*["\']([^"\']+)["\']',
            ]

            for line_num, line in enumerate(content.split("\n"), 1):
                for pattern in patterns:
                    match = re.search(pattern, line)
                    if match:
                        route = match.group(1)
                        if not route.startswith("/") or route == "*":
                            continue
                        pages.append({
                            "route": route,
                            "file": str(file_path.relative_to(project_path)),
                            "line": line_num,
                            "router_type": "react-router",
                        })
                        break

    return pages


def scan_vue_pages(project_path: Path) -> list:
    """
    扫描 Vue 项目中的页面路由（从 router 配置提取）

    Args:
        project_path: 项目根目录

    Returns:
        list: 页面信息列表
    """
    pages: List[Dict[str, Any]] = []
    skip_dirs = {"node_modules", ".nuxt", "dist", "build", "coverage", ".git"}

    # Nuxt.js: pages/ 目录自动路由
    pages_dir = project_path / "pages"
    if pages_dir.exists():
        for file_path in pages_dir.rglob("*.vue"):
            if any(skip in file_path.parts for skip in skip_dirs):
                continue
            if file_path.name.startswith("_"):
                continue

            rel = file_path.relative_to(pages_dir)
            # pages/index.vue → /
            # pages/blog/[id].vue → /blog/:id
            route = "/" + str(rel.with_suffix("")).replace("index", "").strip("/")
            route = re.sub(r"\[([^\]]+)\]", r":\1", route)
            if route == "/":
                route = "/"

            pages.append({
                "route": route,
                "file": str(file_path.relative_to(project_path)),
                "line": 1,
                "router_type": "nuxt-auto",
            })

    # Vue Router 配置文件
    for file_path in project_path.rglob("router/*.[jt]s"):
        if any(skip in file_path.parts for skip in skip_dirs):
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # 匹配 Vue Router 路由定义
        # path: '/login', component: () => import('@/views/Login.vue')
        patterns = [
            r"path:\s*['\"]([^'\"]+)['\"]",
            r"route\s*\(\s*['\"]([^'\"]+)['\"]",
        ]

        for line_num, line in enumerate(content.split("\n"), 1):
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    route = match.group(1)
                    if not route.startswith("/"):
                        continue
                    pages.append({
                        "route": route,
                        "file": str(file_path.relative_to(project_path)),
                        "line": line_num,
                        "router_type": "vue-router",
                    })
                    break

    return pages


def scan_angular_pages(project_path: Path) -> list:
    """
    扫描 Angular 项目中的页面路由（从路由模块提取）

    Args:
        project_path: 项目根目录

    Returns:
        list: 页面信息列表
    """
    pages: List[Dict[str, Any]] = []
    skip_dirs = {"node_modules", "dist", "build", "coverage", ".git"}

    for file_path in project_path.rglob("*-routing.module.ts"):
        if any(skip in file_path.parts for skip in skip_dirs):
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # 匹配 Angular 路由定义
        # { path: 'login', component: LoginComponent }
        patterns = [
            r"path:\s*['\"]([^'\"]+)['\"]",
        ]

        for line_num, line in enumerate(content.split("\n"), 1):
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    route = match.group(1)
                    if route.startswith("**"):
                        continue
                    if not route.startswith("/"):
                        route = "/" + route
                    pages.append({
                        "route": route,
                        "file": str(file_path.relative_to(project_path)),
                        "line": line_num,
                        "router_type": "angular-router",
                    })
                    break

    return pages


def analyze_page(file_path: Path, page_info: dict, framework: str) -> dict:
    """
    分析页面源码，识别表单、认证需求、页面类型

    Args:
        file_path: 页面文件路径
        page_info: 已有的页面信息
        framework: 前端框架

    Returns:
        dict: 补充的分析结果；读取失败时返回空字典
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}

    analysis: Dict[str, Any] = {}

    # 检测表单元素
    form_indicators = [
        r"<form", r"<input", r"<textarea", r"<select",
        r"type=['\"](text|email|password|number|checkbox|radio)",
        r"getByLabel\(", r"getByPlaceholder\(",
        r"getByRole\(['\"]textbox",
        r"v-model", r":model-value",
        r"onChange", r"onSubmit", r"handleSubmit",
    ]
    form_count = sum(len(re.findall(p, content, re.IGNORECASE)) for p in form_indicators)
    analysis["has_form"] = form_count >= 2
    analysis["form_elements"] = min(form_count, 20)

    # 检测按钮
    button_count = len(re.findall(r"<button|getByRole\(['\"]button", content, re.IGNORECASE))
    analysis["buttons"] = button_count

    # 检测链接
    link_count = len(re.findall(r"<a\s+href|<Link\s+to|<RouterLink|getByRole\(['\"]link", content, re.IGNORECASE))
    analysis["links"] = link_count

    # 检测认证需求
    auth_keywords = [
        "useSession", "getSession", "getServerSession",
        "useAuth", "withAuth", "requireAuth", "protected",
        "useUser", "currentUser", "isAuthenticated",
        "middleware", "redirect.*login", "useRouter.*push.*login",
    ]
    auth_score = sum(1 for kw in auth_keywords if kw.lower() in content.lower())
    analysis["needs_auth"] = auth_score >= 1
    analysis["auth_score"] = auth_score

    # 推断页面类型
    route = page_info.get("route", "").lower()
    if any(kw in route for kw in ["login", "signin", "sign-in"]):
        analysis["page_type"] = "登录页"
    elif any(kw in route for kw in ["register", "signup", "sign-up"]):
        analysis["page_type"] = "注册页"
    elif any(kw in route for kw in ["dashboard", "admin", "profile", "account", "settings"]):
        analysis["page_type"] = "用户中心"
    elif any(kw in route for kw in ["search", "filter"]):
        analysis["page_type"] = "搜索页"
    elif any(kw in route for kw in ["cart", "checkout", "payment", "order"]):
        analysis["page_type"] = "交易页"
    elif analysis["has_form"]:
        analysis["page_type"] = "表单页"
    elif analysis["needs_auth"]:
        analysis["page_type"] = "认证页"
    else:
        analysis["page_type"] = "普通页面"

    return analysis


def infer_user_flows(pages: list) -> list:
    """
    根据页面列表推断推荐的用户流程

    Args:
        pages: 页面列表

    Returns:
        list: 用户流程列表
    """
    flows: List[Dict[str, Any]] = []

    # 登录流程
    login_pages = [p for p in pages if p.get("page_type") == "登录页"]
    if login_pages:
        flows.append({
            "name": "登录流程",
            "priority": "P0",
            "steps": [login_pages[0]["route"], "/dashboard", "/"],
            "description": "打开登录页 → 输入凭据 → 提交 → 验证跳转到首页/仪表盘",
        })

    # 注册流程
    register_pages = [p for p in pages if p.get("page_type") == "注册页"]
    if register_pages:
        flows.append({
            "name": "注册流程",
            "priority": "P0",
            "steps": [register_pages[0]["route"]],
            "description": "打开注册页 → 填写信息 → 提交 → 验证注册成功",
        })

    # 搜索流程
    search_pages = [p for p in pages if p.get("page_type") == "搜索页"]
    if search_pages:
        flows.append({
            "name": "搜索流程",
            "priority": "P1",
            "steps": ["/", search_pages[0]["route"]],
            "description": "首页 → 输入搜索关键词 → 查看搜索结果",
        })

    # 表单提交流程
    form_pages = [p for p in pages if p.get("has_form") and p.get("page_type") not in ("登录页", "注册页")]
    for fp in form_pages[:3]:
        flows.append({
            "name": f"表单提交: {fp['route']}",
            "priority": "P1",
            "steps": [fp["route"]],
            "description": f"打开 {fp['route']} → 填写表单 → 提交 → 验证结果",
        })

    # 认证页面访问流程
    auth_pages = [p for p in pages if p.get("needs_auth") and p.get("page_type") not in ("登录页", "注册页")]
    if auth_pages and login_pages:
        flows.append({
            "name": "认证保护流程",
            "priority": "P1",
            "steps": [auth_pages[0]["route"], login_pages[0]["route"]],
            "description": f"未登录访问 {auth_pages[0]['route']} → 应重定向到登录页",
        })

    # 导航流程
    if len(pages) >= 3:
        public_pages = [p for p in pages if not p.get("needs_auth")][:5]
        if len(public_pages) >= 2:
            flows.append({
                "name": "页面导航流程",
                "priority": "P2",
                "steps": [p["route"] for p in public_pages],
                "description": "依次访问各公开页面，验证导航和页面加载正常",
            })

    return flows


def export_json(result: dict, output_path: str) -> None:
    """
    将扫描结果导出为 JSON 文件

    Args:
        result: 扫描结果字典
        output_path: 输出文件路径
    """
    save_json(result, output_path)
    print(f"\n扫描结果已导出到: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scan_pages.py <项目路径> [输出JSON路径]")
        print("示例: python scan_pages.py /path/to/project result.json")
        sys.exit(1)

    project = sys.argv[1]
    result = scan_project(project)

    if result and len(sys.argv) >= 3:
        export_json(result, sys.argv[2])
