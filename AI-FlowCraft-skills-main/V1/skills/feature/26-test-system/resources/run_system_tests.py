#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试辅助脚本 - 测试运行器
功能：运行系统测试（功能/性能/安全），收集结果
用法：python run_system_tests.py <项目路径> [--type all|functional|performance|security] [--output <JSON>]
"""

import json
import re
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

from common import save_json


def run_tests(project_path: str, test_type: str = "all") -> dict:
    """
    运行系统测试

    Args:
        project_path: 项目根目录
        test_type: 测试类型 (all/functional/performance/security/health)

    Returns:
        dict: 测试结果
    """
    result = {"test_type": test_type, "passed": 0, "failed": 0, "skipped": 0, "total": 0}

    # 记录测试开始时间
    start_time = time.time()

    if test_type in ("all", "functional"):
        func_result = _run_functional_tests(project_path)
        result.setdefault("functional", {}).update(func_result)
        result["passed"] += func_result.get("passed", 0)
        result["failed"] += func_result.get("failed", 0)
        result["skipped"] += func_result.get("skipped", 0)

    if test_type in ("all", "security"):
        sec_result = _run_security_tests(project_path)
        result.setdefault("security", {}).update(sec_result)

    if test_type in ("all", "performance"):
        perf_result = _run_performance_tests(project_path)
        result.setdefault("performance", {}).update(perf_result)

    if test_type in ("all", "health"):
        health_result = _run_health_check_tests(project_path)
        result.setdefault("health", {}).update(health_result)
        result["passed"] += health_result.get("passed", 0)
        result["failed"] += health_result.get("failed", 0)
        result["skipped"] += health_result.get("skipped", 0)

    result["total"] = result["passed"] + result["failed"] + result["skipped"]
    total = result["total"]
    passed = result["passed"]
    result["pass_rate"] = round(passed / total * 100, 1) if total > 0 else 0

    # 记录执行时间和时间戳
    result["duration"] = round(time.time() - start_time, 2)
    result["timestamp"] = datetime.now().isoformat()

    return result


def _run_functional_tests(project_path: str) -> dict:
    """
    运行功能性系统测试（Playwright）

    Args:
        project_path: 项目根目录

    Returns:
        dict: 测试结果
    """
    result = {"framework": "playwright", "passed": 0, "failed": 0, "skipped": 0}

    cmd = ["npx", "playwright", "test", "--workers=1", "--reporter=list"]
    print(f"\n[功能性测试] 运行: {' '.join(cmd)}")

    try:
        proc = subprocess.run(cmd, cwd=project_path, capture_output=True, text=True, timeout=600)
        output = proc.stdout + proc.stderr
        print(output)

        # 从输出中解析 PASS/FAIL 数量
        passed = len(re.findall(r"\[PASS\]", output))
        failed = len(re.findall(r"\[FAIL\]", output))
        result["passed"] = passed
        result["failed"] = failed
        result["total"] = passed + failed
        result["raw_output"] = output
    except subprocess.TimeoutExpired:
        result["error"] = "测试运行超时（600秒）"
    except Exception as e:
        result["error"] = str(e)

    return result


def _run_security_tests(project_path: str) -> dict:
    """
    运行安全测试（npm audit + pip audit + cargo audit）

    Args:
        project_path: 项目根目录

    Returns:
        dict: 测试结果
    """
    result = {"framework": "npm-audit", "vulnerabilities": {}}

    pkg = Path(project_path) / "package.json"
    if not pkg.exists():
        result["error"] = "未找到 package.json"
        return result

    # npm audit
    print(f"\n[安全测试] 运行 npm audit...")
    _run_npm_audit(project_path, result)

    # pip audit（Python 项目）
    req = Path(project_path) / "requirements.txt"
    if req.exists():
        print(f"\n[安全测试] 运行 pip audit...")
        _run_pip_audit(project_path, result)

    # cargo audit（Rust 项目）
    cargo_toml = Path(project_path) / "Cargo.toml"
    if cargo_toml.exists():
        print(f"\n[安全测试] 运行 cargo audit...")
        _run_cargo_audit(project_path, result)

    return result


def _run_npm_audit(project_path: str, result: dict):
    """运行 npm audit 并合并结果"""
    try:
        proc = subprocess.run(
            ["npm", "audit", "--json"],
            cwd=project_path, capture_output=True, text=True, timeout=120
        )
        output = proc.stdout + proc.stderr

        try:
            audit_data = json.loads(output)
            vulns = audit_data.get("vulnerabilities", {})
            result["vulnerabilities"] = {
                "critical": len(vulns.get("critical", [])),
                "high": len(vulns.get("high", [])),
                "moderate": len(vulns.get("moderate", [])),
                "low": len(vulns.get("low", [])),
                "info": len(vulns.get("info", [])),
            }
            result["total"] = sum(result["vulnerabilities"].values())
            print(f"  发现漏洞: {result['vulnerabilities']}")
        except json.JSONDecodeError:
            print(f"  npm audit 输出: {output[:500]}")
            result["raw_output"] = output

    except subprocess.TimeoutExpired:
        result["error"] = "安全审计超时"
    except Exception as e:
        result["error"] = str(e)


def _run_pip_audit(project_path: str, result: dict):
    """运行 pip audit 并合并结果"""
    try:
        proc = subprocess.run(
            ["pip", "audit", "--format", "json"],
            cwd=project_path, capture_output=True, text=True, timeout=120
        )
        pip_output = proc.stdout + proc.stderr
        try:
            pip_data = json.loads(pip_output)
            pip_vulns = pip_data.get("vulnerabilities", [])
            if pip_vulns:
                for vuln in pip_vulns:
                    sev = vuln.get("severity", "medium").lower()
                    if sev in result["vulnerabilities"]:
                        result["vulnerabilities"][sev] += 1
                    else:
                        result["vulnerabilities"][sev] = 1
                print(f"  pip audit 发现漏洞: {len(pip_vulns)}")
        except json.JSONDecodeError:
            result["pip_audit_raw"] = pip_output[:500]
    except FileNotFoundError:
        print(f"  pip audit 未安装，跳过 Python 依赖审计")
    except subprocess.TimeoutExpired:
        result["pip_audit_timeout"] = True


def _run_cargo_audit(project_path: str, result: dict):
    """运行 cargo audit 并合并结果"""
    try:
        proc = subprocess.run(
            ["cargo", "audit", "--json"],
            cwd=project_path, capture_output=True, text=True, timeout=120
        )
        cargo_output = proc.stdout + proc.stderr
        try:
            cargo_data = json.loads(cargo_output)
            cargo_vulns = cargo_data.get("vulnerabilities", {}).get("list", [])
            if cargo_vulns:
                for vuln in cargo_vulns:
                    sev = vuln.get("severity", {}).get("severity", "medium").lower()
                    if sev in result["vulnerabilities"]:
                        result["vulnerabilities"][sev] += 1
                    else:
                        result["vulnerabilities"][sev] = 1
                print(f"  cargo audit 发现漏洞: {len(cargo_vulns)}")
        except json.JSONDecodeError:
            result["cargo_audit_raw"] = cargo_output[:500]
    except FileNotFoundError:
        print(f"  cargo audit 未安装，跳过 Rust 依赖审计")
    except subprocess.TimeoutExpired:
        result["cargo_audit_timeout"] = True


def _run_performance_tests(project_path: str) -> dict:
    """
    运行性能测试（检查是否有 k6）

    Args:
        project_path: 项目根目录

    Returns:
        dict: 测试结果
    """
    result = {"framework": "k6", "metrics": {}}

    # 检查 k6 是否可用
    try:
        proc = subprocess.run(["k6", "version"], capture_output=True, text=True, timeout=10)
        if proc.returncode != 0:
            result["error"] = "k6 未安装。安装: brew install k6 或 https://k6.io/docs/getting-started/installation/"
            return result
    except FileNotFoundError:
        result["error"] = "k6 未安装"
        return result

    print(f"\n[性能测试] 运行 k6...")
    try:
        proc = subprocess.run(
            ["k6", "run", "--no-summary", "--out", "json=perf-results.json"],
            cwd=project_path, capture_output=True, text=True, timeout=300
        )
        output = proc.stdout + proc.stderr
        print(output[:2000])
        result["raw_output"] = output
    except subprocess.TimeoutExpired:
        result["error"] = "性能测试超时（300秒）"
    except Exception as e:
        result["error"] = str(e)

    return result


def _run_health_check_tests(project_path: str) -> dict:
    """
    运行健康检查测试（Playwright）

    Args:
        project_path: 项目根目录

    Returns:
        dict: 测试结果
    """
    result = {"framework": "playwright", "passed": 0, "failed": 0, "skipped": 0}

    # 查找健康检查测试目录（支持两种路径）
    health_test_dir = Path(project_path) / "system-tests" / "health"
    if not health_test_dir.exists():
        health_test_dir = Path(project_path) / "tests" / "system" / "health"

    if not health_test_dir.exists():
        result["error"] = "未找到健康检查测试文件"
        return result

    # 安全检查：确保路径在项目目录内，防止路径遍历
    health_test_dir = health_test_dir.resolve()
    project_dir = Path(project_path).resolve()
    try:
        health_test_dir.relative_to(project_dir)
    except ValueError:
        result["error"] = f"健康检查测试路径不在项目目录内: {health_test_dir}"
        return result

    cmd = ["npx", "playwright", "test", str(health_test_dir), "--workers=1", "--reporter=list"]
    print(f"\n[健康检查] 运行: {' '.join(cmd)}")

    try:
        proc = subprocess.run(cmd, cwd=project_path, capture_output=True, text=True, timeout=120)
        output = proc.stdout + proc.stderr
        print(output)

        # 从输出中解析 PASS/FAIL 数量
        passed = len(re.findall(r"\[PASS\]", output))
        failed = len(re.findall(r"\[FAIL\]", output))
        result["passed"] = passed
        result["failed"] = failed
        result["total"] = passed + failed
        result["raw_output"] = output
    except subprocess.TimeoutExpired:
        result["error"] = "健康检查超时（120秒）"
    except Exception as e:
        result["error"] = str(e)

    return result


def main(project_path: str, test_type: str = "all", output_path: str = ""):
    """
    运行系统测试并收集结果

    Args:
        project_path: 项目根目录
        test_type: 测试类型
        output_path: 结果输出路径

    Returns:
        dict: 测试结果
    """
    print(f"项目路径: {project_path}")
    print(f"测试类型: {test_type}")
    print("")

    result = run_tests(project_path, test_type)
    result["project_path"] = project_path

    print(f"\n系统测试结果:")
    print(f"  总数: {result.get('total', 0)}")
    print(f"  通过: {result.get('passed', 0)}")
    print(f"  失败: {result.get('failed', 0)}")
    print(f"  通过率: {result.get('pass_rate', 0)}%")

    if "security" in result and result["security"].get("vulnerabilities"):
        vulns = result["security"]["vulnerabilities"]
        print(f"  安全漏洞: critical={vulns.get('critical',0)} high={vulns.get('high',0)} moderate={vulns.get('moderate',0)}")

    if output_path:
        save_json(result, output_path)
        print(f"\n结果已保存到: {output_path}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="运行系统测试")
    parser.add_argument("project_path", help="项目根目录路径")
    parser.add_argument("--type", "-t", default="all", choices=["all", "functional", "performance", "security", "health"])
    parser.add_argument("--output", "-o", default="", help="结果输出 JSON 路径")

    args = parser.parse_args()
    main(args.project_path, args.type, args.output)
