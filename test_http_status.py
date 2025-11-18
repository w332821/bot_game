#!/usr/bin/env python
"""快速测试HTTP状态码映射"""
import sys
sys.path.insert(0, '/Users/demean5/Desktop/bot_game')

from base.api import error_response
from base.error_codes import ErrorCode
import json

print("🧪 测试HTTP状态码映射\n")

# 测试1: 认证错误 -> 401
response = error_response(ErrorCode.ACCOUNT_OR_PASSWORD_ERROR, "密码错误")
print(f"✅ 测试1: 认证错误")
print(f"   HTTP状态码: {response.status_code} (期望: 401)")
body = json.loads(response.body.decode())
print(f"   响应body: {body}")
assert response.status_code == 401, "认证错误应返回401"
print()

# 测试2: 账户禁用 -> 403
response = error_response(ErrorCode.ACCOUNT_DISABLED, "账户禁用")
print(f"✅ 测试2: 账户禁用")
print(f"   HTTP状态码: {response.status_code} (期望: 403)")
body = json.loads(response.body.decode())
print(f"   响应body: {body}")
assert response.status_code == 403, "账户禁用应返回403"
print()

# 测试3: 数据验证错误 -> 400
response = error_response(ErrorCode.ACCOUNT_ALREADY_EXISTS, "账户已存在")
print(f"✅ 测试3: 数据验证错误")
print(f"   HTTP状态码: {response.status_code} (期望: 400)")
body = json.loads(response.body.decode())
print(f"   响应body: {body}")
assert response.status_code == 400, "数据验证错误应返回400"
print()

# 测试4: 数据不存在 -> 404
response = error_response(ErrorCode.DATA_NOT_FOUND, "数据不存在")
print(f"✅ 测试4: 数据不存在")
print(f"   HTTP状态码: {response.status_code} (期望: 404)")
body = json.loads(response.body.decode())
print(f"   响应body: {body}")
assert response.status_code == 404, "数据不存在应返回404"
print()

# 测试5: 内部错误 -> 500
response = error_response(ErrorCode.INTERNAL_ERROR, "服务器错误")
print(f"✅ 测试5: 内部错误")
print(f"   HTTP状态码: {response.status_code} (期望: 500)")
body = json.loads(response.body.decode())
print(f"   响应body: {body}")
assert response.status_code == 500, "内部错误应返回500"
print()

print("=" * 50)
print("🎉 所有测试通过！HTTP状态码映射正确！")
print("=" * 50)
