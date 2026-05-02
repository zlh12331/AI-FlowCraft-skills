#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
"""
单元测试辅助脚本 - 报告生成器
功能：根据测试结果生成 Markdown 格式的测试报告
用法：python generate_report.py <测试结果JSON> <报告输出路径>
"""

import re
import sys
from datetime import datetime
from pathlib import Path

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


def get_duration(raw_output: str) -> float:
    """
    从测试输出中提取总执行时间（秒）

    Args:
        raw_output: 测试输出文本

    Returns:
        float: 执行时间（秒），未找到返回 0.0
    """
    if not raw_output:
        return 0.0

    # 模式1: "Tests completed in 1.23s" / "Time: 1.23s" / "Duration: 1.23s"
    m = re.search(r"(?:Tests completed in|Time:|Duration:)\s*([\d.]+)\s*s", raw_output, re.IGNORECASE)
    if m:
        return float(m.group(1))

    # 模式2: "real\t0m1.234s" (GNU time 格式)
    m = re.search(r"real\s+(\d+)m([\d.]+)s", raw_output)
    if m:
        return int(m.group(1)) * 60 + float(m.group(2))

    # 模式3: 独立的 "X.Xs" 或 "Xs"（仅在行尾或独立出现时匹配）
    m = re.search(r"\b([\d]+(?:\.\d+)?)\s*s(?:ec|econds)?\b", raw_output, re.IGNORECASE)
    if m:
        val = float(m.group(1))
        # 排除明显不是时间的值（如 100s 以上的大值）
        if val < 3600:
            return val

    return 0.0


def generate_report(test_result_path: str, output_path: str, scan_result_path: str = "") -> None:
    """
    生成 Markdown 格式的单元测试报告

    Args:
        test_result_path: 测试结果 JSON 文件路径
        output_path: 报告输出路径（.md 文件）
        scan_result_path: 扫描结果 JSON 文件路径（可选，用于补充信息）
    """
    # 读取测试结果
    test_data = load_json(test_result_path)
    if test_data is None:
        return

    # 读取扫描结果（可选）
    scan_data = {}
    if scan_result_path:
        loaded = load_json(scan_result_path)
        if loaded is not None:
            scan_data = loaded

    # 使用 report_config 获取章节标题顺序
    # 建立从 report_config 章节标题到现有显示标题的映射（保持现有格式不变）
    _SECTION_TITLE_MAP = {
        "一、测试概览": "概览",
        "二、测试结果": "测试结果",
        "执行时间分析": "执行时间分析",
        "三、覆盖情况": "代码覆盖率",
        "四、失败详情": "失败详情",
        "未覆盖项": "未覆盖函数",
        "五、改进建议": "改进建议",
    }
    # 从 report_config 获取章节顺序，映射为现有的 ## 标题格式
    _section_titles_config = get_section_titles("unit")
    _section_headings = {}
    for config_title in _section_titles_config:
        # 查找映射后的显示名
        display_name = _SECTION_TITLE_MAP.get(config_title, config_title)
        # 未覆盖项是子章节，使用 ### 前缀
        if config_title == "未覆盖项":
            _section_headings[config_title] = f"### {display_name}"
        else:
            _section_headings[config_title] = f"## {display_name}"

    # 构建报告
    lines = []
    lines.append("# 单元测试报告")
    lines.append("")
    lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # === 概览 ===
    # 使用 report_config 中定义的字段列表来驱动概览表格生成
    # 字段名到数据 key 的映射（现有数据格式 -> report_config 字段名）
    _OVERVIEW_FIELD_MAP = {
        "项目类型": ("test_data", "project_type", "未知"),
        "编程语言": ("test_data", "language", "未知"),
        "测试框架": ("test_data", "framework", "未知"),
        "扫描函数数": ("scan_data", "total_functions", 0),
        "可测试函数数": ("scan_data", "testable_functions", 0),
        "测试用例数": ("test_data", "total", 0),
    }
    # 现有格式中字段名与 report_config 定义的字段名有差异，建立显示名映射
    _OVERVIEW_DISPLAY_NAMES = {
        "扫描函数数": "扫描函数总数",
        "可测试函数数": "可测试函数",
        "测试用例数": "测试用例总数",
    }
    # 需要有 scan_data 才显示的字段
    _SCAN_REQUIRED_FIELDS = {"扫描函数数", "可测试函数数"}
    # 现有格式中不显示的字段（保持与原输出一致）
    _HIDDEN_FIELDS = {"编程语言"}

    lines.append(_section_headings["一、测试概览"])
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    for field in OVERVIEW_FIELDS["unit"]:
        # 跳过现有格式中不显示的字段
        if field in _HIDDEN_FIELDS:
            continue
        # 跳过需要 scan_data 但 scan_data 为空的字段
        if field in _SCAN_REQUIRED_FIELDS and not scan_data:
            continue
        source, key, default = _OVERVIEW_FIELD_MAP[field]
        data_source = test_data if source == "test_data" else scan_data
        value = data_source.get(key, default)
        display_name = _OVERVIEW_DISPLAY_NAMES.get(field, field)
        lines.append(f"| {display_name} | {value} |")
    lines.append("")

    # === 测试结果 ===
    # 使用 report_config.format_results 生成结果表格
    # 添加 float() 类型转换，确保 pass_rate 为数值类型
    # 使用 try-except 防止非标准输入（如 None、空字符串）导致崩溃
    try:
        pass_rate = float(test_data.get('pass_rate', 0))
    except (ValueError, TypeError):
        pass_rate = 0.0

    # 构建结果数据并调用 report_config.format_results
    results_data = {
        "total": test_data.get("total", 0),
        "passed": test_data.get("passed", 0),
        "failed": test_data.get("failed", 0),
        "skipped": test_data.get("skipped", 0),
        "pass_rate": pass_rate,
    }
    results_table = format_results(results_data)

    # 后处理：适配现有格式
    # 1. 移除"测试总数"行（现有格式不显示该行）
    # 2. 给状态行添加 emoji（现有格式有 emoji）
    _STATUS_EMOJI_MAP = {
        "全部通过": "✅ 全部通过",
        "部分失败": "⚠️ 部分失败",
        "大量失败": "❌ 大量失败",
    }
    processed_lines = []
    for line in results_table.split("\n"):
        # 跳过"测试总数"行
        if line.startswith("| 测试总数 |"):
            continue
        # 给状态行添加 emoji
        if line.startswith("| 状态 |"):
            for plain, with_emoji in _STATUS_EMOJI_MAP.items():
                line = line.replace(plain, with_emoji)
        processed_lines.append(line)

    lines.append(_section_headings["二、测试结果"])
    lines.append("")
    lines.extend(processed_lines)
    lines.append("")

    # 提前定义 raw_output，避免后续引用时 UnboundLocalError
    raw_output = test_data.get("raw_output", "")

    # 优先使用 duration 字段，否则从 raw_output 解析
    duration_field = test_data.get("duration")
    if duration_field is not None:
        try:
            total_duration = float(duration_field)
        except (ValueError, TypeError):
            total_duration = get_duration(raw_output)
    else:
        total_duration = get_duration(raw_output)
    total_tests = test_data.get("total") or 0
    # 计算平均每个测试的执行时间（毫秒）
    avg_duration_ms = (total_duration / total_tests * 1000) if total_tests > 0 else 0.0

    lines.append(_section_headings["执行时间分析"])
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 总执行时间 | {total_duration:.1f}s |")
    lines.append(f"| 平均每个测试 | {avg_duration_ms:.1f}ms |")
    lines.append("")

    # === 代码覆盖率 ===
    coverage = test_data.get("coverage", {})
    if coverage:
        lines.append(_section_headings["三、覆盖情况"])
        lines.append("")
        lines.append("| 类型 | 覆盖率 | 状态 |")
        lines.append("|------|--------|------|")

        coverage_items = [
            # 默认值改为 None，避免未知覆盖率显示为 0%
            ("行覆盖率 (Lines)", coverage.get("line", coverage.get("statement", None)), 80),
            ("分支覆盖率 (Branches)", coverage.get("branch", None), 70),
            ("函数覆盖率 (Functions)", coverage.get("function", None), 80),
            ("语句覆盖率 (Statements)", coverage.get("statement", None), 80),
        ]

        for name, value, threshold in coverage_items:
            if value is not None:
                status = "✅" if value >= threshold else "⚠️"
                lines.append(f"| {name} | {value}% | {status} |")

        lines.append("")

    # === 失败详情 ===
    if (test_data.get("failed") or 0) > 0 and raw_output:
        lines.append(_section_headings["四、失败详情"])
        lines.append("")
        lines.append("```")
        # 提取失败信息
        failed_lines = []
        for line in raw_output.split("\n"):
            if any(keyword in line.lower() for keyword in ["failed", "error:", "assertionerror", "expected"]):
                failed_lines.append(line)
        if failed_lines:
            lines.append("\n".join(failed_lines[-50:]))  # 最多50行
        else:
            lines.append("（无法解析失败详情，请查看原始输出）")
        lines.append("```")
        lines.append("")

    # === 错误信息 ===
    if "error" in test_data and test_data["error"] is not None:
        lines.append("## 运行错误")
        lines.append("")
        lines.append(f"```\n{test_data['error']}\n```")
        lines.append("")

    # === 函数测试覆盖情况 ===
    # 用于收集未覆盖函数的列表
    uncovered_functions = []

    if scan_data and scan_data.get("functions"):
        lines.append("## 函数测试覆盖情况")
        lines.append("")
        lines.append("| 函数名 | 文件 | 行号 | 参数 | 返回类型 | 分支数 | 测试状态 |")
        lines.append("|--------|------|------|------|----------|--------|----------|")

        # 从 raw_output 中提取所有被测试的函数名（用于判断是否已测试）
        # 复用前面已定义的 raw_output 变量，添加 or "" 保护防止 None
        raw_output_lower = (raw_output or "").lower()

        for func in scan_data["functions"]:
            name = func.get("name", "未知")
            file = func.get("file", "未知")
            line = func.get("line", 0)
            params = func.get("params", "")
            ret_type = func.get("return_type", "未知")
            branches = func.get("branches", 0)
            # 截断过长的参数
            if len(params) > 40:
                params = params[:37] + "..."
            # 保留原始函数名用于匹配（截断前保存）
            original_name = name
            # 截断过长的函数名（仅用于显示）
            if len(name) > 40:
                name = name[:37] + "..."
            # 判断函数是否被测试：在 raw_output 中查找函数名（不区分大小写）
            # 使用负向后瞻替代 \b，避免下划线开头函数名（如 _helper）无法匹配
            # 去除函数名中可能存在的括号等非标识符字符，避免过度转义导致匹配失败
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '', original_name.lower())
            if clean_name and re.search(r'(?<![a-zA-Z0-9_])' + re.escape(clean_name) + r'(?![a-zA-Z0-9_])', raw_output_lower):
                test_status = "✅ 已测试"
            elif raw_output:
                # 有原始输出但未匹配到该函数名
                test_status = "❌ 未测试"
                uncovered_functions.append(name)
            else:
                # 没有原始输出，无法判断
                test_status = "⚠️ 未知"
            lines.append(f"| {name} | {file} | {line} | {params} | {ret_type} | {branches} | {test_status} |")

        lines.append("")

        # === 未覆盖函数列表 ===
        if uncovered_functions:
            lines.append(_section_headings["未覆盖项"])
            lines.append("")
            lines.append("以下函数未在测试中被覆盖，建议补充对应的测试用例：")
            lines.append("")
            for uf in uncovered_functions:
                lines.append(f"- `{uf}`")
            lines.append("")

    # === 改进建议 ===
    lines.append(_section_headings["五、改进建议"])
    lines.append("")

    suggestions = []

    # 基于通过率的建议
    if pass_rate < 100:
        suggestions.append(f"- **修复失败测试**：当前通过率 {pass_rate}%，需要修复 {test_data.get('failed', 0)} 个失败的测试用例")

    # 基于覆盖率的建议
    if coverage:
        stmt_cov = coverage.get("line", coverage.get("statement", None))
        branch_cov = coverage.get("branch")
        func_cov = coverage.get("function")

        if stmt_cov is not None and stmt_cov < 80:
            suggestions.append(f"- **提高行覆盖率**：当前 {stmt_cov}%，目标 ≥ 80%，建议补充未覆盖代码路径的测试")
        if branch_cov is not None and branch_cov < 70:
            suggestions.append(f"- **提高分支覆盖率**：当前 {branch_cov}%，目标 ≥ 70%，建议覆盖所有 if/else、switch 分支")
        if func_cov is not None and func_cov < 80:
            suggestions.append(f"- **提高函数覆盖率**：当前 {func_cov}%，目标 ≥ 80%，建议为未测试的函数编写测试")

    # 基于扫描结果的建议
    if scan_data:
        # 添加 max(0, ...) 保护，避免 untested 为负数
        untested = max(0, (scan_data.get("total_functions") or 0) - (scan_data.get("testable_functions") or 0))
        if untested > 0:
            suggestions.append(f"- **扩展测试范围**：有 {untested} 个函数未被纳入测试，建议评估是否需要补充")

        # 高分支函数
        high_branch_funcs = [f for f in scan_data.get("functions", []) if (f.get("branches") or 0) > 5]
        if high_branch_funcs:
            # 使用 .get() 避免 KeyError（函数可能没有 name 字段）
            names = ", ".join([f.get("name", "未知") for f in high_branch_funcs[:5]])
            suggestions.append(f"- **关注高复杂度函数**：{names} 的分支数 > 5，建议重点测试并考虑重构")

    # 基于执行时间的建议：总执行时间超过60秒时建议并行执行
    if total_duration > 60:
        suggestions.append(f"- **考虑并行执行测试**：当前总执行时间 {total_duration:.1f}s，建议启用并行测试以缩短时间")

    # 基于未覆盖函数的建议：列出具体函数名并建议补充测试
    if uncovered_functions:
        func_names = "、".join(["`" + uf + "`" for uf in uncovered_functions[:10]])
        suggestions.append(f"- **补充未覆盖函数的测试**：{func_names} 未被测试覆盖，建议编写对应的测试用例")

    # 判断是否所有指标均达标：通过率100%且覆盖率达标
    all_pass = pass_rate >= 100
    if coverage:
        stmt_cov2 = coverage.get("line", coverage.get("statement", None))
        branch_cov2 = coverage.get("branch")
        func_cov2 = coverage.get("function")
        # 只有当所有覆盖率指标都存在且达标时才显示恭喜
        all_cov_present = stmt_cov2 is not None and branch_cov2 is not None and func_cov2 is not None
        if all_pass and all_cov_present and stmt_cov2 >= 80 and branch_cov2 >= 70 and func_cov2 >= 80:
            suggestions.append("- 🎉 恭喜！所有指标均达标")

    if not suggestions:
        suggestions.append("- 所有指标均达标，测试质量良好 ✅")

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

    # 通过率
    pr_status = "✅" if pass_rate >= 100 else "❌"
    lines.append(f"| 测试通过率 | 100% | {pass_rate}% | {pr_status} |")

    # 覆盖率（只在值存在时才显示，默认值为 None 表示不显示）
    if coverage:
        stmt = coverage.get("line", coverage.get("statement", None))
        if stmt is not None:
            stmt_status = "✅" if stmt >= 80 else "❌"
            lines.append(f"| 行覆盖率 | ≥ 80% | {stmt}% | {stmt_status} |")

        branch = coverage.get("branch")
        if branch is not None:
            branch_status = "✅" if branch >= 70 else "❌"
            lines.append(f"| 分支覆盖率 | ≥ 70% | {branch}% | {branch_status} |")

        func = coverage.get("function")
        if func is not None:
            func_status = "✅" if func >= 80 else "❌"
            lines.append(f"| 函数覆盖率 | ≥ 80% | {func}% | {func_status} |")

    # 总执行时间（CI/CD 友好标准：< 120s）
    duration_status = "✅" if total_duration < 120 else "❌"
    lines.append(f"| 总执行时间 | < 120s（CI/CD 友好） | {total_duration:.1f}s | {duration_status} |")

    lines.append("")

    # 写入文件
    report_content = "\n".join(lines)
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"报告已生成: {output_path}")
    except OSError as e:
        print(f"错误：无法写入报告文件 {output_path}: {e}", file=sys.stderr)
    print(f"报告大小: {len(report_content)} 字符")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python generate_report.py <测试结果JSON> <报告输出路径> [扫描结果JSON]")
        print("示例: python generate_report.py test_result.json report.md scan_result.json")
        sys.exit(1)

    scan = sys.argv[3] if len(sys.argv) >= 4 else ""
    generate_report(sys.argv[1], sys.argv[2], scan)
