from __future__ import annotations

"""
公共模块 — test-unit 各脚本共享的工具函数和常量

消除 scan_source.py、generate_tests.py、run_tests.py、generate_report.py 之间的代码重复。
"""

import json
from pathlib import Path
from typing import Any, Optional


# ============================================================
# 常量定义
# ============================================================

# 通用排除目录（所有语言共享）
COMMON_SKIP_DIRS = {".git", "node_modules"}

# 各语言额外的排除目录
LANGUAGE_SKIP_DIRS = {
    "js/ts": {".next", ".nuxt", "dist", "build", "coverage", "__pycache__"},
    "python": {"__pycache__", "venv", ".venv", "env", "dist", "build", "coverage"},
    "java": {"target", "build", ".idea"},
    "go": {"vendor"},
    "rust": {"target"},
    "csharp": {"bin", "obj", ".vs", "TestResults"},
}

# 子进程超时常量（秒）
DEFAULT_TIMEOUT = 300
COMPILE_TIMEOUT = 600

# JS 项目类型集合
JS_PROJECT_TYPES = {"javascript", "typescript", "nextjs", "react", "vue", "nuxtjs", "angular", "svelte"}



# ============================================================
# 项目类型检测（统一实现）
# ============================================================

def detect_project_type(project_path: str) -> str:
    """
    根据项目文件判断项目类型

    统一实现，供 scan_source.py 和 run_tests.py 共同引用。
    接受 str 类型参数，内部转换为 Path。

    Args:
        project_path: 项目根目录（str 或 Path 均可）

    Returns:
        str: 项目类型标识（nextjs/react/vue/nuxtjs/angular/svelte/
             javascript/python/java/go/rust/csharp/unknown）
    """
    p = Path(project_path)

    # 检查前端项目
    if (p / "package.json").exists():
        content = (p / "package.json").read_text(encoding="utf-8", errors="ignore")
        if "react" in content and "next" in content:
            return "nextjs"
        if "nuxt" in content:
            return "nuxtjs"
        if "svelte" in content or "@sveltejs/kit" in content:
            return "svelte"
        if "@angular/core" in content or "@angular/cli" in content:
            return "angular"
        if "vue" in content:
            return "vue"
        if "react" in content:
            return "react"
        return "javascript"

    # 检查 Python 项目
    if ((p / "requirements.txt").exists() or
            (p / "pyproject.toml").exists() or
            (p / "setup.py").exists()):
        return "python"

    # 检查 Java 项目
    if ((p / "pom.xml").exists() or
            (p / "build.gradle").exists() or
            (p / "build.gradle.kts").exists()):
        return "java"

    # 检查 Go 项目
    if (p / "go.mod").exists():
        return "go"

    # 检查 Rust 项目
    if (p / "Cargo.toml").exists():
        return "rust"

    # 检查 C# 项目
    if list(p.glob("*.csproj")) or list(p.glob("*.sln")):
        return "csharp"

    # 根据 src 目录中的文件扩展名推断
    for ext, ptype in [(".py", "python"), (".js", "javascript"), (".ts", "typescript"),
                        (".java", "java"), (".go", "go"), (".rs", "rust"), (".cs", "csharp")]:
        if next(p.rglob(f"*{ext}"), None) is not None:
            return ptype

    return "unknown"


# ============================================================
# JSON 读写工具
# ============================================================

def write_json(data: Any, output_path: str) -> None:
    """
    安全写入 JSON 文件（自动创建父目录）

    Args:
        data: 要写入的数据（必须是 JSON 可序列化的）
        output_path: 输出文件路径
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    except OSError as e:
        print(f"错误：无法写入文件 {output_path}: {e}")


def load_json(file_path: str) -> Optional[Any]:
    """
    安全读取 JSON 文件（带异常处理）

    Args:
        file_path: JSON 文件路径

    Returns:
        解析后的数据，失败时返回 None
    """
    path = Path(file_path)
    if not path.exists():
        print(f"错误：文件不存在: {file_path}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"错误：无法读取文件 {file_path}: {e}")
        return None


# ============================================================
# 路径工具
# ============================================================

def get_skip_dirs(language: str) -> set[str]:
    """
    获取指定语言的完整排除目录集合（通用 + 语言特定）

    Args:
        language: 语言标识（js/ts, python, java, go, rust, csharp）

    Returns:
        set: 完整的排除目录集合
    """
    dirs = COMMON_SKIP_DIRS.copy()
    dirs.update(LANGUAGE_SKIP_DIRS.get(language, set()))
    return dirs
