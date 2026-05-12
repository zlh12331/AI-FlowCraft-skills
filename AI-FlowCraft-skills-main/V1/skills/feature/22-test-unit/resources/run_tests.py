#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
"""
单元测试辅助脚本 - 测试运行器
功能：运行项目中的单元测试，收集覆盖率数据，输出 JSON 格式结果
用法：python run_tests.py <项目路径> [--coverage] [--output <输出JSON路径>]
"""

import os
import sys
import json
import re
import subprocess
import xml.etree.ElementTree as ET  # 用于解析 JaCoCo XML 覆盖率报告
from pathlib import Path
from typing import Any

from common import detect_project_type, write_json, JS_PROJECT_TYPES, DEFAULT_TIMEOUT, COMPILE_TIMEOUT


def _run_command(cmd: list[str], timeout: int = DEFAULT_TIMEOUT, cwd: str | None = None) -> dict[str, str | None]:
    """
    执行子进程命令，统一处理超时和异常

    Args:
        cmd: 命令列表
        timeout: 超时时间（秒）
        cwd: 工作目录

    Returns:
        dict: {"output": str, "error": str|None}
    """
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        return {"output": proc.stdout + "\n" + proc.stderr, "error": None}
    except subprocess.TimeoutExpired as e:
        # 保留超时前的部分输出，便于调试
        raw = (e.stdout or b"").decode("utf-8", errors="ignore") + (e.stderr or b"").decode("utf-8", errors="ignore")
        return {"output": raw, "error": f"测试运行超时（{timeout}秒）"}
    except Exception as e:
        return {"output": "", "error": str(e)}


def detect_test_framework(project_path: str, project_type: str) -> str:
    """
    检测已安装的测试框架

    Args:
        project_path: 项目根目录
        project_type: 项目类型

    Returns:
        str: 测试框架名称
    """
    # --- JavaScript 及其子类型（nextjs, react, vue, nuxtjs, angular, svelte）共用 JS 框架检测 ---
    if project_type in JS_PROJECT_TYPES:
        # 检查 package.json 中的 devDependencies
        pkg = Path(project_path) / "package.json"
        if pkg.exists():
            content = pkg.read_text(encoding="utf-8", errors="ignore")
            if "vitest" in content:
                return "vitest"
            if "jest" in content:
                return "jest"
            if "mocha" in content:
                return "mocha"
        return "jest"  # 默认 Jest
    elif project_type == "python":
        # 检查是否安装了 pytest
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return "pytest"
        except Exception:
            pass
        return "unittest"
    elif project_type == "java":
        if (Path(project_path) / "pom.xml").exists():
            return "junit-maven"
        return "junit-gradle"
    elif project_type == "go":
        return "go-testing"
    elif project_type == "rust":
        # Rust 默认使用 cargo test
        return "cargo-test"
    elif project_type == "csharp":
        # C# 框架检测：扫描 *.csproj 文件中的包引用
        p = Path(project_path)
        for csproj in p.glob("*.csproj"):
            content = csproj.read_text(encoding="utf-8", errors="ignore")
            # 按优先级检查常见测试框架
            if "xunit" in content.lower():
                return "xunit"
            if "nunit" in content.lower():
                return "nunit"
            if "mstest" in content.lower():
                return "mstest"
        # 未识别到具体框架时返回默认值
        return "dotnet-test"
    return "unknown"


def run_js_tests(project_path: str, framework: str, with_coverage: bool) -> dict[str, Any]:
    """
    运行 JavaScript/TypeScript 测试

    Args:
        project_path: 项目根目录
        framework: 测试框架名称
        with_coverage: 是否收集覆盖率

    Returns:
        dict: 测试结果
    """
    result = {"framework": framework, "passed": 0, "failed": 0, "skipped": 0, "total": 0}

    cmd = []
    if framework == "vitest":
        cmd = ["npx", "vitest", "run", "--reporter=verbose"]
        if with_coverage:
            cmd.append("--coverage")
    elif framework == "jest":
        cmd = ["npx", "jest", "--verbose"]
        if with_coverage:
            cmd.extend(["--coverage", "--coverageDirectory=coverage"])
    elif framework == "mocha":
        if with_coverage:
            # 使用 spec reporter（文本格式），使后续正则可以匹配
            mocha_cmd = ["npx", "mocha", "--reporter", "spec"]
            cmd = ["npx", "nyc", "--reporter=json"] + mocha_cmd
        else:
            # 使用 spec reporter 而非 json，避免 JSON 输出与文本正则不兼容
            cmd = ["npx", "mocha", "--reporter", "spec"]

    print(f"运行命令: {' '.join(cmd)}")
    cmd_result = _run_command(cmd, timeout=DEFAULT_TIMEOUT, cwd=project_path)
    if cmd_result["error"]:
        result["error"] = cmd_result["error"]
        result["raw_output"] = cmd_result["output"]
        return result
    output = cmd_result["output"]
    print(output)

    # 解析 Jest/Vitest 输出
    # 匹配: Tests: X failed, Y passed, Z total（逗号可选）
    # 兼容 Vitest 无冒号格式: "Tests  1 failed  2 passed  3 total"
    main_match = re.search(r"Tests:?\s*(\d+)\s*failed,?\s*(\d+)\s*passed,?\s*(\d+)\s*total", output)
    if main_match:
        result["failed"] = int(main_match.group(1))
        result["passed"] = int(main_match.group(2))
        result["total"] = int(main_match.group(3))
    else:
        # 尝试匹配其他格式（添加词边界避免误匹配）
        match = re.search(r"\b(\d+)\s+passed\b", output)
        if match:
            result["passed"] = int(match.group(1))
        match = re.search(r"\b(\d+)\s+failed\b", output)
        if match:
            result["failed"] = int(match.group(1))

        # Mocha spec reporter 使用 "passing/failing/pending" 而非 "passed/failed"
        # 格式: "  X passing" "  Y failing" "  Z pending"
        if result["passed"] == 0:
            mocha_pass = re.search(r"\b(\d+)\s+passing\b", output)
            if mocha_pass:
                result["passed"] = int(mocha_pass.group(1))
        if result["failed"] == 0:
            mocha_fail = re.search(r"\b(\d+)\s+failing\b", output)
            if mocha_fail:
                result["failed"] = int(mocha_fail.group(1))
        # Mocha 的 pending 等同于 skipped
        mocha_skip = re.search(r"\b(\d+)\s+pending\b", output)
        if mocha_skip:
            result["skipped"] = int(mocha_skip.group(1))

    # 尝试解析 skipped 数量
    skipped_match = re.search(r"\b(\d+)\s+skipped\b", output, re.IGNORECASE)
    if skipped_match:
        result["skipped"] = int(skipped_match.group(1))

    # 仅在主正则未匹配时才重新计算 total（避免覆盖主正则的精确值）
    if main_match is None:
        # 优先从输出中提取 total（Jest 的 total 包含 todo 等额外计数）
        total_match = re.search(r"(\d+)\s+total\b", output)
        if total_match:
            result["total"] = int(total_match.group(1))
        else:
            result["total"] = result["passed"] + result["failed"] + result["skipped"] + result.get("errors", 0)
    result["raw_output"] = output

    # 解析覆盖率
    if with_coverage:
        result["coverage"] = _parse_js_coverage(output, project_path)

    return result


def run_python_tests(project_path: str, framework: str, with_coverage: bool) -> dict[str, Any]:
    """
    运行 Python 测试

    Args:
        project_path: 项目根目录
        framework: 测试框架名称
        with_coverage: 是否收集覆盖率

    Returns:
        dict: 测试结果
    """
    result = {"framework": framework, "passed": 0, "failed": 0, "skipped": 0, "total": 0}

    if framework == "pytest":
        cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short"]
        if with_coverage:
            cmd.extend(["--cov=.", "--cov-report=term-missing", "--cov-report=json:coverage.json"])
    else:
        cmd = [sys.executable, "-m", "unittest", "discover", "-v"]

    print(f"运行命令: {' '.join(cmd)}")
    cmd_result = _run_command(cmd, timeout=DEFAULT_TIMEOUT, cwd=project_path)
    if cmd_result["error"]:
        result["error"] = cmd_result["error"]
        result["raw_output"] = cmd_result["output"]
        return result
    output = cmd_result["output"]
    print(output)

    # 解析 pytest 输出
    # 匹配: X passed, Y failed, Z skipped（添加词边界避免误匹配）
    match = re.search(r"\b(\d+)\s+passed\b", output)
    if match:
        result["passed"] = int(match.group(1))
    match = re.search(r"\b(\d+)\s+failed\b", output)
    if match:
        result["failed"] = int(match.group(1))
    match = re.search(r"\b(\d+)\s+skipped\b", output)
    if match:
        result["skipped"] = int(match.group(1))
    # 添加词边界，避免 "errors" 匹配到 "error_summary" 等词
    match = re.search(r"\b(\d+)\s+errors?\b", output)
    if match:
        result["errors"] = int(match.group(1))

    result["total"] = result["passed"] + result["failed"] + result["skipped"] + result.get("errors", 0)
    result["raw_output"] = output

    # 解析覆盖率（从 coverage.json 读取）
    if with_coverage:
        cov_file = Path(project_path) / "coverage.json"
        if cov_file.exists():
            result["coverage"] = _parse_python_coverage(cov_file)
        else:
            # 从终端输出解析覆盖率
            result["coverage"] = _parse_coverage_from_output(output)

    return result


def run_java_tests(project_path: str, framework: str, with_coverage: bool) -> dict[str, Any]:
    """
    运行 Java 测试

    Args:
        project_path: 项目根目录
        framework: 测试框架名称
        with_coverage: 是否收集覆盖率

    Returns:
        dict: 测试结果
    """
    result = {"framework": framework, "passed": 0, "failed": 0, "skipped": 0, "total": 0}

    if framework == "junit-maven":
        cmd = ["mvn", "test"]
        if with_coverage:
            cmd.append("-Djacoco.skip=false")
    else:
        # 优先使用 ./gradlew（Gradle Wrapper），不存在时回退到 gradle
        if (Path(project_path) / "gradlew").exists():
            cmd = ["./gradlew", "test"]
        else:
            cmd = ["gradle", "test"]
        if with_coverage:
            cmd.append("jacocoTestReport")

    print(f"运行命令: {' '.join(cmd)}")
    cmd_result = _run_command(cmd, timeout=COMPILE_TIMEOUT, cwd=project_path)
    if cmd_result["error"]:
        result["error"] = cmd_result["error"]
        result["raw_output"] = cmd_result["output"]
        return result
    output = cmd_result["output"]
    print(output)

    # 解析 Maven/Gradle 输出
    # Maven: Tests run: X, Failures: Y, Skips: Z
    match = re.search(r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Skips:\s*(\d+)", output)
    if match:
        result["total"] = int(match.group(1))
        result["failed"] = int(match.group(2))
        result["skipped"] = int(match.group(3))
        result["passed"] = result["total"] - result["failed"] - result["skipped"]

    result["raw_output"] = output

    # 读取 JaCoCo XML 覆盖率报告
    if with_coverage:
        # 根据构建工具确定 JaCoCo 报告路径
        if framework == "junit-maven":
            # Maven 项目：JaCoCo 默认输出到 target/site/jacoco/jacoco.xml
            jacoco_xml = Path(project_path) / "target" / "site" / "jacoco" / "jacoco.xml"
        else:
            # Gradle 项目：JaCoCo 默认输出到 build/reports/jacoco/test/jacocoTestReport.xml
            jacoco_xml = Path(project_path) / "build" / "reports" / "jacoco" / "test" / "jacocoTestReport.xml"

        if jacoco_xml.exists():
            try:
                tree = ET.parse(jacoco_xml)
                root = tree.getroot()
                coverage = {}
                # 只读取 <report> 直接子元素的 counter（顶层汇总值），
                # 避免被内层 counter 覆盖导致覆盖率数据不准确
                for counter in root.findall("counter"):
                    ctype = counter.get("type", "")
                    missed = int(counter.get("missed", 0))
                    covered = int(counter.get("covered", 0))
                    total = covered + missed
                    if total > 0:
                        pct = round(covered / total * 100, 1)
                    else:
                        pct = 0.0
                    # 将类型名转为小写作为键名，与其它语言的覆盖率格式保持一致
                    if ctype == "LINE":
                        coverage["line"] = pct
                    elif ctype == "BRANCH":
                        coverage["branch"] = pct
                    elif ctype == "METHOD":
                        coverage["method"] = pct
                if coverage:
                    result["coverage"] = coverage
            except Exception:
                pass  # XML 解析失败时静默忽略，不影响测试结果

    return result


def run_go_tests(project_path: str, framework: str, with_coverage: bool) -> dict[str, Any]:
    """
    运行 Go 测试

    Args:
        project_path: 项目根目录
        framework: 测试框架名称
        with_coverage: 是否收集覆盖率

    Returns:
        dict: 测试结果
    """
    result = {"framework": framework, "passed": 0, "failed": 0, "skipped": 0, "total": 0}

    cmd = ["go", "test", "-v", "./..."]
    if with_coverage:
        cmd.extend(["-coverprofile=coverage.out", "-covermode=atomic"])

    print(f"运行命令: {' '.join(cmd)}")
    cmd_result = _run_command(cmd, timeout=DEFAULT_TIMEOUT, cwd=project_path)
    if cmd_result["error"]:
        result["error"] = cmd_result["error"]
        result["raw_output"] = cmd_result["output"]
        return result
    output = cmd_result["output"]
    print(output)

    # 解析 go test -v 输出中的 --- PASS: 和 --- FAIL: 行
    # 使用 ^ 锚定行首（配合 re.MULTILINE），因为 \b 在 --- 前无法匹配
    # （- 和 \n 都是非单词字符，之间不存在词边界）
    passed = len(re.findall(r"^---\s+PASS:\s+.+", output, re.MULTILINE))
    failed = len(re.findall(r"^---\s+FAIL:\s+.+", output, re.MULTILINE))
    skipped = len(re.findall(r"^---\s+SKIP:\s+.+", output, re.MULTILINE))
    result["passed"] = passed
    result["failed"] = failed
    result["skipped"] = skipped

    result["total"] = result["passed"] + result["failed"] + result["skipped"]

    # 解析覆盖率
    if with_coverage:
        cov_match = re.search(r"coverage:\s*([\d.]+)%", output)
        if cov_match:
            result["coverage"] = {
                "statement": float(cov_match.group(1))
            }

    result["raw_output"] = output

    return result


def run_rust_tests(project_path: str, framework: str, with_coverage: bool) -> dict[str, Any]:
    """
    运行 Rust 测试

    使用 cargo test 运行测试；覆盖率工具优先使用 cargo-tarpaulin，
    不可用时回退到 cargo-llvm-cov。

    Args:
        project_path: 项目根目录
        framework: 测试框架名称（此处固定为 "cargo-test"）
        with_coverage: 是否收集覆盖率

    Returns:
        dict: 测试结果
    """
    result = {"framework": framework, "passed": 0, "failed": 0, "skipped": 0, "total": 0}

    # --- 构建测试命令 ---
    if with_coverage:
        # 优先尝试 cargo-tarpaulin（输出更友好，支持 HTML/JSON）
        cmd = ["cargo", "tarpaulin", "--out", "Stdout", "--out", "Json"]
    else:
        cmd = ["cargo", "test"]

    print(f"运行命令: {' '.join(cmd)}")
    cmd_result = _run_command(cmd, timeout=COMPILE_TIMEOUT, cwd=project_path)
    if cmd_result["error"]:
        result["error"] = cmd_result["error"]
        result["raw_output"] = cmd_result["output"]
        return result
    output = cmd_result["output"]
    print(output)

    # --- 解析 cargo test 输出 ---
    # 匹配格式: test result: ok. X passed; Y failed; Z ignored; 0 measured; 0 filtered out
    # 或:     test result: FAILED. X passed; Y failed; Z ignored
    match = re.search(
        r"test result:\s*(ok|FAILED)\.\s*(\d+)\s*passed;\s*(\d+)\s*failed;\s*(\d+)\s*ignored",
        output
    )
    if match:
        result["passed"] = int(match.group(2))
        result["failed"] = int(match.group(3))
        result["skipped"] = int(match.group(4))  # Rust 中 "ignored" 等同于跳过
        result["total"] = result["passed"] + result["failed"] + result["skipped"]
    else:
        # 备用匹配：尝试从汇总行提取 passed / failed（添加词边界避免误匹配）
        passed_match = re.search(r"\b(\d+)\s+passed\b", output)
        if passed_match:
            result["passed"] = int(passed_match.group(1))
        failed_match = re.search(r"\b(\d+)\s+failed\b", output)
        if failed_match:
            result["failed"] = int(failed_match.group(1))
        result["total"] = result["passed"] + result["failed"] + result["skipped"]

    # --- 解析覆盖率 ---
    if with_coverage:
        # cargo-tarpaulin 会在输出中包含覆盖率百分比
        cov_match = re.search(r"(\d+\.\d+)%\s*coverage", output)
        if cov_match:
            result["coverage"] = {"statement": float(cov_match.group(1))}
        else:
            # 尝试从 tarpaulin 的 JSON 输出文件中读取
            tarpaulin_json = Path(project_path) / "tarpaulin-report.json"
            if tarpaulin_json.exists():
                try:
                    cov_data = json.loads(tarpaulin_json.read_text(encoding="utf-8"))
                    result["coverage"] = {
                        "statement": float(cov_data.get("coverage", 0))
                    }
                except Exception:
                    pass

    result["raw_output"] = output

    return result


def run_csharp_tests(project_path: str, framework: str, with_coverage: bool) -> dict[str, Any]:
    """
    运行 C# 测试

    使用 dotnet test 运行测试；覆盖率通过 --collect:"XPlat Code Coverage" 收集。

    Args:
        project_path: 项目根目录
        framework: 测试框架名称（xunit / nunit / mstest / dotnet-test）
        with_coverage: 是否收集覆盖率

    Returns:
        dict: 测试结果
    """
    result = {"framework": framework, "passed": 0, "failed": 0, "skipped": 0, "total": 0}

    # --- 构建测试命令 ---
    cmd = ["dotnet", "test"]
    if with_coverage:
        # 使用跨平台代码覆盖率收集器
        cmd.extend(["--collect", "XPlat Code Coverage"])

    print(f"运行命令: {' '.join(cmd)}")
    cmd_result = _run_command(cmd, timeout=DEFAULT_TIMEOUT, cwd=project_path)
    if cmd_result["error"]:
        result["error"] = cmd_result["error"]
        result["raw_output"] = cmd_result["output"]
        return result
    output = cmd_result["output"]
    print(output)

    # --- 解析 dotnet test 输出 ---
    # 匹配格式: Passed!  - Failed: X, Passed: Y, Skipped: Z
    match = re.search(
        r"(Passed|Failed)!\s*-\s*Failed:\s*(\d+),\s*Passed:\s*(\d+),\s*Skipped:\s*(\d+)",
        output
    )
    if match:
        result["failed"] = int(match.group(2))
        result["passed"] = int(match.group(3))
        result["skipped"] = int(match.group(4))
        result["total"] = result["passed"] + result["failed"] + result["skipped"]
    else:
        # 备用匹配：添加更精确的上下文约束，避免误匹配无关数字
        passed_match = re.search(r"\bPassed!\s*-\s*Passed:\s*(\d+)", output)
        if not passed_match:
            passed_match = re.search(r"\bPassed:\s*(\d+)", output)
        if passed_match:
            result["passed"] = int(passed_match.group(1))
        failed_match = re.search(r"\bFailed:\s*(\d+)", output)
        if failed_match:
            result["failed"] = int(failed_match.group(1))
        skipped_match = re.search(r"\bSkipped:\s*(\d+)", output)
        if skipped_match:
            result["skipped"] = int(skipped_match.group(1))
        result["total"] = result["passed"] + result["failed"] + result["skipped"]

    # --- 解析覆盖率 ---
    if with_coverage:
        # dotnet test 会在输出中打印覆盖率摘要
        # 格式: | Module  | Line  | Branch | Method |
        #        | Total   | XX.X% | XX.X%  | XX.X%  |
        line_cov = re.search(r"Line\s*\|\s*([\d.]+)%", output)
        branch_cov = re.search(r"Branch\s*\|\s*([\d.]+)%", output)
        method_cov = re.search(r"Method\s*\|\s*([\d.]+)%", output)
        coverage = {}
        if line_cov:
            coverage["line"] = float(line_cov.group(1))
        if branch_cov:
            coverage["branch"] = float(branch_cov.group(1))
        if method_cov:
            coverage["method"] = float(method_cov.group(1))
        # 如果正则未能从 stdout 匹配到覆盖率，尝试从 Cobertura XML 文件中解析
        # dotnet test --collect "XPlat Code Coverage" 会在 TestResults 目录下生成 coverage.cobertura.xml
        if not coverage:
            try:
                # 在项目目录下递归查找 Cobertura XML 覆盖率文件
                project_dir = Path(project_path)
                cobertura_files = list(project_dir.rglob("coverage.cobertura.xml"))
                if cobertura_files:
                    # 取第一个找到的覆盖率文件进行解析
                    cob_tree = ET.parse(str(cobertura_files[0]))
                    cob_root = cob_tree.getroot()
                    # Cobertura XML 顶层 <coverage> 元素的 line-rate 和 branch-rate 属性
                    # 值为 0-1 的小数，需要转换为百分比
                    line_rate = cob_root.get("line-rate")
                    branch_rate = cob_root.get("branch-rate")
                    if line_rate is not None:
                        coverage["line"] = round(float(line_rate) * 100, 1)
                    if branch_rate is not None:
                        coverage["branch"] = round(float(branch_rate) * 100, 1)
            except Exception:
                pass  # Cobertura XML 解析失败时静默忽略，不影响测试结果
        if coverage:
            result["coverage"] = coverage

    result["raw_output"] = output

    return result


def _parse_js_coverage(output: str, project_path: str) -> dict[str, float]:
    """
    解析 JavaScript 测试覆盖率

    Args:
        output: 测试输出
        project_path: 项目路径

    Returns:
        dict: 覆盖率数据
    """
    coverage = {}
    # 从终端输出解析 Jest/Vitest 覆盖率
    # 格式: Statements : 80% ( 120/150 ), Branches : 70% ( 35/50 ), ...
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
            data = json.loads(summary_file.read_text(encoding="utf-8"))
            total = data.get("total", {})
            # 使用显式 None 检查，避免 JSON 中 pct 为 null 时覆盖终端解析的有效值
            for key, json_key in [("statement", "statements"), ("branch", "branches"),
                                   ("function", "functions"), ("line", "lines")]:
                pct = total.get(json_key, {}).get("pct")
                if pct is not None:
                    coverage[key] = pct
        except Exception:
            pass

    return coverage


def _parse_python_coverage(cov_file: Path) -> dict[str, Any]:
    """
    从 coverage.json 解析 Python 覆盖率

    Args:
        cov_file: coverage.json 文件路径

    Returns:
        dict: 覆盖率数据
    """
    try:
        data = json.loads(cov_file.read_text(encoding="utf-8"))
        totals = data.get("totals", {})
        return {
            "statement": round(totals.get("percent_covered") or 0, 1),
            "missing_lines": totals.get("missing_lines", 0),
            "excluded_lines": totals.get("excluded_lines", 0),
        }
    except Exception:
        return {}


def _parse_coverage_from_output(output: str) -> dict[str, float]:
    """
    从终端输出解析覆盖率

    Args:
        output: 测试输出

    Returns:
        dict: 覆盖率数据
    """
    coverage = {}
    # pytest-cov 输出格式: TOTAL  120 30 80%
    match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
    if match:
        coverage["statement"] = float(match.group(1))
    return coverage


def run_tests(project_path: str, with_coverage: bool = False, output_path: str = "") -> dict[str, Any]:
    """
    运行项目测试并收集结果

    Args:
        project_path: 项目根目录
        with_coverage: 是否收集覆盖率
        output_path: 结果输出 JSON 路径

    Returns:
        dict: 测试结果
    """
    project_path = str(Path(project_path).resolve())
    print(f"项目路径: {project_path}")
    print(f"收集覆盖率: {'是' if with_coverage else '否'}")
    print("")

    # 验证项目路径存在
    if not Path(project_path).exists():
        print(f"错误：项目路径不存在: {project_path}")
        return {"error": "项目路径不存在"}

    # 检测项目类型和测试框架
    project_type = detect_project_type(project_path)
    framework = detect_test_framework(project_path, project_type)
    print(f"项目类型: {project_type}")
    print(f"测试框架: {framework}")
    print("")

    # 运行测试（JS 子类型共用 run_js_tests）
    if project_type in JS_PROJECT_TYPES:
        result = run_js_tests(project_path, framework, with_coverage)
    elif project_type == "python":
        result = run_python_tests(project_path, framework, with_coverage)
    elif project_type == "java":
        result = run_java_tests(project_path, framework, with_coverage)
    elif project_type == "go":
        result = run_go_tests(project_path, framework, with_coverage)
    elif project_type == "rust":
        result = run_rust_tests(project_path, framework, with_coverage)
    elif project_type == "csharp":
        result = run_csharp_tests(project_path, framework, with_coverage)
    else:
        result = {"error": f"不支持的项目类型: {project_type}"}

    # 计算通过率
    total = result.get("total", 0)
    passed = result.get("passed", 0)
    result["pass_rate"] = round(passed / total * 100, 1) if total > 0 else 0
    result["project_type"] = project_type
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

    # 保存结果
    if output_path:
        write_json(result, output_path)
        print(f"\n结果已保存到: {output_path}")

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="运行单元测试并收集覆盖率")
    parser.add_argument("project_path", help="项目路径")
    parser.add_argument("--coverage", action="store_true", help="是否收集覆盖率")
    parser.add_argument("--output", "-o", default="", help="测试结果输出 JSON 路径")
    args = parser.parse_args()
    result = run_tests(args.project_path, args.coverage, args.output)
    if result.get("error"):
        print(f"错误：{result['error']}", file=sys.stderr)
        sys.exit(1)
    elif result.get("failed", 0) > 0:
        sys.exit(1)
