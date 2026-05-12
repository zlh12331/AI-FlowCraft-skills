#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试辅助脚本 - 系统架构扫描器
功能：扫描项目中的服务组件、外部集成、配置文件、安全相关配置
用法：python scan_system.py <项目路径> [输出JSON路径]
"""

import sys
import re
from pathlib import Path

from common import (
    save_json,
    validate_project_path,
    read_file_content,
)


def scan_project(project_path: str) -> dict:
    """
    扫描项目目录，识别系统架构和组件

    Args:
        project_path: 项目根目录路径

    Returns:
        dict: 系统架构信息；路径无效时返回空字典
    """
    # 路径安全检查：规范化并验证路径
    path = validate_project_path(project_path)
    if path is None:
        return {}

    # 扫描各类组件
    services = scan_services(path)
    database = scan_database(path)
    cache = scan_cache(path)
    message_queues = scan_message_queues(path)
    external_integrations = scan_external_integrations(path)
    configs = scan_configs(path)
    security = scan_security(path)
    env_vars = scan_env_vars(path)

    # 汇总组件列表（为每个组件添加 category 标签）
    category_map = [
        (services, "service"),
        (database, "database"),
        (cache, "cache"),
        (message_queues, "message_queue"),
        (external_integrations, "external"),
    ]
    all_components = []
    for items, category in category_map:
        for item in items:
            item["category"] = category
            all_components.append(item)

    result = {
        "services_count": len(services),
        "database_count": len(database),
        "cache_count": len(cache),
        "message_queue_count": len(message_queues),
        "external_count": len(external_integrations),
        "config_files": configs,
        "security_findings": security,
        "env_vars": env_vars,
        "components": all_components,
    }

    # 输出扫描摘要
    _print_scan_summary(services, database, cache, message_queues,
                        external_integrations, configs, security, env_vars)

    return result


def _print_scan_summary(services, database, cache, message_queues,
                        external_integrations, configs, security, env_vars):
    """打印扫描结果摘要到 stdout"""
    print("系统架构扫描结果:")
    print(f"  服务组件: {len(services)}")
    print(f"  数据库: {len(database)}")
    print(f"  缓存: {len(cache)}")
    print(f"  消息队列: {len(message_queues)}")
    print(f"  外部集成: {len(external_integrations)}")
    print(f"  配置文件: {len(configs)}")
    print(f"  安全发现: {len(security)}")
    print(f"  环境变量: {len(env_vars)} 个")

    # 打印各分类详情
    _print_component_list("服务列表", services, lambda s: f"  {s['name']} ({s.get('file', '-')})")
    _print_component_list("数据库", database, lambda d: f"  {d['name']} ({d.get('type', '-')})")
    _print_component_list("外部集成", external_integrations,
                          lambda e: f"  {e['name']} ({e.get('file', '-')})")
    _print_component_list("消息队列", message_queues,
                          lambda mq: f"  {mq['name']} ({mq.get('file', '-')})")

    if security:
        print("\n安全发现:")
        for sec in security:
            icon = '🔴' if sec.get('severity') == 'high' else '🟡'
            print(f"  {icon} {sec['name']}: {sec['detail']}")


def _print_component_list(title, items, formatter):
    """打印组件列表（仅在有内容时输出）"""
    if items:
        print(f"\n{title}:")
        for item in items:
            print(formatter(item))


def scan_services(project_path: Path) -> list:
    """
    扫描项目中的服务组件

    Args:
        project_path: 项目根目录

    Returns:
        list: 服务信息列表
    """
    services = []

    # 前端服务（从 package.json 检测）
    pkg = project_path / "package.json"
    if pkg.exists():
        content = read_file_content(pkg)
        # 前端框架关键词映射
        frontend_keywords = {
            "react": "Frontend (React)",
            "vue": "Frontend (Vue)",
            "next": "Frontend (Next.js)",
            "nuxt": "Frontend (Nuxt.js)",
            "svelte": None,  # 特殊处理
        }
        for keyword, name in frontend_keywords.items():
            if keyword == "svelte":
                # Svelte 需要匹配 svelte 或 @sveltejs/kit
                if "svelte" in content or "@sveltejs/kit" in content:
                    services.append({"name": "Frontend (Svelte)", "file": "package.json", "type": "frontend"})
            elif keyword in content:
                services.append({"name": name, "file": "package.json", "type": "frontend"})

        # 后端框架关键词映射
        backend_keywords = {
            "express": "Backend (Express)",
            "nestjs": "Backend (NestJS)",
            "fastify": "Backend (Fastify)",
        }
        for keyword, name in backend_keywords.items():
            if keyword in content:
                services.append({"name": name, "file": "package.json", "type": "backend"})

    # Python 后端（从 requirements.txt 或 pyproject.toml 检测）
    _scan_python_backend(project_path, services)

    # Java 后端（从 pom.xml 或 build.gradle 检测）
    _scan_java_backend(project_path, services)

    # Go 后端
    if (project_path / "go.mod").exists():
        services.append({"name": "Backend (Go)", "file": "go.mod", "type": "backend"})

    # Rust 后端
    if (project_path / "Cargo.toml").exists():
        services.append({"name": "Backend (Rust)", "file": "Cargo.toml", "type": "backend"})

    # C# 后端（从 .csproj 或 .sln 检测）
    _scan_csharp_backend(project_path, services)

    # Docker 服务（从 docker-compose.yml 检测）
    _scan_docker_services(project_path, services)

    # Nginx 代理
    for nginx_file in ["nginx.conf", "nginx/nginx.conf"]:
        if (project_path / nginx_file).exists():
            services.append({"name": "Reverse Proxy (Nginx)", "file": nginx_file, "type": "proxy"})
            break

    return services


def _scan_python_backend(project_path: Path, services: list):
    """扫描 Python 后端服务"""
    for req_file in ["requirements.txt", "pyproject.toml"]:
        req_path = project_path / req_file
        if not req_path.exists():
            continue
        content = read_file_content(req_path)
        python_keywords = {
            "flask": "Backend (Flask)",
            "django": "Backend (Django)",
            "fastapi": "Backend (FastAPI)",
        }
        for keyword, name in python_keywords.items():
            if keyword in content:
                services.append({"name": name, "file": req_file, "type": "backend"})
        break  # 只检查第一个存在的文件


def _scan_java_backend(project_path: Path, services: list):
    """扫描 Java 后端服务"""
    for build_file in ["pom.xml", "build.gradle"]:
        if (project_path / build_file).exists():
            services.append({"name": "Backend (Java/Spring)", "file": build_file, "type": "backend"})
            break


def _scan_csharp_backend(project_path: Path, services: list):
    """扫描 C# 后端服务"""
    csproj_files = list(project_path.glob("*.csproj"))
    if csproj_files:
        services.append({"name": "Backend (C#/.NET)", "file": csproj_files[0].name, "type": "backend"})
        return
    sln_files = list(project_path.glob("*.sln"))
    if sln_files:
        services.append({"name": "Backend (C#/.NET)", "file": sln_files[0].name, "type": "backend"})


def _scan_docker_services(project_path: Path, services: list):
    """扫描 Docker Compose 中的服务"""
    docker_compose = project_path / "docker-compose.yml"
    if not docker_compose.exists():
        return
    content = read_file_content(docker_compose)
    # 提取服务名（跳过 YAML 顶层关键字）
    skip_names = {"version", "services", "volumes", "networks"}
    svc_matches = re.findall(r"^\s+(\w+):\s*$", content, re.MULTILINE)
    for svc_name in svc_matches:
        if svc_name not in skip_names:
            services.append({"name": f"Docker: {svc_name}", "file": "docker-compose.yml", "type": "docker"})


def scan_database(project_path: Path) -> list:
    """
    扫描项目中的数据库配置

    Args:
        project_path: 项目根目录

    Returns:
        list: 数据库信息列表
    """
    databases = []

    # 从配置文件检测数据库类型
    check_files = [
        "docker-compose.yml", ".env", ".env.example", ".env.local",
        "prisma/schema.prisma", "config/database.py", "config/database.ts",
    ]
    # 数据库关键词映射（关键词 -> (名称, 类型)）
    db_keywords = {
        "mysql": ("MySQL", "relational"),
        "postgres": ("PostgreSQL", "relational"),
        "mongodb": ("MongoDB", "document"),
        "redis": ("Redis", "cache"),
        "sqlite": ("SQLite", "relational"),
        "elasticsearch": ("Elasticsearch", "search"),
    }

    for cf in check_files:
        fp = project_path / cf
        if not fp.exists():
            continue
        content = read_file_content(fp).lower()

        for keyword, (name, db_type) in db_keywords.items():
            if keyword in content and not any(d["name"] == name for d in databases):
                databases.append({"name": name, "type": db_type, "file": cf})

    # 从 ORM 依赖检测
    pkg = project_path / "package.json"
    if pkg.exists():
        content = read_file_content(pkg)
        orm_keywords = {
            "prisma": "Prisma DB",
            "sequelize": "Sequelize DB",
            "mongoose": "Mongoose DB",
        }
        for keyword, name in orm_keywords.items():
            if keyword in content and not any(d["name"] == name for d in databases):
                databases.append({"name": name, "type": "orm", "file": "package.json"})

    return databases


def scan_cache(project_path: Path) -> list:
    """
    扫描项目中的缓存配置

    Args:
        project_path: 项目根目录

    Returns:
        list: 缓存信息列表
    """
    caches = []
    check_files = ["docker-compose.yml", ".env", ".env.example", "package.json", "requirements.txt"]
    # 缓存关键词映射
    cache_keywords = {
        "redis": "Redis",
        "memcached": "Memcached",
    }

    for cf in check_files:
        fp = project_path / cf
        if not fp.exists():
            continue
        content = read_file_content(fp).lower()

        for keyword, name in cache_keywords.items():
            if keyword in content and not any(c["name"] == name for c in caches):
                caches.append({"name": name, "file": cf})

    return caches


def scan_message_queues(project_path: Path) -> list:
    """
    扫描项目中的消息队列配置

    Args:
        project_path: 项目根目录

    Returns:
        list: 消息队列信息列表
    """
    queues = []
    check_files = ["docker-compose.yml", ".env", ".env.example", "package.json",
                   "requirements.txt", "pyproject.toml", "go.mod", "Cargo.toml"]

    # 消息队列关键词映射（支持正则）
    mq_keywords = {
        "rabbitmq": "RabbitMQ",
        "amqp": "RabbitMQ (AMQP)",
        "kafka": "Apache Kafka",
        "nats": "NATS",
        "redis.*stream": "Redis Streams",
        "bull": "Bull (Redis Queue)",
        "celery": "Celery (Python Queue)",
        "sidekiq": "Sidekiq (Ruby Queue)",
        "activemq": "ActiveMQ",
        "sqs": "AWS SQS",
        "pubsub": "Google Pub/Sub",
        "eventhub": "Azure Event Hub",
    }

    for cf in check_files:
        fp = project_path / cf
        if not fp.exists():
            continue
        content = read_file_content(fp).lower()

        for keyword, name in mq_keywords.items():
            if re.search(keyword, content) and not any(q["name"] == name for q in queues):
                queues.append({"name": name, "file": cf})

    return queues


def scan_external_integrations(project_path: Path) -> list:
    """
    扫描项目中的外部服务集成

    Args:
        project_path: 项目根目录

    Returns:
        list: 外部服务信息列表
    """
    integrations = []

    # 外部服务关键词映射
    service_keywords = {
        "stripe": "Stripe (支付)",
        "paypal": "PayPal (支付)",
        "razorpay": "Razorpay (支付)",
        "alipay": "支付宝",
        "wechatpay": "微信支付",
        "aws-sdk": "AWS",
        "firebase": "Firebase",
        "supabase": "Supabase",
        "sendgrid": "SendGrid (邮件)",
        "nodemailer": "Nodemailer (邮件)",
        "twilio": "Twilio (短信)",
        "s3": "AWS S3 (存储)",
        "cloudinary": "Cloudinary (图片)",
        "googleapis": "Google API",
        "facebook": "Facebook API",
        "github": "GitHub API",
        "oauth": "OAuth (认证)",
        "jwt": "JWT (认证)",
        "sentry": "Sentry (监控)",
        "datadog": "Datadog (监控)",
        "elasticsearch": "Elasticsearch (搜索)",
        "openai": "OpenAI (AI)",
        "anthropic": "Anthropic (AI)",
        "langchain": "LangChain (AI)",
        "redis": "Redis Cloud",
        "upstash": "Upstash (Redis)",
        "vercel": "Vercel (部署)",
        "netlify": "Netlify (部署)",
        "docker": "Docker (容器)",
        "kubernetes": "Kubernetes (编排)",
        "grafana": "Grafana (监控)",
        "prometheus": "Prometheus (监控)",
        "loki": "Loki (日志)",
        "minio": "MinIO (存储)",
        "cloudflare": "Cloudflare (CDN)",
    }

    # 扫描依赖文件
    dep_files = ["package.json", "requirements.txt", "pyproject.toml", "go.mod"]
    for dep_file in dep_files:
        fp = project_path / dep_file
        if not fp.exists():
            continue
        content = read_file_content(fp).lower()

        for keyword, name in service_keywords.items():
            if keyword in content and not any(i["name"] == name for i in integrations):
                integrations.append({"name": name, "file": dep_file, "keyword": keyword})

    return integrations


def scan_configs(project_path: Path) -> list:
    """
    扫描项目中的配置文件

    Args:
        project_path: 项目根目录

    Returns:
        list: 配置文件路径列表
    """
    config_patterns = [
        "docker-compose*.yml", "Dockerfile*", ".env*", "nginx*",
        "tsconfig*.json", "jest.config.*", "vitest.config.*",
        "next.config.*", "vite.config.*", "webpack.config.*",
        ".eslintrc*", ".prettierrc*", "tailwind.config.*",
        "prisma/schema.prisma",
    ]

    configs = []
    for pattern in config_patterns:
        for fp in project_path.glob(pattern):
            if fp.is_file():
                configs.append(str(fp.relative_to(project_path)))

    return sorted(configs)


def scan_security(project_path: Path) -> list:
    """
    扫描项目中的安全相关配置和潜在问题

    Args:
        project_path: 项目根目录

    Returns:
        list: 安全发现列表
    """
    findings = []

    # 检查 .gitignore 是否包含敏感文件模式
    _check_gitignore(project_path, findings)

    # 检查环境变量中的明文密钥
    _check_env_secrets(project_path, findings)

    # 检查 HTTPS 配置
    _check_https_config(project_path, findings)

    # 检查 CORS 配置
    _check_cors_config(project_path, findings)

    # 检查 CSRF 保护
    _check_csrf_protection(project_path, findings)

    # 检查 Rate Limiting
    _check_rate_limiting(project_path, findings)

    # 检查 Python 不安全模块
    _check_python_security(project_path, findings)

    return findings


def _check_gitignore(project_path: Path, findings: list):
    """检查 .gitignore 是否包含敏感文件模式"""
    gitignore = project_path / ".gitignore"
    if not gitignore.exists():
        return
    content = read_file_content(gitignore)
    # 需要忽略的敏感文件模式
    sensitive_patterns = [".env", "*.key", "*.pem", "credentials", "secret"]
    for pattern in sensitive_patterns:
        if pattern not in content:
            findings.append({
                "name": f".gitignore 缺少 {pattern}",
                "severity": "medium",
                "detail": f"敏感文件 {pattern} 可能被提交到版本控制",
            })


def _check_env_secrets(project_path: Path, findings: list):
    """检查环境变量文件中的明文密钥"""
    # 明文密钥检测模式（正则, 描述）
    secret_patterns = [
        (r"password\s*=\s*\S+", "明文密码"),
        (r"secret\s*=\s*\S+", "明文密钥"),
        (r"api_key\s*=\s*\S+", "明文 API Key"),
        (r"private_key\s*=\s*\S+", "明文私钥"),
    ]

    for env_file in [".env", ".env.local", ".env.production"]:
        fp = project_path / env_file
        if not fp.exists():
            continue
        content = read_file_content(fp)
        for pattern, desc in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                findings.append({
                    "name": f"{env_file} 包含{desc}",
                    "severity": "high",
                    "detail": f"在 {env_file} 中发现可能的明文敏感信息",
                })
                break  # 每个文件只报告一次


def _check_https_config(project_path: Path, findings: list):
    """检查 HTTPS 配置"""
    pkg = project_path / "package.json"
    if not pkg.exists():
        return
    content = read_file_content(pkg)
    if "https" not in content.lower() and "ssl" not in content.lower():
        findings.append({
            "name": "未检测到 HTTPS 配置",
            "severity": "medium",
            "detail": "项目可能未配置 HTTPS，生产环境需要 HTTPS",
        })


def _check_cors_config(project_path: Path, findings: list):
    """检查 CORS 配置是否过宽"""
    for src_file in project_path.rglob("*.[jt]s"):
        if "node_modules" in str(src_file):
            continue
        content = read_file_content(src_file)
        if not content:
            continue
        if "cors" in content.lower() and ("*" in content or "Access-Control-Allow-Origin" in content):
            findings.append({
                "name": "CORS 配置可能过宽",
                "severity": "medium",
                "detail": f"在 {src_file.relative_to(project_path)} 中发现可能的通配 CORS 配置",
            })
            break


def _check_csrf_protection(project_path: Path, findings: list):
    """检查 CSRF 保护"""
    csrf_found = _search_in_source_files(project_path, ["csrf", "xsrf"])
    if not csrf_found and (project_path / "package.json").exists():
        findings.append({
            "name": "未检测到 CSRF 保护",
            "severity": "medium",
            "detail": "POST/PUT/DELETE 端点可能缺少 CSRF 令牌验证",
        })


def _check_rate_limiting(project_path: Path, findings: list):
    """检查 Rate Limiting"""
    rate_limit_found = _search_in_source_files(
        project_path,
        ["rate-limit", "ratelimit", "rate_limit", "throttle", "express-rate-limit"],
    )
    if not rate_limit_found and (project_path / "package.json").exists():
        findings.append({
            "name": "未检测到 Rate Limiting",
            "severity": "low",
            "detail": "API 端点可能缺少请求频率限制，易受暴力攻击",
        })


def _search_in_source_files(project_path: Path, keywords: list) -> bool:
    """
    在项目源码文件中搜索关键词

    Args:
        project_path: 项目根目录
        keywords: 要搜索的关键词列表

    Returns:
        bool: 是否找到任一关键词
    """
    for src_file in project_path.rglob("*.[jt]s"):
        if "node_modules" in str(src_file):
            continue
        content = read_file_content(src_file)
        if not content:
            continue
        if any(kw in content.lower() for kw in keywords):
            return True
    return False


def _check_python_security(project_path: Path, findings: list):
    """检查 Python 不安全模块"""
    req_path = project_path / "requirements.txt"
    if not req_path.exists():
        return
    content = read_file_content(req_path).lower()
    dangerous = []
    if "pickle" in content:
        dangerous.append("pickle")
    if "eval(" in content or "exec(" in content:
        dangerous.append("eval/exec")
    if "yaml.load" in content and "yaml.safe_load" not in content:
        dangerous.append("yaml.load (不安全)")
    if dangerous:
        findings.append({
            "name": "Python 依赖使用不安全模块",
            "severity": "high",
            "detail": f"发现不安全的 Python 模块: {', '.join(dangerous)}",
        })


def scan_env_vars(project_path: Path) -> list:
    """
    扫描项目中的环境变量（不读取值，只提取变量名）

    Args:
        project_path: 项目根目录

    Returns:
        list: 环境变量名列表
    """
    env_vars = []
    for env_file in [".env", ".env.example", ".env.local", ".env.staging", ".env.test"]:
        fp = project_path / env_file
        if not fp.exists():
            continue
        content = read_file_content(fp)
        # 匹配大写字母开头的环境变量名（VAR_NAME=value 格式）
        matches = re.findall(r"^([A-Z_][A-Z0-9_]*)\s*=", content, re.MULTILINE)
        for var in matches:
            if var not in env_vars:
                env_vars.append(var)

    return env_vars


def export_json(result: dict, output_path: str):
    """
    将扫描结果导出为 JSON 文件

    Args:
        result: 扫描结果字典
        output_path: 输出文件路径
    """
    if save_json(result, output_path):
        print(f"\n扫描结果已导出到: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scan_system.py <项目路径> [输出JSON路径]")
        print("示例: python scan_system.py /path/to/project result.json")
        sys.exit(1)

    project = sys.argv[1]
    result = scan_project(project)

    if result and len(sys.argv) >= 3:
        export_json(result, sys.argv[2])
