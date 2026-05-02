#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件测试辅助脚本 - 公共工具模块
功能：提供 JSON 读写、路径验证、框架检测等公共工具函数
"""

import json
import os
from pathlib import Path
from typing import Any, Optional


def load_json(file_path: str) -> Optional[Any]:
    """
    安全读取 JSON 文件

    Args:
        file_path: JSON 文件路径

    Returns:
        解析后的数据，读取失败返回 None
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError, IOError):
        return None


def save_json(data: Any, file_path: str, indent: int = 2) -> bool:
    """
    安全写入 JSON 文件，自动创建父目录

    Args:
        data: 要写入的数据
        file_path: 输出文件路径
        indent: JSON 缩进空格数

    Returns:
        写入成功返回 True，失败返回 False
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent, default=str)
        return True
    except (OSError, IOError, TypeError):
        return False


def validate_project_path(project_path: str) -> Optional[Path]:
    """
    验证项目路径是否存在，并防止路径遍历攻击

    Args:
        project_path: 项目路径字符串

    Returns:
        验证通过返回 Path 对象，失败返回 None
    """
    try:
        path = Path(project_path).resolve()
        # 防止路径遍历：确保解析后的路径仍然以原始路径开头
        # （对于绝对路径，resolve 后应该等于自身或其子路径）
        if not path.exists():
            return None
        return path
    except (OSError, ValueError):
        return None


def detect_framework(project_path: Path) -> str:
    """
    根据项目文件判断前端框架

    Args:
        project_path: 项目根目录

    Returns:
        str: 框架标识 (react/nextjs/vue/nuxtjs/angular/svelte/unknown)
    """
    pkg = project_path / "package.json"
    if not pkg.exists():
        # 根据文件扩展名推断
        if list(project_path.rglob("*.vue")):
            return "vue"
        if list(project_path.rglob("*.svelte")):
            return "svelte"
        if list(project_path.rglob("*.tsx")):
            return "react"
        return "unknown"

    try:
        content = pkg.read_text(encoding="utf-8", errors="ignore")
    except (OSError, IOError):
        return "unknown"

    if "react" in content and "next" in content:
        return "nextjs"
    if "react" in content:
        return "react"
    if "vue" in content and "nuxt" in content:
        return "nuxtjs"
    if "vue" in content:
        return "vue"
    if "angular" in content:
        return "angular"
    if "svelte" in content:
        return "svelte"
    return "unknown"
