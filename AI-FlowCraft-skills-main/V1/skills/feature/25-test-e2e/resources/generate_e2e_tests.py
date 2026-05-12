#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E 测试辅助脚本 - 测试代码生成器
功能：根据扫描结果，自动生成 Playwright E2E 测试代码骨架
用法：python generate_e2e_tests.py <扫描结果JSON> <输出目录>
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

from common import load_json


def generate_playwright_tests(scan_result: dict, output_dir: str) -> None:
    """
    生成 Playwright E2E 测试代码

    Args:
        scan_result: 扫描结果字典
        output_dir: 测试文件输出目录
    """
    pages: List[Dict[str, Any]] = scan_result.get("pages", [])
    flows: List[Dict[str, Any]] = scan_result.get("user_flows", [])
    framework: str = scan_result.get("framework", "unknown")

    if not pages and not flows:
        print("没有可测试的页面或用户流程")
        return

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    print(f"\n生成 Playwright E2E 测试代码...")

    # === 为每个用户流程生成测试文件 ===
    for flow in flows:
        flow_name: str = flow["name"]
        # 文件名：安全化处理
        safe_name = flow_name.replace(" ", "_").replace(":", "").replace("/", "_").replace("-", "_")
        test_file = Path(output_dir) / f"{safe_name}.spec.ts"

        lines: List[str] = []
        lines.append(f"// 自动生成的 E2E 测试 - {flow_name}")
        lines.append(f"// 测试框架: Playwright")
        lines.append(f"// 前端框架: {framework}")
        lines.append(f"// 注意：以下测试代码为骨架，AI 需根据页面源码分析结果填充具体操作步骤和断言")
        lines.append("")
        lines.append(f"import {{ test, expect }} from '@playwright/test';")
        lines.append("")

        # describe 块
        lines.append(f"test.describe('{flow_name}', () => {{")
        lines.append(f"  // 流程说明: {flow.get('description', '')}")
        lines.append(f"  // 优先级: {flow.get('priority', 'P2')}")
        lines.append(f"  // 涉及页面: {', '.join(flow.get('steps', []))}")
        lines.append("")

        steps: List[str] = flow.get("steps", [])

        # === 正向流程测试 ===
        lines.append(f"  test('完整流程应正常完成', async ({{ page }}) => {{")
        for i, step in enumerate(steps):
            lines.append(f"    // 步骤 {i+1}: 访问 {step}")
            lines.append(f"    await page.goto('{step}');")
            lines.append(f"    // 验证页面加载成功（标题非空即表示页面已渲染）")
            lines.append(f"    await expect(page).toHaveTitle(/.+/);")
            lines.append("")
        lines.append(f"    // TODO: 执行流程中的关键操作（填写表单、点击按钮等）")
        lines.append(f"    // TODO: 验证最终结果 - 根据实际业务流程断言最终页面状态")
        lines.append(f"  }});")
        lines.append("")

        # === 表单验证测试（如果涉及表单页面） ===
        form_pages_in_flow: List[Dict[str, Any]] = []
        for step in steps:
            for p in pages:
                if p.get("route") == step and p.get("has_form"):
                    form_pages_in_flow.append(p)
                    break

        if form_pages_in_flow:
            fp = form_pages_in_flow[0]
            lines.append(f"  test('表单验证：空提交应显示错误提示', async ({{ page }}) => {{")
            lines.append(f"    await page.goto('{fp['route']}');")
            lines.append(f"    // TODO: 替换 '提交' 为实际的提交按钮文本或 role")
            lines.append(f"    await page.getByRole('button', {{ name: '提交' }}).click();")
            lines.append(f"    // 验证页面显示错误提示（任意可见的错误/必填提示文本）")
            lines.append(f"    await expect(page.getByText(/必填|不能为空|请填写|required/i)).toBeVisible();")
            lines.append(f"  }});")
            lines.append("")

            lines.append(f"  test('表单验证：格式错误应显示提示', async ({{ page }}) => {{")
            lines.append(f"    await page.goto('{fp['route']}');")
            lines.append(f"    // TODO: 替换 '邮箱' 为实际的表单字段 label，'invalid-email' 为对应格式的错误值")
            lines.append(f"    await page.getByLabel('邮箱').fill('invalid-email');")
            lines.append(f"    await page.getByRole('button', {{ name: '提交' }}).click();")
            lines.append(f"    // 验证页面显示格式错误提示")
            lines.append(f"    await expect(page.getByText(/格式|无效|不正确|invalid/i)).toBeVisible();")
            lines.append(f"  }});")
            lines.append("")

        # === 认证保护测试 ===
        auth_pages_in_flow: List[Dict[str, Any]] = []
        for step in steps:
            for p in pages:
                if p.get("route") == step and p.get("needs_auth"):
                    auth_pages_in_flow.append(p)
                    break

        if auth_pages_in_flow:
            ap = auth_pages_in_flow[0]
            lines.append(f"  test('未登录访问受保护页面应重定向', async ({{ page }}) => {{")
            lines.append(f"    await page.goto('{ap['route']}');")
            lines.append(f"    // 验证重定向到登录页（URL 包含 /login 或 /signin）")
            lines.append(f"    await expect(page).toHaveURL(/\\/login|\\/signin/i);")
            lines.append(f"  }});")
            lines.append("")

        # === 响应式测试 ===
        if steps:
            lines.append(f"  test('移动端布局应正确显示', async ({{ page, browserName }}) => {{")
            lines.append(f"    // 跳过非 Chromium 浏览器（移动端模拟仅 Chromium 支持）")
            lines.append(f"    test.skip(browserName !== 'chromium', '移动端模拟仅支持 Chromium');")
            lines.append(f"    await page.setViewportSize({{ width: 375, height: 667 }});")
            lines.append(f"    await page.goto('{steps[0]}');")
            lines.append(f"    // 验证页面在移动端视口下仍能正常渲染")
            lines.append(f"    await expect(page).toHaveTitle(/.+/);")
            lines.append(f"    // TODO: 替换为实际的移动端关键元素选择器")
            lines.append(f"    // await expect(page.locator('header, nav, [role=\"navigation\"]')).toBeVisible();")
            lines.append(f"  }});")
            lines.append("")

        lines.append("});")
        lines.append("")

        test_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"  已生成: {test_file}")

    # === 为没有包含在流程中的表单页面补充测试 ===
    flow_routes: set = set()
    for flow in flows:
        for step in flow.get("steps", []):
            flow_routes.add(step)

    standalone_form_pages = [
        p for p in pages
        if p.get("has_form") and p.get("route") not in flow_routes
    ]

    if standalone_form_pages:
        test_file = Path(output_dir) / "standalone_forms.spec.ts"
        lines = []
        lines.append(f"// 自动生成的 E2E 测试 - 独立表单页面")
        lines.append(f"// 测试框架: Playwright")
        lines.append("")
        lines.append(f"import {{ test, expect }} from '@playwright/test';")
        lines.append("")

        for page in standalone_form_pages[:10]:
            route = page["route"]
            page_type = page.get("page_type", "表单页")
            lines.append(f"test.describe('{page_type}: {route}', () => {{")
            lines.append(f"  test('页面应正确加载并显示表单', async ({{ page }}) => {{")
            lines.append(f"    await page.goto('{route}');")
            lines.append(f"    // 验证页面加载成功")
            lines.append(f"    await expect(page).toHaveTitle(/.+/);")
            lines.append(f"    // TODO: 替换为实际的表单选择器（如 data-testid、form action 等）")
            lines.append(f"    // await expect(page.locator('form')).toBeVisible();")
            lines.append(f"  }});")
            lines.append("")
            lines.append(f"  test('填写并提交表单应成功', async ({{ page }}) => {{")
            lines.append(f"    await page.goto('{route}');")
            lines.append(f"    // TODO: 填写表单字段 - 根据实际表单字段替换选择器和值")
            lines.append(f"    // TODO: 点击提交 - 替换为实际的提交按钮选择器")
            lines.append(f"    // TODO: 验证提交结果 - 根据实际业务逻辑断言（成功提示、页面跳转等）")
            lines.append(f"  }});")
            lines.append("")
            lines.append("});")
            lines.append("")

        test_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"  已生成: {test_file}")

    print(f"\n测试文件已生成到: {output_dir}")
    print(f"\n⚠️  注意：生成的测试代码为骨架，包含 TODO 占位符")
    print(f"   AI 需要读取页面源码分析结果，填充具体的操作步骤和断言")


def generate_e2e_tests(scan_result_path: str, output_dir: str) -> None:
    """
    根据扫描结果生成 E2E 测试代码

    Args:
        scan_result_path: 扫描结果 JSON 文件路径
        output_dir: 测试文件输出目录

    Raises:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON 格式错误
        IOError: IO 错误
    """
    data = load_json(scan_result_path)
    generate_playwright_tests(data, output_dir)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python generate_e2e_tests.py <扫描结果JSON> <输出目录>")
        print("示例: python generate_e2e_tests.py scan_result.json ./e2e/")
        sys.exit(1)

    generate_e2e_tests(sys.argv[1], sys.argv[2])
