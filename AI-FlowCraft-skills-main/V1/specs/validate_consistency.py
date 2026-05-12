#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpecForge V4 — 跨文档一致性自动校验脚本

本脚本用于校验 SpecForge V4 各 Skill 生成文档之间的字段名、API 路径、
页面清单和 API 响应格式的一致性，防止跨文档不一致成为 bug 源。

支持的校验类型：
  - field-names    : 数据模型字段名 vs 数据库表结构字段名 / API 响应字段名
  - api-paths      : API 接口文档路径 vs 后端技术方案 / 实际代码
  - page-list      : 信息架构页面清单 vs 交互设计页面定义
  - api-responses  : API 响应格式 vs 后端技术方案 / 前端技术方案
  - all            : 执行以上全部校验

用法示例：
  python validate_consistency.py --specs-dir /path/to/specs --check field-names
  python validate_consistency.py --specs-dir /path/to/specs --check all
  python validate_consistency.py --specs-dir /path/to/specs --check api-paths --verbose
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ============================================================================
# 工具函数
# ============================================================================

def read_markdown_file(file_path: Path) -> Optional[str]:
    """
    读取 Markdown 文件内容。

    Args:
        file_path: 文件路径

    Returns:
        文件内容字符串，文件不存在时返回 None
    """
    if not file_path.exists():
        return None
    # 尝试 UTF-8 读取，失败则尝试 GBK
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="gbk")


def extract_tables(content: str) -> List[List[List[str]]]:
    """
    从 Markdown 内容中提取所有表格，返回三维列表。

    每个表格是一个二维列表（行 x 列），自动跳过表头分隔行。

    Args:
        content: Markdown 文本内容

    Returns:
        表格列表，每个表格是 [[列1, 列2, ...], ...] 的结构
    """
    tables = []
    # 匹配 Markdown 表格：以 | 开头的连续行
    table_pattern = re.compile(
        r"((?:^\|.+\|\s*\n)+)",
        re.MULTILINE
    )
    for match in table_pattern.finditer(content):
        table_text = match.group(1)
        rows = []
        for line in table_text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            # 跳过分隔行（如 |---|---|---|）
            if re.match(r"^\|[\s\-:|]+\|$", line):
                continue
            # 按管道符分割，去除首尾空管道
            cells = [cell.strip() for cell in line.split("|")]
            # 去除首尾空元素（由 | 开头和结尾产生）
            if cells and cells[0] == "":
                cells = cells[1:]
            if cells and cells[-1] == "":
                cells = cells[:-1]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables


def extract_entity_field_tables(content: str) -> Dict[str, List[Dict[str, str]]]:
    """
    从数据模型字段约定文档中提取各实体的字段定义。

    文档结构为：
      ### 实体名
      | 字段名 | 类型 | 约束 | 说明 |

    Args:
        content: 数据模型字段约定文档内容

    Returns:
        字典：{实体名: [{字段名, 类型, 约束, 说明}, ...]}
    """
    entities = {}
    # 匹配 ### 标题作为实体名
    # 文档 Section 1 下的 ### 子标题即为实体名
    sections = re.split(r"^###\s+(.+)$", content, flags=re.MULTILINE)
    # sections 格式: [前置文本, 标题1, 内容1, 标题2, 内容2, ...]
    for i in range(1, len(sections), 2):
        entity_name = sections[i].strip()
        # 过滤掉章节编号开头的行（如 "5.3 特殊例外"、"6.1 基础字段"），
        # 这些是章节标题而非实体名
        if re.match(r"^\d+\.\d+", entity_name):
            continue
        section_content = sections[i + 1] if i + 1 < len(sections) else ""
        # 提取该 section 下的第一个表格（字段定义表）
        tables = extract_tables(section_content)
        if tables:
            header = tables[0][0] if tables[0] else []
            # 确认是字段定义表（第一列应为"字段名"）
            if header and "字段名" in header[0]:
                field_name_idx = 0
                type_idx = 1 if len(header) > 1 else None
                constraint_idx = 2 if len(header) > 2 else None
                desc_idx = 3 if len(header) > 3 else None
                fields = []
                for row in tables[0][1:]:  # 跳过表头
                    if len(row) > field_name_idx:
                        field = {"字段名": row[field_name_idx]}
                        if type_idx is not None and len(row) > type_idx:
                            field["类型"] = row[type_idx]
                        if constraint_idx is not None and len(row) > constraint_idx:
                            field["约束"] = row[constraint_idx]
                        if desc_idx is not None and len(row) > desc_idx:
                            field["说明"] = row[desc_idx]
                        fields.append(field)
                entities[entity_name] = fields
    return entities


def extract_db_table_fields(content: str) -> Dict[str, List[Dict[str, str]]]:
    """
    从数据库设计文档中提取各表的字段定义。

    文档结构为：
      ### 3.N 表名
      #### 字段定义
      | 字段名 | 类型 | 约束 | 默认值 | 说明 |

    Args:
        content: 数据库设计文档内容

    Returns:
        字典：{表名: [{字段名, 类型, 约束, 默认值, 说明}, ...]}
    """
    tables = {}
    # 匹配 ### 3.N 表名 格式的标题
    table_sections = re.split(
        r"^###\s+3\.\d+\s+(.+)$", content, flags=re.MULTILINE
    )
    for i in range(1, len(table_sections), 2):
        table_name = table_sections[i].strip()
        section_content = table_sections[i + 1] if i + 1 < len(table_sections) else ""
        # 在该 section 中查找 "字段定义" 子标题下的表格
        field_sections = re.split(
            r"^####\s+.*字段定义\s*$", section_content, flags=re.MULTILINE
        )
        if len(field_sections) > 1:
            field_content = field_sections[1]
            extracted = extract_tables(field_content)
            if extracted:
                header = extracted[0][0] if extracted[0] else []
                if header and "字段名" in header[0]:
                    field_name_idx = 0
                    type_idx = 1 if len(header) > 1 else None
                    constraint_idx = 2 if len(header) > 2 else None
                    default_idx = 3 if len(header) > 3 else None
                    desc_idx = 4 if len(header) > 4 else None
                    fields = []
                    for row in extracted[0][1:]:
                        if len(row) > field_name_idx:
                            field = {"字段名": row[field_name_idx]}
                            if type_idx is not None and len(row) > type_idx:
                                field["类型"] = row[type_idx]
                            if constraint_idx is not None and len(row) > constraint_idx:
                                field["约束"] = row[constraint_idx]
                            if default_idx is not None and len(row) > default_idx:
                                field["默认值"] = row[default_idx]
                            if desc_idx is not None and len(row) > desc_idx:
                                field["说明"] = row[desc_idx]
                            fields.append(field)
                    tables[table_name] = fields
    return tables


def extract_api_endpoints(content: str) -> List[Dict[str, str]]:
    """
    从 API 接口文档中提取所有 API 端点定义。

    提取来源：
      1. Section 2 "接口列表总览" 表格
      2. Section 5 "接口详情" 中的 ### 标题（如 "### 5.1 POST /api/v1/auth/login"）

    Args:
        content: API 接口文档内容

    Returns:
        端点列表：[{method, path, description}, ...]
    """
    endpoints = []

    # 方法 1：从接口详情的 ### 标题中提取
    # 格式：### 5.N METHOD /path
    detail_pattern = re.compile(
        r"^###\s+\d+\.\d+\s+(GET|POST|PUT|DELETE|PATCH)\s+(\S+)",
        re.MULTILINE
    )
    for match in detail_pattern.finditer(content):
        endpoints.append({
            "method": match.group(1).upper(),
            "path": match.group(2),
            "description": ""  # 标题中无描述
        })

    # 方法 2：从接口列表总览表格中提取（补充描述信息）
    # 查找 Section 2 下的表格
    section2_match = re.search(
        r"^##\s+2\.\s+接口列表总览\s*\n(.*?)(?=^##\s|\Z)",
        content,
        re.MULTILINE | re.DOTALL
    )
    if section2_match:
        overview_tables = extract_tables(section2_match.group(1))
        if overview_tables:
            for row in overview_tables[0][1:]:  # 跳过表头
                if len(row) >= 3:
                    method = row[0].strip().upper()
                    path = row[1].strip()
                    desc = row[2].strip()
                    # 检查是否已在详情中存在，若存在则补充描述
                    found = False
                    for ep in endpoints:
                        if ep["method"] == method and ep["path"] == path:
                            ep["description"] = desc
                            found = True
                            break
                    if not found:
                        endpoints.append({
                            "method": method,
                            "path": path,
                            "description": desc
                        })

    return endpoints


def extract_api_response_fields(content: str) -> Dict[str, List[str]]:
    """
    从 API 接口文档中提取各接口的响应字段名。

    从接口详情的成功响应 JSON 代码块中提取字段名。

    Args:
        content: API 接口文档内容

    Returns:
        字典：{接口路径: [字段名列表]}
    """
    response_fields = {}
    # 匹配每个接口详情 section
    api_sections = re.split(
        r"^###\s+\d+\.\d+\s+(GET|POST|PUT|DELETE|PATCH)\s+(\S+)",
        content,
        flags=re.MULTILINE
    )
    for i in range(1, len(api_sections), 2):
        method = api_sections[i].upper()
        path = api_sections[i + 1].strip() if i + 1 < len(api_sections) else ""
        section_content = api_sections[i + 2] if i + 2 < len(api_sections) else ""
        key = f"{method} {path}"

        # 提取成功响应中的 JSON 代码块
        json_blocks = re.findall(
            r"```json\s*\n(.*?)```",
            section_content,
            re.DOTALL
        )
        for block in json_blocks:
            fields = _extract_json_keys(block)
            if fields:
                response_fields[key] = fields
                break  # 只取第一个 JSON 块（成功响应）

    return response_fields


def _extract_json_keys(json_str: str) -> List[str]:
    """
    从 JSON 字符串中递归提取所有键名。

    Args:
        json_str: JSON 格式字符串

    Returns:
        键名列表（扁平化）
    """
    keys = []
    # 使用正则提取所有 JSON 键名
    key_pattern = re.compile(r'"(\w+)"\s*:')
    for match in key_pattern.finditer(json_str):
        key = match.group(1)
        if key not in keys:
            keys.append(key)
    return keys


def extract_pages_from_info_arch(content: str) -> List[Dict[str, str]]:
    """
    从信息架构文档中提取页面清单。

    提取 Section 3 "页面清单表" 中的表格。

    Args:
        content: 信息架构文档内容

    Returns:
        页面列表：[{name, path, module}, ...]
    """
    pages = []
    # 查找 Section 3 页面清单表
    section_match = re.search(
        r"^##\s+3\.\s+页面清单表\s*\n(.*?)(?=^##\s|\Z)",
        content,
        re.MULTILINE | re.DOTALL
    )
    if section_match:
        tables = extract_tables(section_match.group(1))
        if tables:
            # 表头: 序号 | 页面名称 | 路由路径 | 所属模块 | 访问角色 | 说明
            for row in tables[0][1:]:  # 跳过表头
                if len(row) >= 4:
                    pages.append({
                        "name": row[1].strip(),
                        "path": row[2].strip(),
                        "module": row[3].strip()
                    })
    return pages


def extract_pages_from_interaction(content: str) -> List[Dict[str, str]]:
    """
    从交互设计文档中提取页面定义。

    提取 Section 4 "各页面交互详述" 中的 ### 标题。

    Args:
        content: 交互设计文档内容

    Returns:
        页面列表：[{name, path: ""}, ...]
    """
    pages = []
    # 查找 Section 4 下的 ### 页面名
    section_match = re.search(
        r"^##\s+4\.\s+各页面交互详述\s*\n(.*?)(?=^##\s|\Z)",
        content,
        re.MULTILINE | re.DOTALL
    )
    if section_match:
        section_content = section_match.group(1)
        page_headers = re.findall(
            r"^###\s+4\.\d+\.\d+\s+(.+)$",
            section_content,
            re.MULTILINE
        )
        for name in page_headers:
            pages.append({
                "name": name.strip(),
                "path": ""  # 交互设计中通常不包含路由路径
            })
    return pages


def extract_backend_api_refs(content: str) -> List[Dict[str, str]]:
    """
    从后端技术方案文档中提取引用的 API 端点。

    查找文档中出现的 API 路径模式，如 /api/v1/xxx。

    Args:
        content: 后端技术方案文档内容

    Returns:
        端点列表：[{method, path}, ...]
    """
    endpoints = []
    # 使用精确正则只提取 METHOD /path 部分，去掉逗号和描述性文字
    # 匹配如 "POST /api/v1/todos" 而非 "POST /api/v1/todos，携带合法"
    path_pattern = re.compile(r"(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s,，]+)")
    for match in path_pattern.finditer(content):
        endpoints.append({
            "method": match.group(1).upper(),
            "path": match.group(2)
        })
    # 去重
    seen = set()
    unique = []
    for ep in endpoints:
        key = f"{ep['method']} {ep['path']}"
        if key not in seen:
            seen.add(key)
            unique.append(ep)
    return unique


def extract_code_api_calls(source_dir: Path) -> List[Dict[str, str]]:
    """
    从实际代码文件中提取 API 调用。

    搜索常见模式：fetch('/api/...'), axios.get('/api/...'), apiClient.xxx 等。

    Args:
        source_dir: 代码源码目录

    Returns:
        端点列表：[{method, path}, ...]
    """
    endpoints = []
    if not source_dir.exists():
        return endpoints

    # 常见的 API 调用正则模式
    patterns = [
        # fetch('GET', '/api/...') 或 fetch('/api/...')
        re.compile(r"""(?:fetch|axios)\.(get|post|put|delete|patch)\s*\(\s*['"`'](/api/[^'"`\s]+)['"`']"""),
        # { method: 'GET', url: '/api/...' }
        re.compile(r"""method\s*:\s*['"`'](GET|POST|PUT|DELETE|PATCH)['"`'].*?url\s*:\s*['"`'](/api/[^'"`\s]+)['"`']""", re.DOTALL),
        # 路由定义: router.get('/api/...', ...)
        re.compile(r"""router\.(get|post|put|delete|patch)\s*\(\s*['"`'](/api/[^'"`\s]+)['"`']"""),
        # @GetMapping("/api/...") 或 @PostMapping 等
        re.compile(r"""@(Get|Post|Put|Delete|Patch)Mapping\s*\(\s*['"`'](/api/[^'"`\s]+)['"`']"""),
        # Rust Axum 路由方法: .get("/api/...") 等
        re.compile(r"""\.(get|post|put|delete|patch)\s*\(\s*["'](/api/[^"'\s]+)["']"""),
        # C# ASP.NET 属性: [HttpGet("/api/...")] 等
        re.compile(r"""\[(HttpGet|HttpPost|HttpPut|HttpDelete|HttpPatch)\s*\(\s*["'](/api/[^"'\s]+)["']\s*\)]"""),
    ]

    # 搜索代码文件（.ts, .tsx, .js, .jsx, .py, .java, .go, .rs, .cs）
    code_extensions = {".ts", ".tsx", ".js", ".jsx", ".py", ".java", ".go", ".rs", ".cs"}
    for ext in code_extensions:
        for file_path in source_dir.rglob(f"*{ext}"):
            try:
                file_content = file_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue
            for pattern in patterns:
                for match in pattern.finditer(file_content):
                    method = match.group(1).upper()
                    path = match.group(2)
                    endpoints.append({"method": method, "path": path})

    # 去重
    seen = set()
    unique = []
    for ep in endpoints:
        key = f"{ep['method']} {ep['path']}"
        if key not in seen:
            seen.add(key)
            unique.append(ep)
    return unique


def camel_to_snake(name: str) -> str:
    """
    将 camelCase 转换为 snake_case。

    Args:
        name: camelCase 字符串

    Returns:
        snake_case 字符串
    """
    # 处理连续大写字母的情况，如 userID -> user_id
    result = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    result = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", result)
    return result.lower()


def snake_to_camel(name: str) -> str:
    """
    将 snake_case 转换为 camelCase。

    Args:
        name: snake_case 字符串

    Returns:
        camelCase 字符串
    """
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def normalize_path(path: str) -> str:
    """
    规范化 API 路径，去除尾部斜杠和路径参数的差异。

    将 :param 和 {param} 统一为 {param} 格式。

    Args:
        path: API 路径字符串

    Returns:
        规范化后的路径
    """
    path = path.rstrip("/")
    # 将 :param 格式统一为 {param}
    path = re.sub(r":(\w+)", r"{\1}", path)
    return path


# ============================================================================
# 校验函数
# ============================================================================

def check_field_names(
    specs_dir: Path,
    verbose: bool = False
) -> Dict:
    """
    校验 P0-1, P0-2：数据模型字段名与数据库表结构 / API 响应字段名的一致性。

    对比逻辑：
      - Skill 5（数据模型字段约定）中的实体字段名
        vs Skill 7（数据库设计）中的表字段名
      - Skill 5（数据模型字段约定）中的实体字段名
        vs Skill 8（API 接口文档）中的响应字段名

    命名映射：数据模型使用 camelCase，数据库使用 snake_case，
    API 响应使用 camelCase。脚本会自动进行命名风格转换后比对。

    Args:
        specs_dir: specs 文档目录
        verbose: 是否输出详细信息

    Returns:
        校验结果字典
    """
    checks = []
    summary = {"pass": 0, "fail": 0, "warn": 0, "skip": 0}

    # ---- 读取上游文档：数据模型字段约定 ----
    data_model_file = specs_dir / "数据模型字段约定.md"
    data_model_content = read_markdown_file(data_model_file)
    if data_model_content is None:
        checks.append({
            "source": "数据模型字段约定.md",
            "target": "数据库设计.md",
            "field": "-",
            "source_value": "-",
            "target_value": "-",
            "status": "WARN",
            "message": f"上游文档不存在: {data_model_file}"
        })
        summary["warn"] += 1
        return {
            "check_type": "field-names",
            "status": "WARN",
            "checks": checks,
            "summary": summary
        }

    # 提取数据模型实体字段
    entities = extract_entity_field_tables(data_model_content)
    if not entities:
        checks.append({
            "source": "数据模型字段约定.md",
            "target": "数据库设计.md",
            "field": "-",
            "source_value": "-",
            "target_value": "-",
            "status": "WARN",
            "message": "数据模型文档中未找到实体字段定义"
        })
        summary["warn"] += 1
        return {
            "check_type": "field-names",
            "status": "WARN",
            "checks": checks,
            "summary": summary
        }

    # ---- 校验 P0-1：数据模型 vs 数据库设计 ----
    db_file = specs_dir / "数据库设计.md"
    db_content = read_markdown_file(db_file)

    if db_content is not None:
        db_tables = extract_db_table_fields(db_content)

        # 对每个实体，查找对应的数据库表进行字段比对
        for entity_name, entity_fields in entities.items():
            # 尝试匹配表名：实体名可能是 camelCase，表名可能是 snake_case 或复数
            entity_snake = camel_to_snake(entity_name)
            possible_table_names = [
                entity_snake,           # user_order
                entity_snake + "s",     # user_orders
                entity_name.lower(),    # userorder
                entity_name.lower() + "s",  # userorders
                entity_name,            # 原始名称
            ]

            matched_table = None
            for table_name in db_tables:
                table_lower = table_name.lower()
                if table_lower in [n.lower() for n in possible_table_names]:
                    matched_table = table_name
                    break

            if matched_table is None:
                # 未找到匹配的表，记录警告
                checks.append({
                    "source": "数据模型字段约定.md",
                    "target": "数据库设计.md",
                    "field": entity_name,
                    "source_value": f"{len(entity_fields)} 个字段",
                    "target_value": "未找到对应表",
                    "status": "WARN",
                    "message": f"实体 '{entity_name}' 在数据库设计中未找到对应表（尝试匹配: {possible_table_names}）"
                })
                summary["warn"] += 1
                continue

            # 逐字段比对
            db_fields = db_tables[matched_table]
            db_field_names = {f["字段名"].lower() for f in db_fields}

            for ef in entity_fields:
                field_name = ef["字段名"]
                field_type = ef.get("类型", "")

                # 数据模型字段名转 snake_case 后与数据库比对
                snake_name = camel_to_snake(field_name)
                # 同时检查原始名称（可能本身就是 snake_case）
                possible_names = [snake_name, field_name.lower(), field_name]

                matched = False
                for pn in possible_names:
                    if pn in db_field_names:
                        matched = True
                        # 获取数据库中的类型
                        db_type = ""
                        for df in db_fields:
                            if df["字段名"].lower() == pn:
                                db_type = df.get("类型", "")
                                break
                        checks.append({
                            "source": "数据模型字段约定.md",
                            "target": "数据库设计.md",
                            "field": field_name,
                            "source_value": field_type,
                            "target_value": db_type,
                            "status": "PASS",
                            "message": f"字段 '{field_name}' -> '{pn}' 匹配成功"
                        })
                        summary["pass"] += 1
                        break

                if not matched:
                    checks.append({
                        "source": "数据模型字段约定.md",
                        "target": "数据库设计.md",
                        "field": field_name,
                        "source_value": field_type,
                        "target_value": "未找到",
                        "status": "FAIL",
                        "message": f"实体 '{entity_name}' 的字段 '{field_name}' 在表 '{matched_table}' 中未找到匹配（尝试: {possible_names}）"
                    })
                    summary["fail"] += 1

            # 反向检查：数据库中有但数据模型中没有的字段
            entity_field_names = {
                camel_to_snake(f["字段名"]).lower() for f in entity_fields
            }
            entity_field_names.update({f["字段名"].lower() for f in entity_fields})

            for df in db_fields:
                db_fn = df["字段名"].lower()
                # 跳过通用审计字段
                if db_fn in ("id", "created_at", "updated_at", "deleted_at",
                             "created_by", "updated_by"):
                    continue
                if db_fn not in entity_field_names:
                    checks.append({
                        "source": "数据库设计.md",
                        "target": "数据模型字段约定.md",
                        "field": df["字段名"],
                        "source_value": df.get("类型", ""),
                        "target_value": "未在数据模型中定义",
                        "status": "WARN",
                        "message": f"表 '{matched_table}' 的字段 '{df['字段名']}' 在实体 '{entity_name}' 中未定义（可能是新增字段或遗漏）"
                    })
                    summary["warn"] += 1
    else:
        checks.append({
            "source": "数据模型字段约定.md",
            "target": "数据库设计.md",
            "field": "-",
            "source_value": "-",
            "target_value": "-",
            "status": "WARN",
            "message": f"下游文档不存在: {db_file}"
        })
        summary["warn"] += 1

    # ---- 校验 P0-2：数据模型 vs API 响应字段名 ----
    api_file = specs_dir / "API接口文档.md"
    # 尝试多种可能的文件名
    if not api_file.exists():
        alt_names = ["api-design.md", "API设计.md", "api接口文档.md"]
        for alt in alt_names:
            alt_path = specs_dir / alt
            if alt_path.exists():
                api_file = alt_path
                break

    api_content = read_markdown_file(api_file)
    if api_content is not None:
        api_response_fields = extract_api_response_fields(api_content)

        if api_response_fields:
            # 将所有 API 响应字段名收集到一个集合中
            all_api_fields = set()
            for endpoint, fields in api_response_fields.items():
                for f in fields:
                    # 跳过通用响应字段
                    if f in ("code", "message", "data", "details"):
                        continue
                    all_api_fields.add(f)

            for entity_name, entity_fields in entities.items():
                for ef in entity_fields:
                    field_name = ef["字段名"]
                    field_type = ef.get("类型", "")

                    # 数据模型字段名（camelCase）应与 API 响应字段名一致
                    if field_name in all_api_fields:
                        checks.append({
                            "source": "数据模型字段约定.md",
                            "target": "API接口文档.md",
                            "field": field_name,
                            "source_value": field_type,
                            "target_value": "存在于 API 响应中",
                            "status": "PASS",
                            "message": f"字段 '{field_name}' 在 API 响应中找到"
                        })
                        summary["pass"] += 1
                    else:
                        # 检查 snake_case 版本
                        snake_name = camel_to_snake(field_name)
                        if snake_name in all_api_fields:
                            checks.append({
                                "source": "数据模型字段约定.md",
                                "target": "API接口文档.md",
                                "field": field_name,
                                "source_value": field_type,
                                "target_value": f"API 中为 '{snake_name}'",
                                "status": "WARN",
                                "message": f"字段 '{field_name}' 在 API 响应中为 snake_case 形式 '{snake_name}'，与数据模型命名风格不一致"
                            })
                            summary["warn"] += 1
                        # 不在 API 响应中不一定有问题（可能是非接口字段），不记录
        else:
            checks.append({
                "source": "数据模型字段约定.md",
                "target": "API接口文档.md",
                "field": "-",
                "source_value": "-",
                "target_value": "-",
                "status": "WARN",
                "message": "API 接口文档中未找到响应字段定义"
            })
            summary["warn"] += 1
    else:
        checks.append({
            "source": "数据模型字段约定.md",
            "target": "API接口文档.md",
            "field": "-",
            "source_value": "-",
            "target_value": "-",
            "status": "WARN",
            "message": f"下游文档不存在: {api_file}"
        })
        summary["warn"] += 1

    # 确定整体状态
    status = "PASS"
    if summary["fail"] > 0:
        status = "FAIL"
    elif summary["warn"] > 0:
        status = "WARN"

    return {
        "check_type": "field-names",
        "status": status,
        "checks": checks,
        "summary": summary
    }


def check_api_paths(
    specs_dir: Path,
    verbose: bool = False
) -> Dict:
    """
    校验 P0-3, P0-4：API 路径在 API 文档、后端技术方案和实际代码中的一致性。

    对比逻辑：
      - Skill 8（API 接口文档）中的 API 路径
        vs Skill 10（后端技术方案）中引用的 API 路径
      - Skill 8（API 接口文档）中的 API 路径
        vs 实际代码中的 API 路径

    Args:
        specs_dir: specs 文档目录
        verbose: 是否输出详细信息

    Returns:
        校验结果字典
    """
    checks = []
    summary = {"pass": 0, "fail": 0, "warn": 0, "skip": 0}

    # ---- 读取上游文档：API 接口文档 ----
    api_file = specs_dir / "API接口文档.md"
    alt_names = ["api-design.md", "API设计.md", "api接口文档.md"]
    for alt in alt_names:
        if not api_file.exists():
            alt_path = specs_dir / alt
            if alt_path.exists():
                api_file = alt_path
                break

    api_content = read_markdown_file(api_file)
    if api_content is None:
        checks.append({
            "source": "API接口文档.md",
            "target": "后端技术方案",
            "field": "-",
            "source_value": "-",
            "target_value": "-",
            "status": "WARN",
            "message": f"上游文档不存在: {api_file}"
        })
        summary["warn"] += 1
        return {
            "check_type": "api-paths",
            "status": "WARN",
            "checks": checks,
            "summary": summary
        }

    api_endpoints = extract_api_endpoints(api_content)
    if not api_endpoints:
        checks.append({
            "source": "API接口文档.md",
            "target": "后端技术方案",
            "field": "-",
            "source_value": "-",
            "target_value": "-",
            "status": "WARN",
            "message": "API 接口文档中未找到端点定义"
        })
        summary["warn"] += 1
        return {
            "check_type": "api-paths",
            "status": "WARN",
            "checks": checks,
            "summary": summary
        }

    # 规范化 API 文档中的端点
    api_endpoint_map = {}
    for ep in api_endpoints:
        key = f"{ep['method']} {normalize_path(ep['path'])}"
        api_endpoint_map[key] = ep

    # ---- 校验 P0-3：API 文档 vs 后端技术方案 ----
    # 查找 features 目录下的后端技术方案
    features_dir = specs_dir / "features"
    backend_endpoints = []

    if features_dir.exists():
        for f in features_dir.glob("*后端技术方案*"):
            content = read_markdown_file(f)
            if content:
                backend_endpoints.extend(extract_backend_api_refs(content))

    if backend_endpoints:
        # 规范化后端方案中的端点
        backend_endpoint_map = {}
        for ep in backend_endpoints:
            key = f"{ep['method']} {normalize_path(ep['path'])}"
            backend_endpoint_map[key] = ep

        # 比对：API 文档中的端点是否在后端方案中都有
        for key, api_ep in api_endpoint_map.items():
            if key in backend_endpoint_map:
                checks.append({
                    "source": "API接口文档.md",
                    "target": "后端技术方案",
                    "field": key,
                    "source_value": api_ep.get("description", ""),
                    "target_value": "已引用",
                    "status": "PASS",
                    "message": f"端点 '{key}' 在后端技术方案中已引用"
                })
                summary["pass"] += 1
            else:
                checks.append({
                    "source": "API接口文档.md",
                    "target": "后端技术方案",
                    "field": key,
                    "source_value": api_ep.get("description", ""),
                    "target_value": "未引用",
                    "status": "WARN",
                    "message": f"端点 '{key}' 在后端技术方案中未找到引用（可能尚未开发或遗漏）"
                })
                summary["warn"] += 1

        # 反向检查：后端方案中有但 API 文档中没有的端点
        for key in backend_endpoint_map:
            if key not in api_endpoint_map:
                checks.append({
                    "source": "后端技术方案",
                    "target": "API接口文档.md",
                    "field": key,
                    "source_value": "后端方案中引用",
                    "target_value": "未在 API 文档中定义",
                    "status": "FAIL",
                    "message": f"端点 '{key}' 在后端技术方案中引用但未在 API 接口文档中定义"
                })
                summary["fail"] += 1
    else:
        checks.append({
            "source": "API接口文档.md",
            "target": "后端技术方案",
            "field": "-",
            "source_value": f"{len(api_endpoints)} 个端点",
            "target_value": "未找到后端技术方案",
            "status": "WARN",
            "message": "未找到后端技术方案文档，跳过 API 路径比对"
        })
        summary["warn"] += 1

    # ---- 校验 P0-4：API 文档 vs 实际代码 ----
    # 在 specs_dir 的上级目录中查找源码目录
    source_dirs = []
    project_root = specs_dir.parent
    for candidate in ["src", "source", "app", "server", "backend", "api"]:
        candidate_path = project_root / candidate
        if candidate_path.exists():
            source_dirs.append(candidate_path)

    if source_dirs:
        code_endpoints = []
        for sd in source_dirs:
            code_endpoints.extend(extract_code_api_calls(sd))

        if code_endpoints:
            code_endpoint_map = {}
            for ep in code_endpoints:
                key = f"{ep['method']} {normalize_path(ep['path'])}"
                code_endpoint_map[key] = ep

            for key, api_ep in api_endpoint_map.items():
                if key in code_endpoint_map:
                    checks.append({
                        "source": "API接口文档.md",
                        "target": "实际代码",
                        "field": key,
                        "source_value": api_ep.get("description", ""),
                        "target_value": "已实现",
                        "status": "PASS",
                        "message": f"端点 '{key}' 在代码中已实现"
                    })
                    summary["pass"] += 1
                else:
                    checks.append({
                        "source": "API接口文档.md",
                        "target": "实际代码",
                        "field": key,
                        "source_value": api_ep.get("description", ""),
                        "target_value": "未实现",
                        "status": "WARN",
                        "message": f"端点 '{key}' 在代码中未找到实现（可能尚未开发）"
                    })
                    summary["warn"] += 1

            # 反向检查
            for key in code_endpoint_map:
                if key not in api_endpoint_map:
                    checks.append({
                        "source": "实际代码",
                        "target": "API接口文档.md",
                        "field": key,
                        "source_value": "代码中实现",
                        "target_value": "未在 API 文档中定义",
                        "status": "FAIL",
                        "message": f"端点 '{key}' 在代码中实现但未在 API 接口文档中定义"
                    })
                    summary["fail"] += 1
        else:
            checks.append({
                "source": "API接口文档.md",
                "target": "实际代码",
                "field": "-",
                "source_value": f"{len(api_endpoints)} 个端点",
                "target_value": "未找到 API 调用",
                "status": "WARN",
                "message": f"在源码目录 {source_dirs} 中未找到 API 调用定义"
            })
            summary["warn"] += 1
    else:
        checks.append({
            "source": "API接口文档.md",
            "target": "实际代码",
            "field": "-",
            "source_value": f"{len(api_endpoints)} 个端点",
            "target_value": "未找到源码目录",
            "status": "WARN",
            "message": "未找到源码目录（src/source/app/server），跳过代码比对"
        })
        summary["warn"] += 1

    # 确定整体状态
    status = "PASS"
    if summary["fail"] > 0:
        status = "FAIL"
    elif summary["warn"] > 0:
        status = "WARN"

    return {
        "check_type": "api-paths",
        "status": status,
        "checks": checks,
        "summary": summary
    }


def check_page_list(
    specs_dir: Path,
    verbose: bool = False
) -> Dict:
    """
    校验 P1-5：信息架构页面清单与交互设计页面定义的一致性。

    对比逻辑：
      - Skill 4（信息架构图）Section 3 中的页面清单
        vs Skill 6（交互设计）Section 4 中的页面定义

    Args:
        specs_dir: specs 文档目录
        verbose: 是否输出详细信息

    Returns:
        校验结果字典
    """
    checks = []
    summary = {"pass": 0, "fail": 0, "warn": 0, "skip": 0}

    # ---- 读取上游文档：信息架构图 ----
    info_arch_file = specs_dir / "信息架构图.md"
    alt_names = ["information-architecture.md", "InformationArchitecture.md"]
    for alt in alt_names:
        if not info_arch_file.exists():
            alt_path = specs_dir / alt
            if alt_path.exists():
                info_arch_file = alt_path
                break

    info_arch_content = read_markdown_file(info_arch_file)
    if info_arch_content is None:
        checks.append({
            "source": "信息架构图.md",
            "target": "交互设计文档.md",
            "field": "-",
            "source_value": "-",
            "target_value": "-",
            "status": "WARN",
            "message": f"上游文档不存在: {info_arch_file}"
        })
        summary["warn"] += 1
        return {
            "check_type": "page-list",
            "status": "WARN",
            "checks": checks,
            "summary": summary
        }

    info_pages = extract_pages_from_info_arch(info_arch_content)
    if not info_pages:
        checks.append({
            "source": "信息架构图.md",
            "target": "交互设计文档.md",
            "field": "-",
            "source_value": "-",
            "target_value": "-",
            "status": "WARN",
            "message": "信息架构文档中未找到页面清单"
        })
        summary["warn"] += 1
        return {
            "check_type": "page-list",
            "status": "WARN",
            "checks": checks,
            "summary": summary
        }

    # ---- 读取下游文档：交互设计 ----
    interaction_file = specs_dir / "交互设计文档.md"
    alt_names = ["interaction-design.md", "InteractionDesign.md"]
    for alt in alt_names:
        if not interaction_file.exists():
            alt_path = specs_dir / alt
            if alt_path.exists():
                interaction_file = alt_path
                break

    interaction_content = read_markdown_file(interaction_file)
    if interaction_content is None:
        checks.append({
            "source": "信息架构图.md",
            "target": "交互设计文档.md",
            "field": "-",
            "source_value": f"{len(info_pages)} 个页面",
            "target_value": "-",
            "status": "WARN",
            "message": f"下游文档不存在: {interaction_file}"
        })
        summary["warn"] += 1
        return {
            "check_type": "page-list",
            "status": "WARN",
            "checks": checks,
            "summary": summary
        }

    interaction_pages = extract_pages_from_interaction(interaction_content)

    # 构建交互设计页面名集合（用于快速查找）
    interaction_page_names = {p["name"] for p in interaction_pages}

    # 比对：信息架构中的页面是否在交互设计中都有定义
    for page in info_pages:
        page_name = page["name"]
        if page_name in interaction_page_names:
            checks.append({
                "source": "信息架构图.md",
                "target": "交互设计文档.md",
                "field": page_name,
                "source_value": f"路由: {page['path']}, 模块: {page['module']}",
                "target_value": "已定义交互",
                "status": "PASS",
                "message": f"页面 '{page_name}' 在交互设计中已定义"
            })
            summary["pass"] += 1
        else:
            # 模糊匹配：检查是否包含关系
            fuzzy_match = None
            for ip_name in interaction_page_names:
                if page_name in ip_name or ip_name in page_name:
                    fuzzy_match = ip_name
                    break

            if fuzzy_match:
                checks.append({
                    "source": "信息架构图.md",
                    "target": "交互设计文档.md",
                    "field": page_name,
                    "source_value": f"路由: {page['path']}, 模块: {page['module']}",
                    "target_value": f"模糊匹配: '{fuzzy_match}'",
                    "status": "WARN",
                    "message": f"页面 '{page_name}' 在交互设计中未精确匹配，但找到相似页面 '{fuzzy_match}'"
                })
                summary["warn"] += 1
            else:
                checks.append({
                    "source": "信息架构图.md",
                    "target": "交互设计文档.md",
                    "field": page_name,
                    "source_value": f"路由: {page['path']}, 模块: {page['module']}",
                    "target_value": "未定义交互",
                    "status": "FAIL",
                    "message": f"页面 '{page_name}' 在交互设计中未找到对应定义"
                })
                summary["fail"] += 1

    # 反向检查：交互设计中有但信息架构中没有的页面
    info_page_names = {p["name"] for p in info_pages}
    for page in interaction_pages:
        if page["name"] not in info_page_names:
            checks.append({
                "source": "交互设计文档.md",
                "target": "信息架构图.md",
                "field": page["name"],
                "source_value": "交互设计中定义",
                "target_value": "未在页面清单中",
                "status": "WARN",
                "message": f"页面 '{page['name']}' 在交互设计中定义但未在信息架构页面清单中列出"
            })
            summary["warn"] += 1

    # 确定整体状态
    status = "PASS"
    if summary["fail"] > 0:
        status = "FAIL"
    elif summary["warn"] > 0:
        status = "WARN"

    # 检测是否存在 _v2 版本的交互设计文档，添加 INFO 提示
    info_messages = []
    interaction_base_name = interaction_file.stem  # 如 "交互设计文档"
    v2_file = interaction_file.parent / f"{interaction_base_name}_v2.md"
    if v2_file.exists():
        info_messages.append(
            f"INFO: 检测到存在更新版本的交互设计文档 '{v2_file.name}'，"
            f"当前校验使用的是 '{interaction_file.name}'。"
            f"如果校验结果存在 FAIL，请检查是否应使用 _v2 版本文档。"
        )

    return {
        "check_type": "page-list",
        "status": status,
        "checks": checks,
        "summary": summary,
        "info": info_messages if info_messages else None
    }


def check_api_responses(
    specs_dir: Path,
    verbose: bool = False
) -> Dict:
    """
    校验 P1-6：API 响应格式在后端技术方案和前端技术方案中的一致性。

    对比逻辑：
      - Skill 8（API 接口文档）中的响应字段
        vs Skill 10（后端技术方案）中的响应定义
      - Skill 10（后端技术方案）中的响应定义
        vs Skill 11（前端技术方案）中的接口调用

    Args:
        specs_dir: specs 文档目录
        verbose: 是否输出详细信息

    Returns:
        校验结果字典
    """
    checks = []
    summary = {"pass": 0, "fail": 0, "warn": 0, "skip": 0}

    # ---- 读取 API 接口文档 ----
    api_file = specs_dir / "API接口文档.md"
    alt_names = ["api-design.md", "API设计.md", "api接口文档.md"]
    for alt in alt_names:
        if not api_file.exists():
            alt_path = specs_dir / alt
            if alt_path.exists():
                api_file = alt_path
                break

    api_content = read_markdown_file(api_file)
    if api_content is None:
        checks.append({
            "source": "API接口文档.md",
            "target": "后端技术方案",
            "field": "-",
            "source_value": "-",
            "target_value": "-",
            "status": "WARN",
            "message": f"上游文档不存在: {api_file}"
        })
        summary["warn"] += 1
        return {
            "check_type": "api-responses",
            "status": "WARN",
            "checks": checks,
            "summary": summary
        }

    api_response_fields = extract_api_response_fields(api_content)
    if not api_response_fields:
        checks.append({
            "source": "API接口文档.md",
            "target": "后端技术方案",
            "field": "-",
            "source_value": "-",
            "target_value": "-",
            "status": "WARN",
            "message": "API 接口文档中未找到响应字段定义"
        })
        summary["warn"] += 1
        return {
            "check_type": "api-responses",
            "status": "WARN",
            "checks": checks,
            "summary": summary
        }

    # ---- 校验：API 文档 vs 后端技术方案 ----
    features_dir = specs_dir / "features"
    backend_response_fields = {}

    if features_dir.exists():
        for f in features_dir.glob("*后端技术方案*"):
            content = read_markdown_file(f)
            if content:
                # 从后端方案中提取响应相关的 JSON 块
                json_blocks = re.findall(r"```json\s*\n(.*?)```", content, re.DOTALL)
                for block in json_blocks:
                    keys = _extract_json_keys(block)
                    if keys:
                        backend_response_fields[f.name] = keys

    if backend_response_fields:
        # 将后端方案中的所有响应字段收集到一个集合
        all_backend_fields = set()
        for filename, fields in backend_response_fields.items():
            for f in fields:
                if f not in ("code", "message", "data", "details"):
                    all_backend_fields.add(f)

        # 将 API 文档中的所有响应字段收集
        all_api_fields = set()
        for endpoint, fields in api_response_fields.items():
            for f in fields:
                if f not in ("code", "message", "data", "details"):
                    all_api_fields.add(f)

        # 比对共有字段
        common_fields = all_api_fields & all_backend_fields
        for field in sorted(common_fields):
            checks.append({
                "source": "API接口文档.md",
                "target": "后端技术方案",
                "field": field,
                "source_value": "API 响应中定义",
                "target_value": "后端方案中定义",
                "status": "PASS",
                "message": f"响应字段 '{field}' 在 API 文档和后端方案中一致"
            })
            summary["pass"] += 1

        # API 文档中有但后端方案中没有的字段
        api_only = all_api_fields - all_backend_fields
        for field in sorted(api_only):
            checks.append({
                "source": "API接口文档.md",
                "target": "后端技术方案",
                "field": field,
                "source_value": "API 响应中定义",
                "target_value": "后端方案中未定义",
                "status": "WARN",
                "message": f"响应字段 '{field}' 在 API 文档中定义但在后端方案中未找到"
            })
            summary["warn"] += 1

        # 后端方案中有但 API 文档中没有的字段
        backend_only = all_backend_fields - all_api_fields
        for field in sorted(backend_only):
            checks.append({
                "source": "后端技术方案",
                "target": "API接口文档.md",
                "field": field,
                "source_value": "后端方案中定义",
                "target_value": "API 文档中未定义",
                "status": "WARN",
                "message": f"响应字段 '{field}' 在后端方案中定义但在 API 文档中未找到"
            })
            summary["warn"] += 1
    else:
        checks.append({
            "source": "API接口文档.md",
            "target": "后端技术方案",
            "field": "-",
            "source_value": f"{len(api_response_fields)} 个接口响应",
            "target_value": "未找到后端技术方案",
            "status": "WARN",
            "message": "未找到后端技术方案文档，跳过响应格式比对"
        })
        summary["warn"] += 1

    # ---- 校验：后端技术方案 vs 前端技术方案 ----
    frontend_response_fields = {}
    if features_dir.exists():
        for f in features_dir.glob("*前端技术方案*"):
            content = read_markdown_file(f)
            if content:
                # 从前端方案中提取接口调用相关的字段引用
                # 查找 API 调用和类型定义中的字段名
                json_blocks = re.findall(r"```(?:json|typescript|ts)\s*\n(.*?)```", content, re.DOTALL)
                for block in json_blocks:
                    keys = _extract_json_keys(block)
                    if keys:
                        frontend_response_fields[f.name] = keys

    if frontend_response_fields and backend_response_fields:
        all_frontend_fields = set()
        for filename, fields in frontend_response_fields.items():
            for f in fields:
                if f not in ("code", "message", "data", "details"):
                    all_frontend_fields.add(f)

        # 比对前端和后端共有的字段
        common_fb = all_backend_fields & all_frontend_fields
        for field in sorted(common_fb):
            checks.append({
                "source": "后端技术方案",
                "target": "前端技术方案",
                "field": field,
                "source_value": "后端方案中定义",
                "target_value": "前端方案中引用",
                "status": "PASS",
                "message": f"响应字段 '{field}' 在后端方案和前端方案中一致"
            })
            summary["pass"] += 1

        # 后端有但前端没有引用的字段
        backend_only_fb = all_backend_fields - all_frontend_fields
        for field in sorted(backend_only_fb):
            checks.append({
                "source": "后端技术方案",
                "target": "前端技术方案",
                "field": field,
                "source_value": "后端方案中定义",
                "target_value": "前端方案中未引用",
                "status": "WARN",
                "message": f"响应字段 '{field}' 在后端方案中定义但前端方案中未引用（可能未使用）"
            })
            summary["warn"] += 1
    elif frontend_response_fields and not backend_response_fields:
        checks.append({
            "source": "后端技术方案",
            "target": "前端技术方案",
            "field": "-",
            "source_value": "-",
            "target_value": f"{len(frontend_response_fields)} 个前端方案",
            "status": "WARN",
            "message": "找到前端技术方案但未找到后端技术方案，无法比对"
        })
        summary["warn"] += 1

    # 确定整体状态
    status = "PASS"
    if summary["fail"] > 0:
        status = "FAIL"
    elif summary["warn"] > 0:
        status = "WARN"

    return {
        "check_type": "api-responses",
        "status": status,
        "checks": checks,
        "summary": summary
    }


# ============================================================================
# 主入口
# ============================================================================

def main():
    """脚本主入口，解析命令行参数并执行校验。"""
    parser = argparse.ArgumentParser(
        description="SpecForge V4 跨文档一致性自动校验工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  # 校验字段名一致性（数据模型 vs 数据库/API）
  python validate_consistency.py --specs-dir /path/to/specs --check field-names

  # 校验 API 路径一致性（API 文档 vs 后端方案/代码）
  python validate_consistency.py --specs-dir /path/to/specs --check api-paths

  # 校验页面清单一致性（信息架构 vs 交互设计）
  python validate_consistency.py --specs-dir /path/to/specs --check page-list

  # 校验 API 响应格式一致性（后端方案 vs 前端方案）
  python validate_consistency.py --specs-dir /path/to/specs --check api-responses

  # 全量校验
  python validate_consistency.py --specs-dir /path/to/specs --check all

  # 输出详细结果到文件
  python validate_consistency.py --specs-dir /path/to/specs --check all --output result.json
        """
    )

    parser.add_argument(
        "--specs-dir",
        type=str,
        required=True,
        help="specs 文档目录路径"
    )
    parser.add_argument(
        "--check",
        type=str,
        required=True,
        choices=["field-names", "api-paths", "page-list", "api-responses", "all"],
        help="校验类型"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="输出 JSON 文件路径（默认输出到 stdout）"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="输出详细校验信息"
    )

    args = parser.parse_args()

    specs_dir = Path(args.specs_dir)
    if not specs_dir.exists():
        result = {
            "error": f"specs 目录不存在: {specs_dir}",
            "status": "FAIL"
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 根据校验类型执行对应的校验函数
    check_functions = {
        "field-names": check_field_names,
        "api-paths": check_api_paths,
        "page-list": check_page_list,
        "api-responses": check_api_responses,
    }

    if args.check == "all":
        # 全量校验：执行所有校验类型
        results = []
        overall_pass = 0
        overall_fail = 0
        overall_warn = 0

        for check_name, check_func in check_functions.items():
            result = check_func(specs_dir, verbose=args.verbose)
            results.append(result)
            overall_pass += result["summary"]["pass"]
            overall_fail += result["summary"]["fail"]
            overall_warn += result["summary"]["warn"]

        # 汇总结果
        overall_status = "PASS"
        if overall_fail > 0:
            overall_status = "FAIL"
        elif overall_warn > 0:
            overall_status = "WARN"

        output = {
            "check_type": "all",
            "status": overall_status,
            "summary": {
                "pass": overall_pass,
                "fail": overall_fail,
                "warn": overall_warn,
                "skip": 0
            },
            "details": results
        }
    else:
        # 单项校验
        check_func = check_functions[args.check]
        output = check_func(specs_dir, verbose=args.verbose)

    # 输出结果
    json_output = json.dumps(output, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_output, encoding="utf-8")
        print(f"校验结果已写入: {output_path}")
    else:
        print(json_output)

    # 输出人类可读的摘要
    if args.verbose:
        print("\n" + "=" * 60)
        print("校验摘要")
        print("=" * 60)
        if args.check == "all":
            for r in output["details"]:
                print(f"\n[{r['check_type']}] {r['status']}")
                print(f"  通过: {r['summary']['pass']}, "
                      f"失败: {r['summary']['fail']}, "
                      f"警告: {r['summary']['warn']}")
                # 输出 INFO 级别的提示信息
                if r.get("info"):
                    for info_msg in r["info"]:
                        print(f"  [INFO] {info_msg}")
        else:
            print(f"\n[{output['check_type']}] {output['status']}")
            print(f"  通过: {output['summary']['pass']}, "
                  f"失败: {output['summary']['fail']}, "
                  f"警告: {output['summary']['warn']}")
            # 输出失败和警告的详细信息
            for check in output["checks"]:
                if check["status"] in ("FAIL", "WARN"):
                    print(f"  [{check['status']}] {check['field']}: {check['message']}")
            # 输出 INFO 级别的提示信息
            if output.get("info"):
                for info_msg in output["info"]:
                    print(f"  [INFO] {info_msg}")


if __name__ == "__main__":
    main()
