#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试辅助脚本 - 测试运行器
功能：运行项目中的集成测试，收集结果，输出 JSON 格式
用法：python run_integration_tests.py <项目路径> [--coverage] [--output <输出JSON路径>]
"""

import sys
import re
import subprocess
from pathlib import Path
from typing import Dict, List

from common import detect_tech_stack, save_json, validate_project_path


def detect_test_framework(tech_stack: List[str]) -> str:
    """
    检测已安装的测试框架

    Args:
        tech_stack: 技术栈

    Returns:
        str: 测试框架名称
    """
    if any(t in tech_stack for t in ["express", "koa", "fastify", "nestjs"]):
        return "jest"
    if any(t in tech_stack for t in ["flask", "django", "fastapi"]):
        return "pytest"
    if any(t in tech_stack for t in ["gin", "echo"]):
        return "go-testing"
    return "unknown"


def run_tests(project_path: str, tech_stack: List[str], framework: str, with_coverage: bool) -> Dict:
    """
    运行集成测试

    Args:
        project_path: 项目根目录
        tech_stack: 技术栈
        framework: 测试框架
        with_coverage: 是否收集覆盖率

    Returns:
        dict: 测试结果
    """
    result: Dict = {"framework": framework, "passed": 0, "failed": 0, "skipped": 0, "total": 0}

    cmd: List[str] = []
    if framework == "jest":
        cmd = ["npx", "jest", "--testPathPattern=integration", "--verbose", "--runInBand", "--forceExit"]
        if with_coverage:
            cmd.extend(["--coverage", "--coverageDirectory=coverage"])
    elif framework == "pytest":
        cmd = ["python", "-m", "pytest", "tests/integration/", "-v", "--tb=short"]
        if with_coverage:
            cmd.extend(["--cov=.", "--cov-report=term-missing"])
    elif framework == "go-testing":
        cmd = ["go", "test", "./tests/integration/...", "-v"]
        if with_coverage:
            cmd.extend(["-coverprofile=coverage.out"])
    else:
        result["error"] = f"未知的测试框架: {framework}"
        return result

    print(f"运行命令: {' '.join(cmd)}")
    try:
        proc = subprocess.run(
            cmd, cwd=project_path,
            capture_output=True, text=True, timeout=600  # 集成测试超时 10 分钟
        )
        output = proc.stdout + proc.stderr
        print(output)

        # 解析结果
        match = re.search(r"Tests:\s*(\d+)\s*failed?,\s*(\d+)\s*passed?,\s*(\d+)\s*total", output)
        if match:
            result["failed"] = int(match.group(1))
            result["passed"] = int(match.group(2))
            result["total"] = int(match.group(3))
        else:
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
            result["coverage"] = _parse_coverage(output)

    except subprocess.TimeoutExpired:
        result["error"] = "测试运行超时（600秒）"
    except FileNotFoundError:
        result["error"] = f"测试命令未找到，请确保已安装 {framework}"
    except Exception as e:
        result["error"] = str(e)

    return result


def _parse_coverage(output: str) -> Dict:
    """
    解析覆盖率数据

    Args:
        output: 测试输出

    Returns:
        dict: 覆盖率数据
    """
    coverage: Dict = {}
    stmt_match = re.search(r"Statements?\s*:\s*([\d.]+)%", output)
    branch_match = re.search(r"Branches?\s*:\s*([\d.]+)%", output)
    func_match = re.search(r"Functions?\s*:\s*([\d.]+)%", output)
    line_match = re.search(r"Lines?\s*:\s*([\d.]+)%", output)

    if stmt_match:
        coverage["statement"] = float(stmt_match.group(1))
    if branch_match:
        coverage["branch"] = float(branch_match.group(1))
    if func_match:
        coverage["function"] = float(func_match.group(1))
    if line_match:
        coverage["line"] = float(line_match.group(1))

    return coverage


def main(project_path: str, with_coverage: bool = False, output_path: str = "") -> Dict:
    """
    运行集成测试并收集结果

    Args:
        project_path: 项目根目录
        with_coverage: 是否收集覆盖率
        output_path: 结果输出 JSON 路径

    Returns:
        dict: 测试结果
    """
    # 验证项目路径
    try:
        validated_path = validate_project_path(project_path)
    except ValueError as e:
        print(f"错误：{e}")
        return {"error": str(e), "framework": "unknown", "passed": 0, "failed": 0, "skipped": 0, "total": 0}

    project_path = str(validated_path)
    print(f"项目路径: {project_path}")
    print(f"收集覆盖率: {'是' if with_coverage else '否'}")
    print("")

    # 使用 common.py 的统一 detect_tech_stack
    tech_stack = detect_tech_stack(validated_path)
    framework = detect_test_framework(tech_stack)
    print(f"技术栈: {', '.join(tech_stack)}")
    print(f"测试框架: {framework}")
    print("")

    result = run_tests(project_path, tech_stack, framework, with_coverage)

    total = result.get("total", 0)
    passed = result.get("passed", 0)
    result["pass_rate"] = round(passed / total * 100, 1) if total > 0 else 0
    result["tech_stack"] = tech_stack
    result["project_path"] = project_path

    print(f"\n测试结果:")
    print(f"  总数: {result.get('total', 0)}")
    print(f"  通过: {result.get('passed', 0)}")
    print(f"  失败: {result.get('failed', 0)}")
    print(f"  通过率: {result.get('pass_rate', 0)}%")
    if "coverage" in result:
        print(f"  覆盖率: {result['coverage']}")
    if "error" in result:
        print(f"  错误: {result['error']}")

    if output_path:
        save_json(result, output_path)
        print(f"\n结果已保存到: {output_path}")

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="运行集成测试并收集结果")
    parser.add_argument("project_path", help="项目根目录路径")
    parser.add_argument("--coverage", action="store_true", help="收集代码覆盖率")
    parser.add_argument("--output", "-o", default="", help="结果输出 JSON 路径")

    args = parser.parse_args()
    main(args.project_path, args.coverage, args.output)
