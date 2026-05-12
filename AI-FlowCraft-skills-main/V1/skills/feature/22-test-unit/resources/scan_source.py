#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
"""
单元测试辅助脚本 - 源码扫描器
功能：扫描项目源码，识别可测试的函数/方法，分析函数体（返回类型、异常、依赖）
用法：python scan_source.py <项目路径> [输出JSON路径]
"""

import ast
import itertools
import re
import sys
from pathlib import Path

from common import detect_project_type, write_json, get_skip_dirs
from typing import Any, Optional


def scan_project(project_path: str) -> dict[str, Any]:
    """
    扫描项目目录，识别项目类型和可测试的函数/方法

    Args:
        project_path: 项目根目录路径

    Returns:
        dict: 项目信息、函数列表、分析结果
    """
    project_path = Path(project_path).resolve()
    if not project_path.exists():
        print(f"错误：路径不存在 - {project_path}")
        return {}

    # 识别项目类型
    project_type = detect_project_type(project_path)
    print(f"项目类型: {project_type}")

    # 根据项目类型选择扫描策略
    functions = []
    if project_type in ["javascript", "typescript", "react", "vue", "nextjs", "angular", "nuxtjs", "svelte"]:
        functions = scan_js_ts(project_path)
    elif project_type == "python":
        functions = scan_python(project_path)
    elif project_type == "java":
        functions = scan_java(project_path)
    elif project_type == "go":
        functions = scan_go(project_path)
    elif project_type == "rust":
        functions = scan_rust(project_path)
    elif project_type == "csharp":
        functions = scan_csharp(project_path)

    # 过滤掉不适合测试的函数
    filtered = [f for f in functions if not should_skip(f)]

    # 对每个函数进行深度分析（读取函数体）
    analyzed = []
    for func in filtered:
        file_full_path = project_path / func["file"]
        if file_full_path.exists():
            analysis = analyze_function_body(file_full_path, func)
            func.update(analysis)
        analyzed.append(func)

    result = {
        "project_type": project_type,
        "total_functions": len(functions),
        "testable_functions": len(filtered),
        "functions": analyzed
    }

    # 输出结果
    print(f"\n扫描结果:")
    print(f"  总函数数: {len(functions)}")
    print(f"  可测试函数: {len(filtered)}")
    print(f"\n可测试函数列表:")
    for func in filtered:
        return_type = func.get("return_type", "未知")
        exceptions = func.get("exceptions", [])
        deps = func.get("dependencies", [])
        print(f"  - {func['name']} ({func['file']}:{func['line']})")
        print(f"    参数: {func['params']}")
        print(f"    返回类型: {return_type}")
        if exceptions:
            print(f"    异常: {', '.join(exceptions)}")
        if deps:
            print(f"    依赖: {', '.join(deps)}")

    return result


def scan_js_ts(project_path: Path) -> list[dict[str, Any]]:
    """
    扫描 JavaScript/TypeScript 源码，提取可测试的函数
    支持多行函数声明（跨行参数列表）

    Args:
        project_path: 项目根目录

    Returns:
        list: 函数信息列表
    """
    functions = []
    # 排除目录
    skip_dirs = get_skip_dirs("js/ts")

    # JS/TS 文件后缀集合
    JS_TS_SUFFIXES = {".js", ".jsx", ".ts", ".tsx"}
    # 使用 itertools.chain 合并多个精确 glob，避免 rgub("*") 遍历所有文件
    js_ts_files = itertools.chain(
        project_path.rglob("*.js"),
        project_path.rglob("*.jsx"),
        project_path.rglob("*.ts"),
        project_path.rglob("*.tsx"),
    )
    for file_path in js_ts_files:
        # 跳过排除目录
        if any(skip in file_path.parts for skip in skip_dirs):
            continue
        # 跳过测试文件和配置文件
        if any(keyword in file_path.name for keyword in [".test.", ".spec.", "config.", "jest.", "vitest."]):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # === 单行匹配模式 ===
        single_line_patterns = [
            # export async function name<T>(params): ReturnType
            r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*<([^>]+)>\s*\(([^)]*)\)\s*:\s*([^{]+)",
            # export async function name(params): ReturnType
            r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*:\s*([^{]+)",
            # export function name(params)
            r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)",
            # const/let name = async (params): ReturnType =>
            r"(?:export\s+)?(?:const|let)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*:\s*([^{]+)\s*=>",
            # const/let name = async (params) =>
            r"(?:export\s+)?(?:const|let)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>",
        ]

        for line_num, line in enumerate(content.split("\n"), 1):
            for pattern in single_line_patterns:
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1)
                    # 判断参数和返回类型的位置（根据捕获组数量）
                    if match.lastindex >= 4:
                        params = match.group(3).strip() if match.group(3) else "无参数"
                        return_type = match.group(4).strip() if match.group(4) else "unknown"
                    elif match.lastindex >= 3:
                        params = match.group(2).strip() if match.group(2) else "无参数"
                        return_type = match.group(3).strip() if match.group(3) else "unknown"
                    else:
                        params = match.group(2).strip() if match.lastindex >= 2 and match.group(2) else "无参数"
                        return_type = "unknown"

                    # 计算列位置，用于多行匹配去重
                    start_col = match.start()
                    functions.append({
                        "name": func_name,
                        "file": str(file_path.relative_to(project_path)),
                        "line": line_num,
                        "col": start_col,
                        "params": params if params else "无参数",
                        "language": "js/ts",
                        "return_type": return_type,
                        "exceptions": [],
                        "dependencies": [],
                        "docstring": "",
                        "branches": 0,
                    })
                    break  # 一行只匹配一次

        # === 多行函数声明匹配（跨行参数） ===
        # 匹配 function name( 开头但参数跨越多行的情况
        multiline_pattern = r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*(?:<[^>]+>)?\s*\("
        for match in re.finditer(multiline_pattern, content):
            func_name = match.group(1)
            # 计算起始行号和列位置，用于精确去重
            line_num = content[:match.start()].count("\n") + 1
            start_col = match.start() - content[:match.start()].rfind("\n") - 1
            # 检查是否已被单行匹配捕获（按名称、行号和列位置精确匹配）
            if any(f["name"] == func_name and f["line"] == line_num and f.get("col") == start_col for f in functions):
                continue
            # 找到匹配的起始行
            start_line = content[:match.start()].count("\n") + 1
            # 从匹配位置向后查找闭合括号和返回类型
            rest = content[match.end():]
            # 使用括号深度计数器找到匹配的闭合括号
            paren_depth = 1
            paren_end = None  # 使用 None 作为"未找到"的哨兵值
            for k, ch in enumerate(rest):
                if ch == '(':
                    paren_depth += 1
                elif ch == ')':
                    paren_depth -= 1
                    if paren_depth == 0:
                        paren_end = k
                        break
            if paren_end is None:
                continue  # 未找到匹配的闭合括号，跳过
            params = rest[:paren_end].strip()
            # 查找返回类型（: ReturnType {）
            after_paren = rest[paren_end + 1:].lstrip()
            return_type = "unknown"
            ret_match = re.match(r":\s*([^{]+?)\s*\{", after_paren)
            if ret_match:
                return_type = ret_match.group(1).strip()

            functions.append({
                "name": func_name,
                "file": str(file_path.relative_to(project_path)),
                "line": start_line,
                "col": start_col,
                "params": params if params else "无参数",
                "language": "js/ts",
                "return_type": return_type,
                "exceptions": [],
                "dependencies": [],
                "docstring": "",
                "branches": 0,
            })

    return functions


def _process_python_node(item, file_path: Path, project_path: Path, content: str) -> Optional[dict[str, Any]]:
    """
    处理单个 Python 函数/方法节点，提取函数信息

    统一处理顶层函数定义和类中方法定义的公共逻辑，
    消除 scan_python() 中的重复代码。

    Args:
        item: AST 节点（FunctionDef 或 AsyncFunctionDef）
        file_path: 文件路径
        project_path: 项目根路径
        content: 文件原始内容（用于依赖分析）

    Returns:
        Optional[dict]: 函数信息字典，如果应跳过则返回 None
    """
    func_name = item.name

    # 跳过私有方法（以 _ 开头但非 __init__）
    if func_name.startswith("_") and func_name != "__init__":
        return None

    # 提取参数列表
    params = _extract_python_params(item)

    # 提取返回类型注解
    return_type = "unknown"
    if item.returns:
        return_type = ast.unparse(item.returns) if hasattr(ast, 'unparse') else "typed"

    # 提取 docstring
    docstring = ast.get_docstring(item) or ""

    # 分析函数体：异常、依赖、分支数
    exceptions = _find_python_exceptions(item)
    dependencies = _find_python_dependencies(item, content)
    branches = _count_python_branches(item)

    return {
        "name": func_name,
        "file": str(file_path.relative_to(project_path)),
        "line": item.lineno,
        "params": params if params else "无参数",
        "language": "python",
        "return_type": return_type,
        "exceptions": exceptions,
        "dependencies": dependencies,
        "docstring": docstring,
        "branches": branches,
    }


def scan_python(project_path: Path) -> list[dict[str, Any]]:
    """
    扫描 Python 源码，使用 AST 解析提取可测试的函数（比正则更准确）

    Args:
        project_path: 项目根目录

    Returns:
        list: 函数信息列表
    """
    functions = []
    skip_dirs = get_skip_dirs("python")

    for file_path in project_path.rglob("*.py"):
        if any(skip in file_path.parts for skip in skip_dirs):
            continue
        # 跳过测试文件
        if "test_" in file_path.name or "_test.py" in file_path.name:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            # 使用 AST 解析（比正则更准确）
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            # AST 解析失败，回退到正则
            functions.extend(_scan_python_regex(file_path, project_path, content))
            continue
        except Exception as e:
            # 非 SyntaxError 异常输出警告到 stderr，便于排查问题
            print(f"警告: 解析 {file_path} 时发生异常: {e}", file=sys.stderr)
            continue

        # 遍历 AST 顶层节点，提取函数定义（避免遍历嵌套函数）
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 处理顶层函数定义
                func_info = _process_python_node(node, file_path, project_path, content)
                if func_info:
                    functions.append(func_info)
            elif isinstance(node, ast.ClassDef):
                # 处理类中的方法定义
                for item in ast.iter_child_nodes(node):
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_info = _process_python_node(item, file_path, project_path, content)
                        if func_info:
                            functions.append(func_info)

    return functions


def _scan_python_regex(file_path: Path, project_path: Path, content: str) -> list[dict[str, Any]]:
    """
    正则回退方案：当 AST 解析失败时使用正则扫描 Python 文件

    Args:
        file_path: 文件路径
        project_path: 项目根目录
        content: 文件内容

    Returns:
        list: 函数信息列表
    """
    functions = []
    pattern = r"def\s+(\w+)\s*\(([^)]*)\)"
    for line_num, line in enumerate(content.split("\n"), 1):
        match = re.search(pattern, line)
        if match:
            func_name = match.group(1)
            # 跳过私有方法
            if func_name.startswith("_") and func_name != "__init__":
                continue
            params = match.group(2).strip()
            functions.append({
                "name": func_name,
                "file": str(file_path.relative_to(project_path)),
                "line": line_num,
                "params": params if params else "无参数",
                "language": "python",
                "return_type": "unknown",
                "exceptions": [],
                "dependencies": [],
                "docstring": "",
                "branches": 0,
            })
    return functions


def _extract_python_params(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """
    从 AST 节点提取 Python 函数参数列表

    Args:
        node: 函数 AST 节点

    Returns:
        str: 参数字符串
    """
    params = []
    for arg in node.args.args:
        param_str = arg.arg
        # 如果有类型注解，附加类型
        if arg.annotation:
            type_str = ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else "typed"
            param_str += f": {type_str}"
        params.append(param_str)

    # 处理 *args
    if node.args.vararg:
        params.append(f"*{node.args.vararg.arg}")

    # 处理 **kwargs
    if node.args.kwarg:
        params.append(f"**{node.args.kwarg.arg}")

    return ", ".join(params) if params else "无参数"


def _walk_skip_nested_funcs(node: ast.AST) -> list[ast.AST]:
    """
    辅助函数：遍历 AST 节点，但跳过嵌套函数/类的子节点。
    用于替代 ast.walk，避免将嵌套函数中的异常、依赖、分支
    错误地计入外层函数。

    Args:
        node: 起始 AST 节点

    Returns:
        list: 所有子节点列表（不包含嵌套函数/类的内部节点）
    """
    result = []
    # 使用栈进行深度优先遍历
    stack = [node]
    while stack:
        current = stack.pop()
        result.append(current)
        for child in ast.iter_child_nodes(current):
            # 跳过嵌套的函数定义和类定义，不递归进入其子节点
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                # 仍然将嵌套函数/类本身加入结果，但不遍历其内部
                result.append(child)
                continue
            stack.append(child)
    return result


def _find_python_exceptions(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """
    分析 Python 函数中可能抛出的异常

    Args:
        node: 函数 AST 节点

    Returns:
        list: 异常类型列表
    """
    exceptions = set()

    for child in _walk_skip_nested_funcs(node):
        # 查找 raise 语句
        if isinstance(child, ast.Raise):
            if isinstance(child.exc, ast.Name):
                exceptions.add(child.exc.id)
            elif isinstance(child.exc, ast.Call) and isinstance(child.exc.func, ast.Name):
                exceptions.add(child.exc.func.id)
            elif isinstance(child.exc, ast.Call) and isinstance(child.exc.func, ast.Attribute):
                exceptions.add(child.exc.func.attr)

        # 查找 except 子句（说明函数可能抛出这些异常）
        if isinstance(child, ast.ExceptHandler):
            if child.type:
                if isinstance(child.type, ast.Name):
                    exceptions.add(child.type.id)
                elif isinstance(child.type, ast.Tuple):
                    for elt in child.type.elts:
                        if isinstance(elt, ast.Name):
                            exceptions.add(elt.id)

    return list(exceptions)


def _find_python_dependencies(node: ast.FunctionDef | ast.AsyncFunctionDef, content: str) -> list[str]:
    """
    分析 Python 函数的外部依赖（import 的模块、调用的外部函数）

    Args:
        node: 函数 AST 节点
        content: 文件完整内容

    Returns:
        list: 依赖名称列表
    """
    dependencies = set()

    for child in _walk_skip_nested_funcs(node):
        # 查找属性调用（如 requests.get、db.session）
        if isinstance(child, ast.Attribute):
            if isinstance(child.value, ast.Name):
                dep = child.value.id
                # 过滤掉内置和 self/cls
                if dep not in ("self", "cls", "True", "False", "None"):
                    dependencies.add(dep)

        # 查找 import 调用（如 from X import Y）
        if isinstance(child, ast.ImportFrom):
            if child.module:
                dependencies.add(child.module.split(".")[0])

    # 从文件顶部提取 import 的外部模块
    try:
        file_tree = ast.parse(content)
        for top_node in ast.iter_child_nodes(file_tree):
            if isinstance(top_node, ast.Import):
                for alias in top_node.names:
                    dependencies.add(alias.name.split(".")[0])
            elif isinstance(top_node, ast.ImportFrom):
                if top_node.module and not top_node.module.startswith("."):
                    dependencies.add(top_node.module.split(".")[0])
    except SyntaxError:
        pass

    # 过滤掉 Python 内置模块
    builtins = {
        "os", "sys", "json", "re", "math", "datetime", "time", "collections",
        "itertools", "functools", "typing", "dataclasses", "abc", "copy",
        "pathlib", "io", "logging", "warnings", "contextlib", "enum",
        "hashlib", "base64", "uuid", "random", "secrets",
    }
    return [d for d in dependencies if d not in builtins and not d.startswith("_")]


def _count_python_branches(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """
    统计 Python 函数中的条件分支数量（用于评估测试复杂度）

    Args:
        node: 函数 AST 节点

    Returns:
        int: 分支数量
    """
    count = 0
    for child in _walk_skip_nested_funcs(node):
        if isinstance(child, (ast.If, ast.While, ast.For)):
            count += 1
        # 三元表达式
        if isinstance(child, ast.IfExp):
            count += 1
        # match-case（Python 3.10+）
        if hasattr(ast, "Match") and isinstance(child, ast.Match):
            count += len(child.cases)
    return count


def scan_java(project_path: Path) -> list[dict[str, Any]]:
    """
    扫描 Java 源码，提取可测试的方法

    Args:
        project_path: 项目根目录

    Returns:
        list: 方法信息列表
    """
    functions = []
    skip_dirs = get_skip_dirs("java")

    for file_path in project_path.rglob("*.java"):
        if any(skip in file_path.parts for skip in skip_dirs):
            continue
        # 跳过测试文件
        if "Test" in file_path.stem:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # 匹配 public/protected 方法声明，包含返回类型
        # 格式: [public/protected] [static] [final] ReturnType methodName(params) [throws Exception]
        pattern = (
            r"(?:public|protected)\s+(?:static\s+)?(?:final\s+)?"
            r"([\w<>\[\],\s]+?)\s+"  # 返回类型
            r"(\w+)\s*"               # 方法名
            r"\(([^)]*)\)"            # 参数列表
            r"\s*(?:throws\s+([\w,\s]+))?"  # throws 声明
        )
        for line_num, line in enumerate(content.split("\n"), 1):
            match = re.search(pattern, line)
            if match:
                return_type = match.group(1).strip()
                method_name = match.group(2).strip()
                params = match.group(3).strip()
                throws = match.group(4).strip() if match.group(4) else ""

                # 跳过 main 方法和 getter/setter
                if method_name in ["main", "equals", "hashCode", "toString"]:
                    continue
                # 仅当第四个字符为大写时才视为 getter/setter（与 should_skip 函数保持一致）
                if (method_name.startswith("get") or method_name.startswith("set")) \
                        and len(method_name) > 3 and method_name[3:4].isupper():
                    continue

                # 解析 throws 中的异常类型
                exceptions = [e.strip() for e in throws.split(",") if e.strip()] if throws else []

                # 分析函数体中的依赖和分支
                dependencies = _find_java_dependencies(content, line_num)
                branches = _count_java_branches(content, line_num)

                functions.append({
                    "name": method_name,
                    "file": str(file_path.relative_to(project_path)),
                    "line": line_num,
                    "params": params if params else "无参数",
                    "language": "java",
                    "return_type": return_type,
                    "exceptions": exceptions,
                    "dependencies": dependencies,
                    "docstring": "",
                    "branches": branches,
                })

    return functions


def _find_java_dependencies(content: str, start_line: int) -> list[str]:
    """
    分析 Java 方法中的外部依赖（方法调用、字段访问）

    Args:
        content: 文件完整内容
        start_line: 方法起始行号

    Returns:
        list: 依赖名称列表
    """
    # 提取方法体（复用通用工具函数）
    clean_body = _get_clean_method_body(content, start_line, "java")

    # 查找方法调用模式: object.method() 或 Class.method()
    call_pattern = r"([\w]+)\.\w+\s*\("
    calls = set(re.findall(call_pattern, clean_body))

    # 过滤掉 Java 内置类型和常用类
    java_builtins = {
        "this", "super", "System", "Arrays", "Objects", "Collections",
        "Math", "String", "Integer", "Long", "Double", "Boolean",
        "List", "Map", "Set", "Optional", "Stream",
    }
    calls = {c for c in calls if c not in java_builtins}

    # 查找注解中的依赖（如 @Autowired, @Inject）
    inject_pattern = r"@(?:Autowired|Inject|Resource|Value)\b"
    has_injection = bool(re.search(inject_pattern, clean_body))

    deps = list(calls)
    if has_injection:
        deps.append("@Injected")
    return deps


def _count_java_branches(content: str, start_line: int) -> int:
    """
    统计 Java 方法中的条件分支数量

    Args:
        content: 文件完整内容
        start_line: 方法起始行号

    Returns:
        int: 分支数量
    """
    clean_body = _get_clean_method_body(content, start_line, "java")
    count = 0
    # if/else, switch, for, while, try-catch
    count += len(re.findall(r"\bif\s*\(", clean_body))
    count += len(re.findall(r"\bswitch\s*\(", clean_body))
    count += len(re.findall(r"\bfor\s*\(", clean_body))
    count += len(re.findall(r"\bwhile\s*\(", clean_body))
    count += len(re.findall(r"\bcatch\s*\(", clean_body))
    # 三元表达式
    count += len(re.findall(r"\?\s*[^:]+:", clean_body))
    return count


def scan_go(project_path: Path) -> list[dict[str, Any]]:
    """
    扫描 Go 源码，提取可测试的函数

    Args:
        project_path: 项目根目录

    Returns:
        list: 函数信息列表
    """
    functions = []
    skip_dirs = get_skip_dirs("go")

    for file_path in project_path.rglob("*.go"):
        if any(skip in file_path.parts for skip in skip_dirs):
            continue
        # 跳过测试文件
        if file_path.name.endswith("_test.go"):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # 匹配导出函数（大写开头），包含返回类型
        # 先尝试匹配带 receiver 的方法: func (s *Type) MethodName(params) ReturnType
        method_pattern = r"func\s+\([^)]+\)\s+(\w+)\s*\(([^)]*)\)"
        # 再尝试匹配普通函数: func FunctionName(params) ReturnType
        func_pattern = r"func\s+(\w+)\s*\(([^)]*)\)\s*(?:\(([^)]*)\)|([\w\[\]*.]+))?"
        for line_num, line in enumerate(content.split("\n"), 1):
            match = re.search(method_pattern, line)
            if not match:
                match = re.search(func_pattern, line)
            if match:
                func_name = match.group(1)
                if not func_name:
                    continue
                # 只匹配导出函数（大写开头）
                if not func_name[0].isupper():
                    continue
                params = match.group(2).strip()
                # 返回类型：带 receiver 的方法需要额外解析返回类型
                if re.search(method_pattern, line):
                    # 带 receiver 的方法，需要先找到方法名后的参数列表闭合括号，
                    # 再从其后提取返回类型，避免将 receiver 部分误匹配为返回类型
                    return_type = _find_go_return_type(line, func_name)
                else:
                    # 普通函数，返回类型：优先取括号内的多返回值，否则取单个返回值
                    return_type = match.group(3).strip() if match.group(3) else ""
                    if not return_type and match.group(4):
                        return_type = match.group(4).strip()
                    if not return_type:
                        return_type = "void"
                    # 如果返回类型包含未闭合的括号，尝试提取完整返回类型
                    if return_type and return_type.count("(") > return_type.count(")"):
                        # 使用括号深度计数器从原始行中提取完整返回类型
                        line_text = line.strip()
                        func_idx = line_text.find(f"func {func_name}")
                        if func_idx >= 0:
                            after_params = line_text.find(")", line_text.find(")", func_idx) + 1)
                            if after_params >= 0:
                                brace_idx = line_text.find("{", after_params)
                                full_return = line_text[after_params+1:brace_idx].strip() if brace_idx >= 0 else line_text[after_params+1:].strip()
                                if full_return:
                                    return_type = full_return

                # 分析函数体
                dependencies = _find_go_dependencies(content, line_num)
                branches = _count_go_branches(content, line_num)
                exceptions = _find_go_errors(content, line_num)

                functions.append({
                    "name": func_name,
                    "file": str(file_path.relative_to(project_path)),
                    "line": line_num,
                    "params": params if params else "无参数",
                    "language": "go",
                    "return_type": return_type,
                    "exceptions": exceptions,
                    "dependencies": dependencies,
                    "docstring": "",
                    "branches": branches,
                })

    return functions


def _find_go_return_type(line: str, func_name: str) -> str:
    """
    从 Go 方法声明行中提取返回类型，正确处理带 receiver 的方法。
    例如: func (s *Service) MethodName(param string) error -> "error"
    例如: func (s *Service) MethodName() (int, error) -> "(int, error)"

    Args:
        line: 方法声明所在行
        func_name: 方法名

    Returns:
        str: 返回类型字符串，无返回值时返回 "void"
    """
    # 找到方法名在行中的位置
    name_pos = line.find(func_name)
    if name_pos == -1:
        return "void"

    # 从方法名之后开始查找参数列表的起始括号
    after_name = line[name_pos + len(func_name):]
    paren_start = after_name.find('(')
    if paren_start == -1:
        return "void"

    # 使用括号深度计数器找到参数列表的闭合括号
    rest = after_name[paren_start + 1:]
    paren_depth = 1
    paren_end = None  # 使用 None 作为"未找到"的哨兵值
    for k, ch in enumerate(rest):
        if ch == '(':
            paren_depth += 1
        elif ch == ')':
            paren_depth -= 1
            if paren_depth == 0:
                paren_end = k
                break

    if paren_end is None:
        return "void"

    # 闭合括号之后的内容即为返回类型部分
    after_params = rest[paren_end + 1:].strip()
    if not after_params:
        return "void"

    # 匹配返回类型：可能是括号内的多返回值 (int, error) 或单个返回值 error
    # 使用括号深度计数器正确处理嵌套括号，如 (map[string]func() error, error)
    if after_params.startswith('('):
        depth = 0
        ret_end = 0
        for k, c in enumerate(after_params):
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    ret_end = k
                    break
        if ret_end > 0:
            # 保留外层括号，如 (int, error) 或 (map[string]func() error, error)
            return "(" + after_params[1:ret_end].strip() + ")"

    # 单个返回值（直到行尾或大括号）
    single_match = re.match(r'([\w\[\]*.]+)', after_params)
    if single_match:
        return single_match.group(1).strip()

    return "void"


def _find_go_dependencies(content: str, start_line: int) -> list[str]:
    """
    分析 Go 函数中的外部依赖

    Args:
        content: 文件完整内容
        start_line: 函数起始行号

    Returns:
        list: 依赖名称列表
    """
    clean_body = _get_clean_method_body(content, start_line, "go")

    # 查找方法调用: object.Method() 或 package.Function()
    call_pattern = r"([\w.]+)\.[\w]+\s*\("
    calls = set(re.findall(call_pattern, clean_body))

    # 过滤掉 Go 内置
    builtins = {"fmt", "os", "log", "time", "strings", "strconv", "math", "sync", "context"}
    return [c for c in calls if c.split(".")[0] not in builtins]


def _count_go_branches(content: str, start_line: int) -> int:
    """
    统计 Go 函数中的条件分支数量

    Args:
        content: 文件完整内容
        start_line: 函数起始行号

    Returns:
        int: 分支数量
    """
    clean_body = _get_clean_method_body(content, start_line, "go")
    count = 0
    # 统计所有 if 语句（包括 if err != nil 模式）
    count += len(re.findall(r"\bif\s+", clean_body))
    count += len(re.findall(r"\bswitch\s+", clean_body))
    count += len(re.findall(r"\bfor\s+", clean_body))
    count += len(re.findall(r"\bselect\s+{", clean_body))
    return count


def _find_go_errors(content: str, start_line: int) -> list[str]:
    """
    分析 Go 函数中返回的错误类型

    Args:
        content: 文件完整内容
        start_line: 函数起始行号

    Returns:
        list: 错误相关描述
    """
    clean_body = _get_clean_method_body(content, start_line, "go")
    errors = []

    # 查找 errors.New, fmt.Errorf
    error_patterns = [
        r"errors\.New\(([^)]+)\)",
        r"fmt\.Errorf\(([^)]+)\)",
        r"return\s+[^,]+,\s*(err(?:or)?)\s*$",  # 返回 error（仅匹配 err 或 error）
    ]
    for pattern in error_patterns:
        matches = re.findall(pattern, clean_body)
        errors.extend(matches)

    return errors if errors else []


def scan_rust(project_path: Path) -> list[dict[str, Any]]:
    """
    扫描 Rust 源码，提取可测试的函数（pub fn）

    Args:
        project_path: 项目根目录

    Returns:
        list: 函数信息列表
    """
    functions = []
    skip_dirs = get_skip_dirs("rust")

    for file_path in project_path.rglob("*.rs"):
        if any(skip in file_path.parts for skip in skip_dirs):
            continue
        # 跳过测试文件和 build.rs
        if file_path.name.endswith("_test.rs") or file_path.name == "build.rs":
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # 匹配 pub fn / pub async fn，支持多行参数
        # 格式: pub async fn name<T>(params) -> ReturnType
        pattern = r"(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*(?:<[^>]+>)?\s*\(([^)]*)\)\s*(?:->\s*([^{]+))?"
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            match = re.search(pattern, line)
            if match:
                func_name = match.group(1)
                # 检查是否为 pub 函数（可能在匹配行或前一行）
                is_pub = "pub" in line or (i > 1 and "pub" in lines[i - 2])
                if not is_pub:
                    continue
                params = match.group(2).strip() if match.group(2) else "无参数"
                return_type = match.group(3).strip() if match.group(3) else "()"
                if not return_type:
                    return_type = "()"

                # 分析函数体
                dependencies = _find_rust_dependencies(content, i)
                branches = _count_rust_branches(content, i)
                errors = _find_rust_errors(content, i)

                functions.append({
                    "name": func_name,
                    "file": str(file_path.relative_to(project_path)),
                    "line": i,
                    "params": params if params else "无参数",
                    "language": "rust",
                    "return_type": return_type,
                    "exceptions": errors,
                    "dependencies": dependencies,
                    "docstring": "",
                    "branches": branches,
                })

    return functions


def _find_rust_dependencies(content: str, start_line: int) -> list[str]:
    """
    分析 Rust 函数中的外部依赖

    Args:
        content: 文件完整内容
        start_line: 函数起始行号

    Returns:
        list: 依赖名称列表
    """
    clean_body = _get_clean_method_body(content, start_line, "rust")

    # 查找方法调用: object.method() 或 Type::method()
    call_pattern = r"([\w]+)\s*(?:\.\w+|::\w+)\s*\("
    calls = set(re.findall(call_pattern, clean_body))

    # 过滤掉 Rust 内置类型和常用宏
    builtins = {"vec", "String", "Box", "Rc", "Arc", "Option", "Result",
                "Some", "None", "Ok", "Err", "format", "println",
                "eprintln", "dbg", "panic", "assert", "todo", "unimplemented",
                "self", "Self", "super", "crate", "std", "true", "false"}
    return [c for c in calls if c not in builtins]


def _count_rust_branches(content: str, start_line: int) -> int:
    """
    统计 Rust 函数中的条件分支数量

    Args:
        content: 文件完整内容
        start_line: 函数起始行号

    Returns:
        int: 分支数量
    """
    clean_body = _get_clean_method_body(content, start_line, "rust")

    count = 0
    # 排除 is_err()/is_ok() 调用（不是控制流分支，而是布尔检查）
    filtered_body = re.sub(r"\bif\s+\w+\.is_(err|ok)\(\)", "", clean_body)
    # 使用负向前瞻排除 if let，避免双重计数
    count += len(re.findall(r"\bif\s+(?!let\b)", filtered_body))
    count += len(re.findall(r"\bmatch\s+", filtered_body))
    count += len(re.findall(r"\bfor\s+", filtered_body))
    count += len(re.findall(r"\bwhile\s+let\b", filtered_body))
    count += len(re.findall(r"\bloop\s*\{", filtered_body))
    count += len(re.findall(r"if\s+let\s+", filtered_body))  # if let 模式匹配
    return count


def _find_rust_errors(content: str, start_line: int) -> list[str]:
    """
    分析 Rust 函数中返回的错误类型

    Args:
        content: 文件完整内容
        start_line: 函数起始行号

    Returns:
        list: 错误相关描述
    """
    clean_body = _get_clean_method_body(content, start_line, "rust")

    errors = []
    # 查找 Error:: / anyhow! / thiserror
    error_patterns = [
        r"Error::(\w+)",
        r"anyhow!\(([^)]+)\)",
        r"bail!\(([^)]+)\)",
    ]
    for pattern in error_patterns:
        matches = re.findall(pattern, clean_body)
        errors.extend(matches)
    return errors if errors else []


def scan_csharp(project_path: Path) -> list[dict[str, Any]]:
    """
    扫描 C# 源码，提取可测试的方法（public 方法）

    Args:
        project_path: 项目根目录

    Returns:
        list: 方法信息列表
    """
    functions = []
    skip_dirs = get_skip_dirs("csharp")

    for file_path in project_path.rglob("*.cs"):
        if any(skip in file_path.parts for skip in skip_dirs):
            continue
        # 跳过测试文件和自动生成文件
        # 匹配 *Tests.cs（复数）、*Test.cs（单数）、*.Spec.cs、自动生成文件、测试目录
        test_patterns = ("Tests.cs", "Test.cs", ".Spec.cs")
        test_dirs = {"Tests", "Test", "Specs", "Specifications", "__tests__"}
        is_test_file = any(file_path.name.endswith(p) for p in test_patterns)
        is_test_dir = any(part in test_dirs for part in file_path.parts)
        if is_test_file or is_test_dir:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # 匹配 public/protected/internal 方法声明
        # 格式: [public/protected/internal] [static] [async] ReturnType MethodName(params)
        pattern = (
            r"(?:public|protected|internal)\s+(?:static\s+)?(?:async\s+)?(?:virtual\s+|override\s+|abstract\s+)?"
            r"([\w<>\[\],\s\?]+?)\s+"  # 返回类型
            r"(\w+)\s*"               # 方法名
            r"\(([^)]*)\)"            # 参数列表
        )
        for line_num, line in enumerate(content.split("\n"), 1):
            match = re.search(pattern, line)
            if match:
                return_type = match.group(1).strip()
                method_name = match.group(2).strip()
                params = match.group(3).strip()

                # 跳过不需要测试的方法
                skip_methods = {"Main", "Equals", "GetHashCode", "ToString",
                                "GetType", "MemberwiseClone", "Finalize",
                                "Dispose", "ConfigureAwait"}
                if method_name in skip_methods:
                    continue
                # 跳过 getter/setter 属性
                if (method_name.startswith("get_") or method_name.startswith("set_")):
                    continue

                # 分析函数体
                dependencies = _find_csharp_dependencies(content, line_num)
                branches = _count_csharp_branches(content, line_num)
                exceptions = _find_csharp_exceptions(content, line_num)

                functions.append({
                    "name": method_name,
                    "file": str(file_path.relative_to(project_path)),
                    "line": line_num,
                    "params": params if params else "无参数",
                    "language": "csharp",
                    "return_type": return_type,
                    "exceptions": exceptions,
                    "dependencies": dependencies,
                    "docstring": "",
                    "branches": branches,
                })

    return functions


def _find_csharp_dependencies(content: str, start_line: int) -> list[str]:
    """
    分析 C# 方法中的外部依赖

    Args:
        content: 文件完整内容
        start_line: 方法起始行号

    Returns:
        list: 依赖名称列表
    """
    clean_body = _get_clean_method_body(content, start_line, "csharp")

    # 查找方法调用: object.Method() 或 await xxx.MethodAsync()
    call_pattern = r"(?:await\s+)?([\w]+)\.\w+\s*\("
    calls = set(re.findall(call_pattern, clean_body))

    # 过滤掉 C# 内置
    builtins = {"Console", "Convert", "Math", "String", "DateTime", "Guid",
                "Environment", "File", "Directory", "Path", "Task", "List",
                "Dictionary", "Enumerable", "int", "string", "bool", "var",
                "this", "base", "typeof", "nameof"}
    return [c for c in calls if c not in builtins]


def _count_csharp_branches(content: str, start_line: int) -> int:
    """
    统计 C# 方法中的条件分支数量

    Args:
        content: 文件完整内容
        start_line: 方法起始行号

    Returns:
        int: 分支数量
    """
    clean_body = _get_clean_method_body(content, start_line, "csharp")

    count = 0
    count += len(re.findall(r"\bif\s*\(", clean_body))
    count += len(re.findall(r"\bswitch\s*\(", clean_body))
    count += len(re.findall(r"\bfor\s*\(", clean_body))
    count += len(re.findall(r"\bforeach\s*\(", clean_body))
    count += len(re.findall(r"\bwhile\s*\(", clean_body))
    count += len(re.findall(r"\bcatch\s*\(", clean_body))
    # 三元表达式（已在 clean_body 中剥离注释和字符串）
    ternary_count = len(re.findall(r"\?\s*[^?:]+:", clean_body))
    count += ternary_count
    return count


def _find_csharp_exceptions(content: str, start_line: int) -> list[str]:
    """
    分析 C# 方法中抛出的异常

    Args:
        content: 文件完整内容
        start_line: 方法起始行号

    Returns:
        list: 异常类型列表
    """
    clean_body = _get_clean_method_body(content, start_line, "csharp")

    exceptions = set()
    # throw new XxxException
    throw_matches = re.findall(r"throw\s+new\s+(\w+Exception)", clean_body)
    exceptions.update(throw_matches)
    return list(exceptions)


def _strip_comments_and_strings(body: str, lang: str) -> str:
    """
    通用辅助函数：剥离代码中的注释和字符串内容，避免分支计数时误匹配。
    将注释和字符串替换为空格（保留长度以维持行号对应关系）。

    Args:
        body: 方法体文本
        lang: 语言标识 ("java", "go", "rust", "csharp")

    Returns:
        str: 剥离注释和字符串后的代码
    """
    result = []
    i = 0
    n = len(body)

    while i < n:
        ch = body[i]

        # === 处理块注释（支持 Go 嵌套块注释 /* /* nested */ */） ===
        if ch == '/' and i + 1 < n and body[i + 1] == '*':
            # 使用嵌套深度计数器，支持任意深度的块注释嵌套
            depth = 1
            j = i + 2
            while j < n and depth > 0:
                if body[j] == '/' and j + 1 < n and body[j + 1] == '*':
                    depth += 1
                    j += 2
                elif body[j] == '*' and j + 1 < n and body[j + 1] == '/':
                    depth -= 1
                    j += 2
                else:
                    j += 1
            # 将整个块注释替换为空格（保留换行符以维持行号对应）
            for k in range(i, j):
                result.append(' ' if body[k] != '\n' else '\n')
            i = j
            continue

        # === 处理行注释（Java/Go/Rust/C# 通用） ===
        if ch == '/' and i + 1 < n and body[i + 1] == '/':
            # 行注释 // ...，替换到行尾
            while i < n and body[i] != '\n':
                result.append(' ')
                i += 1
            continue

        # === 处理 Rust 特有的行注释和文档注释 ===
        # Rust 也使用 //，已在上面的通用逻辑中处理

        # === 处理字符串 ===
        # Rust 原始字符串：r"..." 和 r#"..."#, r##"..."## 等（必须在普通双引号之前检测）
        if lang == "rust" and ch == 'r' and i + 1 < n and body[i + 1] == '"':
            result.append(' ')
            result.append(' ')
            i += 2
            # r"..." 形式：查找下一个未转义的 "
            while i < n and body[i] != '"':
                result.append(' ' if body[i] != '\n' else '\n')
                i += 1
            if i < n:
                result.append(' ')
                i += 1
            continue

        # Rust 原始字符串带井号：r#"..."#, r##"..."## 等
        if lang == "rust" and ch == 'r' and i + 1 < n and body[i + 1] == '#':
            # 计算前导井号数量
            hash_count = 0
            k = i + 1
            while k < n and body[k] == '#':
                hash_count += 1
                k += 1
            # 检查井号后面是否紧跟 "
            if k < n and body[k] == '"':
                # 将 r + #...# + " 替换为空格
                for _ in range(k - i + 1):
                    result.append(' ')
                i = k + 1
                # 查找匹配的结束 "#...#"
                end_marker = '"' + '#' * hash_count
                end_pos = body.find(end_marker, i)
                if end_pos == -1:
                    # 未闭合，替换到末尾
                    while i < n:
                        result.append(' ' if body[i] != '\n' else '\n')
                        i += 1
                else:
                    for j in range(i, end_pos + len(end_marker)):
                        result.append(' ' if body[j] != '\n' else '\n')
                    i = end_pos + len(end_marker)
                continue

        if ch == '"':
            # 双引号字符串
            result.append(' ')  # 保留起始引号位置
            i += 1
            while i < n and body[i] != '"':
                if body[i] == '\\' and i + 1 < n:
                    result.append(' ')
                    result.append(' ')
                    i += 2
                else:
                    result.append(' ' if body[i] != '\n' else '\n')
                    i += 1
            if i < n:
                result.append(' ')  # 保留结束引号位置
                i += 1
            continue

        if ch == "'":
            # Rust 生命周期标注检查：'a, 'static, '_ref 等不是字符字面量
            # 当 lang 为 rust 时，如果 ' 后紧跟字母/下划线，扫描完整生命周期名称
            if lang == "rust" and i + 1 < n and (body[i + 1].isalpha() or body[i + 1] == '_'):
                # 扫描完整的生命周期名称（如 'a, 'static, '_ref）
                lifetime_end = i + 2
                while lifetime_end < n and (body[lifetime_end].isalnum() or body[lifetime_end] == '_'):
                    lifetime_end += 1
                # 检查生命周期名称后的分隔符（如 'a>, 'static,, 'a), 'a , 'a], 'a:, 'a+）
                # lifetime_end >= n 时（行尾/文件尾），也识别为生命周期标注
                if lifetime_end >= n or body[lifetime_end] in ('>', ',', ')', ' ', ']', ':', '+'):
                    # 保留完整的生命周期标注（从 ' 到名称末尾）
                    for k in range(i, lifetime_end):
                        result.append(body[k])
                    i = lifetime_end
                    continue
            # 单引号字符/字符串
            result.append(' ')
            i += 1
            while i < n and body[i] != "'":
                if body[i] == '\\' and i + 1 < n:
                    result.append(' ')
                    result.append(' ')
                    i += 2
                else:
                    result.append(' ' if body[i] != '\n' else '\n')
                    i += 1
            if i < n:
                result.append(' ')
                i += 1
            continue

        # C# 支持 @"" 原始字符串
        if lang == "csharp" and ch == '@' and i + 1 < n and body[i + 1] == '"':
            result.append(' ')
            result.append(' ')
            i += 2
            while i < n:
                if body[i] == '"' and i + 1 < n and body[i + 1] == '"':
                    result.append(' ')
                    result.append(' ')
                    i += 2
                elif body[i] == '"':
                    result.append(' ')
                    i += 1
                    break
                else:
                    result.append(' ' if body[i] != '\n' else '\n')
                    i += 1
            continue

        # JS/TS 支持反引号模板字符串 `...${...}...`，需处理 ${...} 表达式嵌套
        if lang == "javascript" and ch == '`':
            result.append(' ')  # 保留起始反引号位置
            i += 1
            brace_depth = 0  # ${...} 表达式嵌套深度
            while i < n:
                if body[i] == '`' and brace_depth == 0:
                    # 模板字符串结束
                    result.append(' ')
                    i += 1
                    break
                elif body[i] == '$' and i + 1 < n and body[i + 1] == '{':
                    # 进入 ${...} 表达式
                    result.append(' ')
                    result.append(' ')
                    i += 2
                    brace_depth += 1
                elif body[i] == '{' and brace_depth > 0:
                    # 表达式内嵌套的 {
                    result.append(' ')
                    i += 1
                    brace_depth += 1
                elif body[i] == '}' and brace_depth > 0:
                    # 表达式内嵌套的 }
                    result.append(' ')
                    i += 1
                    brace_depth -= 1
                elif body[i] == '\\' and i + 1 < n:
                    # 转义字符
                    result.append(' ')
                    result.append(' ')
                    i += 2
                else:
                    result.append(' ' if body[i] != '\n' else '\n')
                    i += 1
            continue

        # Go 支持 `` 原始字符串
        if lang == "go" and ch == '`':
            result.append(' ')
            i += 1
            while i < n and body[i] != '`':
                result.append(' ' if body[i] != '\n' else '\n')
                i += 1
            if i < n:
                result.append(' ')
                i += 1
            continue

        result.append(ch)
        i += 1

    return ''.join(result)


def _extract_method_body(lines: list[str], start_line: int) -> list[str]:
    """
    从起始行提取方法体（大括号匹配），跳过字符串和注释中的大括号

    Args:
        lines: 文件所有行
        start_line: 方法开始的行号（1-based）

    Returns:
        list: 方法体的行列表
    """
    if start_line < 1 or start_line > len(lines):
        return []

    body = []
    brace_count = 0
    in_string = None  # 当前字符串引号类型: '"', "'", '`', 或 None
    in_line_comment = False  # 行注释 //
    in_block_comment = False  # 块注释 /* */

    for i in range(start_line - 1, min(start_line + 500, len(lines))):
        line = lines[i]
        body.append(line)

        # 每行开始时重置行注释状态，避免上一行的 // 注释影响后续行的大括号计数
        in_line_comment = False

        j = 0
        while j < len(line):
            ch = line[j]

            # 处理块注释
            if in_block_comment:
                if ch == '*' and j + 1 < len(line) and line[j + 1] == '/':
                    in_block_comment = False
                    j += 2
                    continue
                j += 1
                continue

            # 处理行注释
            if in_line_comment:
                break

            # 处理字符串
            if in_string:
                if ch == '\\':
                    j += 2  # 跳过转义字符
                    continue
                if ch == in_string:
                    in_string = None
                j += 1
                continue

            # 检测字符串开始
            if ch in ('"', "'", '`'):
                in_string = ch
                j += 1
                continue

            # 检测行注释
            if ch == '/' and j + 1 < len(line) and line[j + 1] == '/':
                in_line_comment = True
                break

            # 检测块注释开始
            if ch == '/' and j + 1 < len(line) and line[j + 1] == '*':
                in_block_comment = True
                j += 2
                continue

            # 大括号计数（仅在非字符串、非注释中）
            if ch == '{':
                brace_count += 1
            elif ch == '}':
                brace_count -= 1
                if brace_count == 0:
                    return body

            j += 1

    return body


def _get_clean_method_body(content: str, start_line: int, lang: str) -> str:
    """
    提取并清理方法体（组合 _extract_method_body + _strip_comments_and_strings）

    Args:
        content: 文件完整内容
        start_line: 方法起始行号（0-based）
        lang: 语言标识

    Returns:
        str: 清理后的方法体文本
    """
    lines = content.split("\n")
    method_lines = _extract_method_body(lines, start_line)
    method_body = "\n".join(method_lines)
    return _strip_comments_and_strings(method_body, lang)


def analyze_function_body(file_path: Path, func_info: dict[str, Any]) -> dict[str, Any]:
    """
    分析函数体，提取返回类型、异常、依赖等信息
    （用于 JS/TS 等无法使用 AST 的语言）

    Args:
        file_path: 源文件路径
        func_info: 已有的函数信息

    Returns:
        dict: 补充的分析结果
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}

    lines = content.split("\n")
    start_line = func_info["line"]

    # 提取函数体（复用通用工具函数）
    body_lines = _extract_method_body(lines, start_line)
    body = "\n".join(body_lines)

    analysis = {}

    # 提取 docstring / JSDoc 注释（函数上方的注释）
    if start_line >= 2:
        comment_lines = []
        for i in range(start_line - 2, max(start_line - 10, -1), -1):
            line = lines[i].strip()
            if line.startswith("/**") or line.startswith("/*") or line.startswith("*") or line.startswith("//"):
                comment_lines.insert(0, line)
            elif line.startswith('"""') or line.startswith("'''"):
                comment_lines.insert(0, line)
            else:
                break
        if comment_lines:
            analysis["docstring"] = "\n".join(comment_lines)

    # 分析 JS/TS 函数
    if func_info.get("language") in ("js/ts", "javascript", "typescript"):
        # 先剥离注释和字符串，避免注释/字符串中的关键字被误匹配
        clean_body = _strip_comments_and_strings(body, "javascript")

        # 查找 return 语句推断返回类型
        return_types = set()
        return_matches = re.findall(r"return\s+(.+?);", clean_body)
        for ret in return_matches:
            ret = ret.strip()
            if ret == "null":
                return_types.add("null")
            elif ret == "undefined":
                return_types.add("undefined")
            elif ret.startswith('"') or ret.startswith("'") or ret.startswith("`"):
                return_types.add("string")
            elif ret.lstrip("-").isdigit() or re.match(r"^[\d.]+$", ret):
                return_types.add("number")
            elif ret in ("true", "false"):
                return_types.add("boolean")
            elif ret.startswith("["):
                return_types.add("Array")
            elif ret.startswith("{"):
                return_types.add("Object")
            elif ret.startswith("new "):
                return_types.add("instance")
            else:
                return_types.add(ret.split("(")[0].split(".")[0])  # 函数调用或变量名
        analysis["return_type"] = ", ".join(return_types) if return_types else func_info.get("return_type", "void")

        # 查找 throw 语句
        throw_matches = re.findall(r"throw\s+(?:new\s+)?(\w+)", clean_body)
        analysis["exceptions"] = list(set(throw_matches)) if throw_matches else []

        # 查找外部依赖（方法调用）
        dep_matches = re.findall(r"(?:await\s+)?(\w+)\.\w+\s*\(", clean_body)
        builtins = {"console", "Math", "JSON", "Object", "Array", "String", "Number", "Promise", "Date", "Error", "Map", "Set"}
        analysis["dependencies"] = [d for d in set(dep_matches) if d not in builtins]

        # 统计分支数（复用已剥离的 clean_body）
        branch_count = 0
        branch_count += len(re.findall(r"\bif\s*\(", clean_body))
        branch_count += len(re.findall(r"\bswitch\s*\(", clean_body))
        branch_count += len(re.findall(r"\bfor\s*\(", clean_body))
        branch_count += len(re.findall(r"\bwhile\s*\(", clean_body))
        branch_count += len(re.findall(r"\bcatch\s*\(", clean_body))
        branch_count += len(re.findall(r"\?\s*[^:]+:", clean_body))  # 三元表达式
        analysis["branches"] = branch_count

    return analysis


def should_skip(func: dict[str, Any]) -> bool:
    """
    判断函数是否应该跳过（不适合单元测试）

    Args:
        func: 函数信息字典

    Returns:
        bool: 是否跳过
    """
    skip_names = {
        # 生命周期方法
        "constructor", "componentDidMount", "componentWillUnmount",
        "componentDidUpdate", "render", "shouldComponentUpdate",
        "componentWillMount", "componentWillReceiveProps",
        "useEffect", "useState", "useRef", "useMemo", "useCallback",
        "useReducer", "useContext", "useLayoutEffect",
        "__init__", "__str__", "__repr__", "__eq__", "__hash__",
        "__del__", "__new__", "__getattr__", "__setattr__",
        "main", "toString", "hashCode", "equals",
        # 配置相关
        "configure", "setup", "init", "dispose",
        # getter/setter
        "getter", "setter",
    }

    # 按名称跳过
    if func["name"] in skip_names:
        return True

    # 跳过 getter/setter（Java/JS 风格）
    name = func["name"]
    if (name.startswith("get") or name.startswith("set")) and len(name) > 3 and name[3:4].isupper():
        return True

    # 跳过 React/Vue 生命周期方法（名称匹配）
    lifecycle_patterns = ("onMount", "onUnmount", "onUpdated", "onBeforeMount",
                          "onBeforeUnmount", "onBeforeUpdate", "created", "mounted",
                          "beforeCreate", "beforeMount", "beforeUpdate", "beforeDestroy",
                          "updated", "destroyed", "activated", "deactivated",
                          "setup", "configure", "dispose")
    if name in lifecycle_patterns:
        return True

    return False


def export_json(result: dict, output_path: str) -> None:
    """
    将扫描结果导出为 JSON 文件

    Args:
        result: 扫描结果字典
        output_path: 输出文件路径
    """
    write_json(result, output_path)
    print(f"\n扫描结果已导出到: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scan_source.py <项目路径> [输出JSON路径]")
        print("示例: python scan_source.py /path/to/project result.json")
        sys.exit(1)

    project = sys.argv[1]
    result = scan_project(project)

    if result and len(sys.argv) >= 3:
        export_json(result, sys.argv[2])
