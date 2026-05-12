#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试辅助脚本 - 公共模块
提供 JSON 读写、路径验证、错误处理等公共功能，
供 scan_system.py、generate_system_tests.py、run_system_tests.py、generate_report.py 共用。
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def load_json(file_path: str) -> Dict[str, Any]:
    """
    从 JSON 文件加载数据，统一处理各类异常

    Args:
        file_path: JSON 文件路径

    Returns:
        dict: 解析后的字典

    Raises:
        SystemExit: 文件不存在、解析失败或读取错误时退出
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误：文件不存在 - {file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误：JSON 解析失败 - {e}", file=sys.stderr)
        sys.exit(1)
    except (IOError, OSError) as e:
        print(f"错误：无法读取文件 {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def load_json_safe(file_path: str) -> Optional[Dict[str, Any]]:
    """
    安全加载 JSON 文件，失败时返回 None 而非退出

    用于可选的配置文件（如扫描结果），失败时降级处理。

    Args:
        file_path: JSON 文件路径

    Returns:
        dict 或 None: 解析成功返回字典，失败返回 None
    """
    if not Path(file_path).exists():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError, OSError) as e:
        print(f"警告：读取 {file_path} 失败，将跳过 - {e}", file=sys.stderr)
        return None


def save_json(data: Any, output_path: str, exit_on_error: bool = False) -> bool:
    """
    将数据保存为 JSON 文件

    Args:
        data: 要保存的数据（需可 JSON 序列化）
        output_path: 输出文件路径
        exit_on_error: 是否在错误时调用 sys.exit(1)

    Returns:
        bool: 保存是否成功
    """
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return True
    except (IOError, OSError) as e:
        print(f"错误：无法写入文件 {output_path}: {e}", file=sys.stderr)
    except (TypeError, ValueError) as e:
        print(f"错误：数据序列化失败: {e}", file=sys.stderr)

    if exit_on_error:
        sys.exit(1)
    return False


def validate_project_path(project_path: str) -> Optional[Path]:
    """
    验证项目路径是否为有效目录

    Args:
        project_path: 待验证的路径字符串

    Returns:
        Path 或 None: 验证通过返回解析后的 Path，否则返回 None
    """
    path = Path(project_path).resolve()
    if not path.exists():
        print(f"错误：路径不存在 - {path}", file=sys.stderr)
        return None
    if not path.is_dir():
        print(f"错误：路径不是目录 - {path}", file=sys.stderr)
        return None
    return path


def read_file_content(file_path: Path) -> str:
    """
    安全读取文件内容，处理编码和 IO 异常

    Args:
        file_path: 文件路径

    Returns:
        str: 文件内容，读取失败返回空字符串
    """
    try:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    except (IOError, OSError):
        return ""
