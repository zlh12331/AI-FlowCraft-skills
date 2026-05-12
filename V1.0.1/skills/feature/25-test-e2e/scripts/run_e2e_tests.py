#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E 测试辅助脚本 - 测试运行器
功能：运行 Playwright E2E 测试，收集结果，输出 JSON 格式
用法：python run_e2e_tests.py <项目路径> [--headed] [--browser chromium] [--output <输出JSON路径>]
"""

import sys
import re
import subprocess
from pathlib import Path
from typing import Any, Dict

from common import detect_framework, save_json


def detect_e2e_framework(project_path: str) -> str:
    """
    检测已安装的 E2E 测试框架

    Args:
        project_path: 项目根目录

    Returns:
        str: 框架名称（playwright/cypress/unknown）
    """
    pkg = Path(project_path) / "package.json"
    if pkg.exists():
        content = pkg.read_text(encoding="utf-8", errors="ignore")
        if "playwright" in content:
            return "playwright"
        if "cypress" in content:
            return "cypress"
    return "playwright"  # 默认 Playwright


def run_tests(project_path: str, framework: str, headed: bool = False, browser: str = "") -> dict:
    """
    运行 E2E 测试

    Args:
        project_path: 项目根目录
        framework: E2E 测试框架
        headed: 是否有头模式
        browser: 指定浏览器

    Returns:
        dict: 测试结果
    """
    result: Dict[str, Any] = {"framework": framework, "passed": 0, "failed": 0, "skipped": 0, "total": 0}

    cmd: list = []
    if framework == "playwright":
        cmd = ["npx", "playwright", "test"]
        if headed:
            cmd.append("--headed")
        if browser:
            cmd.extend(["--project", browser])
        # E2E 测试建议串行运行
        cmd.extend(["--workers=1", "--reporter=list"])
    elif framework == "cypress":
        if headed:
            cmd = ["npx", "cypress", "run", "--headed"]
        else:
            cmd = ["npx", "cypress", "run"]
        if browser:
            cmd.extend(["--browser", browser])

    print(f"运行命令: {' '.join(cmd)}")
    try:
        proc = subprocess.run(
            cmd, cwd=project_path,
            capture_output=True, text=True, timeout=600  # E2E 测试超时 10 分钟
        )
        output = proc.stdout + proc.stderr
        print(output)

        # 解析 Playwright 输出
        # 格式: 1) [chromium] › login.spec.ts:5:3 › 合法凭据应成功登录 [PASS]
        passed_matches = re.findall(r"\[PASS\]", output)
        failed_matches = re.findall(r"\[FAIL\]", output)
        skipped_matches = re.findall(r"\[SKIPPED\]", output)

        result["passed"] = len(passed_matches)
        result["failed"] = len(failed_matches)
        result["skipped"] = len(skipped_matches)
        result["total"] = result["passed"] + result["failed"] + result["skipped"]

        # 如果正则没匹配到，尝试其他格式
        if result["total"] == 0:
            match = re.search(r"(\d+)\s*passed", output)
            if match:
                result["passed"] = int(match.group(1))
            match = re.search(r"(\d+)\s*failed", output)
            if match:
                result["failed"] = int(match.group(1))

        result["total"] = result["passed"] + result["failed"] + result["skipped"]
        result["raw_output"] = output

    except subprocess.TimeoutExpired:
        result["error"] = "测试运行超时（600秒）"
    except FileNotFoundError:
        result["error"] = "测试命令未找到，请确认已安装测试框架"
    except Exception as e:
        result["error"] = str(e)

    return result


def main(project_path: str, headed: bool = False, browser: str = "", output_path: str = "") -> dict:
    """
    运行 E2E 测试并收集结果

    Args:
        project_path: 项目根目录
        headed: 是否有头模式
        browser: 指定浏览器
        output_path: 结果输出 JSON 路径

    Returns:
        dict: 测试结果
    """
    project_path = str(project_path)
    print(f"项目路径: {project_path}")
    print(f"有头模式: {'是' if headed else '否'}")
    if browser:
        print(f"浏览器: {browser}")
    print("")

    framework = detect_e2e_framework(project_path)
    print(f"E2E 框架: {framework}")
    print("")

    result = run_tests(project_path, framework, headed, browser)

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
    if "error" in result:
        print(f"  错误: {result['error']}")

    # 保存结果
    if output_path:
        save_json(result, output_path)
        print(f"\n结果已保存到: {output_path}")

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="运行 E2E 测试并收集结果")
    parser.add_argument("project_path", help="项目根目录路径")
    parser.add_argument("--headed", action="store_true", help="有头模式（可视化）")
    parser.add_argument("--browser", "-b", default="", help="指定浏览器 (chromium/firefox/webkit)")
    parser.add_argument("--output", "-o", default="", help="结果输出 JSON 路径")

    args = parser.parse_args()
    main(args.project_path, args.headed, args.browser, args.output)
