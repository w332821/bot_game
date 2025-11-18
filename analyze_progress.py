#!/usr/bin/env python3
"""
分析项目完成进度
对比 API_DOCS(3).md 中定义的接口与实际实现
"""

import re
import os
from pathlib import Path

# 从 API_DOCS 中要求的51个接口
REQUIRED_APIS = [
    "POST /auth/login",
    "POST /auth/logout",
    "GET /home/online-count",
    "GET /home/online-trend",
    "GET /users/members",
    "POST /users/members",
    "PUT /users/members/:id",
    "GET /users/members/:account",
    "GET /users/members/:account/login-log",
    "GET /users/members/:account/bet-orders",
    "GET /users/members/:account/transactions",
    "GET /users/members/:account/account-changes",
    "GET /users/agents",
    "POST /users/agents",
    "PUT /users/agents/:id",
    "GET /users/agents/:account",
    "GET /users/agents/:account/login-log",
    "GET /users/agents/:account/members",
    "GET /users/agents/:account/transactions",
    "GET /users/agents/:account/account-changes",
    "GET /users/rebate/:account",
    "PUT /users/rebate/:account",
    "GET /personal/basic",
    "PUT /personal/basic",
    "POST /personal/promote/domain",
    "GET /personal/lottery-rebate-config",
    "PUT /personal/lottery-rebate-config",
    "GET /personal/login-log",
    "PUT /personal/password",
    "GET /roles",
    "GET /roles/:id",
    "POST /roles",
    "PUT /roles/:id",
    "DELETE /roles/:id",
    "GET /roles/permissions",
    "GET /roles/sub-accounts",
    "POST /roles/sub-accounts",
    "PUT /roles/sub-accounts/:id",
    "DELETE /roles/sub-accounts/:id",
    "GET /reports/financial-summary",
    "GET /reports/financial",
    "GET /reports/win-loss",
    "GET /reports/agent-win-loss",
    "GET /reports/deposit-withdrawal",
    "GET /reports/category",
    "GET /reports/downline-details",
    "POST /reports/financial-summary/recalculate",
    "GET /reports/export/:type",
    "GET /lottery/results",
    "GET /lottery/results/:id",
    "GET /health",
]

def extract_routes_from_file(file_path):
    """从Python文件中提取路由定义"""
    routes = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 首先提取路由的prefix
        prefix_pattern = r'router\s*=\s*APIRouter\(.*?prefix=["\']([^"\']+)["\']'
        prefix_match = re.search(prefix_pattern, content)
        prefix = prefix_match.group(1) if prefix_match else ""

        # 匹配 @router.get("/path") 等装饰器
        route_pattern = r'@router\.(get|post|put|delete)\(["\']([^"\']+)["\']\)'
        matches = re.findall(route_pattern, content)

        for method, path in matches:
            # 组合prefix和path
            full_path = prefix + path if path != "/" else prefix
            routes.append(f"{method.upper()} {full_path}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return routes

def scan_api_files():
    """扫描所有API文件"""
    api_dir = Path("/Users/demean5/Desktop/bot_game/biz")
    all_routes = []

    for api_file in api_dir.rglob("*_api.py"):
        routes = extract_routes_from_file(api_file)
        for route in routes:
            all_routes.append((route, api_file.relative_to(api_dir)))

    return all_routes

def normalize_path(path):
    """标准化路径，统一参数格式"""
    # 将 {id} 转换为 :id
    path = re.sub(r'\{([^}]+)\}', r':\1', path)
    # 确保以 / 开头
    if not path.startswith('/'):
        path = '/' + path
    # 确保有 /api 前缀的去掉（统一比较）
    path = path.replace('/api/', '/')
    return path

def compare_routes():
    """比较要求的API与实际实现"""
    implemented_routes = scan_api_files()

    # Debug: 打印前几个实现的路由
    print("\n🔍 调试信息 - 实际实现的路由示例:")
    for route, file_path in implemented_routes[:10]:
        print(f"  {route}")
    print()

    # 创建已实现路由的集合（标准化后）
    implemented_set = {}
    for route, file_path in implemented_routes:
        method, path = route.split(' ', 1)
        normalized = normalize_path(path)
        key = f"{method} {normalized}"
        implemented_set[key] = file_path

    # Debug: 打印前几个标准化后的key
    print("🔍 调试信息 - 标准化后的路由示例:")
    for key in list(implemented_set.keys())[:10]:
        print(f"  {key}")
    print()

    print("=" * 80)
    print("📊 API 实现进度分析")
    print("=" * 80)
    print()

    # 检查每个要求的API
    implemented = []
    not_implemented = []

    for required in REQUIRED_APIS:
        method, path = required.split(' ', 1)
        normalized = normalize_path(path)
        key = f"{method} {normalized}"

        if key in implemented_set:
            implemented.append((required, implemented_set[key]))
        else:
            not_implemented.append(required)

    # 输出结果
    print(f"✅ 已实现: {len(implemented)}/{len(REQUIRED_APIS)} ({len(implemented)*100//len(REQUIRED_APIS)}%)")
    print(f"❌ 未实现: {len(not_implemented)}/{len(REQUIRED_APIS)}")
    print()

    if implemented:
        print("=" * 80)
        print("✅ 已实现的接口:")
        print("=" * 80)
        for api, file_path in sorted(implemented):
            print(f"  ✓ {api:<50} [{file_path}]")
        print()

    if not_implemented:
        print("=" * 80)
        print("❌ 未实现的接口:")
        print("=" * 80)
        for api in sorted(not_implemented):
            print(f"  ✗ {api}")
        print()

    # 分析未实现接口的模块分布
    if not_implemented:
        module_count = {}
        for api in not_implemented:
            module = api.split('/')[1] if len(api.split('/')) > 1 else 'other'
            module_count[module] = module_count.get(module, 0) + 1

        print("=" * 80)
        print("📈 未实现接口按模块分布:")
        print("=" * 80)
        for module, count in sorted(module_count.items(), key=lambda x: -x[1]):
            print(f"  {module}: {count} 个接口")
        print()

    return len(implemented), len(REQUIRED_APIS)

if __name__ == '__main__':
    implemented_count, total_count = compare_routes()
    print("=" * 80)
    print(f"📊 完成度: {implemented_count}/{total_count} ({implemented_count*100//total_count}%)")
    print("=" * 80)
