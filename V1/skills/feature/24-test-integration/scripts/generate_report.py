#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试辅助脚本 - 报告生成器
功能：根据集成测试结果生成 Markdown 格式的测试报告
用法：python generate_report.py <测试结果JSON> <报告输出路径> [扫描结果JSON]
"""

import sys
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

# 将 scripts 目录加入 sys.path，以便 import report_config
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from report_config import (
    OVERVIEW_FIELDS,
    format_overview,
    format_results,
    get_section_titles,
)

from common import load_json


def generate_report(test_result_path: str, output_path: str, scan_result_path: str = "") -> None:
    """
    生成 Markdown 格式的集成测试报告

    Args:
        test_result_path: 测试结果 JSON 文件路径
        output_path: 报告输出路径（.md 文件）
        scan_result_path: 扫描结果 JSON 文件路径（可选）
    """
    # 读取测试结果
    try:
        test_data = load_json(test_result_path)
    except FileNotFoundError:
        print(f"错误：测试结果文件不存在 - {test_result_path}")
        return
    except Exception as e:
        print(f"错误：读取测试结果失败 - {e}")
        return

    # 读取扫描结果（可选）
    scan_data: Dict[str, Any] = {}
    if scan_result_path:
        try:
            scan_data = load_json(scan_result_path)
        except FileNotFoundError:
            print(f"警告：扫描结果文件不存在 - {scan_result_path}，将跳过集成点分析")
        except Exception as e:
            print(f"警告：读取扫描结果失败 - {e}，将跳过集成点分析")

    # 构建报告
    lines: List[str] = []
    lines.append("# 集成测试报告")
    lines.append("")
    lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # === 概览 ===
    lines.append("## 概览")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    tech_stack = test_data.get("tech_stack", [])
    lines.append(f"| 技术栈 | {', '.join(tech_stack)} |")
    lines.append(f"| 测试框架 | {test_data.get('framework', '未知')} |")

    if scan_data:
        lines.append(f"| API 路由 | {scan_data.get('api_routes_count', 0)} |")
        lines.append(f"| 数据库模型 | {scan_data.get('db_models_count', 0)} |")
        lines.append(f"| 中间件 | {scan_data.get('middleware_count', 0)} |")
        lines.append(f"| 外部服务 | {scan_data.get('external_services_count', 0)} |")
        lines.append(f"| 总集成点 | {scan_data.get('total_integration_points', 0)} |")

    lines.append(f"| 测试用例总数 | {test_data.get('total', 0)} |")
    lines.append("")

    # === 测试结果 ===
    lines.append("## 测试结果")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 通过 | {test_data.get('passed', 0)} |")
    lines.append(f"| 失败 | {test_data.get('failed', 0)} |")
    lines.append(f"| 跳过 | {test_data.get('skipped', 0)} |")
    pass_rate = test_data.get('pass_rate', 0)
    lines.append(f"| 通过率 | {pass_rate}% |")

    if pass_rate >= 100:
        lines.append(f"| 状态 | 全部通过 |")
    elif pass_rate >= 80:
        lines.append(f"| 状态 | 部分失败 |")
    else:
        lines.append(f"| 状态 | 大量失败 |")
    lines.append("")

    # === 代码覆盖率 ===
    coverage = test_data.get("coverage", {})
    if coverage:
        lines.append("## 代码覆盖率")
        lines.append("")
        lines.append("| 类型 | 覆盖率 | 状态 |")
        lines.append("|------|--------|------|")

        coverage_items = [
            ("行覆盖率 (Lines)", coverage.get("line", coverage.get("statement", 0)), 80),
            ("分支覆盖率 (Branches)", coverage.get("branch", 0), 70),
            ("函数覆盖率 (Functions)", coverage.get("function", 0), 80),
            ("语句覆盖率 (Statements)", coverage.get("statement", 0), 80),
        ]

        for name, value, threshold in coverage_items:
            if value:
                status = "达标" if value >= threshold else "未达标"
                lines.append(f"| {name} | {value}% | {status} |")

        lines.append("")

    # === 失败详情 ===
    raw_output = test_data.get("raw_output", "")
    if test_data.get("failed", 0) > 0 and raw_output:
        lines.append("## 失败详情")
        lines.append("")
        lines.append("```")
        failed_lines: List[str] = []
        for line in raw_output.split("\n"):
            if any(kw in line.lower() for kw in ["fail", "error", "assert", "expected", "status"]):
                failed_lines.append(line)
        if failed_lines:
            lines.append("\n".join(failed_lines[-50:]))
        else:
            lines.append("（无法解析失败详情，请查看原始输出）")
        lines.append("```")
        lines.append("")

    # === 错误信息 ===
    if "error" in test_data:
        lines.append("## 运行错误")
        lines.append("")
        lines.append(f"```\n{test_data['error']}\n```")
        lines.append("")

    # === 集成点覆盖情况 ===
    if scan_data and scan_data.get("integration_points"):
        lines.append("## 集成点覆盖情况")
        lines.append("")

        # API 路由
        api_routes = [p for p in scan_data["integration_points"] if p.get("category") == "api"]
        if api_routes:
            lines.append("### API 路由")
            lines.append("")
            lines.append("| 方法 | 路径 | 文件 | 需要认证 |")
            lines.append("|------|------|------|---------|")
            for route in api_routes[:30]:
                auth = "是" if route.get("auth_required") else "否"
                lines.append(f"| {route.get('method', '-')} | {route.get('path', '-')} | {route.get('file', '-')} | {auth} |")
            if len(api_routes) > 30:
                lines.append(f"| ... | 还有 {len(api_routes) - 30} 个路由 | | |")
            lines.append("")

        # 数据库模型
        db_models = [p for p in scan_data["integration_points"] if p.get("category") == "database"]
        if db_models:
            lines.append("### 数据库模型")
            lines.append("")
            lines.append("| 模型名 | ORM | 字段 |")
            lines.append("|--------|-----|------|")
            for model in db_models[:20]:
                fields = model.get("fields", [])
                fields_str = ", ".join(fields[:5]) + ("..." if len(fields) > 5 else "")
                lines.append(f"| {model.get('name', '-')} | {model.get('orm', '-')} | {fields_str} |")
            lines.append("")

        # 外部服务
        ext_services = [p for p in scan_data["integration_points"] if p.get("category") == "external_service"]
        if ext_services:
            lines.append("### 外部服务依赖")
            lines.append("")
            lines.append("| 服务 | 文件 | URL 示例 |")
            lines.append("|------|------|---------|")
            for svc in ext_services[:15]:
                urls = svc.get("urls", [])
                url_str = urls[0] if urls else "-"
                lines.append(f"| {svc.get('name', '-')} | {svc.get('file', '-')} | {url_str} |")
            lines.append("")

    # === 改进建议 ===
    lines.append("## 改进建议")
    lines.append("")

    suggestions: List[str] = []

    if pass_rate < 100:
        suggestions.append(f"- **修复失败测试**：当前通过率 {pass_rate}%，需要修复 {test_data.get('failed', 0)} 个失败的测试用例")

    if coverage:
        stmt_cov = coverage.get("statement", coverage.get("line", 100))
        branch_cov = coverage.get("branch", 100)
        if stmt_cov < 80:
            suggestions.append(f"- **提高行覆盖率**：当前 {stmt_cov}%，目标 >= 80%")
        if branch_cov < 70:
            suggestions.append(f"- **提高分支覆盖率**：当前 {branch_cov}%，目标 >= 70%")

    if scan_data:
        # 未覆盖的 API 路由
        api_count = scan_data.get("api_routes_count", 0)
        if api_count > 0:
            suggestions.append(f"- **扩展 API 覆盖**：共发现 {api_count} 个 API 路由，建议全部编写集成测试")

        # 需要认证的路由
        auth_routes = [p for p in scan_data.get("integration_points", []) if p.get("category") == "api" and p.get("auth_required")]
        if auth_routes:
            suggestions.append(f"- **补充认证测试**：{len(auth_routes)} 个 API 需要认证，确保 Token 过期/无效场景已覆盖")

        # 外部服务
        ext_count = scan_data.get("external_services_count", 0)
        if ext_count > 0:
            suggestions.append(f"- **Mock 外部服务**：发现 {ext_count} 个外部服务依赖，确保集成测试中已正确 Mock")

    if not suggestions:
        suggestions.append("- 所有指标均达标，集成测试质量良好")

    for s in suggestions:
        lines.append(s)
    lines.append("")

    # === 通过标准 ===
    lines.append("---")
    lines.append("")
    lines.append("## 通过标准")
    lines.append("")
    lines.append("| 指标 | 标准 | 实际 | 状态 |")
    lines.append("|------|------|------|------|")

    pr_status = "通过" if pass_rate >= 100 else "未通过"
    lines.append(f"| 测试通过率 | 100% | {pass_rate}% | {pr_status} |")

    if coverage:
        stmt = coverage.get("statement", coverage.get("line", 0))
        stmt_status = "通过" if stmt >= 80 else "未通过"
        lines.append(f"| 行覆盖率 | >= 80% | {stmt}% | {stmt_status} |")

        branch = coverage.get("branch", 0)
        branch_status = "通过" if branch >= 70 else "未通过"
        lines.append(f"| 分支覆盖率 | >= 70% | {branch}% | {branch_status} |")

    lines.append("")

    # 写入文件
    report_content = "\n".join(lines)
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"报告已生成: {output_path}")
        print(f"报告大小: {len(report_content)} 字符")
    except OSError as e:
        print(f"错误：写入报告失败 - {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python generate_report.py <测试结果JSON> <报告输出路径> [扫描结果JSON]")
        print("示例: python generate_report.py test_result.json report.md scan_result.json")
        sys.exit(1)

    scan = sys.argv[3] if len(sys.argv) >= 4 else ""
    generate_report(sys.argv[1], sys.argv[2], scan)
