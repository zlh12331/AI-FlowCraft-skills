#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试辅助脚本 - 公共模块
功能：提供所有脚本共享的工具函数（JSON 读写、路径验证、技术栈检测等）
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


def detect_tech_stack(project_path: Path) -> List[str]:
    """
    检测项目技术栈（统一实现，供 scan 和 run 脚本共用）

    Args:
        project_path: 项目根目录

    Returns:
        list: 技术栈列表
    """
    stack: List[str] = []

    # Node.js 项目
    pkg = project_path / "package.json"
    if pkg.exists():
        content = pkg.read_text(encoding="utf-8", errors="ignore")
        # 使用更精确的匹配，避免误匹配（如 "express" 不匹配 "express-middleware"）
        frameworks = {
            "express": r'\bexpress\b',
            "koa": r'\bkoa\b',
            "fastify": r'\bfastify\b',
            "nestjs": r'@nestjs',
            "hapi": r'@hapi/hapi',
            "prisma": r'\bprisma\b',
            "sequelize": r'\bsequelize\b',
            "mongoose": r'\bmongoose\b',
            "typeorm": r'\btypeorm\b',
        }
        for name, pattern in frameworks.items():
            if re.search(pattern, content):
                stack.append(name)

    # Python 项目
    for req_file in ["requirements.txt", "pyproject.toml", "setup.py"]:
        req_path = project_path / req_file
        if req_path.exists():
            content = req_path.read_text(encoding="utf-8", errors="ignore")
            py_frameworks = {
                "flask": r'\bflask\b',
                "django": r'\bdjango\b',
                "fastapi": r'\bfastapi\b',
                "sqlalchemy": r'\bsqlalchemy\b',
                "pymongo": r'\bpymongo\b',
                "redis": r'\bredis\b',
            }
            for fw, pattern in py_frameworks.items():
                if re.search(pattern, content):
                    stack.append(fw)
            break

    # Java 项目
    for build_file in ["pom.xml", "build.gradle"]:
        build_path = project_path / build_file
        if build_path.exists():
            content = build_path.read_text(encoding="utf-8", errors="ignore")
            java_frameworks = {
                "spring-boot": r'\bspring-boot\b',
                "mybatis": r'\bmybatis\b',
                "hibernate": r'\bhibernate\b',
                "jpa": r'\bjpa\b',
            }
            for fw, pattern in java_frameworks.items():
                if re.search(pattern, content):
                    stack.append(fw)
            break

    # Go 项目
    go_mod = project_path / "go.mod"
    if go_mod.exists():
        content = go_mod.read_text(encoding="utf-8", errors="ignore")
        go_frameworks = {
            "gin": r'\bgin\b',
            "echo": r'\becho\b',
            "gorm": r'\bgorm\b',
            "sqlx": r'\bsqlx\b',
        }
        for fw, pattern in go_frameworks.items():
            if re.search(pattern, content):
                stack.append(fw)

    return stack if stack else ["unknown"]
