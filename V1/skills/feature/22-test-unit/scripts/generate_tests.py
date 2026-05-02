#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
"""
单元测试生成脚本
功能：根据扫描结果，自动生成单元测试代码框架
支持：JavaScript/TypeScript (Jest)、Python (pytest)、Java (JUnit 5)、Go (testing)、Rust (testing + test-case)、C# (xUnit)
用法：python generate_tests.py <扫描结果JSON> <输出目录> [项目路径]
"""

import os
import re
import sys
from pathlib import Path

from typing import Any

from common import load_json


# ============================================================
# 公共辅助函数
# ============================================================

def _safe_identifier(name: str) -> str:
    """将名称转换为安全的标识符（仅保留字母、数字、下划线）"""
    return re.sub(r'[^a-zA-Z0-9]', '_', name)


def _safe_exception_name(exc: str) -> str:
    """提取异常的简单类名（去除包路径）"""
    return exc.split(".")[-1] if "." in exc else exc


def _parse_func_params(func: dict[str, Any]) -> tuple[list[str], bool, str]:
    """统一解析函数参数，返回 (参数列表, 是否有参数, 原始参数字符串)"""
    raw_params = func.get("params", "")
    if raw_params in ("无参数", ""):
        return [], False, ""
    param_parts = [p.strip() for p in raw_params.split(",") if p.strip() not in ("self", "cls")]
    return param_parts, len(param_parts) > 0, raw_params


def _group_functions_by_file(functions: list[dict[str, Any]]) -> dict[str, list[dict]]:
    """
    按文件路径分组函数列表

    Args:
        functions: 函数信息列表

    Returns:
        dict: {文件路径: [函数列表]}
    """
    groups = {}
    for func in functions:
        fp = func.get("file", "unknown")
        if fp not in groups:
            groups[fp] = []
        groups[fp].append(func)
    return groups


def _write_test_file(file_path: Path, lines: list[str], output_dir: str, label: str = "已生成") -> None:
    """
    通用测试文件写入（自动创建目录并打印日志）

    Args:
        file_path: 目标文件路径
        lines: 代码行列表
        output_dir: 输出根目录（用于计算相对路径显示）
        label: 日志前缀，默认为"已生成"
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        file_path.write_text("\n".join(lines), encoding="utf-8")
    except OSError as e:
        print(f"错误：无法写入测试文件 {file_path}: {e}")
    try:
        rel_path = file_path.relative_to(Path(output_dir))
    except ValueError:
        rel_path = file_path
    print(f"  {label}: {rel_path}")


def generate_js_tests(functions: list[dict[str, Any]], output_dir: str, project_path: str = "") -> None:
    """
    生成 JavaScript/TypeScript 单元测试代码（Jest 框架）

    Args:
        functions: 函数列表（含分析结果）
        output_dir: 测试文件输出目录
        project_path: 项目根目录（用于读取源码）
    """
    # 按文件分组
    file_groups = _group_functions_by_file(functions)

    for file_path, funcs in file_groups.items():
        # 生成测试文件路径：原文件路径 + .test 后缀
        # 使用 Path 后缀操作，避免 .replace() 全局替换导致 .tsx/.jsx 路径错误
        src_path = Path(file_path)
        if src_path.suffix in (".tsx", ".jsx", ".ts", ".js"):
            test_name = src_path.stem + ".test" + src_path.suffix
            test_file = Path(output_dir) / src_path.parent / test_name
        else:
            test_file = Path(output_dir) / (file_path + ".test")

        # 生成测试代码
        lines = []
        lines.append(f"// 自动生成的单元测试 - {file_path}")
        lines.append(f"// 测试框架: Jest")
        lines.append(f"// 注意：以下测试代码为骨架，AI 需根据源码分析结果填充具体测试值和断言")
        lines.append("")
        # 导入被测模块
        # 使用 os.path.relpath 计算从测试文件到源文件的相对路径，避免基于目录深度推算的不准确性
        src_dir = str(src_path.parent)
        test_dir = str(test_file.parent)
        try:
            rel_dir = os.path.relpath(src_dir, test_dir)
            import_path = (rel_dir + "/" + src_path.stem).replace(os.sep, '/')
        except ValueError:
            # 跨驱动器时 relpath 可能抛出 ValueError，回退到原始逻辑
            depth = src_dir.count(os.sep) + src_dir.count("/")
            prefix = "../" * (depth + 1) if depth >= 0 else "./"
            import_path = prefix + str(Path(file_path).with_suffix("")).replace(os.sep, '/')
        func_names = ", ".join(f['name'] for f in funcs if f.get('name'))
        # 只有存在有效函数名时才生成 import 语句，避免生成 "import { } from '...';"
        if func_names:
            lines.append(f"import {{ {func_names} }} from '{import_path}';")
            lines.append("")

        for func in funcs:
            # 跳过函数名为空的条目，避免后续 KeyError 或生成无效代码
            if not func.get("name"):
                continue
            # 函数注释信息
            docstring = func.get("docstring", "")
            return_type = func.get("return_type", "unknown")
            exceptions = func.get("exceptions", [])
            dependencies = func.get("dependencies", [])
            branches = func.get("branches", 0)

            lines.append(f"describe('{func['name']}', () => {{")
            lines.append(f"  // 函数位置: {func['file']}:{func['line']}")
            lines.append(f"  // 参数: {func['params']}")
            lines.append(f"  // 返回类型: {return_type}")
            if exceptions:
                lines.append(f"  // 可能抛出: {', '.join(exceptions)}")
            if dependencies:
                lines.append(f"  // 外部依赖: {', '.join(dependencies)} → 需要 Mock")
            if branches > 0:
                lines.append(f"  // 条件分支数: {branches} → 至少需要 {branches + 1} 个测试用例")
            if docstring:
                lines.append(f"  // 说明: {docstring.split(chr(10))[0].strip(' /*')}")
            lines.append("")

            # === 正向测试 ===
            lines.append(f"  describe('正向测试', () => {{")
            lines.append(f"    it('正常输入应返回预期结果', () => {{")
            # 根据返回类型生成断言
            if return_type in ("string", "String"):
                lines.append(f"      const result = {func['name']}(/* 替换为正常参数 */);")
                lines.append(f"      expect(typeof result).toBe('string');")
                lines.append(f"      expect(result).not.toBe('');")
            elif return_type in ("number", "Number", "int", "float"):
                lines.append(f"      const result = {func['name']}(/* 替换为正常参数 */);")
                lines.append(f"      expect(typeof result).toBe('number');")
            elif return_type in ("boolean", "Boolean", "bool"):
                lines.append(f"      const result = {func['name']}(/* 替换为正常参数 */);")
                lines.append(f"      expect(typeof result).toBe('boolean');")
            elif return_type in ("Array", "array", "list", "List"):
                lines.append(f"      const result = {func['name']}(/* 替换为正常参数 */);")
                lines.append(f"      expect(Array.isArray(result)).toBe(true);")
            elif return_type in ("Object", "object", "dict", "Dict"):
                lines.append(f"      const result = {func['name']}(/* 替换为正常参数 */);")
                lines.append(f"      expect(result).toBeDefined();")
                lines.append(f"      expect(typeof result).toBe('object');")
            else:
                lines.append(f"      const result = {func['name']}(/* 替换为正常参数 */);")
                lines.append(f"      expect(result).toBeDefined();")
            lines.append(f"    }});")
            lines.append(f"  }});")
            lines.append("")

            # === 边界值测试 ===
            lines.append(f"  describe('边界值测试', () => {{")
            lines.append(f"    it('null/undefined 输入应正确处理', () => {{")
            if exceptions:
                lines.append(f"      // 函数可能抛出 {', '.join(exceptions[:2])}")
                lines.append(f"      expect(() => {func['name']}(null)).toThrow();")
            else:
                lines.append(f"      const result = {func['name']}(null);")
                lines.append(f"      expect(result).toBeDefined();")
            lines.append(f"    }});")
            lines.append("")
            lines.append(f"    it('空字符串/空数组应正确处理', () => {{")
            lines.append(f"      // TODO: 根据参数类型选择合适的空值（''、[]、{{}}、0）")
            lines.append(f"      const result = {func['name']}('' /* 或 [] */);")
            lines.append(f"      expect(result).toBeDefined();")
            lines.append(f"    }});")
            lines.append("")
            lines.append(f"    it('极值输入应正确处理', () => {{")
            lines.append(f"      // TODO: 测试 Number.MAX_SAFE_INTEGER、Number.MIN_SAFE_INTEGER、超长字符串等")
            lines.append(f"      const result = {func['name']}(/* 极值参数 */);")
            lines.append(f"      expect(result).toBeDefined();")
            lines.append(f"    }});")
            lines.append(f"  }});")
            lines.append("")

            # === 类型错误测试 ===
            lines.append(f"  describe('类型错误测试', () => {{")
            lines.append(f"    it('错误类型输入应抛出异常或返回默认值', () => {{")
            lines.append(f"      // TODO: 传入错误类型（如期望字符串传入数字）")
            lines.append(f"      const result = {func['name']}(123 /* 错误类型 */);")
            lines.append(f"      // 根据函数设计，可能是抛异常或返回默认值")
            lines.append(f"      expect(result).toBeDefined();")
            lines.append(f"    }});")
            lines.append(f"  }});")
            lines.append("")

            # === 分支覆盖测试（如有分支） ===
            if branches > 0:
                lines.append(f"  describe('分支覆盖测试', () => {{")
                lines.append(f"    // 函数有 {branches} 个条件分支，需要覆盖每个分支路径")
                lines.append(f"    it('分支路径 1: 条件为 true', () => {{")
                lines.append(f"      // TODO: 构造使第一个条件为 true 的输入")
                lines.append(f"      const result = {func['name']}(/* 使条件为 true 的参数 */);")
                lines.append(f"      expect(result).toBeDefined();")
                lines.append(f"    }});")
                lines.append("")
                lines.append(f"    it('分支路径 2: 条件为 false', () => {{")
                lines.append(f"      // TODO: 构造使第一个条件为 false 的输入")
                lines.append(f"      const result = {func['name']}(/* 使条件为 false 的参数 */);")
                lines.append(f"      expect(result).toBeDefined();")
                lines.append(f"    }});")
                lines.append(f"  }});")
                lines.append("")

            # === 异常测试（如有异常声明） ===
            if exceptions:
                lines.append(f"  describe('异常测试', () => {{")
                for exc in exceptions[:3]:  # 最多生成3个异常测试
                    lines.append(f"    it('应抛出 {exc}', () => {{")
                    lines.append(f"      // TODO: 构造会触发 {exc} 的输入")
                    lines.append(f"      expect(() => {func['name']}(/* 触发异常的参数 */)).toThrow();")
                    lines.append(f"    }});")
                    lines.append("")
                lines.append(f"  }});")
                lines.append("")

            # === 参数化测试 ===
            lines.append(f"  describe('参数化测试', () => {{")
            lines.append(f"    // 使用 test.each 进行参数化测试")
            lines.append(f"    const normalCases = [")
            lines.append(f"      // TODO: 替换为实际的正向测试数据组")
            lines.append(f"      {{ input: null, expected: null, description: '正向用例1' }},")
            lines.append(f"      {{ input: null, expected: null, description: '正向用例2' }},")
            lines.append(f"      {{ input: null, expected: null, description: '正向用例3' }},")
            lines.append(f"    ];")
            lines.append(f"    test.each(normalCases)('$description', ({{ input, expected }}) => {{")
            lines.append(f"      const result = {func['name']}(input);")
            lines.append(f"      expect(result).toBeDefined();")
            lines.append(f"      // TODO: 根据预期值补充断言，如 expect(result).toBe(expected);")
            lines.append(f"    }});")
            lines.append(f"")
            lines.append(f"    const boundaryCases = [")
            lines.append(f"      // TODO: 替换为实际的边界值数据组")
            lines.append(f"      {{ input: null, expected: null, description: '最小边界值' }},")
            lines.append(f"      {{ input: null, expected: null, description: '最大边界值' }},")
            lines.append(f"    ];")
            lines.append(f"    test.each(boundaryCases)('$description', ({{ input, expected }}) => {{")
            lines.append(f"      const result = {func['name']}(input);")
            lines.append(f"      expect(result).toBeDefined();")
            lines.append(f"      // TODO: 根据预期值补充断言")
            lines.append(f"    }});")
            lines.append(f"  }});")
            lines.append("")

            lines.append("});")
            lines.append("")

        # 写入文件
        _write_test_file(test_file, lines, output_dir)


def generate_python_tests(functions: list[dict[str, Any]], output_dir: str, project_path: str = "") -> None:
    """
    生成 Python 单元测试代码（pytest 框架）

    Args:
        functions: 函数列表（含分析结果）
        output_dir: 测试文件输出目录
        project_path: 项目根目录
    """
    # 按文件分组
    file_groups = _group_functions_by_file(functions)

    for file_path, funcs in file_groups.items():
        # 生成测试文件路径（保留子目录结构，避免不同目录下同名文件互相覆盖）
        # 例如: src/utils/helper.py → output_dir/src/utils/test_helper.py
        src_path = Path(file_path)
        test_file = Path(output_dir) / src_path.parent / f"test_{src_path.stem}.py"

        # 计算导入路径
        # 去除前导 ./ 避免生成无效的模块路径（如 from ./.module import ...）
        # 注意：不能使用 lstrip("./")，因为它会逐字符剥离，导致 "lib/utils.py" 变成 "ib/utils.py"
        clean_path = file_path[2:] if file_path.startswith("./") else file_path
        module_path = Path(clean_path).with_suffix("").as_posix().replace("/", ".")

        lines = []
        lines.append(f"# 自动生成的单元测试 - {file_path}")
        lines.append(f"# 测试框架: pytest")
        lines.append(f"# 注意：以下测试代码为骨架，AI 需根据源码分析结果填充具体测试值和断言")
        lines.append("")
        lines.append(f"import pytest")
        py_func_names = ', '.join(f['name'] for f in funcs if f.get('name'))
        # 只有存在有效函数名时才生成 import 语句
        if py_func_names:
            lines.append(f"from {module_path} import {py_func_names}")
        lines.append("")

        for func in funcs:
            # 跳过函数名为空的条目，避免后续 IndexError
            if not func.get("name"):
                continue

            # 函数分析信息
            docstring = func.get("docstring", "")
            return_type = func.get("return_type", "unknown")
            exceptions = func.get("exceptions", [])
            dependencies = func.get("dependencies", [])
            branches = func.get("branches", 0)

            # 清理参数中的 self/cls
            # 使用公共辅助函数统一解析参数
            param_parts, has_params_raw, raw_params = _parse_func_params(func)
            if has_params_raw:
                params = ", ".join(param_parts)
                param_list = [p.strip().split(":")[0].strip() for p in params.split(",") if p.strip()] if params else []
                has_params = len(param_list) > 0
            else:
                params = ""
                param_list = []
                has_params = False

            # 类名
            class_name = f"Test{func['name'][0].upper()}{func['name'][1:]}"

            lines.append(f"class {class_name}:")
            lines.append(f"    \"\"\"{func['name']} 函数测试\"\"\"")
            lines.append(f"    # 函数位置: {func['file']}:{func['line']}")
            lines.append(f"    # 参数: {func['params']}")
            lines.append(f"    # 返回类型: {return_type}")
            if exceptions:
                lines.append(f"    # 可能抛出: {', '.join(exceptions)}")
            if dependencies:
                lines.append(f"    # 外部依赖: {', '.join(dependencies)} → 需要 Mock")
            if branches > 0:
                lines.append(f"    # 条件分支数: {branches} → 至少需要 {branches + 1} 个测试用例")
            if docstring:
                lines.append(f"    # 说明: {docstring.split(chr(10))[0].strip()}")
            lines.append("")

            # === 正向测试 ===
            lines.append(f"    def test_normal_input(self):")
            lines.append(f"        \"\"\"正向测试：正常输入应返回预期结果\"\"\"")
            if has_params:
                # 根据参数类型生成 Mock 值
                mock_args = []
                for p in param_list:
                    mock_args.append(f"'{p}_mock_value'")
                args_str = ", ".join(mock_args)
                lines.append(f"        # TODO: 替换为实际参数值")
                lines.append(f"        result = {func['name']}({args_str})")
            else:
                lines.append(f"        result = {func['name']}()")

            # 根据返回类型生成断言
            if return_type in ("str", "string", "String"):
                lines.append(f"        assert isinstance(result, str)")
                lines.append(f"        assert len(result) > 0")
            elif return_type in ("int", "float", "number"):
                lines.append(f"        assert isinstance(result, (int, float))")
            elif return_type in ("bool", "boolean"):
                lines.append(f"        assert isinstance(result, bool)")
            elif return_type in ("list", "List", "Array"):
                lines.append(f"        assert isinstance(result, list)")
            elif return_type in ("dict", "Dict", "Object"):
                lines.append(f"        assert isinstance(result, dict)")
            elif return_type == "None":
                lines.append(f"        assert result is None")
            elif "tuple" in return_type:
                lines.append(f"        assert isinstance(result, tuple)")
            else:
                lines.append(f"        assert result is not None")
            lines.append("")

            # === 边界值测试 ===
            lines.append(f"    def test_none_input(self):")
            lines.append(f"        \"\"\"边界值测试：None 输入应正确处理\"\"\"")
            if has_params:
                if exceptions:
                    lines.append(f"        # 函数可能抛出 {exceptions[0]}")
                    # 清理异常名中的非法字符，确保生成有效的 Python 标识符
                    safe_exc_name = re.sub(r'[^a-zA-Z0-9_.]', '', exceptions[0])
                    args = ", ".join(["None"] * len(param_list))
                    lines.append(f"        with pytest.raises({safe_exc_name}):")
                    lines.append(f"            {func['name']}({args})")
                else:
                    args = ", ".join(["None"] * len(param_list))
                    lines.append(f"        result = {func['name']}({args})")
                    lines.append(f"        assert result is not None")
            else:
                lines.append(f"        {func['name']}()  # 无参数函数，仅验证不崩溃")
            lines.append("")

            lines.append(f"    def test_empty_input(self):")
            lines.append(f"        \"\"\"边界值测试：空字符串/空列表应正确处理\"\"\"")
            if has_params:
                # 根据返回类型推测参数类型
                if return_type in ("str", "string", "String"):
                    args = ", ".join(["''"] * len(param_list))
                elif return_type in ("list", "List", "Array"):
                    args = ", ".join(["[]"] * len(param_list))
                elif return_type in ("dict", "Dict", "Object"):
                    args = ", ".join(["{}"] * len(param_list))
                else:
                    args = ", ".join(["''"] * len(param_list))
                lines.append(f"        # TODO: 根据参数实际类型选择空值（''、[]、{{}}、0）")
                lines.append(f"        result = {func['name']}({args})")
                lines.append(f"        assert result is not None")
            else:
                lines.append(f"        {func['name']}()")
            lines.append("")

            # === 类型错误测试 ===
            lines.append(f"    def test_wrong_type_input(self):")
            lines.append(f"        \"\"\"异常测试：非法类型输入应抛出异常\"\"\"")
            if has_params:
                # 根据参数类型生成错误类型输入（复用已过滤的 param_parts）
                # param_parts 已在上方处理过 "无参数" / 空字符串的情况
                wrong_args = []
                for p in param_parts:
                    # 简单推断参数类型
                    if "str" in p or "string" in p.lower():
                        wrong_args.append("123")  # 对字符串参数传数字
                    elif "int" in p or "float" in p or "num" in p.lower():
                        wrong_args.append('"abc"')  # 对数字参数传字符串
                    else:
                        wrong_args.append("123")  # 默认传数字
                args = ", ".join(wrong_args)
                if exceptions:
                    lines.append(f"        with pytest.raises((TypeError, ValueError)):")
                    lines.append(f"            {func['name']}({args})")
                else:
                    lines.append(f"        result = {func['name']}({args})")
                    lines.append(f"        # 函数未声明异常，验证是否返回默认值")
                    lines.append(f"        assert result is not None")
            else:
                lines.append(f"        pytest.skip(\"无参数函数，跳过类型测试\")")
            lines.append("")

            # === 分支覆盖测试 ===
            if branches > 0:
                lines.append(f"    def test_branch_coverage(self):")
                lines.append(f"        \"\"\"分支覆盖：覆盖所有条件分支路径\"\"\"")
                lines.append(f"        # 函数有 {branches} 个条件分支")
                lines.append(f"        # TODO: 为每个分支构造对应的输入")
                lines.append(f"        # 分支 1: 条件为 True")
                lines.append(f"        result_1 = {func['name']}({', '.join(['True'] * len(param_list))})")
                lines.append(f"        assert result_1 is not None")
                lines.append(f"        # 分支 2: 条件为 False")
                lines.append(f"        result_2 = {func['name']}({', '.join(['False'] * len(param_list))})")
                lines.append(f"        assert result_2 is not None")
                lines.append("")

            # === 异常测试 ===
            if exceptions:
                for exc in exceptions[:2]:
                    # 将异常名中的非法字符替换为下划线，避免生成非法方法名
                    safe_exc = _safe_identifier(exc.lower())
                    # 清理异常名用于 pytest.raises，保留点号以支持完整限定名
                    safe_exc_name = re.sub(r'[^a-zA-Z0-9_.]', '', exc)
                    lines.append(f"    def test_raises_{safe_exc}(self):")
                    lines.append(f"        \"\"\"异常测试：应抛出 {exc}\"\"\"")
                    if has_params:
                        lines.append(f"        # TODO: 构造触发 {exc} 的输入")
                        args = ", ".join(["None"] * len(param_list))
                        lines.append(f"        with pytest.raises({safe_exc_name}):")
                        lines.append(f"            {func['name']}({args})")
                    else:
                        lines.append(f"        with pytest.raises({safe_exc_name}):")
                        lines.append(f"            {func['name']}()")
                    lines.append("")

            # === 参数化测试 ===
            # 正向测试数据组（至少 3 组）
            lines.append(f"    @pytest.mark.parametrize(")
            lines.append(f"        'input_val, expected', [")
            lines.append(f"            # TODO: 替换为实际的正向测试数据组")
            lines.append(f"            (None, None),  # 正向用例1")
            lines.append(f"            (None, None),  # 正向用例2")
            lines.append(f"            (None, None),  # 正向用例3")
            lines.append(f"        ])")
            lines.append(f"    def test_parametrized_normal(self, input_val, expected):")
            lines.append(f"        \"\"\"参数化测试：正向测试数据组\"\"\"")
            # 根据参数数量生成调用（复用已过滤的 param_parts，避免重复解析 "无参数"）
            param_count = len(param_parts)
            if param_count == 0:
                lines.append(f"        result = {func['name']}()")
            elif param_count == 1:
                lines.append(f"        result = {func['name']}(input_val)")
            else:
                lines.append(f"        # TODO: 函数有 {param_count} 个参数，需修改为: result = {func['name']}(input_val, ...)")
                lines.append(f"        result = {func['name']}(input_val)  # FIXME: 参数不足")
            lines.append(f"        # TODO: 根据预期值补充断言，如 assert result == expected")
            lines.append(f"        assert result is not None")
            lines.append("")

            # 边界值数据组（至少 2 组）
            lines.append(f"    @pytest.mark.parametrize(")
            lines.append(f"        'input_val, expected', [")
            lines.append(f"            # TODO: 替换为实际的边界值数据组")
            lines.append(f"            (None, None),  # 最小边界值")
            lines.append(f"            (None, None),  # 最大边界值")
            lines.append(f"        ])")
            lines.append(f"    def test_parametrized_boundary(self, input_val, expected):")
            lines.append(f"        \"\"\"参数化测试：边界值数据组\"\"\"")
            # 根据参数数量生成调用
            if param_count == 0:
                lines.append(f"        result = {func['name']}()")
            elif param_count == 1:
                lines.append(f"        result = {func['name']}(input_val)")
            else:
                lines.append(f"        # TODO: 函数有 {param_count} 个参数，需修改为: result = {func['name']}(input_val, ...)")
                lines.append(f"        result = {func['name']}(input_val)  # FIXME: 参数不足")
            lines.append(f"        # TODO: 根据预期值补充断言")
            lines.append(f"        assert result is not None")
            lines.append("")

        _write_test_file(test_file, lines, output_dir)


def generate_java_tests(functions: list[dict[str, Any]], output_dir: str, project_path: str = "") -> None:
    """
    生成 Java 单元测试代码（JUnit 5 框架）

    Args:
        functions: 函数列表（含分析结果）
        output_dir: 测试文件输出目录
        project_path: 项目根目录
    """
    # 按文件分组
    file_groups = _group_functions_by_file(functions)

    for file_path, funcs in file_groups.items():
        # 生成测试文件路径：src/main/java/X.java → src/test/java/XTest.java
        # 只替换第一次出现，避免路径中多次包含 src/main/java 时被全局替换
        if "src/main/java" in file_path:
            # 标准 Maven/Gradle 目录结构：将 src/main/java 替换为 src/test/java
            test_file = Path(output_dir) / file_path.replace("src/main/java", "src/test/java", 1)
        else:
            # 非标准路径：将文件放到 src/test/java/ 下，保持相对目录结构
            test_file = Path(output_dir) / "src/test/java" / file_path
        # 添加 Test 后缀生成测试文件名（避免双重 Test 后缀）
        stem = test_file.stem
        if stem.endswith("Test"):
            test_file = test_file.with_name(f"{stem}.java")
        else:
            test_file = test_file.with_name(f"{stem}Test.java")

        # 提取包名和类名
        package = ""
        # test_file.stem 可能已包含 Test 后缀（如 calcTest），避免重复添加
        stem_name = test_file.stem
        if stem_name.endswith("Test"):
            class_name = stem_name
        else:
            class_name = f"{stem_name}Test"
        if "src/main/java/" in file_path:
            rel = file_path.replace("src/main/java/", "")
            parts = rel.split("/")
            if len(parts) > 1:
                package = ".".join(parts[:-1])
                # 从原始文件名提取类名，并应用去重逻辑避免双重 Test 后缀
                raw_class = parts[-1].replace(".java", "")
                class_name = raw_class if raw_class.endswith("Test") else f"{raw_class}Test"

        lines = []
        lines.append(f"// 自动生成的单元测试 - {file_path}")
        lines.append(f"// 测试框架: JUnit 5")
        lines.append(f"// 注意：以下测试代码为骨架，AI 需根据源码分析结果填充具体测试值和断言")
        lines.append("")
        if package:
            lines.append(f"package {package};")
            lines.append("")

        # 导入
        lines.append(f"import org.junit.jupiter.api.Test;")
        lines.append(f"import org.junit.jupiter.api.DisplayName;")
        lines.append(f"import org.junit.jupiter.api.Nested;")
        lines.append(f"import org.junit.jupiter.params.ParameterizedTest;")
        lines.append(f"import org.junit.jupiter.params.provider.ValueSource;")
        lines.append(f"import static org.junit.jupiter.api.Assertions.*;")
        lines.append("")

        # 类声明
        lines.append(f"@DisplayName(\"{class_name} 单元测试\")")
        lines.append(f"class {class_name} {{")

        for func in funcs:
            # 跳过函数名为空的条目
            if not func.get("name"):
                continue
            # 函数分析信息
            return_type = func.get("return_type", "void")
            exceptions = func.get("exceptions", [])
            dependencies = func.get("dependencies", [])
            branches = func.get("branches", 0)

            lines.append("")
            lines.append(f"    @Nested")
            lines.append(f"    @DisplayName(\"{func['name']} 测试\")")
            lines.append(f"    class {func['name']}Test {{")
            lines.append(f"        // 函数位置: {func['file']}:{func['line']}")
            lines.append(f"        // 参数: {func['params']}")
            lines.append(f"        // 返回类型: {return_type}")
            if exceptions:
                lines.append(f"        // 可能抛出: {', '.join(exceptions)}")
            if dependencies:
                lines.append(f"        // 外部依赖: {', '.join(dependencies[:5])} → 需要 @Mock")
            lines.append("")

            # === 正向测试 ===
            lines.append(f"        @Test")
            lines.append(f"        @DisplayName(\"正向测试：正常输入应返回预期结果\")")
            lines.append(f"        void testNormalInput() {{")
            lines.append(f"            // TODO: 创建被测类的实例（如需要）")
            lines.append(f"            // TODO: 替换为实际参数值")
            lines.append(f"            // var result = instance.{func['name']}(/* 参数 */);")
            if return_type == "void":
                lines.append(f"            // void 返回类型，验证副作用或无异常")
                lines.append(f"            assertDoesNotThrow(() -> {{")
                lines.append(f"                // instance.{func['name']}(/* 参数 */);")
                lines.append(f"            }});")
            elif return_type in ("int", "long", "short", "byte", "float", "double"):
                lines.append(f"            // assertInstanceOf(Number.class, result);")
                lines.append(f"            // assertNotNull(result);")
            else:
                lines.append(f"            // assertNotNull(result);")
            lines.append(f"        }}")
            lines.append("")

            # === 边界值测试 ===
            lines.append(f"        @Test")
            lines.append(f"        @DisplayName(\"边界值测试：null 输入应正确处理\")")
            lines.append(f"        void testNullInput() {{")
            if exceptions:
                lines.append(f"            // 函数声明抛出 {exceptions[0]}")
                # 当异常名不包含包路径（简单类名）时，提示用户需要手动添加 import
                if "." not in exceptions[0]:
                    lines.append(f"            // 注意：请确保已导入 {exceptions[0]}，例如 import {exceptions[0]};")
                lines.append(f"            assertThrows({exceptions[0]}.class, () -> {{")
                lines.append(f"                // instance.{func['name']}(null);")
                lines.append(f"            }});")
            else:
                lines.append(f"            // assertDoesNotThrow(() -> instance.{func['name']}(null));")
            lines.append(f"        }}")
            lines.append("")

            # === 异常测试 ===
            if exceptions:
                for exc in exceptions[:2]:
                    # 只取异常的简单类名（去掉包路径）
                    simple_exc = _safe_exception_name(exc)
                    lines.append(f"        @Test")
                    lines.append(f"        @DisplayName(\"异常测试：应抛出 {exc}\")")
                    lines.append(f"        void testThrows{simple_exc}() {{")
                    lines.append(f"            // TODO: 构造触发 {exc} 的输入")
                    # 当异常名不包含包路径（简单类名）时，提示用户需要手动添加 import
                    if "." not in exc:
                        lines.append(f"            // 注意：请确保已导入 {exc}，例如 import {exc};")
                    lines.append(f"            assertThrows({exc}.class, () -> {{")
                    lines.append(f"                // instance.{func['name']}(/* 触发异常的参数 */);")
                    lines.append(f"            }});")
                    lines.append(f"        }}")
                    lines.append("")

            # === 参数化测试 ===
            # 根据返回类型选择 ValueSource 类型和对应的方法参数类型
            ret = func.get("return_type", "")
            # 精确映射：不同整数类型使用对应的 ValueSource 属性和参数类型
            if ret and ret.lower() in ("int", "integer"):
                value_source = "@ValueSource(ints = {/* TODO: 填入整数测试值 */})"
                param_type = "int"
            elif ret and ret.lower() == "long":
                value_source = "@ValueSource(longs = {/* TODO: 填入长整数测试值 */})"
                param_type = "long"
            elif ret and ret.lower() == "short":
                value_source = "@ValueSource(shorts = {/* TODO: 填入短整数测试值 */})"
                param_type = "short"
            elif ret and ret.lower() == "byte":
                value_source = "@ValueSource(bytes = {/* TODO: 填入字节测试值 */})"
                param_type = "byte"
            elif ret and ret.lower() in ("double", "float"):
                value_source = "@ValueSource(doubles = {/* TODO: 填入浮点数测试值 */})"
                param_type = "double"
            else:
                value_source = "@ValueSource(strings = {/* TODO: 填入字符串测试值 */})"
                param_type = "String"

            lines.append(f"        @ParameterizedTest")
            lines.append(f"        @DisplayName(\"参数化测试：正向测试数据组\")")
            lines.append(f"        {value_source}")
            lines.append(f"        void testParameterizedNormal({param_type} input) {{")
            lines.append(f"            // TODO: 替换为实际调用和断言")
            lines.append(f"            // var result = instance.{func['name']}(input);")
            lines.append(f"            // assertNotNull(result);")
            lines.append(f"        }}")
            lines.append("")
            lines.append(f"        @ParameterizedTest")
            lines.append(f"        @DisplayName(\"参数化测试：边界值数据组\")")
            lines.append(f"        {value_source}")
            lines.append(f"        void testParameterizedBoundary({param_type} input) {{")
            lines.append(f"            // TODO: 替换为实际调用和断言")
            lines.append(f"            // var result = instance.{func['name']}(input);")
            lines.append(f"            // assertNotNull(result);")
            lines.append(f"        }}")
            lines.append("")

            lines.append(f"    }}")

        lines.append(f"}}")
        lines.append("")

        _write_test_file(test_file, lines, output_dir)


def generate_go_tests(functions: list[dict[str, Any]], output_dir: str, project_path: str = "") -> None:
    """
    生成 Go 单元测试代码（testing 包 + testify）

    Args:
        functions: 函数列表（含分析结果）
        output_dir: 测试文件输出目录
        project_path: 项目根目录
    """
    # 按文件分组
    file_groups = _group_functions_by_file(functions)

    for file_path, funcs in file_groups.items():
        # 生成测试文件路径：xxx.go → xxx_test.go
        # 如果输入已经是测试文件（以 _test.go 结尾），避免生成 _test_test.go
        src_stem = Path(file_path).stem
        if src_stem.endswith("_test"):
            # 已经是测试文件，直接使用原始文件名作为测试文件名
            test_file = Path(output_dir) / Path(file_path).parent / (src_stem + ".go")
        else:
            test_file = Path(output_dir) / Path(file_path).parent / (src_stem + "_test.go")

        # 提取包名
        package = "main"
        try:
            content = (Path(project_path) / file_path).read_text(encoding="utf-8", errors="ignore") if project_path else ""
            pkg_match = re.search(r"package\s+(\w+)", content)
            if pkg_match:
                package = pkg_match.group(1)
        except Exception:
            pass

        lines = []
        # any 是 Go 1.18 引入的类型别名，添加构建标签确保兼容性
        lines.append(f"//go:build go1.18")
        lines.append(f"")
        lines.append(f"// 自动生成的单元测试 - {file_path}")
        lines.append(f"// 测试框架: Go testing + testify")
        lines.append(f"// 注意：以下测试代码为骨架，AI 需根据源码分析结果填充具体测试值和断言")
        lines.append(f"// 注意：本测试文件使用了 Go 1.18 引入的 any 类型别名，需要 Go 1.18+ 编译")
        lines.append("")
        lines.append(f"package {package}")
        lines.append("")
        lines.append(f'import (')
        lines.append(f'    "testing"')
        lines.append(f'    // 注意：需要安装 testify: go get github.com/stretchr/testify')
        lines.append(f'    "github.com/stretchr/testify/assert"')
        lines.append(f'    "github.com/stretchr/testify/require"')
        lines.append(f')')
        lines.append("")

        for func in funcs:
            # 跳过函数名为空的条目
            if not func.get("name"):
                continue
            # 函数分析信息
            return_type = func.get("return_type", "void")
            exceptions = func.get("exceptions", [])
            dependencies = func.get("dependencies", [])
            branches = func.get("branches", 0)

            # === 正向测试 ===
            lines.append(f"func Test{func['name']}_NormalInput(t *testing.T) {{")
            lines.append(f"    // 函数位置: {func['file']}:{func['line']}")
            lines.append(f"    // 参数: {func['params']}")
            lines.append(f"    // 返回类型: {return_type}")
            if exceptions:
                lines.append(f"    // 可能的错误: {', '.join(exceptions[:3])}")
            lines.append(f"    // TODO: 替换为实际参数值")
            lines.append(f"    // result, err := {func['name']}(/* 参数 */)")
            lines.append(f"    // require.NoError(t, err)")
            lines.append(f"    // assert.NotNil(t, result)")
            lines.append(f"}}")
            lines.append("")

            # === 边界值测试 ===
            lines.append(f"func Test{func['name']}_EmptyInput(t *testing.T) {{")
            lines.append(f"    // 边界值测试：空值/零值输入")
            lines.append(f"    // TODO: 根据参数类型选择零值（\"\"、nil、0、[]int{{}}）")
            lines.append(f"    // result, err := {func['name']}(/* 空值参数 */)")
            lines.append(f"    // require.NoError(t, err)")
            lines.append(f"}}")
            lines.append("")

            # === 错误处理测试 ===
            if "error" in return_type or exceptions:
                lines.append(f"func Test{func['name']}_Error(t *testing.T) {{")
                lines.append(f"    // 错误处理测试：应返回 error")
                lines.append(f"    // TODO: 构造会触发错误的输入")
                lines.append(f"    // _, err := {func['name']}(/* 触发错误的参数 */)")
                lines.append(f"    // require.Error(t, err)")
                lines.append(f"    // assert.Contains(t, err.Error(), \"预期错误信息\")")
                lines.append(f"}}")
                lines.append("")

            # === 分支覆盖测试 ===
            if branches > 0:
                lines.append(f"func Test{func['name']}_BranchCoverage(t *testing.T) {{")
                lines.append(f"    // 分支覆盖测试：函数有 {branches} 个条件分支")
                lines.append(f"    // TODO: 为每个分支构造对应的输入")
                lines.append(f"    t.Run(\"branch_true\", func(t *testing.T) {{")
                lines.append(f"        // result, err := {func['name']}(/* 使条件为 true */)")
                lines.append(f"        // require.NoError(t, err)")
                lines.append(f"    }})")
                lines.append(f"    t.Run(\"branch_false\", func(t *testing.T) {{")
                lines.append(f"        // result, err := {func['name']}(/* 使条件为 false */)")
                lines.append(f"        // require.NoError(t, err)")
                lines.append(f"    }})")
                lines.append(f"}}")
                lines.append("")

            # === 参数化测试（使用 t.Run 子测试循环） ===
            lines.append(f"func Test{func['name']}_Parameterized(t *testing.T) {{")
            lines.append(f"    // 参数化测试：使用 t.Run 子测试循环")
            lines.append(f"    normalCases := []struct {{")
            lines.append(f"        name     string")
            lines.append(f"        input    any  // TODO: 替换为实际的参数类型")
            lines.append(f"        expected any  // TODO: 替换为实际的返回类型")
            lines.append(f"    }}{{")
            lines.append(f"        // TODO: 替换为实际的正向测试数据组")
            lines.append(f"        {{ name: \"正向用例1\", input: nil, expected: nil }},")
            lines.append(f"        {{ name: \"正向用例2\", input: nil, expected: nil }},")
            lines.append(f"        {{ name: \"正向用例3\", input: nil, expected: nil }},")
            lines.append(f"    }}")
            lines.append(f"    for _, tc := range normalCases {{")
            lines.append(f"        t.Run(tc.name, func(t *testing.T) {{")
            lines.append(f"            // result, err := {func['name']}(tc.input)")
            lines.append(f"            // require.NoError(t, err)")
            lines.append(f"            // assert.Equal(t, tc.expected, result)")
            lines.append(f"        }})")
            lines.append(f"    }}")
            lines.append(f"")
            lines.append(f"    boundaryCases := []struct {{")
            lines.append(f"        name     string")
            lines.append(f"        input    any  // TODO: 替换为实际的参数类型")
            lines.append(f"        expected any  // TODO: 替换为实际的返回类型")
            lines.append(f"    }}{{")
            lines.append(f"        // TODO: 替换为实际的边界值数据组")
            lines.append(f"        {{ name: \"最小边界值\", input: nil, expected: nil }},")
            lines.append(f"        {{ name: \"最大边界值\", input: nil, expected: nil }},")
            lines.append(f"    }}")
            lines.append(f"    for _, tc := range boundaryCases {{")
            lines.append(f"        t.Run(tc.name, func(t *testing.T) {{")
            lines.append(f"            // result, err := {func['name']}(tc.input)")
            lines.append(f"            // require.NoError(t, err)")
            lines.append(f"            // assert.Equal(t, tc.expected, result)")
            lines.append(f"        }})")
            lines.append(f"    }}")
            lines.append(f"}}")
            lines.append("")

        _write_test_file(test_file, lines, output_dir)


def generate_rust_tests(functions: list[dict[str, Any]], output_dir: str, project_path: str = "") -> None:
    """
    生成 Rust 单元测试代码（内置 testing 框架 + test-case crate）

    Args:
        functions: 函数列表（含分析结果）
        output_dir: 测试文件输出目录
        project_path: 项目根目录（用于读取源码）
    """
    # 按文件分组
    file_groups = _group_functions_by_file(functions)

    for file_path, funcs in file_groups.items():
        # 生成测试文件路径：xxx.rs → xxx_test.rs（Rust 惯例是独立测试文件）
        test_file = Path(output_dir) / Path(file_path).parent / (Path(file_path).stem + "_test.rs")

        # 提取模块路径（使用完整相对路径，将目录分隔符替换为 ::）
        raw_module_path = str(Path(file_path).with_suffix("")).replace(os.sep, "::").replace("/", "::")
        # 只去除 "src::" 前缀，使用 crate:: 前缀确保路径正确
        # 例如 src::utils::helper → crate::utils::helper
        # 注意：不能盲目去除第一个目录段，否则会破坏非 src 目录下的路径
        module_path = raw_module_path[5:] if raw_module_path.startswith("src::") else raw_module_path
        # 特殊处理：src/lib.rs 是 crate root，应生成 use crate::*; 而非 use crate::lib::*;
        if module_path == "lib":
            module_path = ""

        lines = []
        lines.append(f"// 自动生成的单元测试 - {file_path}")
        lines.append(f"// 测试框架: Rust 内置 testing + test-case crate")
        lines.append(f"// 注意：以下测试代码为骨架，AI 需根据源码分析结果填充具体测试值和断言")
        lines.append(f"// 注意：此测试文件只能访问 pub 函数。如需测试私有函数，")
        lines.append(f"// 请将测试代码移到源文件末尾的 #[cfg(test)] mod tests {{ ... }} 块中")
        lines.append(f"// Cargo.toml 中需添加: test-case = \"3\"")
        lines.append("")
        lines.append(f"use test_case::test_case;")
        lines.append(f"")
        # 导入被测模块
        # 使用 crate:: 前缀，从项目根开始的绝对路径
        # 如果 module_path 为空（如 src/lib.rs），则使用 use crate::*;
        if module_path:
            lines.append(f"use crate::{module_path}::*;")
        else:
            lines.append(f"use crate::*;")
        lines.append("")

        for func in funcs:
            # 跳过函数名为空的条目
            if not func.get("name"):
                continue
            # 函数分析信息
            docstring = func.get("docstring", "")
            return_type = func.get("return_type", "unknown")
            exceptions = func.get("exceptions", [])
            dependencies = func.get("dependencies", [])
            branches = func.get("branches", 0)

            lines.append(f"// ===== {func['name']} 测试 =====")
            lines.append(f"// 函数位置: {func['file']}:{func['line']}")
            lines.append(f"// 参数: {func['params']}")
            lines.append(f"// 返回类型: {return_type}")
            if exceptions:
                lines.append(f"// 可能的错误: {', '.join(exceptions)}")
            if dependencies:
                lines.append(f"// 外部依赖: {', '.join(dependencies)} → 需要 Mock")
            if branches > 0:
                lines.append(f"// 条件分支数: {branches} → 至少需要 {branches + 1} 个测试用例")
            if docstring:
                lines.append(f"// 说明: {docstring.split(chr(10))[0].strip()}")
            lines.append("")

            # === 正向测试 ===
            lines.append(f"#[test]")
            lines.append(f"fn test_{func['name']}_normal_input() {{")
            lines.append(f"    // 正向测试：正常输入应返回预期结果")
            lines.append(f"    // TODO: 替换为实际参数值")
            lines.append(f"    // let result = {func['name']}(/* 参数 */);")
            lines.append(f"    // assert!(result.is_some());  // 或 assert!(!result.is_empty())")
            lines.append(f"    // assert_eq!(result, expected);")
            lines.append(f"}}")
            lines.append("")

            # === 边界值测试 ===
            lines.append(f"#[test]")
            lines.append(f"fn test_{func['name']}_empty_input() {{")
            lines.append(f"    // 边界值测试：空值/零值输入")
            lines.append(f"    // TODO: 根据参数类型选择零值（\"\"、0、None、vec![]）")
            lines.append(f"    // let result = {func['name']}(/* 空值参数 */);")
            lines.append(f"    // assert!(result.is_some());")
            lines.append(f"}}")
            lines.append("")

            lines.append(f"#[test]")
            lines.append(f"fn test_{func['name']}_extreme_values() {{")
            lines.append(f"    // 边界值测试：极值输入")
            lines.append(f"    // TODO: 测试 i32::MAX、i32::MIN、超长字符串等")
            lines.append(f"    // let result = {func['name']}(/* 极值参数 */);")
            lines.append(f"    // assert!(result.is_some());")
            lines.append(f"}}")
            lines.append("")

            # === 错误处理测试 ===
            lines.append(f"#[test]")
            lines.append(f"fn test_{func['name']}_error_handling() {{")
            lines.append(f"    // 错误处理测试：应返回 Err 或 panic")
            lines.append(f"    // TODO: 构造会触发错误的输入")
            lines.append(f"    // let result = {func['name']}(/* 触发错误的参数 */);")
            lines.append(f"    // assert!(result.is_err());")
            lines.append(f"}}")
            lines.append("")

            # === 参数化测试（使用 test_case 宏） ===
            lines.append(f"// 参数化测试：正向测试数据组")
            # 使用 () 作为占位符，/* TODO */ 在 Rust 宏中无法编译
            lines.append(f"#[test_case(() => (); \"正向用例1\")]")
            lines.append(f"#[test_case(() => (); \"正向用例2\")]")
            lines.append(f"#[test_case(() => (); \"正向用例3\")]")
            lines.append(f"fn test_{func['name']}_parametrized_normal(input: /* TODO: 参数类型 */) -> /* TODO: 返回类型 */ {{")
            lines.append(f"    // TODO: 替换为实际调用和断言")
            lines.append(f"    // let result = {func['name']}(input);")
            lines.append(f"    // result")
            lines.append(f"}}")
            lines.append("")

            # === 参数化测试：边界值数据组 ===
            lines.append(f"// 参数化测试：边界值数据组")
            lines.append(f"#[test_case(() => (); \"最小边界值\")]")
            lines.append(f"#[test_case(() => (); \"最大边界值\")]")
            lines.append(f"fn test_{func['name']}_parametrized_boundary(input: /* TODO: 参数类型 */) -> /* TODO: 返回类型 */ {{")
            lines.append(f"    // TODO: 替换为实际调用和断言")
            lines.append(f"    // let result = {func['name']}(input);")
            lines.append(f"    // result")
            lines.append(f"}}")
            lines.append("")

            # === 分支覆盖测试 ===
            if branches > 0:
                lines.append(f"#[test]")
                lines.append(f"fn test_{func['name']}_branch_coverage() {{")
                lines.append(f"    // 分支覆盖测试：函数有 {branches} 个条件分支")
                lines.append(f"    // TODO: 为每个分支构造对应的输入")
                lines.append(f"    // 分支 1: 条件为 true")
                lines.append(f"    // let result_1 = {func['name']}(/* 使条件为 true */);")
                lines.append(f"    // assert!(result_1.is_some());")
                lines.append(f"    // 分支 2: 条件为 false")
                lines.append(f"    // let result_2 = {func['name']}(/* 使条件为 false */);")
                lines.append(f"    // assert!(result_2.is_some());")
                lines.append(f"}}")
                lines.append("")

        # 写入文件
        _write_test_file(test_file, lines, output_dir)


def generate_csharp_tests(functions: list[dict[str, Any]], output_dir: str, project_path: str = "") -> None:
    """
    生成 C# 单元测试代码（xUnit 框架 + FluentAssertions + Moq）

    Args:
        functions: 函数列表（含分析结果）
        output_dir: 测试文件输出目录
        project_path: 项目根目录（用于读取源码）
    """
    # 按文件分组
    file_groups = _group_functions_by_file(functions)

    for file_path, funcs in file_groups.items():
        # 生成测试文件路径：Xxx.cs → XxxTests.cs
        test_file = Path(output_dir) / Path(file_path).parent / (Path(file_path).stem + "Tests.cs")

        # 提取命名空间和类名
        namespace = ""
        class_name = Path(file_path).stem
        try:
            content = (Path(project_path) / file_path).read_text(encoding="utf-8", errors="ignore") if project_path else ""
            ns_match = re.search(r"namespace\s+([\w.]+)", content)
            if ns_match:
                namespace = ns_match.group(1)
        except Exception:
            pass

        lines = []
        lines.append(f"// 自动生成的单元测试 - {file_path}")
        lines.append(f"// 测试框架: xUnit + FluentAssertions + Moq")
        lines.append(f"// 注意：以下测试代码为骨架，AI 需根据源码分析结果填充具体测试值和断言")
        lines.append("")
        if namespace:
            lines.append(f"using {namespace};")
        lines.append(f"using Xunit;")
        lines.append(f"using FluentAssertions;")
        lines.append(f"using Moq;")
        lines.append("")

        # 类声明
        test_class_name = f"{class_name}Tests"
        lines.append(f"/// <summary>")
        lines.append(f"/// {class_name} 单元测试")
        lines.append(f"/// </summary>")
        lines.append(f"public class {test_class_name}")
        lines.append(f"{{")

        for func in funcs:
            # 跳过函数名为空的条目
            if not func.get("name"):
                continue
            # 函数分析信息
            return_type = func.get("return_type", "void")
            exceptions = func.get("exceptions", [])
            dependencies = func.get("dependencies", [])
            branches = func.get("branches", 0)

            lines.append(f"    // ===== {func['name']} 测试 =====")
            lines.append(f"    // 函数位置: {func['file']}:{func['line']}")
            lines.append(f"    // 参数: {func['params']}")
            lines.append(f"    // 返回类型: {return_type}")
            if exceptions:
                lines.append(f"    // 可能抛出: {', '.join(exceptions)}")
            if dependencies:
                lines.append(f"    // 外部依赖: {', '.join(dependencies[:5])} → 需要 Mock")
            if branches > 0:
                lines.append(f"    // 条件分支数: {branches} → 至少需要 {branches + 1} 个测试用例")
            lines.append("")

            # === 正向测试 [Fact] ===
            lines.append(f"    [Fact]")
            lines.append(f"    public void {func['name']}_NormalInput_ShouldReturnExpected()")
            lines.append(f"    {{")
            lines.append(f"        // 正向测试：正常输入应返回预期结果")
            lines.append(f"        // TODO: 创建被测类的实例（如需要）")
            lines.append(f"        // TODO: 替换为实际参数值")
            lines.append(f"        // var result = instance.{func['name']}(/* 参数 */);")
            lines.append(f"        // result.Should().NotBeNull();")
            lines.append(f"        // result.Should().Be(expected);")
            lines.append(f"    }}")
            lines.append("")

            # === 边界值测试 [Fact] ===
            lines.append(f"    [Fact]")
            lines.append(f"    public void {func['name']}_NullInput_ShouldHandleCorrectly()")
            lines.append(f"    {{")
            lines.append(f"        // 边界值测试：null 输入应正确处理")
            if exceptions:
                lines.append(f"        // 函数可能抛出 {exceptions[0]}")
                lines.append(f"        // Action act = () => instance.{func['name']}(null);")
                lines.append(f"        // act.Should().Throw<{exceptions[0]}>();")
            else:
                lines.append(f"        // var result = instance.{func['name']}(null);")
                lines.append(f"        // result.Should().NotBeNull();")
            lines.append(f"    }}")
            lines.append("")

            lines.append(f"    [Fact]")
            lines.append(f"    public void {func['name']}_EmptyInput_ShouldHandleCorrectly()")
            lines.append(f"    {{")
            lines.append(f"        // 边界值测试：空值输入应正确处理")
            lines.append(f"        // TODO: 根据参数类型选择空值（\"\"、Array.Empty、default）")
            lines.append(f"        // var result = instance.{func['name']}(/* 空值参数 */);")
            lines.append(f"        // result.Should().NotBeNull();")
            lines.append(f"    }}")
            lines.append("")

            # === 错误处理测试 ===
            if exceptions:
                for exc in exceptions[:2]:
                    # 只取异常的简单类名（去掉包路径，避免方法名含非法字符 `.`）
                    simple_exc = _safe_exception_name(exc)
                    lines.append(f"    [Fact]")
                    lines.append(f"    public void {func['name']}_ShouldThrow{simple_exc}()")
                    lines.append(f"    {{")
                    lines.append(f"        // 异常测试：应抛出 {exc}")
                    lines.append(f"        // TODO: 构造触发 {exc} 的输入")
                    lines.append(f"        // Action act = () => instance.{func['name']}(/* 触发异常的参数 */);")
                    lines.append(f"        // act.Should().Throw<{exc}>();")
                    lines.append(f"    }}")
                    lines.append("")

            # === 参数化测试 [Theory] + [InlineData] ===
            # 根据函数参数数量生成对应数量的 InlineData 参数
            # 使用公共辅助函数统一解析参数
            param_parts, _, _ = _parse_func_params(func)
            param_count = len(param_parts)
            # 方法参数：每个函数参数一个 + expected（使用 0 作为占位符，/* TODO */ 不是有效的 C# 表达式）
            method_params = ", ".join([f"int /* TODO: 参数{i+1} */" for i in range(param_count)] + ["int /* TODO: 预期结果 */"])
            inline_args = ", ".join(["0" for _ in range(param_count + 1)])  # +1 for expected

            lines.append(f"    // 参数化测试：正向测试数据组")
            lines.append(f"    [Theory]")
            lines.append(f"    [InlineData({inline_args})]")
            lines.append(f"    [InlineData({inline_args})]")
            lines.append(f"    [InlineData({inline_args})]")
            lines.append(f"    public void {func['name']}_ParameterizedNormal_ShouldReturnExpected({method_params})")
            lines.append(f"    {{")
            lines.append(f"        // TODO: 替换为实际调用和断言")
            lines.append(f"        // var result = instance.{func['name']}(/* 参数 */);")
            lines.append(f"        // result.Should().Be(expected);")
            lines.append(f"    }}")
            lines.append("")

            # === 参数化测试：边界值数据组 ===
            lines.append(f"    // 参数化测试：边界值数据组")
            lines.append(f"    [Theory]")
            lines.append(f"    [InlineData({inline_args})]")
            lines.append(f"    [InlineData({inline_args})]")
            lines.append(f"    public void {func['name']}_ParameterizedBoundary_ShouldHandleCorrectly({method_params})")
            lines.append(f"    {{")
            lines.append(f"        // TODO: 替换为实际调用和断言")
            lines.append(f"        // var result = instance.{func['name']}(/* 参数 */);")
            lines.append(f"        // result.Should().Be(expected);")
            lines.append(f"    }}")
            lines.append("")

        lines.append(f"}}")
        lines.append("")

        # 写入文件
        _write_test_file(test_file, lines, output_dir)


def generate_mock_templates(functions: list[dict[str, Any]], output_dir: str) -> None:
    """
    根据函数的 dependencies 字段自动生成 Mock 模板文件

    支持语言：
    - JS/TS: 生成 __mocks__/*.mock.ts，使用 jest.mock() 模式
    - Python: 生成 conftest.py 中的 @pytest.fixture fixture
    - Java: 生成包含 @Mock 注解的 Mock 字段声明
    - Go: 生成接口 Mock 实现（使用 testify/mock）
    - Rust: 生成 trait Mock 实现
    - C#: 生成 Moq Mock 对象设置

    Args:
        functions: 函数列表（含分析结果，每个函数需有 dependencies 字段）
        output_dir: Mock 模板文件输出目录
    """
    # 收集所有需要 Mock 的依赖项（按语言分组）
    # dependencies_map: { language: { dependency_name: [func_names] } }
    dependencies_map = {}
    for func in functions:
        # 跳过函数名为空的条目
        if not func.get("name"):
            continue
        language = func.get("language", "unknown")
        deps = func.get("dependencies", [])
        if not deps:
            continue

        if language not in dependencies_map:
            dependencies_map[language] = {}

        for dep in deps:
            if dep not in dependencies_map[language]:
                dependencies_map[language][dep] = []
            dependencies_map[language][dep].append(func["name"])

    if not dependencies_map:
        print("  没有需要 Mock 的外部依赖")
        return

    # 按语言生成 Mock 模板
    for language, deps in dependencies_map.items():
        if language in ("js", "ts", "javascript", "typescript", "js/ts"):
            _generate_js_mock_templates(deps, output_dir)
        elif language == "python":
            _generate_python_mock_templates(deps, output_dir)
        elif language == "java":
            _generate_java_mock_templates(deps, output_dir)
        elif language == "go":
            _generate_go_mock_templates(deps, output_dir)
        elif language == "rust":
            _generate_rust_mock_templates(deps, output_dir)
        elif language in ("csharp", "c#"):
            _generate_csharp_mock_templates(deps, output_dir)
        else:
            print(f"  暂不支持 {language} 语言的 Mock 模板生成")


def _generate_js_mock_templates(deps: dict[str, list[str]], output_dir: str) -> None:
    """
    生成 JS/TS 的 Mock 模板文件（jest.mock() 模式）

    Args:
        deps: 依赖项字典 { dep_name: [func_names] }
        output_dir: 输出目录
    """
    # 创建 __mocks__ 目录（_write_test_file 也会自动创建，此处保留语义清晰）
    mocks_dir = Path(output_dir) / "__mocks__"

    for dep_name, func_names in deps.items():
        # 生成 Mock 文件名（将路径分隔符替换为下划线，确保文件平铺在 __mocks__/ 下）
        # 同时生成安全的标识符名（去除特殊字符），用于代码中的变量名
        safe_dep_name = dep_name.replace("/", "_").replace("\\", "_")
        safe_identifier = _safe_identifier(dep_name)
        mock_file = mocks_dir / f"{safe_dep_name}.mock.ts"
        lines = []
        lines.append(f"// 自动生成的 Mock 模板 - {dep_name}")
        lines.append(f"// 被以下函数依赖: {', '.join(func_names)}")
        lines.append(f"// Mock 模式: jest.mock()")
        lines.append(f"// 注意：AI 需根据源码分析结果填充具体 Mock 行为")
        lines.append("")
        lines.append(f"// 默认 Mock 导出")
        lines.append(f"const mock{safe_identifier} = {{")
        lines.append(f"    // TODO: 根据模块实际导出填充 Mock 方法")
        lines.append(f"    // 示例：")
        lines.append(f"    // methodName: jest.fn().mockReturnValue(/* 默认返回值 */),")
        lines.append(f"    // asyncMethod: jest.fn().mockResolvedValue(/* 默认返回值 */),")
        lines.append(f"}};")
        lines.append("")
        lines.append(f"export default mock{safe_identifier};")
        lines.append("")
        lines.append(f"// 如果模块有命名导出，取消注释以下内容：")
        lines.append(f"// export const namedExport = {{")
        lines.append(f"//     // TODO: 填充命名导出的 Mock 行为")
        lines.append(f"// }};")
        lines.append("")

        _write_test_file(mock_file, lines, output_dir, label="已生成 Mock 模板")


def _generate_python_mock_templates(deps: dict[str, list[str]], output_dir: str) -> None:
    """
    生成 Python 的 Mock 模板文件（conftest.py 中的 @pytest.fixture）

    Args:
        deps: 依赖项字典 { dep_name: [func_names] }
        output_dir: 输出目录
    """
    conftest_file = Path(output_dir) / "conftest.py"
    lines = []
    lines.append(f"# 自动生成的 Mock 模板 - conftest.py")
    lines.append(f"# Mock 模式: @pytest.fixture")
    lines.append(f"# 注意：AI 需根据源码分析结果填充具体 Mock 行为")
    lines.append("")
    lines.append(f"import pytest")
    lines.append(f"from unittest.mock import MagicMock, AsyncMock, patch")
    lines.append(f"import contextlib")
    lines.append("")

    # 用于检测 safe_name 碰撞的集合（必须在循环外初始化）
    used_names = set()

    for dep_name, func_names in deps.items():
        # 清洗 dep_name，去除特殊字符，生成安全的 Python 标识符
        # 例如: "@Injected" → "injected", "my-module" → "my_module"
        safe_name = _safe_identifier(dep_name.lower())
        # 防止不同 dep_name 清洗后产生相同的 safe_name（如 "my-module" 和 "my.module"）
        # 通过追加数字后缀解决碰撞
        base_safe_name = safe_name
        counter = 2
        while safe_name in used_names:
            safe_name = f"{base_safe_name}_{counter}"
            counter += 1
        used_names.add(safe_name)
        # 转义 dep_name 中的单引号和反斜杠，避免生成的 Python 代码出现语法错误
        escaped_dep_name = dep_name.replace("\\", "\\\\").replace("'", "\\'")
        lines.append(f"# 被以下函数依赖: {', '.join(func_names)}")
        lines.append(f"@pytest.fixture")
        lines.append(f"def mock_{safe_name}():")
        lines.append(f'    """Mock fixture: {dep_name}"""')
        lines.append(f"    # TODO: 根据模块实际接口填充 Mock 行为")
        lines.append(f"    mock_obj = MagicMock()")
        lines.append(f"    # 示例：设置 Mock 方法返回值")
        lines.append(f"    # mock_obj.method_name.return_value = /* 默认返回值 */")
        lines.append(f"    # mock_obj.async_method = AsyncMock(return_value=/* 默认返回值 */)")
        lines.append(f"    return mock_obj")
        lines.append("")
        lines.append(f"@pytest.fixture")
        lines.append(f"def patch_{safe_name}():")
        lines.append(f'    """Patch fixture: 用于 monkeypatch {dep_name}"""')
        lines.append(f"    # TODO: 替换为实际的模块路径")
        # 不使用 with 语句，避免 Python < 3.10 中 yield 与 context manager 的兼容性问题
        lines.append(f"    stack = contextlib.ExitStack()")
        lines.append(f"    mock_{safe_name} = stack.enter_context(patch('{escaped_dep_name}'))")
        lines.append(f"    yield mock_{safe_name}")
        lines.append(f"    stack.close()")
        lines.append("")

    _write_test_file(conftest_file, lines, output_dir, label="已生成 Mock 模板")


def _generate_java_mock_templates(deps: dict[str, list[str]], output_dir: str) -> None:
    """
    生成 Java 的 Mock 模板文件（@Mock 注解的 Mock 字段声明）

    Args:
        deps: 依赖项字典 { dep_name: [func_names] }
        output_dir: 输出目录
    """
    mock_file = Path(output_dir) / "MockTemplates.java"
    lines = []
    lines.append(f"// 自动生成的 Mock 模板")
    lines.append(f"// Mock 模式: Mockito @Mock 注解")
    lines.append(f"// 注意：AI 需根据源码分析结果填充具体 Mock 行为")
    lines.append("")
    lines.append(f"import org.junit.jupiter.api.BeforeEach;")
    lines.append(f"import org.mockito.Mock;")
    lines.append(f"import org.mockito.MockitoAnnotations;")
    lines.append(f"import static org.mockito.Mockito.*;")
    lines.append("")
    lines.append(f"/**")
    lines.append(f" * Mock 字段声明模板")
    lines.append(f" * 使用方式：在测试类中继承或复制这些字段")
    lines.append(f" */")
    lines.append(f"public abstract class MockTemplates {{")
    lines.append("")

    for dep_name, func_names in deps.items():
        # 生成安全的标识符名（去除特殊字符），用于 Java 字段名
        safe_identifier = _safe_identifier(dep_name)
        # 生成首字母小写的变量名
        var_name = safe_identifier[0].lower() + safe_identifier[1:] if safe_identifier else 'mockObj'
        lines.append(f"    // 被以下函数依赖: {', '.join(func_names)}")
        lines.append(f"    @Mock")
        lines.append(f"    // TODO: 替换为实际的类类型")
        lines.append(f"    // private {safe_identifier} {var_name};")
        lines.append(f"    private Object {var_name};  // TODO: 替换 Object 为实际类型")
        lines.append("")

    lines.append(f"    @BeforeEach")
    lines.append(f"    void setUp() {{")
    lines.append(f"        MockitoAnnotations.openMocks(this);")
    lines.append(f"        // TODO: 在此设置 Mock 的默认行为")
    lines.append(f"        // when(mockObj.method()).thenReturn(/* 默认值 */);")
    lines.append(f"    }}")
    lines.append(f"}}")
    lines.append("")

    _write_test_file(mock_file, lines, output_dir, label="已生成 Mock 模板")


def _generate_go_mock_templates(deps: dict[str, list[str]], output_dir: str) -> None:
    """
    生成 Go 的 Mock 模板文件（testify/mock 接口实现）

    Args:
        deps: 依赖项字典 { dep_name: [func_names] }
        output_dir: 输出目录
    """
    for dep_name, func_names in deps.items():
        # 将路径分隔符替换为下划线，避免创建子目录
        safe_dep_name = dep_name.lower().replace("/", "_").replace("\\", "_")
        # 生成安全的标识符名（去除特殊字符如 . @ - 等），用于 Go 类型名
        safe_identifier = _safe_identifier(dep_name)
        mock_file = Path(output_dir) / f"mock_{safe_dep_name}.go"
        lines = []
        lines.append(f"// 自动生成的 Mock 模板 - {dep_name}")
        lines.append(f"// 被以下函数依赖: {', '.join(func_names)}")
        lines.append(f"// Mock 模式: testify/mock")
        lines.append(f"// 注意：AI 需根据源码分析结果填充具体 Mock 行为")
        lines.append("")
        lines.append(f"package mocks  // TODO: 替换为实际的包名")
        lines.append("")
        lines.append(f'import "github.com/stretchr/testify/mock"')
        lines.append("")
        lines.append(f"// Mock{safe_identifier} 是 {dep_name} 接口的 Mock 实现")
        lines.append(f"type Mock{safe_identifier} struct {{")
        lines.append(f"    mock.Mock")
        lines.append(f"}}")
        lines.append("")
        lines.append(f"// TODO: 根据接口实际方法生成 Mock 方法")
        lines.append(f"// 示例：")
        lines.append(f"// func (m *Mock{safe_identifier}) MethodName(arg string) (string, error) {{")
        lines.append(f"//     args := m.Called(arg)")
        lines.append(f"//     return args.String(0), args.Error(1)")
        lines.append(f"// }}")
        lines.append("")

        _write_test_file(mock_file, lines, output_dir, label="已生成 Mock 模板")


def _generate_rust_mock_templates(deps: dict[str, list[str]], output_dir: str) -> None:
    """
    生成 Rust 的 Mock 模板文件（trait Mock 实现）

    Args:
        deps: 依赖项字典 { dep_name: [func_names] }
        output_dir: 输出目录
    """
    for dep_name, func_names in deps.items():
        # 将路径分隔符替换为下划线，避免创建子目录
        safe_dep_name = dep_name.lower().replace("/", "_").replace("\\", "_")
        # 生成安全的标识符名（去除特殊字符），用于 Rust trait 名
        safe_identifier = _safe_identifier(dep_name)
        mock_file = Path(output_dir) / f"mock_{safe_dep_name}.rs"
        lines = []
        lines.append(f"// 自动生成的 Mock 模板 - {dep_name}")
        lines.append(f"// 被以下函数依赖: {', '.join(func_names)}")
        lines.append(f"// Mock 模式: trait Mock 实现（可配合 mockall crate 使用）")
        lines.append(f"// 注意：AI 需根据源码分析结果填充具体 Mock 行为")
        lines.append(f"// Cargo.toml 中需添加: mockall = \"0.11\"")
        lines.append("")
        lines.append(f"use mockall::automock;")
        lines.append("")
        lines.append(f"// TODO: 替换为实际的 trait 定义")
        lines.append(f"// #[automock]")
        lines.append(f"// pub trait {safe_identifier} {{")
        lines.append(f"//     fn method_name(&self, arg: /* 参数类型 */) -> /* 返回类型 */;")
        lines.append(f"// }}")
        lines.append("")
        lines.append(f"// 使用示例：")
        lines.append(f"// let mut mock = Mock{safe_identifier}::new();")
        lines.append(f"// mock.expect_method_name()")
        lines.append(f"//     .withf(|arg| arg == /* 预期值 */)")
        lines.append(f"//     .times(1)")
        lines.append(f"//     .returning(|_| /* 返回值 */);")
        lines.append("")

        _write_test_file(mock_file, lines, output_dir, label="已生成 Mock 模板")


def _generate_csharp_mock_templates(deps: dict[str, list[str]], output_dir: str) -> None:
    """
    生成 C# 的 Mock 模板文件（Moq Mock 对象设置）

    Args:
        deps: 依赖项字典 { dep_name: [func_names] }
        output_dir: 输出目录
    """
    mock_file = Path(output_dir) / "MockTemplates.cs"
    lines = []
    lines.append(f"// 自动生成的 Mock 模板")
    lines.append(f"// Mock 模式: Moq 框架")
    lines.append(f"// 注意：AI 需根据源码分析结果填充具体 Mock 行为")
    lines.append("")
    lines.append(f"using Moq;")
    lines.append("")

    for dep_name, func_names in deps.items():
        # 生成安全的标识符名（去除特殊字符），用于 C# 变量名
        safe_identifier = _safe_identifier(dep_name)
        lines.append(f"// 被以下函数依赖: {', '.join(func_names)}")
        lines.append(f"// TODO: 替换为实际的接口/类类型")
        lines.append(f"// var mock{safe_identifier} = new Mock<{safe_identifier}>();")
        lines.append(f"// mock{safe_identifier}.Setup(x => x.MethodName(/* 参数 */))")
        lines.append(f"//     .Returns(/* 默认返回值 */);")
        lines.append(f"// mock{safe_identifier}.Setup(x => x.AsyncMethod(/* 参数 */))")
        lines.append(f"//     .ReturnsAsync(/* 默认返回值 */);")
        lines.append(f"// var instance = mock{safe_identifier}.Object;")
        lines.append("")

    _write_test_file(mock_file, lines, output_dir, label="已生成 Mock 模板")


def generate_tests(scan_result_path: str, output_dir: str, project_path: str = "") -> None:
    """
    根据扫描结果生成对应语言的测试代码

    Args:
        scan_result_path: 扫描结果 JSON 文件路径
        output_dir: 测试文件输出目录
        project_path: 项目根目录（用于读取源码）
    """
    # 路径规范化，消除符号链接和相对路径
    scan_result_path = str(Path(scan_result_path).resolve())
    output_dir = str(Path(output_dir).resolve())
    if project_path:
        project_path = str(Path(project_path).resolve())

    # 读取扫描结果
    scan_file = Path(scan_result_path)
    if not scan_file.exists():
        print(f"错误：扫描结果文件不存在: {scan_result_path}")
        return
    data = load_json(scan_result_path)
    if data is None:
        print(f"错误：无法读取扫描结果文件: {scan_result_path}")
        return

    functions = data.get("functions", [])
    if not functions:
        print("没有可测试的函数")
        return

    # 按语言分组，分别调用对应的生成器
    language_groups = {}
    for func in functions:
        lang = func.get("language", "unknown")
        if lang not in language_groups:
            language_groups[lang] = []
        language_groups[lang].append(func)

    # 语言到生成器函数的映射
    generators = {
        "js": ("JavaScript/TypeScript", generate_js_tests),
        "ts": ("JavaScript/TypeScript", generate_js_tests),
        "javascript": ("JavaScript/TypeScript", generate_js_tests),
        "typescript": ("JavaScript/TypeScript", generate_js_tests),
        "js/ts": ("JavaScript/TypeScript", generate_js_tests),
        "python": ("Python", generate_python_tests),
        "java": ("Java", generate_java_tests),
        "go": ("Go", generate_go_tests),
        "rust": ("Rust", generate_rust_tests),
        "csharp": ("C#", generate_csharp_tests),
        "c#": ("C#", generate_csharp_tests),
    }

    for lang, funcs in language_groups.items():
        if lang in generators:
            lang_name, gen_func = generators[lang]
            print(f"\n生成 {lang_name} 单元测试代码（{len(funcs)} 个函数）...")
            gen_func(funcs, output_dir, project_path)
        else:
            print(f"\n⚠️ 暂不支持 {lang} 语言的测试代码生成（{len(funcs)} 个函数）")

    # 检查是否有函数存在外部依赖，自动生成 Mock 模板
    has_dependencies = any(func.get("dependencies") for func in functions)
    if has_dependencies:
        print(f"\n检测到外部依赖，自动生成 Mock 模板...")
        generate_mock_templates(functions, output_dir)

    print(f"\n测试文件已生成到: {output_dir}")
    print(f"共生成 {len(functions)} 个函数的测试用例")
    print(f"\n⚠️  注意：生成的测试代码为骨架，包含 TODO 占位符")
    print(f"   AI 需要读取源码分析结果，填充具体的测试参数值和预期断言")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python generate_tests.py <扫描结果JSON> <输出目录> [项目路径]")
        print("示例: python generate_tests.py scan_result.json ./tests/ /path/to/project")
        sys.exit(1)

    project = sys.argv[3] if len(sys.argv) >= 4 else ""
    generate_tests(sys.argv[1], sys.argv[2], project)
