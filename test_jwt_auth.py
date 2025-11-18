"""
测试JWT认证功能
"""
import sys
sys.path.insert(0, '.')

from biz.auth.utils.jwt_utils import create_access_token, verify_token

print("=" * 60)
print("JWT认证功能测试")
print("=" * 60)

# 测试1: 生成Token
print("\n1. 测试Token生成...")
test_data = {
    "admin_id": "admin_123",
    "username": "testadmin",
    "role": "super_admin"
}

try:
    token = create_access_token(test_data)
    print(f"✅ Token生成成功")
    print(f"   Token前80字符: {token[:80]}...")
except Exception as e:
    print(f"❌ Token生成失败: {e}")
    sys.exit(1)

# 测试2: 验证Token
print("\n2. 测试Token验证...")
try:
    payload = verify_token(token)
    if payload:
        print(f"✅ Token验证成功")
        print(f"   admin_id: {payload.get('admin_id')}")
        print(f"   username: {payload.get('username')}")
        print(f"   role: {payload.get('role')}")
    else:
        print(f"❌ Token验证失败")
        sys.exit(1)
except Exception as e:
    print(f"❌ Token验证异常: {e}")
    sys.exit(1)

# 测试3: 验证无效Token
print("\n3. 测试无效Token...")
invalid_token = "invalid_token_string"
payload = verify_token(invalid_token)
if payload is None:
    print(f"✅ 无效Token正确拒绝")
else:
    print(f"❌ 无效Token验证应该失败")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 所有JWT功能测试通过！")
print("=" * 60)
