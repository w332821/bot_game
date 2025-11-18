"""
测试子账号管理 CRUD 接口
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from biz.roles.service.subaccount_service import SubAccountService
from biz.roles.repo.subaccount_repo import SubAccountRepository


class TestSubAccountList:
    """测试子账号列表"""

    @pytest.mark.asyncio
    async def test_get_sub_accounts_success(self):
        """测试成功获取子账号列表"""
        mock_repo = AsyncMock(spec=SubAccountRepository)
        mock_repo.get_parent_user_id_by_agent_account = AsyncMock(return_value="user_001")
        mock_repo.get_sub_accounts = AsyncMock(return_value={
            "list": [
                {
                    "id": 1,
                    "account": "agent001_sub_001",
                    "name": "子账号1",
                    "role": "管理员",
                    "createDate": "2023-11-17 10:00:00",
                    "status": "启用"
                }
            ],
            "total": 1
        })

        service = SubAccountService(subaccount_repo=mock_repo)
        result = await service.get_sub_accounts("agent001", 1, 20)

        assert result["total"] == 1
        assert len(result["list"]) == 1

    @pytest.mark.asyncio
    async def test_get_sub_accounts_agent_not_found(self):
        """测试代理不存在"""
        mock_repo = AsyncMock(spec=SubAccountRepository)
        mock_repo.get_parent_user_id_by_agent_account = AsyncMock(return_value=None)

        service = SubAccountService(subaccount_repo=mock_repo)

        with pytest.raises(ValueError, match="代理账号不存在"):
            await service.get_sub_accounts("nonexistent", 1, 20)


class TestSubAccountCreate:
    """测试创建子账号"""

    @pytest.mark.asyncio
    async def test_create_sub_account_success(self):
        """测试成功创建子账号"""
        mock_repo = AsyncMock(spec=SubAccountRepository)
        mock_repo.get_parent_user_id_by_agent_account = AsyncMock(return_value="user_001")
        mock_repo.get_role_id_by_name = AsyncMock(return_value=1)
        mock_repo.generate_account = AsyncMock(return_value="agent001_sub_001")
        mock_repo.check_account_exists = AsyncMock(return_value=False)
        mock_repo.create_sub_account = AsyncMock(return_value=1)

        service = SubAccountService(subaccount_repo=mock_repo)
        sub_id = await service.create_sub_account(
            "agent001", "password123", "pay123", "子账号名称", "管理员"
        )

        assert sub_id == 1
        mock_repo.create_sub_account.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_sub_account_agent_not_found(self):
        """测试代理不存在"""
        mock_repo = AsyncMock(spec=SubAccountRepository)
        mock_repo.get_parent_user_id_by_agent_account = AsyncMock(return_value=None)

        service = SubAccountService(subaccount_repo=mock_repo)

        with pytest.raises(ValueError, match="代理账号不存在"):
            await service.create_sub_account(
                "nonexistent", "password123", "pay123", "名称", "管理员"
            )

    @pytest.mark.asyncio
    async def test_create_sub_account_role_not_found(self):
        """测试角色不存在"""
        mock_repo = AsyncMock(spec=SubAccountRepository)
        mock_repo.get_parent_user_id_by_agent_account = AsyncMock(return_value="user_001")
        mock_repo.get_role_id_by_name = AsyncMock(return_value=None)

        service = SubAccountService(subaccount_repo=mock_repo)

        with pytest.raises(ValueError, match="角色不存在"):
            await service.create_sub_account(
                "agent001", "password123", "pay123", "名称", "不存在的角色"
            )

    @pytest.mark.asyncio
    async def test_create_sub_account_invalid_password(self):
        """测试密码长度无效"""
        mock_repo = AsyncMock(spec=SubAccountRepository)
        mock_repo.get_parent_user_id_by_agent_account = AsyncMock(return_value="user_001")

        service = SubAccountService(subaccount_repo=mock_repo)

        with pytest.raises(ValueError, match="登录密码长度必须在 6-20 之间"):
            await service.create_sub_account(
                "agent001", "12345", "pay123", "名称", "管理员"
            )


class TestSubAccountUpdate:
    """测试更新子账号"""

    @pytest.mark.asyncio
    async def test_update_sub_account_success(self):
        """测试成功更新子账号"""
        mock_repo = AsyncMock(spec=SubAccountRepository)
        mock_repo.get_sub_account_by_id = AsyncMock(return_value={"id": 1})
        mock_repo.get_role_id_by_name = AsyncMock(return_value=2)
        mock_repo.update_sub_account = AsyncMock(return_value=True)

        service = SubAccountService(subaccount_repo=mock_repo)
        result = await service.update_sub_account(
            1, "新名称", "新角色", "禁用"
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_update_sub_account_not_found(self):
        """测试子账号不存在"""
        mock_repo = AsyncMock(spec=SubAccountRepository)
        mock_repo.get_sub_account_by_id = AsyncMock(return_value=None)

        service = SubAccountService(subaccount_repo=mock_repo)

        with pytest.raises(ValueError, match="子账号不存在"):
            await service.update_sub_account(999, "名称", "角色", "启用")

    @pytest.mark.asyncio
    async def test_update_sub_account_invalid_status(self):
        """测试状态无效"""
        mock_repo = AsyncMock(spec=SubAccountRepository)
        mock_repo.get_sub_account_by_id = AsyncMock(return_value={"id": 1})
        mock_repo.get_role_id_by_name = AsyncMock(return_value=1)

        service = SubAccountService(subaccount_repo=mock_repo)

        with pytest.raises(ValueError, match="无效的状态"):
            await service.update_sub_account(1, "名称", "角色", "无效状态")


class TestSubAccountDelete:
    """测试删除子账号"""

    @pytest.mark.asyncio
    async def test_delete_sub_account_success(self):
        """测试成功删除子账号"""
        mock_repo = AsyncMock(spec=SubAccountRepository)
        mock_repo.get_sub_account_by_id = AsyncMock(return_value={"id": 1})
        mock_repo.delete_sub_account = AsyncMock(return_value=True)

        service = SubAccountService(subaccount_repo=mock_repo)
        result = await service.delete_sub_account(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_sub_account_not_found(self):
        """测试子账号不存在"""
        mock_repo = AsyncMock(spec=SubAccountRepository)
        mock_repo.get_sub_account_by_id = AsyncMock(return_value=None)

        service = SubAccountService(subaccount_repo=mock_repo)

        with pytest.raises(ValueError, match="子账号不存在"):
            await service.delete_sub_account(999)


class TestValidation:
    """测试验证逻辑"""

    def test_validate_account_name(self):
        """测试账户名称验证"""
        mock_repo = MagicMock(spec=SubAccountRepository)
        service = SubAccountService(subaccount_repo=mock_repo)

        # 正常名称
        assert service.validate_account_name("子账号1") == "子账号1"

        # 空名称
        with pytest.raises(ValueError):
            service.validate_account_name("")

        # 过长名称
        with pytest.raises(ValueError):
            service.validate_account_name("a" * 51)

    def test_validate_passwords(self):
        """测试密码验证"""
        mock_repo = MagicMock(spec=SubAccountRepository)
        service = SubAccountService(subaccount_repo=mock_repo)

        # 正常密码
        login, payment = service.validate_passwords("password123", "pay123456")
        assert login == "password123"
        assert payment == "pay123456"

        # 登录密码过短
        with pytest.raises(ValueError):
            service.validate_passwords("12345", "pay123456")

        # 支付密码过短
        with pytest.raises(ValueError):
            service.validate_passwords("password123", "12345")

    def test_validate_status(self):
        """测试状态验证"""
        mock_repo = MagicMock(spec=SubAccountRepository)
        service = SubAccountService(subaccount_repo=mock_repo)

        # 正常状态
        assert service.validate_status("启用") == "启用"
        assert service.validate_status("禁用") == "禁用"

        # 无效状态
        with pytest.raises(ValueError):
            service.validate_status("未知")
