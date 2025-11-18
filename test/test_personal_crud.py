"""
测试个人中心 CRUD 接口
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from biz.users.service.personal_service import PersonalService
from biz.users.repo.personal_repo import PersonalRepository


class TestPersonalBasicInfo:
    """测试个人基本信息"""

    @pytest.mark.asyncio
    async def test_get_basic_info_member(self):
        """测试获取会员基本信息"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)
        mock_repo.get_basic_info = AsyncMock(return_value={
            "account": "member001",
            "balance": 1000.0,
            "plate": "B",
            "superior": "agent001",
            "openTime": "2023-11-17 10:00:00"
        })

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Call service
        result = await service.get_basic_info("member001")

        # Verify
        assert result["account"] == "member001"
        assert result["balance"] == 1000.0
        assert "openPlate" not in result  # 会员没有这个字段

    @pytest.mark.asyncio
    async def test_get_basic_info_agent(self):
        """测试获取代理基本信息"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)
        mock_repo.get_basic_info = AsyncMock(return_value={
            "account": "agent001",
            "balance": 5000.0,
            "plate": "A",
            "superior": "admin",
            "openTime": "2023-11-17 10:00:00",
            "openPlate": ["A", "B", "C"],
            "earnRebate": "partial",
            "subordinateTransfer": "enable",
            "defaultRebatePlate": "B"
        })

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Call service
        result = await service.get_basic_info("agent001")

        # Verify
        assert result["account"] == "agent001"
        assert result["openPlate"] == ["A", "B", "C"]
        assert result["earnRebate"] == "partial"

    @pytest.mark.asyncio
    async def test_update_basic_info_success(self):
        """测试成功更新基本信息"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)
        mock_repo.update_basic_info = AsyncMock(return_value=True)

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Call service
        result = await service.update_basic_info(
            account="agent001",
            plate="C",
            open_plate=["A", "B"],
            earn_rebate="full"
        )

        # Verify
        assert result is True
        mock_repo.update_basic_info.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_basic_info_invalid_open_plate(self):
        """测试更新时提供无效的开放盘口"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Test empty openPlate
        with pytest.raises(ValueError, match="开放盘口不能为空"):
            await service.update_basic_info(
                account="agent001",
                open_plate=[]
            )

        # Test invalid plate
        with pytest.raises(ValueError, match="无效的盘口"):
            await service.update_basic_info(
                account="agent001",
                open_plate=["A", "X"]
            )


class TestPromotionDomain:
    """测试推广域名"""

    @pytest.mark.asyncio
    async def test_add_promotion_domain_success(self):
        """测试成功添加推广域名"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)
        mock_repo.add_promotion_domain = AsyncMock(return_value=True)
        mock_repo.get_promotion_links = AsyncMock(return_value=[
            "https://example.com/?a=ABC12345#/register",
            "https://test.com/?a=ABC12345#/register"
        ])

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Call service
        result = await service.add_promotion_domain("agent001", "test.com")

        # Verify
        assert "promotionLinks" in result
        assert len(result["promotionLinks"]) == 2

    @pytest.mark.asyncio
    async def test_add_promotion_domain_invalid_format(self):
        """测试添加无效格式的域名"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Test invalid domain
        with pytest.raises(ValueError, match="无效的域名格式"):
            await service.add_promotion_domain("agent001", "invalid domain")

        with pytest.raises(ValueError, match="无效的域名格式"):
            await service.add_promotion_domain("agent001", "http://test.com")

    def test_validate_domain(self):
        """测试域名验证"""
        mock_repo = MagicMock(spec=PersonalRepository)
        service = PersonalService(personal_repo=mock_repo)

        # Valid domains
        assert service.validate_domain("example.com") is True
        assert service.validate_domain("test.example.com") is True
        assert service.validate_domain("a-b.example.com") is True

        # Invalid domains
        with pytest.raises(ValueError):
            service.validate_domain("invalid domain")

        with pytest.raises(ValueError):
            service.validate_domain("-example.com")

        with pytest.raises(ValueError):
            service.validate_domain("example-.com")


class TestLotteryRebateConfig:
    """测试彩票退水配置"""

    @pytest.mark.asyncio
    async def test_get_lottery_rebate_config(self):
        """测试获取彩票退水配置"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)
        mock_repo.get_lottery_rebate_config = AsyncMock(return_value=[
            {
                "gameName": "新奥六合彩",
                "isGroup": True,
                "children": [
                    {"betTypeName": "正码1-6", "rebate": 2.5},
                    {"betTypeName": "特码", "rebate": 3.0}
                ]
            }
        ])

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Call service
        result = await service.get_lottery_rebate_config("agent001")

        # Verify
        assert len(result) == 1
        assert result[0]["gameName"] == "新奥六合彩"
        assert result[0]["isGroup"] is True
        assert len(result[0]["children"]) == 2

    @pytest.mark.asyncio
    async def test_save_lottery_rebate_config_success(self):
        """测试成功保存彩票退水配置"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)
        mock_repo.save_lottery_rebate_config = AsyncMock(return_value=True)

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Call service
        config = [
            {
                "gameName": "新奥六合彩",
                "isGroup": True,
                "children": [
                    {"betTypeName": "正码1-6", "rebate": 2.5},
                    {"betTypeName": "特码", "rebate": 3.0}
                ]
            }
        ]

        result = await service.save_lottery_rebate_config("agent001", config)

        # Verify
        assert result is True
        mock_repo.save_lottery_rebate_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_lottery_rebate_config_invalid_game_name(self):
        """测试保存配置时游戏名称无效"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Test invalid game name
        config = [
            {
                "gameName": "Invalid Game",
                "betTypeName": "Test",
                "rebate": 2.5
            }
        ]

        with pytest.raises(ValueError, match="无效的游戏名称"):
            await service.save_lottery_rebate_config("agent001", config)

    @pytest.mark.asyncio
    async def test_save_lottery_rebate_config_missing_children(self):
        """测试保存配置时分组缺少 children"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Test missing children
        config = [
            {
                "gameName": "新奥六合彩",
                "isGroup": True
                # missing children
            }
        ]

        with pytest.raises(ValueError, match="缺少 children 字段"):
            await service.save_lottery_rebate_config("agent001", config)

    @pytest.mark.asyncio
    async def test_save_lottery_rebate_config_invalid_rebate(self):
        """测试保存配置时退水比例无效"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Test invalid rebate
        config = [
            {
                "gameName": "新奥六合彩",
                "isGroup": True,
                "children": [
                    {"betTypeName": "正码1-6", "rebate": 150.0}  # 超出范围
                ]
            }
        ]

        with pytest.raises(ValueError, match="退水比例必须在 0-100 之间"):
            await service.save_lottery_rebate_config("agent001", config)


class TestLoginLogs:
    """测试登录日志"""

    @pytest.mark.asyncio
    async def test_get_login_logs(self):
        """测试获取登录日志"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)
        mock_repo.get_login_logs = AsyncMock(return_value={
            "list": [
                {
                    "loginTime": "2023-11-17 10:00:00",
                    "ipAddress": "192.168.1.1",
                    "ipLocation": "广东省深圳市",
                    "operator": "电信"
                }
            ],
            "total": 1
        })

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Call service
        result = await service.get_login_logs("agent001", 1, 20)

        # Verify
        assert result["total"] == 1
        assert len(result["list"]) == 1
        assert result["list"][0]["ipAddress"] == "192.168.1.1"


class TestPasswordUpdate:
    """测试修改密码"""

    @pytest.mark.asyncio
    async def test_update_password_success(self):
        """测试成功修改密码"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)
        mock_repo.update_password = AsyncMock(return_value=True)

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Call service
        result = await service.update_password(
            account="agent001",
            old_password="oldpass123",
            new_password="newpass456"
        )

        # Verify
        assert result is True
        mock_repo.update_password.assert_called_once_with("agent001", "oldpass123", "newpass456", "agent")

    @pytest.mark.asyncio
    async def test_update_password_invalid_length(self):
        """测试新密码长度不符合要求"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Test password too short
        with pytest.raises(ValueError, match="新密码长度必须在 6-20 之间"):
            await service.update_password(
                account="agent001",
                old_password="oldpass123",
                new_password="12345"  # 少于6位
            )

        # Test password too long
        with pytest.raises(ValueError, match="新密码长度必须在 6-20 之间"):
            await service.update_password(
                account="agent001",
                old_password="oldpass123",
                new_password="a" * 21  # 超过20位
            )

    @pytest.mark.asyncio
    async def test_update_password_wrong_old_password(self):
        """测试旧密码错误"""
        # Mock repository
        mock_repo = AsyncMock(spec=PersonalRepository)
        mock_repo.update_password = AsyncMock(side_effect=ValueError("旧密码错误"))

        # Create service
        service = PersonalService(personal_repo=mock_repo)

        # Call and verify error
        with pytest.raises(ValueError, match="旧密码错误"):
            await service.update_password(
                account="agent001",
                old_password="wrongpass",
                new_password="newpass456"
            )


class TestPydanticValidation:
    """测试 Pydantic 模型验证"""

    def test_update_basic_info_request_validation(self):
        """测试更新基本信息请求验证"""
        from biz.users.api.personal_api import UpdateBasicInfoRequest
        from pydantic import ValidationError

        # 测试无效的盘口
        with pytest.raises(ValidationError):
            UpdateBasicInfoRequest(
                plate="X"  # 无效盘口
            )

        # 测试无效的 openPlate
        with pytest.raises(ValidationError):
            UpdateBasicInfoRequest(
                openPlate=["A", "X"]
            )

        # 测试有效请求
        valid_request = UpdateBasicInfoRequest(
            plate="A",
            openPlate=["A", "B", "C"],
            earnRebate="full",
            subordinateTransfer="enable",
            defaultRebatePlate="B"
        )
        assert valid_request.plate == "A"
        assert valid_request.openPlate == ["A", "B", "C"]

    def test_lottery_rebate_item_validation(self):
        """测试彩票退水配置项验证"""
        from biz.users.api.personal_api import LotteryRebateItem
        from pydantic import ValidationError

        # 测试无效的游戏名称
        with pytest.raises(ValidationError):
            LotteryRebateItem(
                gameName="Invalid Game",
                betTypeName="Test",
                rebate=2.5
            )

        # 测试退水比例超出范围
        with pytest.raises(ValidationError):
            LotteryRebateItem(
                gameName="新奥六合彩",
                betTypeName="正码",
                rebate=150.0
            )

        # 测试有效配置
        valid_item = LotteryRebateItem(
            gameName="新奥六合彩",
            betTypeName="正码1-6",
            rebate=2.5
        )
        assert valid_item.gameName == "新奥六合彩"
        assert valid_item.rebate == 2.5

    def test_update_password_request_validation(self):
        """测试修改密码请求验证"""
        from biz.users.api.personal_api import UpdatePasswordRequest
        from pydantic import ValidationError

        # 测试密码过短
        with pytest.raises(ValidationError):
            UpdatePasswordRequest(
                oldPassword="12345",  # 少于6位
                newPassword="123456"
            )

        # 测试密码过长
        with pytest.raises(ValidationError):
            UpdatePasswordRequest(
                oldPassword="123456",
                newPassword="a" * 21  # 超过20位
            )

        # 测试有效请求
        valid_request = UpdatePasswordRequest(
            oldPassword="oldpass123",
            newPassword="newpass456"
        )
        assert valid_request.oldPassword == "oldpass123"
        assert valid_request.newPassword == "newpass456"
