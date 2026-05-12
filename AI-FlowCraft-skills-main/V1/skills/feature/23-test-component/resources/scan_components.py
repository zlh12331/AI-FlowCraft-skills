#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件测试辅助脚本 - 组件扫描器
功能：扫描前端项目，识别可测试的 UI 组件，分析 Props/Events/Slots/State
用法：python scan_components.py <项目路径> [输出JSON路径]
"""

import sys
import re
from pathlib import Path
from typing import Optional

# 导入公共模块
from common import load_json, save_json, validate_project_path, detect_framework


def scan_project(project_path: str) -> dict:
    """
    扫描项目目录，识别前端框架和可测试的 UI 组件

    Args:
        project_path: 项目根目录路径

    Returns:
        dict: 项目信息和组件列表
    """
    # 使用公共模块验证路径
    validated = validate_project_path(project_path)
    if validated is None:
        print(f"错误：路径不存在 - {project_path}")
        return {}

    # 识别前端框架（使用公共模块）
    framework = detect_framework(validated)
    print(f"前端框架: {framework}")

    # 根据框架选择扫描策略
    components: list = []
    if framework in ("react", "nextjs"):
        components = scan_react_components(validated)
    elif framework in ("vue", "nuxtjs"):
        components = scan_vue_components(validated)
    elif framework == "angular":
        components = scan_angular_components(validated)
    elif framework == "svelte":
        components = scan_svelte_components(validated)

    # 过滤掉不适合测试的组件
    filtered = [c for c in components if not should_skip(c)]

    # 对每个组件进行深度分析
    analyzed: list = []
    for comp in filtered:
        file_full_path = validated / comp["file"]
        if file_full_path.exists():
            analysis = analyze_component(file_full_path, comp, framework)
            comp.update(analysis)
        analyzed.append(comp)

    result = {
        "framework": framework,
        "total_components": len(components),
        "testable_components": len(filtered),
        "components": analyzed
    }

    # 输出结果
    print(f"\n扫描结果:")
    print(f"  总组件数: {len(components)}")
    print(f"  可测试组件: {len(filtered)}")
    print(f"\n可测试组件列表:")
    for comp in filtered:
        props = comp.get("props", [])
        events = comp.get("events", [])
        print(f"  - {comp['name']} ({comp['file']}:{comp['line']})")
        if props:
            print(f"    Props: {', '.join(props[:5])}{'...' if len(props) > 5 else ''}")
        if events:
            print(f"    Events: {', '.join(events[:5])}{'...' if len(events) > 5 else ''}")

    return result


def scan_react_components(project_path: Path) -> list:
    """
    扫描 React/Next.js 项目中的组件

    Args:
        project_path: 项目根目录

    Returns:
        list: 组件信息列表
    """
    components = []
    skip_dirs = {"node_modules", ".next", "dist", "build", "coverage", ".git", "__pycache__"}

    for file_path in project_path.rglob("*.[jt]s*"):
        # 只处理 .js, .jsx, .ts, .tsx 文件
        if file_path.suffix not in (".js", ".jsx", ".ts", ".tsx"):
            continue
        if any(skip in file_path.parts for skip in skip_dirs):
            continue
        # 跳过测试文件和配置文件
        if any(kw in file_path.name for kw in [".test.", ".spec.", "config.", "jest.", "vitest.", "story."]):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # 匹配 React 组件声明
        patterns = [
            # export default function ComponentName()
            r"(?:export\s+default\s+)?function\s+([A-Z]\w+)\s*\(",
            # export default const ComponentName = () =>
            r"(?:export\s+default\s+)?(?:const|let)\s+([A-Z]\w+)\s*=\s*(?:\([^)]*\)|[^=])\s*=>",
            # export default function ComponentName() { return (
            r"export\s+default\s+function\s+([A-Z]\w+)",
        ]

        for line_num, line in enumerate(content.split("\n"), 1):
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    comp_name = match.group(1)
                    # 跳过非组件的大写开头函数
                    if comp_name in ("App", "Layout", "Page", "Document", "_app", "_document"):
                        continue

                    components.append({
                        "name": comp_name,
                        "file": str(file_path.relative_to(project_path)),
                        "line": line_num,
                        "language": "tsx" if file_path.suffix == ".tsx" else "jsx",
                        "props": [],
                        "events": [],
                        "slots": [],
                        "state_hooks": 0,
                        "effect_hooks": 0,
                        "conditional_renders": 0,
                        "list_renders": 0,
                    })
                    break  # 一行只匹配一次

    return components


def scan_vue_components(project_path: Path) -> list:
    """
    扫描 Vue 项目中的组件

    Args:
        project_path: 项目根目录

    Returns:
        list: 组件信息列表
    """
    components = []
    skip_dirs = {"node_modules", ".nuxt", "dist", "build", "coverage", ".git", "__pycache__"}

    for file_path in project_path.rglob("*.vue"):
        if any(skip in file_path.parts for skip in skip_dirs):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # 从文件名提取组件名（PascalCase）
        comp_name = file_path.stem
        # kebab-case 转 PascalCase
        comp_name = "".join(word.capitalize() for word in comp_name.split("-"))

        # 跳过布局和页面级组件
        if comp_name in ("Layout", "Default", "App", "Error"):
            continue
        if "layouts/" in str(file_path) or "pages/" in str(file_path):
            continue

        components.append({
            "name": comp_name,
            "file": str(file_path.relative_to(project_path)),
            "line": 1,
            "language": "vue",
            "props": [],
            "events": [],
            "slots": [],
            "state_hooks": 0,
            "effect_hooks": 0,
            "conditional_renders": 0,
            "list_renders": 0,
        })

    return components


def scan_angular_components(project_path: Path) -> list:
    """
    扫描 Angular 项目中的组件

    Args:
        project_path: 项目根目录

    Returns:
        list: 组件信息列表
    """
    components = []
    skip_dirs = {"node_modules", "dist", "build", "coverage", ".git"}

    for file_path in project_path.rglob("*.component.ts"):
        if any(skip in file_path.parts for skip in skip_dirs):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # 匹配 Angular 组件装饰器
        # @Component({ selector: 'app-xxx', ... })
        match = re.search(r"@Component\s*\(\s*\{[^}]*selector:\s*['\"]([^'\"]+)", content)
        if match:
            selector = match.group(1)
            # 从类名提取组件名
            class_match = re.search(r"class\s+(\w+Component)", content)
            comp_name = class_match.group(1) if class_match else selector

            components.append({
                "name": comp_name,
                "file": str(file_path.relative_to(project_path)),
                "line": 1,
                "language": "angular-ts",
                "props": [],
                "events": [],
                "slots": [],
                "state_hooks": 0,
                "effect_hooks": 0,
                "conditional_renders": 0,
                "list_renders": 0,
            })

    return components


def scan_svelte_components(project_path: Path) -> list:
    """
    扫描 Svelte 项目中的组件

    Args:
        project_path: 项目根目录

    Returns:
        list: 组件信息列表
    """
    components = []
    skip_dirs = {"node_modules", ".svelte-kit", "dist", "build", "coverage", ".git"}

    for file_path in project_path.rglob("*.svelte"):
        if any(skip in file_path.parts for skip in skip_dirs):
            continue

        comp_name = file_path.stem
        comp_name = "".join(word.capitalize() for word in comp_name.split("-"))

        if comp_name in ("Layout", "App", "Error"):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        components.append({
            "name": comp_name,
            "file": str(file_path.relative_to(project_path)),
            "line": 1,
            "language": "svelte",
            "props": [],
            "events": [],
            "slots": [],
            "state_hooks": 0,
            "effect_hooks": 0,
            "conditional_renders": 0,
            "list_renders": 0,
        })

    return components


def analyze_component(file_path: Path, comp_info: dict, framework: str) -> dict:
    """
    深度分析组件源码，提取 Props/Events/Slots/State 等信息

    Args:
        file_path: 组件文件路径
        comp_info: 已有的组件信息
        framework: 前端框架

    Returns:
        dict: 补充的分析结果
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}

    analysis: dict = {}

    if framework in ("react", "nextjs"):
        analysis = _analyze_react_component(content, comp_info)
    elif framework in ("vue", "nuxtjs"):
        analysis = _analyze_vue_component(content, comp_info)
    elif framework == "angular":
        analysis = _analyze_angular_component(content, comp_info)
    elif framework == "svelte":
        analysis = _analyze_svelte_component(content, comp_info)

    return analysis


def _analyze_react_component(content: str, comp_info: dict) -> dict:
    """
    分析 React 组件源码

    Args:
        content: 文件内容
        comp_info: 组件信息

    Returns:
        dict: 分析结果
    """
    analysis: dict = {}

    # 提取 Props（TypeScript interface 或 PropTypes）
    # 匹配: interface XxxProps { ... } 或 type XxxProps = { ... }
    props_match = re.search(
        r"(?:interface|type)\s+\w*Props\s*(?:=\s*)?\{([^}]+)\}",
        content, re.DOTALL
    )
    if props_match:
        props_block = props_match.group(1)
        # 提取每个 prop 名称
        prop_names = re.findall(r"(\w+)\s*(?:\?|\:)", props_block)
        analysis["props"] = list(set(prop_names))
    else:
        # 尝试从函数参数解构中提取
        destructure_match = re.search(r"\(\s*\{([^}]+)\}\s*[:\)]", content)
        if destructure_match:
            prop_names = [p.strip().split(":")[0].strip().replace("?", "") for p in destructure_match.group(1).split(",")]
            analysis["props"] = [p for p in prop_names if p and not p.startswith("_")]

    # 提取 Events（onXxx props）
    if analysis.get("props"):
        analysis["events"] = [p for p in analysis["props"] if p.startswith("on") and len(p) > 2]

    # 统计 Hooks 使用
    analysis["state_hooks"] = len(re.findall(r"useState\s*\(", content))
    analysis["effect_hooks"] = len(re.findall(r"useEffect\s*\(", content))
    analysis["ref_hooks"] = len(re.findall(r"useRef\s*\(", content))
    analysis["memo_hooks"] = len(re.findall(r"useMemo\s*\(", content))
    analysis["callback_hooks"] = len(re.findall(r"useCallback\s*\(", content))

    # 统计条件渲染
    analysis["conditional_renders"] = (
        len(re.findall(r"\?\s*(?:<|{)", content)) +  # 三元表达式
        len(re.findall(r"\{[^}]*&&\s*<", content))     # 逻辑与
    )

    # 统计列表渲染
    analysis["list_renders"] = len(re.findall(r"\.map\s*\(", content))

    # 提取 JSDoc 注释
    jsdoc_match = re.search(r"/\*\*([^*]|\*(?!/))*\*/", content)
    if jsdoc_match:
        analysis["docstring"] = jsdoc_match.group(0).strip()

    return analysis


def _analyze_vue_component(content: str, comp_info: dict) -> dict:
    """
    分析 Vue 组件源码

    Args:
        content: 文件内容
        comp_info: 组件信息

    Returns:
        dict: 分析结果
    """
    analysis: dict = {}

    # Vue 3 <script setup> 中的 defineProps
    # defineProps<{ name: string; age: number }>()
    props_define = re.search(r"defineProps\s*<([^>]+)>", content)
    if props_define:
        props_block = props_define.group(1)
        prop_names = re.findall(r"(\w+)\s*[?:]", props_block)
        analysis["props"] = list(set(prop_names))
    else:
        # defineProps({ name: { type: String, required: true } })
        props_obj = re.search(r"defineProps\s*\(\s*\{([^}]+)\}", content)
        if props_obj:
            prop_names = re.findall(r"(\w+)\s*:", props_obj.group(1))
            analysis["props"] = list(set(prop_names))
        else:
            # Vue 2 Options API: props: { ... }
            props_opt = re.search(r"props\s*:\s*\{([^}]+)\}", content)
            if props_opt:
                prop_names = re.findall(r"(\w+)\s*[:{]", props_opt.group(1))
                analysis["props"] = list(set(prop_names))

    # 提取 Events（defineEmits）
    emits_define = re.search(r"defineEmits\s*(?:<([^>]+)>)?\s*\(([^)]*)\)", content)
    if emits_define:
        if emits_define.group(1):
            # defineEmits<['click', 'change']>()
            events = re.findall(r"'(\w+)'", emits_define.group(1))
            analysis["events"] = events
        elif emits_define.group(2):
            # defineEmits(['click', 'change'])
            events = re.findall(r"'(\w+)'", emits_define.group(2))
            analysis["events"] = events

    # 提取 Slots
    slot_names = re.findall(r"<slot\s+(?:name=['\"](\w+))", content)
    if slot_names:
        analysis["slots"] = slot_names
    elif "<slot" in content:
        analysis["slots"] = ["default"]

    # 统计响应式状态
    analysis["state_hooks"] = (
        len(re.findall(r"(?:ref|reactive|computed)\s*\(", content))
    )
    analysis["effect_hooks"] = (
        len(re.findall(r"(?:watch|watchEffect|onMounted|onUnmounted)\s*\(", content))
    )

    # 统计条件渲染
    analysis["conditional_renders"] = len(re.findall(r"v-if\s*=", content))
    analysis["list_renders"] = len(re.findall(r"v-for\s*=", content))

    return analysis


def _analyze_angular_component(content: str, comp_info: dict) -> dict:
    """
    分析 Angular 组件源码

    Args:
        content: 文件内容
        comp_info: 组件信息

    Returns:
        dict: 分析结果
    """
    analysis: dict = {}

    # 提取 @Input() 装饰器
    inputs = re.findall(r"@Input\(\s*(?:'(\w+)')?\s*\)\s*(\w+)", content)
    analysis["props"] = [name or prop for name, prop in inputs]

    # 提取 @Output() 装饰器
    outputs = re.findall(r"@Output\(\s*(?:'(\w+)')?\s*\)\s*(\w+)", content)
    analysis["events"] = [name or prop for name, prop in outputs]

    # 统计条件渲染（*ngIf）
    analysis["conditional_renders"] = len(re.findall(r"\*ngIf", content))
    # 统计列表渲染（*ngFor）
    analysis["list_renders"] = len(re.findall(r"\*ngFor", content))

    return analysis


def _analyze_svelte_component(content: str, comp_info: dict) -> dict:
    """
    分析 Svelte 组件源码

    Args:
        content: 文件内容
        comp_info: 组件信息

    Returns:
        dict: 分析结果
    """
    analysis: dict = {}

    # Svelte 导出变量即为 Props: export let name = '';
    props = re.findall(r"export\s+let\s+(\w+)", content)
    analysis["props"] = props

    # Svelte 事件: on:click={() => ...}
    events = re.findall(r"on:(\w+)", content)
    analysis["events"] = list(set(events))

    # Slots
    if "<slot" in content:
        slot_names = re.findall(r"<slot\s+name=['\"](\w+)", content)
        analysis["slots"] = slot_names if slot_names else ["default"]

    # 条件渲染 {#if}
    analysis["conditional_renders"] = len(re.findall(r"\{#if", content))
    # 列表渲染 {#each}
    analysis["list_renders"] = len(re.findall(r"\{#each", content))

    return analysis


def should_skip(comp: dict) -> bool:
    """
    判断组件是否应该跳过（不适合组件测试）

    Args:
        comp: 组件信息字典

    Returns:
        bool: 是否跳过
    """
    skip_names = {
        "App", "Layout", "Page", "Document", "Error", "Loading",
        "NotFound", "Redirect", "Head", "Meta", "Link",
        "_app", "_document", "_error",
    }

    # 按名称跳过
    if comp["name"] in skip_names:
        return True

    # 跳过页面级组件（pages/ 目录）
    if "pages/" in comp["file"]:
        return True

    # 跳过布局组件
    if "layouts/" in comp["file"]:
        return True

    # 跳过 storybook stories
    if ".stories." in comp["file"]:
        return True

    return False


def export_json(result: dict, output_path: str) -> bool:
    """
    将扫描结果导出为 JSON 文件

    Args:
        result: 扫描结果字典
        output_path: 输出文件路径

    Returns:
        bool: 导出是否成功
    """
    success = save_json(result, output_path)
    if success:
        print(f"\n扫描结果已导出到: {output_path}")
    else:
        print(f"\n错误：无法导出扫描结果到 {output_path}")
    return success


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scan_components.py <项目路径> [输出JSON路径]")
        print("示例: python scan_components.py /path/to/project result.json")
        sys.exit(1)

    project = sys.argv[1]
    result = scan_project(project)

    if result and len(sys.argv) >= 3:
        export_json(result, sys.argv[2])
