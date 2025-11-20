import asyncio
import httpx
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

async def test_create_member():
    base_url = "http://localhost:3003"
    token = None

    print("=== 测试新增会员功能 ===\n")

    async with httpx.AsyncClient() as client:
        try:
            print("步骤 1: 登录获取 token")
            login_response = await client.post(
                f"{base_url}/api/auth/login",
                json={
                    "account": "admin",
                    "password": "admin123"
                },
                timeout=10.0
            )

            print(f"登录响应状态码: {login_response.status_code}")

            if login_response.status_code != 200:
                print(f"❌ 登录失败: {login_response.text}")
                return

            login_data = login_response.json()
            if login_data.get("code") != 200:
                print(f"❌ 登录失败: {login_data}")
                return

            token = login_data["data"]["token"]
            print(f"✅ 登录成功，获得 token: {token[:20]}...\n")

            print("步骤 2: 创建新会员")
            create_response = await client.post(
                f"{base_url}/api/users/members",
                json={
                    "phone": "13912345678",
                    "password": "test123456",
                    "account": "test_member_001",
                    "plate": "A",
                    "nickname": "测试会员001",
                    "superiorAccount": None,
                    "companyRemarks": "自动化测试创建"
                },
                headers={
                    "Authorization": f"Bearer {token}"
                },
                timeout=10.0
            )

            print(f"响应状态码: {create_response.status_code}")
            print(f"响应内容: {create_response.json()}\n")

            create_data = create_response.json()

            if create_data.get("code") == 200:
                member_id = create_data["data"]["id"]
                print(f"✅ 会员创建成功！member_profile_id = {member_id}")

                print("\n步骤 3: 验证 MongoDB 用户是否创建")
                mongodb_uri = os.getenv("MONGODB_URI")
                mongo_client = AsyncIOMotorClient(mongodb_uri)
                db = mongo_client.yueliao

                mongo_user = await db.users.find_one({"phone": "13912345678"})
                if mongo_user:
                    print(f"✅ MongoDB 用户已创建")
                    print(f"   - ObjectId: {mongo_user['_id']}")
                    print(f"   - 悦聊ID: {mongo_user['yueliaoId']}")
                    print(f"   - 昵称: {mongo_user['nickname']}")
                    print(f"   - 手机号: {mongo_user['phone']}")
                else:
                    print("❌ MongoDB 用户未找到")

                mongo_client.close()

                print("\n步骤 4: 查询会员详情")
                detail_response = await client.get(
                    f"{base_url}/api/users/members/test_member_001",
                    headers={
                        "Authorization": f"Bearer {token}"
                    },
                    timeout=10.0
                )

                detail_data = detail_response.json()
                if detail_data.get("code") == 200:
                    print(f"✅ 会员详情查询成功:")
                    print(f"   {detail_data['data']}")
                else:
                    print(f"❌ 查询失败: {detail_data}")

            else:
                print(f"❌ 创建失败: {create_data}")
                if "手机号" in str(create_data) and "已存在" in str(create_data):
                    print("\n提示: 手机号已存在，可能是之前测试留下的数据")
                    print("请手动清理 MongoDB 和 MySQL 中的测试数据后重试")

        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_create_member())
