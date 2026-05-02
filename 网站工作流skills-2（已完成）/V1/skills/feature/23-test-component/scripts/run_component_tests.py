#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件测试辅助脚本 - 测试运行器
功能：运行前端项目中的组件测试，收集覆盖率数据，输出 JSON 格式结果
用法：python run_component_tests.py <项目路径> [--coverage] [--output <输出JSON路径>]
"""

import sys
import json
import re
import subprocess
from pathlib import Path

# 导入公共模块
from common import load_json, save_json, validate_project_path, detect_framework


def detect_test_framework(project_path: str, framework: str) -> str:
    """
    检测已安装的组件测试框架

    Args:
        project_path: 项目根目录
        framework: 前端框架

    Returns:
        str: 测试框架名称
    """
    pkg = Path(project_path) / "package.json"
    if pkg.exists():
        try:
            content = pkg.read_text(encoding="utf-8", errors="ignore")
        except (OSError, IOError):
            content = ""
        if "vitest" in content:
            return "vitest"
        if "jest" in content:
            return "jest"
    return "jest"  # 默认 Jest


def run_tests(project_path: str, framework: str, test_framework: str, with_coverage: bool) -> dict:
    """
    运行组件测试

    Args:
        project_path: 项目根目录
        framework: 前端框架
        test_framework: 测试框架
        with_coverage: 是否收集覆盖率

    Returns:
        dict: 测试结果
    """
    result: dict = {
        "framework": framework,
        "test_framework": test_framework,
        "passed": 0, "failed": 0, "skipped": 0, "total": 0
    }

    cmd: list = []
    if framework == "angular":
        cmd = ["npx", "ng", "test", "--watch=false", "--browsers=ChromeHeadless"]
        if with_coverage:
            cmd.append("--code-coverage")
    elif test_framework == "vitest":
        cmd = ["npx", "vitest", "run", "--reporter=verbose"]
        if with_coverage:
            cmd.append("--coverage")
    elif test_framework == "jest":
        cmd = ["npx", "jest", "--verbose"]
        if with_coverage:
            cmd.extend(["--coverage", "--coverageDirectory=coverage"])

    print(f"运行命令: {' '.join(cmd)}")
    try:
        proc = subprocess.run(
            cmd, cwd=project_path,
            capture_output=True, text=True, timeout=300
        )
        output = proc.stdout + proc.stderr
        print(output)

        # 解析测试结果
        # Jest/Vitest 格式: Tests: X failed, Y passed, Z total
        match = re.search(r"Tests:\s*(\d+)\s*failed?,\s*(\d+)\s*passed?,\s*(\d+)\s*total", output)
        if match:
            result["failed"] = int(match.group(1))
            result["passed"] = int(match.group(2))
            result["total"] = int(match.group(3))
        else:
            # 尝试其他格式
            match = re.search(r"(\d+)\s*passed", output)
            if match:
                result["passed"] = int(match.group(1))
            match = re.search(r"(\d+)\s*failed", output)
            if match:
                result["failed"] = int(match.group(1))

        result["total"] = result["passed"] + result["failed"] + result["skipped"]
        result["raw_output"] = output

        # 解析覆盖率
        if with_coverage:
            result["coverage"] = _parse_coverage(output, project_path)

    except subprocess.TimeoutExpired:
        result["error"] = "测试运行超时（300秒）"
    except FileNotFoundError:
        result["error"] = f"命令未找到: {cmd[0] if cmd else 'unknown'}"
    except Exception as e:
        result["error"] = str(e)

    return result


def _parse_coverage(output: str, project_path: str) -> dict:
    """
    解析覆盖率数据

    Args:
        output: 测试输出
        project_path: 项目路径

    Returns:
        dict: 覆盖率数据
    """
    coverage: dict = {}

    # 从终端输出解析
    stmt_match = re.search(r"Statements\s*:\s*([\d.]+)%", output)
    branch_match = re.search(r"Branches\s*:\s*([\d.]+)%", output)
    func_match = re.search(r"Functions\s*:\s*([\d.]+)%", output)
    line_match = re.search(r"Lines\s*:\s*([\d.]+)%", output)

    if stmt_match:
        coverage["statement"] = float(stmt_match.group(1))
    if branch_match:
        coverage["branch"] = float(branch_match.group(1))
    if func_match:
        coverage["function"] = float(func_match.group(1))
    if line_match:
        coverage["line"] = float(line_match.group(1))

    # 尝试读取 coverage-summary.json
    summary_file = Path(project_path) / "coverage" / "coverage-summary.json"
    if summary_file.exists():
        try:
            data = json.loads(summary_file.read_text())
            total = data.get("total", {})
            coverage["statement"] = total.get("statements", {}).get("pct", coverage.get("statement", 0))
            coverage["branch"] = total.get("branches", {}).get("pct", coverage.get("branch", 0))
            coverage["function"] = total.get("functions", {}).get("pct", coverage.get("function", 0))
            coverage["line"] = total.get("lines", {}).get("pct", coverage.get("line", 0))
        except Exception:
            pass

    return coverage


def main(project_path: str, with_coverage: bool = False, output_path: str = "") -> dict:
    """
    运行组件测试并收集结果

    Args:
        project_path: 项目根目录
        with_coverage: 是否收集覆盖率
        output_path: 结果输出 JSON 路径

    Returns:
        dict: 测试结果
    """
    project_path = str(project_path)
    print(f"项目路径: {project_path}")
    print(f"收集覆盖率: {'是' if with_coverage else '否'}")
    print("")

    # 使用公共模块验证路径
    validated = validate_project_path(project_path)
    if validated is None:
        print(f"错误：路径不存在 - {project_path}")
        result: dict = {"error": f"路径不存在: {project_path}", "project_path": project_path}
        if output_path:
            save_json(result, output_path)
        return result

    # 检测框架（使用公共模块）
    framework = detect_framework(validated)
    test_framework = detect_test_framework(project_path, framework)
    print(f"前端框架: {framework}")
    print(f"测试框架: {test_framework}")
    print("")

    # 运行测试
    result = run_tests(project_path, framework, test_framework, with_coverage)

    # 计算通过率
    total = result.get("total", 0)
    passed = result.get("passed", 0)
    result["pass_rate"] = round(passed / total * 100, 1) if total > 0 else 0
    result["project_path"] = project_path

    # 输出结果
    print(f"\n测试结果:")
    print(f"  总数: {result.get('total', 0)}")
    print(f"  通过: {result.get('passed', 0)}")
    print(f"  失败: {result.get('failed', 0)}")
    print(f"  跳过: {result.get('skipped', 0)}")
    print(f"  通过率: {result.get('pass_rate', 0)}%")
    if "coverage" in result:
        print(f"  覆盖率: {result['coverage']}")
    if "error" in result:
        print(f"  错误: {result['error']}")

    # 保存结果（使用公共模块）
    if output_path:
        save_json(result, output_path)
        print(f"\n结果已保存到: {output_path}")

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="运行组件测试并收集覆盖率")
    parser.add_argument("project_path", help="项目根目录路径")
    parser.add_argument("--coverage", action="store_true", help="收集代码覆盖率")
    parser.add_argument("--output", "-o", default="", help="结果输出 JSON 路径")

    args = parser.parse_args()
    main(args.project_path, args.coverage, args.output)
