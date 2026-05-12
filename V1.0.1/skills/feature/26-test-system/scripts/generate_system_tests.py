#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试辅助脚本 - 测试代码生成器
功能：根据扫描结果生成系统测试代码骨架（功能+性能+安全）
用法：python generate_system_tests.py <扫描结果JSON> <输出目录>
"""

import sys
from pathlib import Path
from typing import List, Dict, Any

from common import load_json


def generate_system_tests(scan_result: dict, output_dir: str):
    """
    根据扫描结果生成系统测试代码骨架

    Args:
        scan_result: 扫描结果字典
        output_dir: 测试文件输出目录
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    components = scan_result.get("components", [])
    services = [c for c in components if c.get("category") == "service"]
    databases = [c for c in components if c.get("category") == "database"]
    externals = [c for c in components if c.get("category") == "external"]
    security = scan_result.get("security_findings", [])

    print(f"\n生成系统测试代码...")

    # === 1. 功能性系统测试 ===
    _generate_functional_tests(services, databases, externals, output_dir)

    # === 2. 性能测试 ===
    _generate_performance_tests(services, output_dir)

    # === 3. 安全测试 ===
    _generate_security_tests(security, output_dir)

    # === 4. 健康检查测试 ===
    _generate_health_check_tests(services, output_dir)

    # === 5. 兼容性测试 ===
    _generate_compatibility_tests(services, output_dir)

    # === 6. 数据备份恢复测试 ===
    _generate_backup_recovery_tests(databases, output_dir)

    print(f"\n测试文件已生成到: {output_dir}")
    print(f"\n注意：生成的测试代码为骨架，AI 需根据架构分析结果填充具体值")


def _generate_functional_tests(services: List[Dict[str, Any]], databases: List[Dict[str, Any]],
                               externals: List[Dict[str, Any]], output_dir: str) -> None:
    """生成功能性系统测试"""
    test_file = Path(output_dir) / "functional" / "system-flows.spec.ts"
    test_file.parent.mkdir(parents=True, exist_ok=True)

    has_frontend = any("frontend" in s.get("type", "") for s in services)
    has_backend = any("backend" in s.get("type", "") for s in services)
    has_db = len(databases) > 0
    has_external = len(externals) > 0

    lines = []
    lines.append("// 自动生成的功能性系统测试")
    lines.append("// 测试框架: Playwright")
    lines.append("// 注意：以下测试代码为骨架，AI 需根据架构分析结果填充具体操作步骤")
    lines.append("")
    lines.append("import { test, expect } from '@playwright/test';")
    lines.append("")

    lines.append("test.describe('系统测试：核心业务全链路', () => {")
    lines.append("  test.beforeEach(async ({ page }) => {")
    lines.append("    // TODO: 设置测试环境（登录测试账号等）")
    lines.append("  });")
    lines.append("")

    # 全链路测试
    lines.append("  test('完整业务流程应端到端成功', async ({ page }) => {")
    if has_frontend and has_backend:
        lines.append("    // 步骤 1：访问前端页面")
        lines.append("    await page.goto('/');")
        lines.append("    await expect(page).toHaveTitle(/.+/);")
        lines.append("")
        lines.append("    // 步骤 2：执行核心操作（导航、填写、提交）")
        lines.append("    // TODO: 根据实际业务流程填写 - 替换为具体的页面操作步骤")
        lines.append("")
        lines.append("    // 步骤 3：验证后端数据已持久化")
        if has_db:
            lines.append("    // TODO: 调用 API 验证数据库中的数据 - 替换为实际的验证 API 端点")
            lines.append("    // const response = await page.request.get('/api/verify');")
            lines.append("    // expect(response.ok()).toBeTruthy();")
        lines.append("")
        lines.append("    // 步骤 4：验证前端显示与后端数据一致")
        lines.append("    // TODO: 对比页面显示内容和 API 返回数据 - 替换为实际的数据对比逻辑")
    else:
        lines.append("    // TODO: 根据系统架构编写全链路测试")
    lines.append("  });")
    lines.append("")

    # 数据一致性测试
    if has_db:
        lines.append("  test('前端显示应与后端数据一致', async ({ page, request }) => {")
        lines.append("    // TODO: 替换 '/api/data' 为实际的数据 API 端点")
        lines.append("    // const apiData = await request.get('/api/data');")
        lines.append("    // expect(apiData.ok()).toBeTruthy();")
        lines.append("    // TODO: 替换 'data' 为实际的 data-testid 属性值")
        lines.append("    // const pageData = await page.getByTestId('data').textContent();")
        lines.append("    // TODO: 对比两者是否一致 - 根据实际数据结构编写对比逻辑")
        lines.append("  });")
        lines.append("")

    # 外部服务集成测试
    if has_external:
        lines.append("  test('外部服务集成应正常工作', async ({ page }) => {")
        for ext in externals[:3]:
            lines.append(f"    // TODO: 测试 {ext['name']} 集成 - 替换为实际的外部服务调用和响应验证")
        lines.append("  });")
        lines.append("")

    lines.append("});")
    lines.append("")

    test_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"  已生成: {test_file}")


def _generate_performance_tests(services: List[Dict[str, Any]], output_dir: str) -> None:
    """生成性能测试"""
    test_file = Path(output_dir) / "performance" / "load-test.js"
    test_file.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("// 自动生成的性能测试")
    lines.append("// 测试框架: k6")
    lines.append("// 运行: k6 run load-test.js")
    lines.append("// 注意：以下测试代码为骨架，AI 需根据实际 API 端点调整")
    lines.append("")
    lines.append("import http from 'k6/http';")
    lines.append("import { check, sleep } from 'k6';")
    lines.append("")
    lines.append("export const options = {")
    lines.append("  stages: [")
    lines.append("    { duration: '30s', target: 20 },")
    lines.append("    { duration: '60s', target: 50 },")
    lines.append("    { duration: '30s', target: 0 },")
    lines.append("  ],")
    lines.append("  thresholds: {")
    lines.append("    http_req_duration: ['p(95)<500', 'p(99)<1000'],")
    lines.append("    http_req_failed: ['rate<0.01'],")
    lines.append("  },")
    lines.append("};")
    lines.append("")
    lines.append("export default function () {")
    lines.append("  // TODO: 替换为实际的 API 端点")
    lines.append("  const BASE_URL = 'http://localhost:8080';")
    lines.append("")
    lines.append("  // 健康检查")
    lines.append("  const health = http.get(`${BASE_URL}/api/health`);")
    lines.append("  check(health, { '健康检查 200': (r) => r.status === 200 });")
    lines.append("")
    lines.append("  // 核心接口性能测试")
    lines.append("  // TODO: 添加更多 API 端点")
    lines.append("")
    lines.append("  sleep(1);")
    lines.append("}")
    lines.append("")

    test_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"  已生成: {test_file}")

    # Lighthouse 性能测试
    lh_file = Path(output_dir) / "performance" / "lighthouse.spec.ts"
    lines = []
    lines.append("// 自动生成的前端性能测试")
    lines.append("// 测试框架: Playwright + Lighthouse")
    lines.append("// 注意：需要安装 lighthouse (npm install -D lighthouse)")
    lines.append("")
    lines.append("import { test, expect } from '@playwright/test';")
    lines.append("")
    lines.append("test.describe('前端性能基线', () => {")
    lines.append("  test('首页性能分数应 >= 80', async ({ page }) => {")
    lines.append("    // 使用 Performance API 获取页面加载时间")
    lines.append("    await page.goto('/');")
    lines.append("    const metrics = await page.evaluate(() => ({")
    lines.append("      loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,")
    lines.append("    }));")
    lines.append("    // 页面加载时间应小于 3 秒")
    lines.append("    expect(metrics.loadTime).toBeLessThan(3000);")
    lines.append("    // TODO: 如需更精确的性能度量，可集成 Lighthouse CI")
    lines.append("  });")
    lines.append("});")
    lines.append("")

    lh_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"  已生成: {lh_file}")


def _generate_security_tests(security: List[Dict[str, Any]], output_dir: str) -> None:
    """生成安全测试"""
    test_file = Path(output_dir) / "security" / "security-checks.spec.ts"
    test_file.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("// 自动生成的安全测试")
    lines.append("// 测试框架: Playwright")
    lines.append("// 注意：以下测试代码为骨架，AI 需根据安全扫描结果完善")
    lines.append("")
    lines.append("import { test, expect } from '@playwright/test';")
    lines.append("")
    lines.append("test.describe('系统安全基线测试', () => {")
    lines.append("")

    # HTTPS 检查
    lines.append("  test('应使用 HTTPS', async ({ request }) => {")
    lines.append("    // TODO: 替换为实际的 staging/production URL")
    lines.append("    const response = await request.get('https://staging.example.com');")
    lines.append("    expect(response.status()).toBe(200);")
    lines.append("    // TODO: 根据实际部署的 TLS 版本调整协议断言")
    lines.append("    // expect(response.securityDetails().protocol()).toBe('TLS 1.3');")
    lines.append("  });")
    lines.append("")

    # 安全头检查
    lines.append("  test('应包含安全响应头', async ({ request }) => {")
    lines.append("    // TODO: 替换为实际的 staging/production URL")
    lines.append("    const response = await request.get('https://staging.example.com');")
    lines.append("    expect(response.status()).toBe(200);")
    lines.append("    const headers = response.headers();")
    lines.append("    // 验证基本安全响应头存在")
    lines.append("    expect(headers['x-frame-options']).toBeDefined();")
    lines.append("    expect(headers['x-content-type-options']).toBe('nosniff');")
    lines.append("    // TODO: 可补充验证 CSP 头、Strict-Transport-Security 等具体安全策略")
    lines.append("  });")
    lines.append("")

    # 认证安全
    lines.append("  test('密码不应明文传输', async ({ page }) => {")
    lines.append("    // TODO: 替换为实际的登录页面 URL")
    lines.append("    await page.goto('/login');")
    lines.append("    // TODO: 监听网络请求，验证密码字段已加密或使用 HTTPS 传输")
    lines.append("    const requests = [];")
    lines.append("    page.on('request', req => requests.push(req));")
    lines.append("    // TODO: 替换 '密码' 为实际的密码输入框 label，'登录' 为实际的按钮文本")
    lines.append("    await page.getByLabel('密码').fill('test123');")
    lines.append("    await page.getByRole('button', { name: '登录' }).click();")
    lines.append("    const loginReq = requests.find(r => r.url().includes('/api/auth/login'));")
    lines.append("    // 验证登录请求使用 HTTPS 协议")
    lines.append("    expect(loginReq.url()).toMatch(/^https:/);")
    lines.append("  });")
    lines.append("")

    # XSS 防护
    lines.append("  test('应防止 XSS 攻击', async ({ page }) => {")
    lines.append("    // TODO: 替换为实际包含输入框的页面 URL 和输入字段选择器")
    lines.append("    await page.goto('/search');")
    lines.append("    // TODO: 替换 '搜索' 为实际的输入框 placeholder 和按钮文本")
    lines.append("    await page.getByPlaceholder('搜索').fill('<script>alert(1)</script>');")
    lines.append("    await page.getByRole('button', { name: '搜索' }).click();")
    lines.append("    // 验证页面源码中不包含未转义的 script 标签")
    lines.append("    const bodyContent = await page.content();")
    lines.append("    expect(bodyContent).not.toContain('<script>alert(1)</script>');")
    lines.append("  });")
    lines.append("")

    # SQL 注入
    lines.append("  test('应防止 SQL 注入', async ({ page }) => {")
    lines.append("    // TODO: 替换为实际包含输入框的页面 URL 和输入字段选择器")
    lines.append("    await page.goto('/search');")
    lines.append("    // TODO: 替换 '搜索' 为实际的输入框 placeholder 和按钮文本")
    lines.append("    await page.getByPlaceholder('搜索').fill(\"' OR 1=1 --\");")
    lines.append("    await page.getByRole('button', { name: '搜索' }).click();")
    lines.append("    // 验证页面不会返回数据库错误信息")
    lines.append("    const bodyContent = await page.content();")
    lines.append("    expect(bodyContent.toLowerCase()).not.toContain('sql syntax');")
    lines.append("    expect(bodyContent.toLowerCase()).not.toContain('mysql');")
    lines.append("    expect(bodyContent.toLowerCase()).not.toContain('postgresql');")
    lines.append("  });")
    lines.append("")

    # 基于扫描发现的安全测试
    for finding in security:
        if finding.get("severity") == "high":
            finding_name = finding["name"]
            finding_detail = finding["detail"]
            lines.append(f"  test('安全修复: {finding_name}', async () => {{")
            lines.append(f"    // TODO: 验证 {finding_detail} - 根据具体漏洞类型编写验证逻辑")
            lines.append(f"  }});")
            lines.append("")

    lines.append("});")
    lines.append("")

    test_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"  已生成: {test_file}")

    # npm audit 脚本
    audit_file = Path(output_dir) / "security" / "run-audit.sh"
    lines = [
        "#!/bin/bash",
        "# 安全审计脚本",
        "# 运行: bash run-audit.sh",
        "",
        "echo '=== npm 依赖漏洞审计 ==='",
        "npm audit --json > audit-report.json 2>&1 || true",
        "echo '审计报告已保存到 audit-report.json'",
        "",
        "echo '=== Python 依赖审计 ==='",
        "pip audit --format json > pip-audit-report.json 2>&1 || true",
        "echo 'Python 审计报告已保存到 pip-audit-report.json'",
    ]
    audit_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"  已生成: {audit_file}")


def _generate_health_check_tests(services: List[Dict[str, Any]], output_dir: str) -> None:
    """生成健康检查测试"""
    test_file = Path(output_dir) / "health" / "health-check.spec.ts"
    test_file.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("// 自动生成的系统健康检查测试")
    lines.append("// 测试框架: Playwright")
    lines.append("")
    lines.append("import { test, expect } from '@playwright/test';")
    lines.append("")
    lines.append("test.describe('系统健康检查', () => {")
    lines.append("")

    # 前端健康检查
    has_frontend = any("frontend" in s.get("type", "") for s in services)
    if has_frontend:
        lines.append("  test('前端服务应可访问', async ({ request }) => {")
        lines.append("    const response = await request.get('http://localhost:3000');")
        lines.append("    expect(response.status()).toBe(200);")
        lines.append("  });")
        lines.append("")

    # 后端 API 健康检查
    has_backend = any("backend" in s.get("type", "") for s in services)
    if has_backend:
        lines.append("  test('后端 API 健康检查应返回 200', async ({ request }) => {")
        lines.append("    const response = await request.get('http://localhost:8080/api/health');")
        lines.append("    expect(response.status()).toBe(200);")
        lines.append("  });")
        lines.append("")

    # 数据库连接检查
    lines.append("  test('数据库连接应正常', async ({ request }) => {")
    lines.append("    // TODO: 替换为实际的数据库健康检查端点 URL")
    lines.append("    const response = await request.get('http://localhost:8080/api/health/db');")
    lines.append("    expect(response.status()).toBe(200);")
    lines.append("  });")
    lines.append("")

    lines.append("});")
    lines.append("")

    test_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"  已生成: {test_file}")


def _generate_compatibility_tests(services: List[Dict[str, Any]], output_dir: str) -> None:
    """
    生成兼容性测试（多浏览器、多设备、多操作系统）

    Args:
        services: 服务组件列表
        output_dir: 测试文件输出目录
    """
    test_file = Path(output_dir) / "compatibility" / "cross-browser.spec.ts"
    test_file.parent.mkdir(parents=True, exist_ok=True)

    # 检查是否存在前端服务
    has_frontend = any("frontend" in s.get("type", "") for s in services)

    lines = []
    lines.append("// 自动生成的兼容性测试")
    lines.append("// 测试框架: Playwright")
    lines.append("// 注意：以下测试代码为骨架，AI 需根据实际页面调整选择器")
    lines.append("")
    lines.append("import { test, expect } from '@playwright/test';")
    lines.append("")

    if has_frontend:
        # 多浏览器测试
        lines.append("test.describe('跨浏览器兼容性', () => {")
        lines.append("")
        lines.append("  // 测试 Chrome、Firefox、Safari、Edge")
        lines.append("  for (const browser of ['chromium', 'firefox', 'webkit']) {")
        lines.append("    test(`${browser}: 首页应正确渲染`, async ({ browserName, browser }) => {")
        lines.append("      // TODO: 跳过非当前浏览器的测试")
        lines.append("      // test.skip(browserName !== browser, 'Skipping non-target browser');")
        lines.append("")
        lines.append("      const context = await browser.newContext();")
        lines.append("      const page = await context.newPage();")
        lines.append("      await page.goto('/');")
        lines.append("")
        lines.append("      // 验证页面基本元素存在")
        lines.append("      await expect(page).toHaveTitle(/.+/);")
        lines.append("      // TODO: 替换为实际的页面关键元素选择器")
        lines.append("      // await expect(page.locator('header')).toBeVisible();")
        lines.append("      // await expect(page.locator('main')).toBeVisible();")
        lines.append("")
        lines.append("      await context.close();")
        lines.append("    });")
        lines.append("  }")
        lines.append("")
        lines.append("  // 移动端设备测试")
        lines.append("  const devices = [")
        lines.append("    { name: 'iPhone 14', viewport: { width: 390, height: 844 } },")
        lines.append("    { name: 'iPad Pro', viewport: { width: 1024, height: 1366 } },")
        lines.append("    { name: 'Desktop 1920', viewport: { width: 1920, height: 1080 } },")
        lines.append("  ];")
        lines.append("")
        lines.append("  for (const device of devices) {")
        lines.append("    test(`${device.name}: 响应式布局应正确`, async ({ browser }) => {")
        lines.append("      const context = await browser.newContext({")
        lines.append("        viewport: device.viewport,")
        lines.append("      });")
        lines.append("      const page = await context.newPage();")
        lines.append("      await page.goto('/');")
        lines.append("")
        lines.append("      // 验证无水平滚动条（响应式基本要求）")
        lines.append("      const hasHorizontalScroll = await page.evaluate(() => {")
        lines.append("        return document.documentElement.scrollWidth > document.documentElement.clientWidth;")
        lines.append("      });")
        lines.append("      expect(hasHorizontalScroll).toBeFalsy();")
        lines.append("")
        lines.append("      await context.close();")
        lines.append("    });")
        lines.append("  }")
        lines.append("")
        lines.append("});")
        lines.append("")

    test_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"  已生成: {test_file}")


def _generate_backup_recovery_tests(databases: List[Dict[str, Any]], output_dir: str) -> None:
    """
    生成数据备份和恢复测试

    Args:
        databases: 数据库组件列表
        output_dir: 测试文件输出目录
    """
    # 无数据库时跳过
    if not databases:
        return

    test_file = Path(output_dir) / "backup" / "backup-recovery.spec.ts"
    test_file.parent.mkdir(parents=True, exist_ok=True)

    # 提取数据库名称列表
    db_names = [d["name"] for d in databases]

    lines = []
    lines.append("// 自动生成的数据备份恢复测试")
    lines.append("// 测试框架: Playwright (API 测试)")
    lines.append("// 注意：以下测试代码为骨架，AI 需根据实际备份机制调整")
    lines.append("")
    lines.append("import { test, expect } from '@playwright/test';")
    lines.append("")
    lines.append("test.describe('数据备份与恢复', () => {")
    lines.append("")

    # 为每个数据库生成备份测试（最多3个）
    for db_name in db_names[:3]:
        safe_name = db_name.replace(" ", "_")
        lines.append(f"  test('{db_name} 备份应成功创建', async ({{ request }}) => {{")
        lines.append(f"    // TODO: 替换 '/api/admin/backup' 为实际的备份 API 端点")
        lines.append(f"    const response = await request.post('/api/admin/backup', {{")
        lines.append(f"      data: {{ database: '{db_name}' }}")
        lines.append(f"    }});")
        lines.append(f"    expect(response.status()).toBe(200);")
        lines.append(f"    const body = await response.json();")
        lines.append(f"    // TODO: 替换 'backupId' 为实际的备份响应字段名")
        lines.append(f"    // expect(body.backupId).toBeDefined();")
        lines.append(f"  }});")
        lines.append("")

    # 数据一致性验证
    lines.append("  test('备份后数据应与源数据一致', async ({ request }) => {")
    lines.append("    // TODO: 创建备份 -> 读取源数据 -> 从备份恢复 -> 对比数据")
    lines.append("    // 步骤 1: 调用备份 API 创建备份")
    lines.append("    // 步骤 2: 读取当前数据作为基线")
    lines.append("    // 步骤 3: 调用恢复 API 从备份恢复")
    lines.append("    // 步骤 4: 再次读取数据，与基线对比")
    lines.append("  });")
    lines.append("")

    # 恢复测试
    lines.append("  test('从备份恢复后系统应正常运行', async ({ request }) => {")
    lines.append("    // TODO: 从备份恢复 -> 验证所有 API 端点正常 -> 验证前端可访问")
    lines.append("    // TODO: 替换 '/api/health' 为实际的健康检查端点")
    lines.append("    const healthCheck = await request.get('/api/health');")
    lines.append("    expect(healthCheck.status()).toBe(200);")
    lines.append("  });")
    lines.append("")

    lines.append("});")
    lines.append("")

    test_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"  已生成: {test_file}")


def main(scan_result_path: str, output_dir: str):
    """
    根据扫描结果生成系统测试代码

    Args:
        scan_result_path: 扫描结果 JSON 文件路径
        output_dir: 测试文件输出目录
    """
    # 使用公共模块加载 JSON（失败时自动 sys.exit(1)）
    data = load_json(scan_result_path)

    try:
        generate_system_tests(data, output_dir)
    except (IOError, OSError) as e:
        print(f"错误：生成测试文件失败: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误：生成测试代码时发生意外错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python generate_system_tests.py <扫描结果JSON> <输出目录>")
        print("示例: python generate_system_tests.py scan_result.json ./system-tests/")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
