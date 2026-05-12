#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E 测试辅助脚本 - 公共模块
功能：提供所有脚本共享的工具函数（JSON 读写、路径验证、前端框架检测等）
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_json(file_path: str) -> Dict[str, Any]:
    """
    从 JSON 文件加载数据

    Args:
        file_path: JSON 文件路径

    Returns:
        dict: 解析后的字典

    Raises:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON 格式错误
        IOError: IO 错误
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Any, file_path: str, indent: int = 2) -> None:
    """
    将数据保存为 JSON 文件

    Args:
        data: 要保存的数据
        file_path: 输出文件路径
        indent: 缩进空格数

    Raises:
        TypeError: 数据不可序列化
        IOError: IO 错误
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def validate_project_path(project_path: str) -> Path:
    """
    验证项目路径是否存在且安全（防止路径遍历）

    Args:
        project_path: 项目根目录路径

    Returns:
        Path: 解析后的 Path 对象

    Raises:
        ValueError: 路径不存在或包含路径遍历
    """
    p = Path(project_path).resolve()

    # 路径遍历防护：检查解析后的路径是否在合理范围内
    if ".." in Path(project_path).parts:
        raise ValueError(f"路径包含非法遍历组件: {project_path}")

    if not p.exists():
        raise ValueError(f"路径不存在: {project_path}")

    if not p.is_dir():
        raise ValueError(f"路径不是目录: {project_path}")

    return p


def detect_framework(project_path: Path) -> str:
    """
    检测前端框架（统一实现，供 scan 和 run 脚本共用）

    Args:
        project_path: 项目根目录

    Returns:
        str: 框架标识（react/nextjs/vue/nuxtjs/angular/svelte/unknown）
    """
    pkg = project_path / "package.json"
    if not pkg.exists():
        # 无 package.json 时通过文件扩展名推断
        if list(project_path.rglob("*.vue")):
            return "vue"
        if list(project_path.rglob("*.svelte")):
            return "svelte"
        return "unknown"

    content = pkg.read_text(encoding="utf-8", errors="ignore")
    # 使用更精确的匹配，避免误匹配
    if re.search(r'\breact\b', content) and re.search(r'\bnext\b', content):
        return "nextjs"
    if re.search(r'\breact\b', content):
        return "react"
    if re.search(r'\bvue\b', content) and re.search(r'\bnuxt\b', content):
        return "nuxtjs"
    if re.search(r'\bvue\b', content):
        return "vue"
    if re.search(r'\bangular\b', content):
        return "angular"
    return "unknown"
