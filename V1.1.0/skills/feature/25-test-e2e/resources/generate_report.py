#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E 测试辅助脚本 - 报告生成器
功能：根据 E2E 测试结果生成 Markdown 格式的测试报告
用法：python generate_report.py <测试结果JSON> <报告输出路径> [扫描结果JSON]
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

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

from common import load_json, save_json


def generate_report(test_result_path: str, output_path: str, scan_result_path: str = "") -> None:
    """
    生成 Markdown 格式的 E2E 测试报告

    Args:
        test_result_path: 测试结果 JSON 文件路径
        output_path: 报告输出路径（.md 文件）
        scan_result_path: 扫描结果 JSON 文件路径（可选）
    """
    # 读取测试结果
    try:
        test_data: Dict[str, Any] = load_json(test_result_path)
    except (FileNotFoundError, ValueError):
        print(f"错误：无法读取测试结果文件 - {test_result_path}")
        return
    except Exception as e:
        print(f"错误：读取测试结果文件时发生异常 - {e}")
        return

    # 读取扫描结果（可选）
    scan_data: Dict[str, Any] = {}
    if scan_result_path and Path(scan_result_path).exists():
        try:
            scan_data = load_json(scan_result_path)
        except (ValueError, IOError):
            scan_data = {}  # 降级：扫描数据无效时继续生成报告

    # 构建报告
    lines: List[str] = []
    lines.append("# E2E 测试报告")
    lines.append("")
    lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # === 概览 ===
    lines.append("## 概览")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 前端框架 | {scan_data.get('framework', '未知')} |")
    lines.append(f"| E2E 框架 | {test_data.get('framework', '未知')} |")

    if scan_data:
        lines.append(f"| 扫描页面总数 | {scan_data.get('total_pages', 0)} |")
        flows: List[Dict[str, Any]] = scan_data.get("user_flows", [])
        lines.append(f"| 用户流程数 | {len(flows)} |")

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
    pass_rate: float = test_data.get('pass_rate', 0)
    lines.append(f"| 通过率 | {pass_rate}% |")

    if pass_rate >= 100:
        lines.append(f"| 状态 | ✅ 全部通过 |")
    elif pass_rate >= 80:
        lines.append(f"| 状态 | ⚠️ 部分失败 |")
    else:
        lines.append(f"| 状态 | ❌ 大量失败 |")
    lines.append("")

    # === 用户流程覆盖情况 ===
    if scan_data and scan_data.get("user_flows"):
        lines.append("## 用户流程覆盖情况")
        lines.append("")
        lines.append("| 流程名称 | 优先级 | 涉及页面 | 状态 |")
        lines.append("|----------|--------|---------|------|")

        for flow in scan_data["user_flows"]:
            name: str = flow.get("name", "未知")
            priority: str = flow.get("priority", "P2")
            steps: str = " → ".join(flow.get("steps", []))
            # 截断过长的步骤
            if len(steps) > 60:
                steps = steps[:57] + "..."
            # 根据通过率判断状态
            if pass_rate >= 100:
                status = "✅"
            elif pass_rate >= 80:
                status = "⚠️"
            else:
                status = "❌"
            lines.append(f"| {name} | {priority} | {steps} | {status} |")

        lines.append("")

    # === 页面覆盖情况 ===
    if scan_data and scan_data.get("pages"):
        lines.append("## 页面覆盖情况")
        lines.append("")
        lines.append("| 路由 | 文件 | 类型 | 表单 | 需要认证 |")
        lines.append("|------|------|------|------|---------|")

        for page in scan_data["pages"]:
            route: str = page.get("route", "-")
            file: str = page.get("file", "-")
            page_type: str = page.get("page_type", "普通页面")
            has_form: str = "📝" if page.get("has_form") else "-"
            needs_auth: str = "🔒" if page.get("needs_auth") else "-"
            # 截断过长的文件路径
            if len(file) > 40:
                file = "..." + file[-37:]
            lines.append(f"| {route} | {file} | {page_type} | {has_form} | {needs_auth} |")

        lines.append("")

    # === 失败详情 ===
    raw_output: str = test_data.get("raw_output", "")
    if test_data.get("failed", 0) > 0 and raw_output:
        lines.append("## 失败详情")
        lines.append("")
        lines.append("```")
        # 提取失败信息
        failed_lines: List[str] = []
        for line in raw_output.split("\n"):
            if "[FAIL]" in line or "Error:" in line or "expect(" in line:
                failed_lines.append(line)
        if failed_lines:
            lines.append("\n".join(failed_lines[-30:]))
        else:
            lines.append("（无法解析失败详情，请查看 Playwright HTML 报告）")
        lines.append("```")
        lines.append("")
        lines.append("> 💡 使用 `npx playwright show-report` 查看详细报告（含截图和 trace）")
        lines.append("")

    # === 错误信息 ===
    if "error" in test_data:
        lines.append("## 运行错误")
        lines.append("")
        lines.append(f"```\n{test_data['error']}\n```")
        lines.append("")

    # === 改进建议 ===
    lines.append("## 改进建议")
    lines.append("")

    suggestions: List[str] = []

    if pass_rate < 100:
        suggestions.append(f"- **修复失败测试**：当前通过率 {pass_rate}%，需要修复 {test_data.get('failed', 0)} 个失败的测试用例")

    if scan_data:
        # 未覆盖的表单页面
        form_pages = [p for p in scan_data.get("pages", []) if p.get("has_form")]
        auth_pages = [p for p in scan_data.get("pages", []) if p.get("needs_auth")]
        if form_pages:
            suggestions.append(f"- **表单测试**：发现 {len(form_pages)} 个表单页面，确保每个表单都有正向和验证测试")
        if auth_pages:
            suggestions.append(f"- **认证测试**：{len(auth_pages)} 个页面需要认证，确保未登录访问会被重定向")

        # P0 流程
        p0_flows = [f for f in scan_data.get("user_flows", []) if f.get("priority") == "P0"]
        if p0_flows:
            names = ", ".join([f["name"] for f in p0_flows])
            suggestions.append(f"- **P0 流程**：确保核心流程已全部覆盖并通过：{names}")

    if not suggestions:
        suggestions.append("- 所有指标均达标，E2E 测试质量良好 ✅")

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

    pr_status: str = "✅" if pass_rate >= 100 else "❌"
    lines.append(f"| 测试通过率 | 100% | {pass_rate}% | {pr_status} |")

    if scan_data:
        p0_flows = [f for f in scan_data.get("user_flows", []) if f.get("priority") == "P0"]
        p0_status: str = "✅" if len(p0_flows) > 0 else "ℹ️"
        lines.append(f"| P0 核心流程覆盖 | 100% | {len(p0_flows)} 个流程 | {p0_status} |")

    lines.append("")

    # 写入文件
    report_content: str = "\n".join(lines)
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"报告已生成: {output_path}")
        print(f"报告大小: {len(report_content)} 字符")
    except IOError as e:
        print(f"错误：写入报告失败 - {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python generate_report.py <测试结果JSON> <报告输出路径> [扫描结果JSON]")
        print("示例: python generate_report.py test_result.json report.md scan_result.json")
        sys.exit(1)

    scan = sys.argv[3] if len(sys.argv) >= 4 else ""
    generate_report(sys.argv[1], sys.argv[2], scan)
