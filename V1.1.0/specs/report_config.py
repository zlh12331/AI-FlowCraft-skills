#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpecForge V4 - 统一测试报告配置模块
====================================

为 Skills 22-26 的 5 个测试报告生成脚本提供统一的报告结构定义。
本模块是声明式的，不直接修改现有的 generate_report.py 脚本，
各脚本可在后续迭代中引用此配置以实现格式统一。

支持的测试类型:
  - unit       : 单元测试 (Skill 22)
  - component  : 组件测试 (Skill 23)
  - integration: 集成测试 (Skill 24)
  - e2e        : 端到端测试 (Skill 25)
  - system     : 系统测试 (Skill 26)

用法示例:
    from report_config import get_report_structure, format_overview, format_results

    # 获取完整报告结构
    structure = get_report_structure("unit")

    # 格式化概览表格
    overview_text = format_overview("unit", {
        "项目类型": "Python 后端",
        "编程语言": "Python 3.11",
        "测试框架": "pytest",
        "扫描函数数": 42,
        "可测试函数数": 38,
        "测试用例数": 120,
    })

    # 格式化结果表格
    results_text = format_results({
        "total": 120, "passed": 115, "failed": 3, "skipped": 2
    })
"""

from __future__ import annotations

from typing import Dict, List, Optional


# ============================================================
# 一、统一章节结构 - 所有报告必须包含的公共章节
# ============================================================

COMMON_SECTIONS: List[Dict[str, str]] = [
    {
        "id": "overview",
        "title": "一、测试概览",
        "description": "测试环境、技术栈、扫描范围等基本信息",
        "required": True,
    },
    {
        "id": "results",
        "title": "二、测试结果",
        "description": "通过/失败/跳过数量及通过率",
        "required": True,
    },
    {
        "id": "coverage",
        "title": "三、覆盖情况",
        "description": "代码覆盖率或扫描对象覆盖情况",
        "required": True,
    },
    {
        "id": "failures",
        "title": "四、失败详情",
        "description": "失败用例的错误信息和堆栈",
        "required": True,
    },
    {
        "id": "improvements",
        "title": "五、改进建议",
        "description": "基于测试结果生成的优化建议",
        "required": True,
    },
]

# ============================================================
# 二、可选章节 - 按测试类型差异化配置
# ============================================================

OPTIONAL_SECTIONS: Dict[str, List[Dict[str, str]]] = {
    # --- 单元测试：独有执行时间分析和未覆盖函数列表 ---
    "unit": [
        {
            "id": "execution_time",
            "title": "执行时间分析",
            "description": "总执行时间、平均耗时、CI/CD 友好度",
            "position": "after_results",
        },
        {
            "id": "uncovered",
            "title": "未覆盖项",
            "description": "未被测试覆盖的函数列表及补充建议",
            "position": "after_coverage",
        },
    ],
    # --- 组件测试：无额外可选章节 ---
    "component": [],
    # --- 集成测试：无额外可选章节 ---
    "integration": [],
    # --- E2E 测试：独有截图证据章节 ---
    "e2e": [
        {
            "id": "screenshots",
            "title": "截图证据",
            "description": "关键步骤的浏览器截图和 trace 文件引用",
            "position": "after_failures",
        },
    ],
    # --- 系统测试：独有安全、性能、健康检查和总体结果 ---
    "system": [
        {
            "id": "security",
            "title": "安全测试结果",
            "description": "漏洞扫描结果，按严重程度分类统计",
            "position": "after_results",
        },
        {
            "id": "performance",
            "title": "性能测试结果",
            "description": "API 响应时间、吞吐量、并发失败率等指标",
            "position": "after_security",
        },
        {
            "id": "health",
            "title": "健康检查",
            "description": "各服务组件的健康状态检查结果",
            "position": "after_performance",
        },
        {
            "id": "overall",
            "title": "总体结果",
            "description": "功能、安全、性能的综合评估",
            "position": "last",
        },
    ],
}

# ============================================================
# 三、统一概览字段 - 每种测试类型的概览表格列定义
# ============================================================

OVERVIEW_FIELDS: Dict[str, List[str]] = {
    "unit": [
        "项目类型",     # 如 "Python 后端"、"Node.js 全栈"
        "编程语言",     # 如 "Python 3.11"、"TypeScript 5.0"
        "测试框架",     # 如 "pytest"、"vitest"
        "扫描函数数",   # 扫描到的函数总数
        "可测试函数数", # 可被自动测试的函数数
        "测试用例数",   # 实际生成的测试用例总数
    ],
    "component": [
        "前端框架",     # 如 "React 18"、"Vue 3"
        "测试框架",     # 如 "vitest + @testing-library/react"
        "扫描组件数",   # 扫描到的组件总数
        "编写组件数",   # 实际编写测试的组件数
        "测试用例数",   # 实际生成的测试用例总数
    ],
    "integration": [
        "项目类型",     # 如 "全栈应用"、"微服务"
        "框架",         # 如 "Django + DRF"、"Express"
        "扫描集成点数", # 扫描到的集成点总数（API、DB、外部服务等）
        "编写集成点数", # 实际编写测试的集成点数
        "测试用例数",   # 实际生成的测试用例总数
    ],
    "e2e": [
        "前端框架",     # 如 "Next.js 14"、"Nuxt 3"
        "测试框架",     # 如 "Playwright"、"Cypress"
        "扫描页面数",   # 扫描到的页面/路由总数
        "测试流程数",   # 用户流程（user flow）数量
        "测试用例数",   # 实际生成的测试用例总数
    ],
    "system": [
        "服务组件",     # 如 "auth-service, api-gateway, ..."
        "数据库",       # 如 "PostgreSQL, Redis"
        "缓存",         # 如 "Redis"
        "外部集成",     # 如 "Stripe, SendGrid"
        "配置文件",     # 配置文件数量
    ],
}

# ============================================================
# 四、测试类型元数据 - 报告标题和描述
# ============================================================

TEST_TYPE_META: Dict[str, Dict[str, str]] = {
    "unit": {
        "title": "单元测试报告",
        "description": "针对独立函数/方法的自动化测试结果",
    },
    "component": {
        "title": "组件测试报告",
        "description": "针对 UI 组件的自动化测试结果",
    },
    "integration": {
        "title": "集成测试报告",
        "description": "针对模块间交互的自动化测试结果",
    },
    "e2e": {
        "title": "E2E 测试报告",
        "description": "针对完整用户流程的端到端自动化测试结果",
    },
    "system": {
        "title": "系统测试报告",
        "description": "包含功能性、安全性、性能的综合系统测试结果",
    },
}

# ============================================================
# 五、位置映射 - 将 position 字符串映射到插入点
# ============================================================

# 定义各 position 值的含义：
#   after_results     -> 在"测试结果"章节之后
#   after_coverage    -> 在"覆盖情况"章节之后
#   after_failures    -> 在"失败详情"章节之后
#   after_security    -> 在"安全测试结果"章节之后（仅系统测试）
#   after_performance -> 在"性能测试结果"章节之后（仅系统测试）
#   last              -> 在"改进建议"章节之前（公共章节的最后可选位置）
POSITION_ORDER: Dict[str, int] = {
    "after_results": 1,
    "after_coverage": 2,
    "after_failures": 3,
    "after_security": 4,
    "after_performance": 5,
    "last": 6,
}

# ============================================================
# 六、公共 API 函数
# ============================================================


def get_report_structure(test_type: str) -> dict:
    """
    获取指定测试类型的完整报告结构。

    返回值包含公共章节和可选章节，按正确的顺序排列。
    可选章节根据 position 字段插入到对应的公共章节之后。

    Args:
        test_type: 测试类型，可选值:
            "unit" | "component" | "integration" | "e2e" | "system"

    Returns:
        dict: 完整的报告结构，格式如下:
        {
            "test_type": "unit",
            "title": "单元测试报告",
            "description": "...",
            "sections": [
                {"id": "overview", "title": "一、测试概览", "required": True, ...},
                {"id": "results", "title": "二、测试结果", "required": True, ...},
                ...
                {"id": "execution_time", "title": "执行时间分析", "required": False, ...},
                ...
            ],
            "overview_fields": ["项目类型", "编程语言", ...],
        }

    Raises:
        ValueError: 当 test_type 不在支持范围内时抛出
    """
    # 校验测试类型
    if test_type not in TEST_TYPE_META:
        supported = ", ".join(f'"{k}"' for k in TEST_TYPE_META.keys())
        raise ValueError(
            f"不支持的测试类型: \"{test_type}\"，"
            f"支持的类型: {supported}"
        )

    # 获取元数据
    meta = TEST_TYPE_META[test_type]
    optional = OPTIONAL_SECTIONS.get(test_type, [])
    overview = OVERVIEW_FIELDS.get(test_type, [])

    # 构建有序的章节列表
    # 策略：先放置公共章节，再根据 position 将可选章节插入对应位置
    sections = []

    # 公共章节的 id -> 索引映射，用于定位插入点
    # 公共章节顺序: overview -> results -> coverage -> failures -> improvements
    section_id_to_index = {
        "overview": 0,
        "results": 1,
        "coverage": 2,
        "failures": 3,
        "improvements": 4,
    }

    # position -> 对应公共章节 id 的映射
    position_to_anchor = {
        "after_results": "results",
        "after_coverage": "coverage",
        "after_failures": "failures",
        # after_security 和 after_performance 是系统测试特有的，
        # 它们锚定在可选章节自身之后，稍后处理
        "after_security": None,
        "after_performance": None,
        "last": "improvements",  # last 表示在"改进建议"之前
    }

    # 系统测试特有的可选章节锚定关系
    # security 锚定在 results 之后
    # performance 锚定在 security 之后
    # health 锚定在 performance 之后
    # overall 锚定在 improvements 之前（last）
    system_optional_anchor = {
        "security": "results",
        "performance": "security",
        "health": "performance",
        "overall": "improvements",
    }

    # 先复制公共章节
    for section in COMMON_SECTIONS:
        sections.append({
            "id": section["id"],
            "title": section["title"],
            "description": section.get("description", ""),
            "required": True,
        })

    # 如果是系统测试，使用特殊的锚定逻辑处理可选章节
    if test_type == "system":
        # 按照定义顺序逐个插入可选章节
        for opt_section in optional:
            anchor_id = system_optional_anchor.get(opt_section["id"])
            if anchor_id and anchor_id in section_id_to_index:
                # 找到锚定章节的索引，在其后插入
                anchor_index = section_id_to_index[anchor_id]
                insert_index = anchor_index + 1
                sections.insert(insert_index, {
                    "id": opt_section["id"],
                    "title": opt_section["title"],
                    "description": opt_section.get("description", ""),
                    "required": False,
                })
                # 更新后续章节的索引映射（因为插入操作改变了位置）
                for sid in list(section_id_to_index.keys()):
                    if section_id_to_index[sid] >= insert_index:
                        section_id_to_index[sid] += 1
                # 将新插入的可选章节也加入映射
                section_id_to_index[opt_section["id"]] = insert_index
    else:
        # 其他测试类型：按 position 顺序分组，然后逐组插入
        # 先按 position 排序可选章节
        sorted_optional = sorted(
            optional,
            key=lambda s: POSITION_ORDER.get(s.get("position", "last"), 99)
        )

        for opt_section in sorted_optional:
            position = opt_section.get("position", "last")
            anchor_id = position_to_anchor.get(position)

            if anchor_id and anchor_id in section_id_to_index:
                # 找到锚定章节的索引，在其后插入
                anchor_index = section_id_to_index[anchor_id]
                insert_index = anchor_index + 1
                sections.insert(insert_index, {
                    "id": opt_section["id"],
                    "title": opt_section["title"],
                    "description": opt_section.get("description", ""),
                    "required": False,
                })
                # 更新后续章节的索引映射
                for sid in list(section_id_to_index.keys()):
                    if section_id_to_index[sid] >= insert_index:
                        section_id_to_index[sid] += 1
                section_id_to_index[opt_section["id"]] = insert_index

    return {
        "test_type": test_type,
        "title": meta["title"],
        "description": meta["description"],
        "sections": sections,
        "overview_fields": overview,
    }


def format_overview(test_type: str, data: dict) -> str:
    """
    格式化概览章节的 Markdown 表格。

    根据测试类型使用对应的概览字段定义，从 data 字典中取值。
    缺失的字段显示为"未知"。

    Args:
        test_type: 测试类型，如 "unit"、"component" 等
        data: 概览数据字典，键名需与 OVERVIEW_FIELDS 中定义的字段名一致

    Returns:
        str: 格式化后的 Markdown 表格字符串

    Raises:
        ValueError: 当 test_type 不在支持范围内时抛出

    示例:
        >>> format_overview("unit", {
        ...     "项目类型": "Python 后端",
        ...     "编程语言": "Python 3.11",
        ...     "测试框架": "pytest",
        ...     "扫描函数数": 42,
        ...     "可测试函数数": 38,
        ...     "测试用例数": 120,
        ... })
    """
    # 校验测试类型
    if test_type not in OVERVIEW_FIELDS:
        supported = ", ".join(f'"{k}"' for k in OVERVIEW_FIELDS.keys())
        raise ValueError(
            f"不支持的测试类型: \"{test_type}\"，"
            f"支持的类型: {supported}"
        )

    # 获取该类型的概览字段列表
    fields = OVERVIEW_FIELDS[test_type]

    # 构建 Markdown 表格
    lines = []
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")

    for field in fields:
        # 从 data 中取值，缺失时显示"未知"
        value = data.get(field, "未知")
        lines.append(f"| {field} | {value} |")

    return "\n".join(lines)


def format_results(data: dict) -> str:
    """
    格式化测试结果章节的 Markdown 表格。

    统一的结果格式，包含测试总数、通过、失败、跳过、通过率和状态。

    Args:
        data: 测试结果数据字典，需包含以下键:
            - total  (int): 测试总数
            - passed (int): 通过数
            - failed (int): 失败数
            - skipped(int): 跳过数（可选，默认 0）
            - pass_rate (float): 通过率百分比（可选，自动计算）

    Returns:
        str: 格式化后的 Markdown 表格字符串

    示例:
        >>> format_results({
        ...     "total": 120, "passed": 115, "failed": 3, "skipped": 2
        ... })
    """
    # 提取数据，设置安全的默认值
    total = data.get("total", 0)
    passed = data.get("passed", 0)
    failed = data.get("failed", 0)
    skipped = data.get("skipped", 0)

    # 如果未提供 pass_rate，则自动计算
    pass_rate = data.get("pass_rate")
    if pass_rate is None:
        pass_rate = round(passed / total * 100, 1) if total > 0 else 0.0

    # 根据通过率判断状态
    if pass_rate >= 100:
        status = "全部通过"
    elif pass_rate >= 80:
        status = "部分失败"
    else:
        status = "大量失败"

    # 构建表格
    lines = []
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 测试总数 | {total} |")
    lines.append(f"| 通过 | {passed} |")
    lines.append(f"| 失败 | {failed} |")
    lines.append(f"| 跳过 | {skipped} |")
    lines.append(f"| 通过率 | {pass_rate}% |")
    lines.append(f"| 状态 | {status} |")

    return "\n".join(lines)


def get_section_titles(test_type: str) -> List[str]:
    """
    获取指定测试类型报告的所有章节标题（有序列表）。

    便于在生成报告时按顺序输出章节标题。

    Args:
        test_type: 测试类型

    Returns:
        list: 章节标题列表，如 ["一、测试概览", "二、测试结果", ...]
    """
    structure = get_report_structure(test_type)
    return [section["title"] for section in structure["sections"]]


def get_all_test_types() -> List[str]:
    """
    获取所有支持的测试类型列表。

    Returns:
        list: 测试类型字符串列表
    """
    return list(TEST_TYPE_META.keys())


# ============================================================
# 七、模块自测（仅直接运行时执行）
# ============================================================

if __name__ == "__main__":
    # 打印所有测试类型的报告结构
    print("=" * 60)
    print("SpecForge V4 - 统一报告配置模块自测")
    print("=" * 60)

    for test_type in get_all_test_types():
        print(f"\n{'─' * 40}")
        print(f"测试类型: {test_type}")
        print(f"{'─' * 40}")

        # 获取并打印报告结构
        structure = get_report_structure(test_type)
        print(f"报告标题: {structure['title']}")
        print(f"报告描述: {structure['description']}")
        print(f"概览字段: {structure['overview_fields']}")
        print(f"章节顺序:")

        for i, section in enumerate(structure["sections"], 1):
            req_mark = "[必选]" if section["required"] else "[可选]"
            print(f"  {i}. {req_mark} {section['title']} (id={section['id']})")

        # 打印格式化示例
        print(f"\n概览表格示例:")
        # 构造示例数据
        sample_data = {}
        for field in structure["overview_fields"]:
            sample_data[field] = f"示例值"
        print(format_overview(test_type, sample_data))

        print(f"\n结果表格示例:")
        print(format_results({
            "total": 50,
            "passed": 48,
            "failed": 1,
            "skipped": 1,
        }))

    print(f"\n{'=' * 60}")
    print("自测完成")
    print(f"{'=' * 60}")
