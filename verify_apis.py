#!/usr/bin/env python3
"""验证所有51个API是否实现"""
from biz.application import app

# 所需的51个API
REQUIRED = [
    "POST /api/auth/login",
    "POST /api/auth/logout",
    "GET /api/home/online-count",
    "GET /api/home/online-trend",
    "GET /api/users/members",
    "POST /api/users/members",
    "PUT /api/users/members/{member_id}",
    "GET /api/users/members/{account}",
    "GET /api/users/members/{account}/login-log",
    "GET /api/users/members/{account}/bet-orders",
    "GET /api/users/members/{account}/transactions",
    "GET /api/users/members/{account}/account-changes",
    "GET /api/users/agents",
    "POST /api/users/agents",
    "PUT /api/users/agents/{agent_id}",
    "GET /api/users/agents/{account}",
    "GET /api/users/agents/{account}/login-log",
    "GET /api/users/agents/{account}/members",
    "GET /api/users/agents/{account}/transactions",
    "GET /api/users/agents/{account}/account-changes",
    "GET /api/users/rebate/{account}",
    "PUT /api/users/rebate/{account}",
    "GET /api/personal/basic",
    "PUT /api/personal/basic",
    "POST /api/personal/promote/domain",
    "GET /api/personal/lottery-rebate-config",
    "PUT /api/personal/lottery-rebate-config",
    "GET /api/personal/login-log",
    "PUT /api/personal/password",
    "GET /api/roles",
    "GET /api/roles/{role_id}",
    "POST /api/roles",
    "PUT /api/roles/{role_id}",
    "DELETE /api/roles/{role_id}",
    "GET /api/roles/permissions",
    "GET /api/roles/sub-accounts",
    "POST /api/roles/sub-accounts",
    "PUT /api/roles/sub-accounts/{sub_id}",
    "DELETE /api/roles/sub-accounts/{sub_id}",
    "GET /api/reports/financial-summary",
    "GET /api/reports/financial",
    "GET /api/reports/win-loss",
    "GET /api/reports/agent-win-loss",
    "GET /api/reports/deposit-withdrawal",
    "GET /api/reports/category",
    "GET /api/reports/downline-details",
    "POST /api/reports/financial-summary/recalculate",
    "GET /api/reports/export/{type}",
    "GET /api/lottery/results",
    "GET /api/lottery/results/{id}",
    "GET /health",
]

# 获取实际路由
actual = set()
for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        for method in route.methods:
            if method in ['GET', 'POST', 'PUT', 'DELETE']:
                actual.add(f"{method} {route.path}")

# 检查每个必需的API
found = []
missing = []
for req in REQUIRED:
    if req in actual:
        found.append(req)
    else:
        missing.append(req)

print(f"\n{'='*80}")
print(f"API实现验证结果")
print(f"{'='*80}\n")
print(f"✅ 已实现: {len(found)}/51 ({len(found)*100//51}%)")
print(f"❌ 未实现: {len(missing)}/51\n")

if missing:
    print(f"{'='*80}")
    print("未实现的API:")
    print(f"{'='*80}")
    for m in missing:
        print(f"  {m}")
    print()
else:
    print("🎉 所有51个API全部实现!")
