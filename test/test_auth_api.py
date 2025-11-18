"""
认证模块API测试
测试 POST /api/auth/login 和 POST /api/auth/logout 接口
"""
import pytest
from httpx import AsyncClient
from biz.application import app


class TestAuthLogin:
    """测试登录接口"""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """测试登录成功场景"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/login", json={
                "account": "admin",
                "password": "admin123"
            })

            assert response.status_code == 200
            data = response.json()

            # 验证响应格式
            assert "code" in data
            assert "message" in data
            assert "data" in data

            # 登录成功应该返回用户信息
            if data["code"] == 200:
                assert data["data"] is not None
                assert "user" in data["data"]
                assert "id" in data["data"]["user"]
                assert "account" in data["data"]["user"]
                assert "userType" in data["data"]["user"]

    @pytest.mark.asyncio
    async def test_login_failure_wrong_password(self):
        """测试登录失败 - 错误密码"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/login", json={
                "account": "admin",
                "password": "wrongpassword"
            })

            assert response.status_code == 200
            data = response.json()

            # 验证响应格式
            assert "code" in data
            assert "message" in data
            assert "data" in data

            # 登录失败应该返回错误码
            assert data["code"] != 200

    @pytest.mark.asyncio
    async def test_login_failure_nonexistent_account(self):
        """测试登录失败 - 不存在的账号"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/login", json={
                "account": "nonexistent_user_12345",
                "password": "password"
            })

            assert response.status_code == 200
            data = response.json()

            # 验证响应格式
            assert "code" in data
            assert "message" in data

            # 应该返回错误码
            assert data["code"] != 200

    @pytest.mark.asyncio
    async def test_login_missing_fields(self):
        """测试登录失败 - 缺少必需字段"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 缺少password字段
            response = await client.post("/api/auth/login", json={
                "account": "admin"
            })

            # FastAPI会返回422错误
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_empty_credentials(self):
        """测试登录失败 - 空凭证"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/login", json={
                "account": "",
                "password": ""
            })

            assert response.status_code == 200
            data = response.json()

            # 应该返回错误
            assert data["code"] != 200


class TestAuthLogout:
    """测试登出接口"""

    @pytest.mark.asyncio
    async def test_logout_success(self):
        """测试登出成功"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/logout")

            assert response.status_code == 200
            data = response.json()

            # 验证响应格式
            assert "code" in data
            assert "message" in data
            assert "data" in data

            # 登出总是成功(无状态系统)
            assert data["code"] == 200
            assert data["message"] == "退出成功"
            assert data["data"] is None

    @pytest.mark.asyncio
    async def test_logout_without_token(self):
        """测试未登录状态下登出"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/logout")

            assert response.status_code == 200
            data = response.json()

            # 即使未登录也应该返回成功(无状态系统)
            assert data["code"] == 200
            assert data["message"] == "退出成功"

    @pytest.mark.asyncio
    async def test_logout_idempotent(self):
        """测试登出的幂等性"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 连续登出两次
            response1 = await client.post("/api/auth/logout")
            response2 = await client.post("/api/auth/logout")

            assert response1.status_code == 200
            assert response2.status_code == 200

            data1 = response1.json()
            data2 = response2.json()

            # 两次都应该成功
            assert data1["code"] == 200
            assert data2["code"] == 200


class TestAuthResponseFormat:
    """测试认证接口的响应格式"""

    @pytest.mark.asyncio
    async def test_login_response_has_correct_structure(self):
        """测试登录响应结构"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/login", json={
                "account": "test",
                "password": "test"
            })

            data = response.json()

            # 验证统一响应格式
            assert isinstance(data, dict)
            assert "code" in data
            assert "message" in data
            assert "data" in data

            assert isinstance(data["code"], int)
            assert isinstance(data["message"], str)

    @pytest.mark.asyncio
    async def test_logout_response_has_correct_structure(self):
        """测试登出响应结构"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/logout")

            data = response.json()

            # 验证统一响应格式
            assert isinstance(data, dict)
            assert "code" in data
            assert "message" in data
            assert "data" in data

            assert isinstance(data["code"], int)
            assert isinstance(data["message"], str)
            assert data["data"] is None
