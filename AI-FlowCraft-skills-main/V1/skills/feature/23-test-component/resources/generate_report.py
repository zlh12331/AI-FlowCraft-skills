#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件测试辅助脚本 - 报告生成器
功能：根据组件测试结果生成 Markdown 格式的测试报告
用法：python generate_report.py <测试结果JSON> <报告输出路径> [扫描结果JSON]
"""

import sys
from pathlib import Path
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

# 导入公共模块
from common import load_json


def generate_report(test_result_path: str, output_path: str, scan_result_path: str = ""):
    """
    生成 Markdown 格式的组件测试报告

    Args:
        test_result_path: 测试结果 JSON 文件路径
        output_path: 报告输出路径（.md 文件）
        scan_result_path: 扫描结果 JSON 文件路径（可选）
    """
    # 使用公共模块安全读取测试结果
    test_data = load_json(test_result_path)
    if test_data is None:
        print(f"错误：无法读取测试结果文件 - {test_result_path}")
        return

    # 使用公共模块安全读取扫描结果（可选）
    scan_data: dict = {}
    if scan_result_path:
        scan_data = load_json(scan_result_path) or {}

    # 构建报告
    lines: list = []
    lines.append("# 组件测试报告")
    lines.append("")
    lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # === 概览 ===
    lines.append("## 概览")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 前端框架 | {test_data.get('framework', '未知')} |")
    lines.append(f"| 测试框架 | {test_data.get('test_framework', '未知')} |")

    if scan_data:
        lines.append(f"| 扫描组件总数 | {scan_data.get('total_components', 0)} |")
        lines.append(f"| 可测试组件 | {scan_data.get('testable_components', 0)} |")

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
        failed_lines = []
        for line in raw_output.split("\n"):
            if any(kw in line.lower() for kw in ["fail", "error", "expect", "received", "expected"]):
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

    # === 组件测试覆盖情况 ===
    if scan_data and scan_data.get("components"):
        lines.append("## 组件测试覆盖情况")
        lines.append("")
        lines.append("| 组件名 | 文件 | Props | Events | 条件渲染 | 列表渲染 |")
        lines.append("|--------|------|-------|--------|---------|---------|")

        for comp in scan_data["components"]:
            name = comp.get("name", "未知")
            file = comp.get("file", "未知")
            props = comp.get("props", [])
            events = comp.get("events", [])
            cond = comp.get("conditional_renders", 0)
            list_r = comp.get("list_renders", 0)
            # 截断过长的内容
            props_str = ", ".join(props[:3]) + ("..." if len(props) > 3 else "") if props else "-"
            events_str = ", ".join(events[:3]) + ("..." if len(events) > 3 else "") if events else "-"
            lines.append(f"| {name} | {file} | {props_str} | {events_str} | {cond} | {list_r} |")

        lines.append("")

    # === 改进建议 ===
    lines.append("## 改进建议")
    lines.append("")

    suggestions: list = []

    if pass_rate < 100:
        suggestions.append(f"- **修复失败测试**：当前通过率 {pass_rate}%，需要修复 {test_data.get('failed', 0)} 个失败的测试用例")

    if coverage:
        stmt_cov = coverage.get("statement", coverage.get("line", 100))
        branch_cov = coverage.get("branch", 100)
        func_cov = coverage.get("function", 100)

        if stmt_cov < 80:
            suggestions.append(f"- **提高行覆盖率**：当前 {stmt_cov}%，目标 >= 80%，建议为未覆盖的组件分支补充测试")
        if branch_cov < 70:
            suggestions.append(f"- **提高分支覆盖率**：当前 {branch_cov}%，目标 >= 70%，建议覆盖所有条件渲染分支")
        if func_cov < 80:
            suggestions.append(f"- **提高函数覆盖率**：当前 {func_cov}%，目标 >= 80%")

    if scan_data:
        untested = scan_data.get("total_components", 0) - scan_data.get("testable_components", 0)
        if untested > 0:
            suggestions.append(f"- **扩展测试范围**：有 {untested} 个组件未被纳入测试")

        # 高复杂度组件（条件渲染多）
        complex_comps = [c for c in scan_data.get("components", []) if c.get("conditional_renders", 0) > 5]
        if complex_comps:
            names = ", ".join([c["name"] for c in complex_comps[:5]])
            suggestions.append(f"- **关注高复杂度组件**：{names} 的条件渲染 > 5 处，建议重点测试")

        # 修复：有 Props 但没有 Events 的组件建议补充交互测试
        has_props_no_events = [c for c in scan_data.get("components", [])
                               if c.get("props") and not c.get("events") and c.get("state_hooks", 0) > 0]
        if has_props_no_events:
            names = ", ".join([c["name"] for c in has_props_no_events[:5]])
            suggestions.append(f"- **补充交互测试**：{names} 有内部状态但未声明 Events，建议测试用户交互行为")

    if not suggestions:
        suggestions.append("- 所有指标均达标，组件测试质量良好")

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

    pr_status = "达标" if pass_rate >= 100 else "未达标"
    lines.append(f"| 测试通过率 | 100% | {pass_rate}% | {pr_status} |")

    if coverage:
        stmt = coverage.get("statement", coverage.get("line", 0))
        stmt_status = "达标" if stmt >= 80 else "未达标"
        lines.append(f"| 行覆盖率 | >= 80% | {stmt}% | {stmt_status} |")

        branch = coverage.get("branch", 0)
        branch_status = "达标" if branch >= 70 else "未达标"
        lines.append(f"| 分支覆盖率 | >= 70% | {branch}% | {branch_status} |")

        func = coverage.get("function", 0)
        func_status = "达标" if func >= 80 else "未达标"
        lines.append(f"| 函数覆盖率 | >= 80% | {func}% | {func_status} |")

    lines.append("")

    # 写入文件
    report_content = "\n".join(lines)
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"报告已生成: {output_path}")
        print(f"报告大小: {len(report_content)} 字符")
    except (OSError, IOError) as e:
        print(f"错误：无法写入报告文件 - {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python generate_report.py <测试结果JSON> <报告输出路径> [扫描结果JSON]")
        print("示例: python generate_report.py test_result.json report.md scan_result.json")
        sys.exit(1)

    scan = sys.argv[3] if len(sys.argv) >= 4 else ""
    generate_report(sys.argv[1], sys.argv[2], scan)
