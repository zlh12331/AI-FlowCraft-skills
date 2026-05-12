#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试辅助脚本 - 报告生成器
功能：根据系统测试结果生成 Markdown 格式的测试报告
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

from common import load_json, load_json_safe


def generate_report(test_result_path: str, output_path: str, scan_result_path: str = ""):
    """
    生成 Markdown 格式的系统测试报告

    Args:
        test_result_path: 测试结果 JSON 文件路径
        output_path: 报告输出路径
        scan_result_path: 扫描结果 JSON 文件路径（可选）
    """
    # 加载测试结果 JSON（失败时自动 sys.exit(1)）
    test_data = load_json(test_result_path)

    # 加载扫描结果 JSON（可选，失败时降级为空字典）
    scan_data: Dict[str, Any] = load_json_safe(scan_result_path) or {}

    lines = []
    lines.append("# 系统测试报告")
    lines.append("")
    lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # === 概览 ===
    _append_architecture_overview(lines, scan_data)

    # === 功能性测试结果 ===
    _append_functional_results(lines, test_data)

    # === 安全测试结果 ===
    _append_security_results(lines, test_data)

    # === 安全扫描发现 ===
    _append_security_findings(lines, scan_data)

    # === 性能测试结果 ===
    _append_performance_results(lines, test_data)

    # === 执行时间分析 ===
    _append_duration_analysis(lines, test_data)

    # === 健康检查结果 ===
    _append_health_results(lines, test_data)

    # === 总体结果 ===
    _append_summary(lines, test_data, scan_data)

    # === 改进建议 ===
    _append_suggestions(lines, test_data, scan_data)

    # === 通过标准 ===
    _append_pass_criteria(lines, test_data)

    lines.append("")

    # 写入文件（报告为纯文本 Markdown，非 JSON）
    report_content = "\n".join(lines)
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"报告已生成: {output_path}")
        print(f"报告大小: {len(report_content)} 字符")
    except (IOError, OSError) as e:
        print(f"错误：无法写入报告文件 {output_path}: {e}", file=sys.stderr)
        sys.exit(1)


def _append_architecture_overview(lines: List[str], scan_data: Dict[str, Any]):
    """追加系统架构概览章节"""
    lines.append("## 系统架构概览")
    lines.append("")
    lines.append("| 组件 | 数量 | 详情 |")
    lines.append("|------|------|------|")

    if scan_data:
        components = scan_data.get("components", [])
        services = [c for c in components if c.get("category") == "service"]
        databases = [c for c in components if c.get("category") == "database"]
        caches = [c for c in components if c.get("category") == "cache"]
        externals = [c for c in components if c.get("category") == "external"]

        lines.append(f"| 服务组件 | {len(services)} | {', '.join([s['name'] for s in services[:5]])} |")
        lines.append(f"| 数据库 | {len(databases)} | {', '.join([d['name'] for d in databases])} |")
        lines.append(f"| 缓存 | {len(caches)} | {', '.join([c['name'] for c in caches]) or '-'} |")
        lines.append(f"| 外部集成 | {len(externals)} | {', '.join([e['name'] for e in externals[:5]])} |")
        lines.append(f"| 配置文件 | {len(scan_data.get('config_files', []))} | - |")

    lines.append("")


def _append_functional_results(lines: List[str], test_data: Dict[str, Any]):
    """追加功能性测试结果章节"""
    func = test_data.get("functional", {})
    if not func:
        return

    lines.append("## 功能性测试结果")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 通过 | {func.get('passed', 0)} |")
    lines.append(f"| 失败 | {func.get('failed', 0)} |")
    func_total = func.get("passed", 0) + func.get("failed", 0)
    func_rate = round(func.get("passed", 0) / func_total * 100, 1) if func_total > 0 else 0
    lines.append(f"| 通过率 | {func_rate}% |")
    lines.append("")


def _append_security_results(lines: List[str], test_data: Dict[str, Any]):
    """追加安全测试结果章节"""
    sec = test_data.get("security", {})
    if not sec or not sec.get("vulnerabilities"):
        return

    lines.append("## 安全测试结果")
    lines.append("")
    vulns = sec["vulnerabilities"]

    # 统计各严重程度数量（兼容字典和列表两种格式）
    severity_counts = _count_vulnerabilities(vulns)

    lines.append("| 严重程度 | 数量 |")
    lines.append("|---------|------|")
    lines.append(f"| Critical | {severity_counts['critical']} |")
    lines.append(f"| High | {severity_counts['high']} |")
    lines.append(f"| Moderate | {severity_counts['moderate']} |")
    lines.append(f"| Low | {severity_counts['low']} |")
    lines.append(f"| Info | {severity_counts['info']} |")
    total_vulns = sum(severity_counts.values())
    lines.append(f"| **总计** | **{total_vulns}** |")
    lines.append("")


def _count_vulnerabilities(vulns) -> Dict[str, int]:
    """
    统计漏洞严重程度数量（兼容字典和列表两种格式）

    Args:
        vulns: 漏洞数据，字典格式 {"critical": N, ...} 或列表格式 [{"severity": "...", ...}, ...]

    Returns:
        dict: 各严重程度的数量统计
    """
    severity_map = {"critical": 0, "high": 0, "moderate": 0, "low": 0, "info": 0}

    if isinstance(vulns, dict):
        # 字典格式：直接映射
        for key, count in vulns.items():
            sev = key.lower()
            if sev == "medium":
                severity_map["moderate"] += count
            elif sev in severity_map:
                severity_map[sev] += count
    elif isinstance(vulns, list):
        # 列表格式：逐条统计
        for v in vulns:
            sev = v.get("severity", "info").lower()
            if sev == "medium":
                severity_map["moderate"] += 1
            elif sev in severity_map:
                severity_map[sev] += 1

    return severity_map


def _append_security_findings(lines: List[str], scan_data: Dict[str, Any]):
    """追加安全配置发现章节"""
    if not scan_data or not scan_data.get("security_findings"):
        return

    findings = scan_data["security_findings"]
    lines.append("## 安全配置发现")
    lines.append("")
    lines.append("| 问题 | 严重程度 | 详情 |")
    lines.append("|------|---------|------|")
    for f in findings:
        sev = "high" if f.get("severity") == "high" else "medium"
        lines.append(f"| {sev} {f['name']} | {f.get('severity', '-')} | {f.get('detail', '-')} |")
    lines.append("")


def _append_performance_results(lines: List[str], test_data: Dict[str, Any]):
    """追加性能测试结果章节"""
    perf = test_data.get("performance", {})
    if not perf:
        return

    lines.append("## 性能测试结果")
    lines.append("")
    lines.append("| 指标 | 基线 | 实际 | 状态 |")
    lines.append("|------|------|------|------|")

    metrics = perf.get("metrics", {})
    if metrics:
        p95 = metrics.get("http_req_duration_p95", metrics.get("p95_response_time", "N/A"))
        p99 = metrics.get("http_req_duration_p99", metrics.get("p99_response_time", "N/A"))
        error_rate = metrics.get("http_req_failed_rate", metrics.get("error_rate", "N/A"))
        throughput = metrics.get("throughput", "N/A")

        lines.append(f"| API P95 响应时间 | < 500ms | {_format_perf(p95)} | {_check_perf(p95, 500)} |")
        lines.append(f"| API P99 响应时间 | < 1000ms | {_format_perf(p99)} | {_check_perf(p99, 1000)} |")
        lines.append(f"| 并发失败率 | < 1% | {_format_perf(error_rate, '%')} | {_check_perf(error_rate, 1)} |")
        if throughput != "N/A":
            lines.append(f"| 吞吐量 | > 100 req/s | {_format_perf(throughput, ' req/s')} | - |")
    else:
        lines.append("| API P95 响应时间 | < 500ms | N/A | - |")
        lines.append("| API P99 响应时间 | < 1000ms | N/A | - |")
        lines.append("| 并发失败率 | < 1% | N/A | - |")
    lines.append("")


def _format_perf(value, unit: str = "ms") -> str:
    """格式化性能指标值"""
    if isinstance(value, (int, float)):
        return f"{value}{unit}"
    return str(value)


def _check_perf(actual, threshold: int) -> str:
    """检查性能是否达标"""
    if isinstance(actual, (int, float)):
        return "达标" if actual < threshold else "超标"
    return "-"


def _append_duration_analysis(lines: List[str], test_data: Dict[str, Any]):
    """追加执行时间分析章节"""
    duration = test_data.get("duration", 0)
    if not duration:
        return

    total_tests = test_data.get("total", 1)
    avg_time = round(duration / total_tests * 1000, 1) if total_tests > 0 else 0

    lines.append("## 执行时间分析")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 总执行时间 | {duration}s |")
    lines.append(f"| 平均每个测试 | {avg_time}ms |")
    ci_friendly = "达标" if duration < 300 else "超时"
    lines.append(f"| CI/CD 友好 (<300s) | {ci_friendly} |")
    lines.append("")


def _append_health_results(lines: List[str], test_data: Dict[str, Any]):
    """追加健康检查结果章节"""
    health = test_data.get("health", {})
    if not health or not health.get("total"):
        return

    lines.append("## 健康检查结果")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 通过 | {health.get('passed', 0)} |")
    lines.append(f"| 失败 | {health.get('failed', 0)} |")
    health_total = health.get("passed", 0) + health.get("failed", 0)
    health_rate = round(health.get("passed", 0) / health_total * 100, 1) if health_total > 0 else 0
    status = "正常" if health_rate == 100 else "异常"
    lines.append(f"| 状态 | {status} |")
    lines.append("")


def _append_summary(lines: List[str], test_data: Dict[str, Any], scan_data: Dict[str, Any]):
    """追加总体结果章节"""
    lines.append("## 总体结果")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 功能测试通过率 | {test_data.get('pass_rate', 0)}% |")

    # 计算高危漏洞数量
    sec = test_data.get("security", {})
    critical_high_count = _count_critical_high(sec)
    lines.append(f"| 安全漏洞 (Critical+High) | {critical_high_count} |")
    lines.append(f"| 配置文件 | {len(scan_data.get('config_files', [])) if scan_data else 'N/A'} |")
    lines.append(f"| 环境变量 | {len(scan_data.get('env_vars', [])) if scan_data else 'N/A'} |")
    lines.append("")


def _count_critical_high(sec: Dict[str, Any]) -> int:
    """计算 Critical + High 漏洞数量"""
    if not sec or not sec.get("vulnerabilities"):
        return 0
    vulns = sec["vulnerabilities"]
    if isinstance(vulns, dict):
        return vulns.get("critical", 0) + vulns.get("high", 0)
    elif isinstance(vulns, list):
        return sum(1 for v in vulns if v.get("severity", "").lower() in ("critical", "high"))
    return 0


def _append_suggestions(lines: List[str], test_data: Dict[str, Any], scan_data: Dict[str, Any]):
    """追加改进建议章节"""
    lines.append("## 改进建议")
    lines.append("")

    suggestions = _generate_suggestions(test_data, scan_data)

    for s in suggestions:
        lines.append(s)
    lines.append("")


def _generate_suggestions(test_data: Dict[str, Any], scan_data: Dict[str, Any]) -> List[str]:
    """
    根据测试结果生成改进建议

    Args:
        test_data: 测试结果数据
        scan_data: 扫描结果数据

    Returns:
        list: 改进建议列表
    """
    suggestions = []

    # 功能测试失败建议
    func = test_data.get("functional", {})
    if func and func.get("failed", 0) > 0:
        suggestions.append(f"- **修复功能测试失败**：{func['failed']} 个功能性测试失败")

    # 安全漏洞建议
    sec = test_data.get("security", {})
    if sec and sec.get("vulnerabilities"):
        vulns = sec["vulnerabilities"]
        severity_counts = _count_vulnerabilities(vulns)
        if severity_counts["critical"] > 0:
            suggestions.append(f"- **[Critical] 立即修复**：{severity_counts['critical']} 个严重漏洞")
        if severity_counts["high"] > 0:
            suggestions.append(f"- **[High] 尽快修复**：{severity_counts['high']} 个高危漏洞")
        if severity_counts["moderate"] > 0:
            suggestions.append(f"- **[Moderate] 计划修复**：{severity_counts['moderate']} 个中危漏洞")

    # 扫描发现的安全建议
    if scan_data and scan_data.get("security_findings"):
        high_sec = [f for f in scan_data["security_findings"] if f.get("severity") == "high"]
        for f in high_sec:
            suggestions.append(f"- **安全修复**: {f['name']} - {f['detail']}")

    if not suggestions:
        suggestions.append("- 所有指标均达标，系统测试质量良好")

    return suggestions


def _append_pass_criteria(lines: List[str], test_data: Dict[str, Any]):
    """追加通过标准章节"""
    lines.append("## 通过标准")
    lines.append("")
    lines.append("| 指标 | 标准 | 实际 | 状态 |")
    lines.append("|------|------|------|------|")

    # 功能测试通过率
    func_rate = test_data.get("pass_rate", 0)
    func_status = "达标" if func_rate >= 100 else "未达标"
    lines.append(f"| 功能测试通过率 | 100% | {func_rate}% | {func_status} |")

    # 安全漏洞
    sec = test_data.get("security", {})
    critical_high = _count_critical_high(sec)
    sec_status = "达标" if critical_high == 0 else "未达标"
    lines.append(f"| Critical+High 漏洞 | 0 | {critical_high} | {sec_status} |")

    # 性能 P95
    perf = test_data.get("performance", {})
    if perf and perf.get("metrics"):
        p95 = perf["metrics"].get("http_req_duration_p95", perf["metrics"].get("p95_response_time", None))
        if isinstance(p95, (int, float)):
            perf_ok = f"{p95}ms"
            perf_status = "达标" if p95 < 500 else "未达标"
        else:
            perf_ok = "N/A"
            perf_status = "-"
    else:
        perf_ok = "N/A"
        perf_status = "-"
    lines.append(f"| API P95 响应时间 | < 500ms | {perf_ok} | {perf_status} |")

    # 执行时间
    duration = test_data.get("duration", 0)
    dur_status = "达标" if duration < 300 else "未达标"
    lines.append(f"| 总执行时间 | < 300s | {duration}s | {dur_status} |")

    lines.append("")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python generate_report.py <测试结果JSON> <报告输出路径> [扫描结果JSON]")
        print("示例: python generate_report.py test_result.json report.md scan_result.json")
        sys.exit(1)

    scan = sys.argv[3] if len(sys.argv) >= 4 else ""
    generate_report(sys.argv[1], sys.argv[2], scan)
