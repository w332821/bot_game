"""
测试会员管理 CRUD 接口
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from biz.users.service.member_service import MemberService
from biz.users.repo.member_repo import MemberRepository
from base.error_codes import ErrorCode


class TestMemberCreate:
    """测试创建会员"""

    @pytest.mark.asyncio
    async def test_create_member_success(self):
        """测试成功创建会员"""
        # Mock repository
        mock_repo = AsyncMock(spec=MemberRepository)
        mock_repo.create_member = AsyncMock(return_value=123)

        # Create service
        service = MemberService(member_repo=mock_repo)

        # Call service
        member_id = await service.create_member(
            account="test_user",
            password="password123",
            plate="A",
            superior_account="boss",
            company_remarks="测试会员"
        )

        # Verify
        assert member_id == 123
        mock_repo.create_member.assert_called_once_with(
            "test_user", "password123", "A", "boss", "测试会员"
        )

    @pytest.mark.asyncio
    async def test_create_member_duplicate_account(self):
        """测试创建重复账号"""
        # Mock repository to raise error
        mock_repo = AsyncMock(spec=MemberRepository)
        mock_repo.create_member = AsyncMock(side_effect=ValueError("账号已存在"))

        # Create service
        service = MemberService(member_repo=mock_repo)

        # Call and verify error
        with pytest.raises(ValueError, match="账号已存在"):
            await service.create_member(
                account="existing_user",
                password="password123",
                plate="B"
            )


class TestMemberUpdate:
    """测试修改会员"""

    @pytest.mark.asyncio
    async def test_update_member_success(self):
        """测试成功修改会员"""
        # Mock repository
        mock_repo = AsyncMock(spec=MemberRepository)
        mock_repo.update_member = AsyncMock(return_value=True)

        # Create service
        service = MemberService(member_repo=mock_repo)

        # Call service
        result = await service.update_member(
            member_id=123,
            plate="C",
            company_remarks="更新备注"
        )

        # Verify
        assert result is True
        mock_repo.update_member.assert_called_once_with(123, "C", "更新备注")

    @pytest.mark.asyncio
    async def test_update_member_not_found(self):
        """测试修改不存在的会员"""
        # Mock repository to raise error
        mock_repo = AsyncMock(spec=MemberRepository)
        mock_repo.update_member = AsyncMock(side_effect=ValueError("会员不存在"))

        # Create service
        service = MemberService(member_repo=mock_repo)

        # Call and verify error
        with pytest.raises(ValueError, match="会员不存在"):
            await service.update_member(member_id=999, plate="A")


class TestMemberBetOrders:
    """测试会员注单列表"""

    @pytest.mark.asyncio
    async def test_get_bet_orders(self):
        """测试获取注单列表"""
        # Mock data
        mock_data = {
            "list": [
                {
                    "id": 1,
                    "orderNo": "BO20231117001",
                    "betType": "新奥六合彩",
                    "betAmount": 100.0,
                    "winAmount": 200.0,
                    "status": "settled",
                    "betTime": "2023-11-17 10:00:00",
                    "settleTime": "2023-11-17 21:00:00"
                }
            ],
            "total": 1,
            "summary": {
                "totalBet": 100.0,
                "totalWin": 200.0
            }
        }

        # Mock repository
        mock_repo = AsyncMock(spec=MemberRepository)
        mock_repo.get_bet_orders = AsyncMock(return_value=mock_data)

        # Create service
        service = MemberService(member_repo=mock_repo)

        # Call service
        result = await service.get_bet_orders(
            account="test_user",
            page=1,
            page_size=20,
            status="settled",
            bet_type="新奥六合彩"
        )

        # Verify
        assert result["total"] == 1
        assert len(result["list"]) == 1
        assert result["summary"]["totalBet"] == 100.0
        assert result["summary"]["totalWin"] == 200.0


class TestMemberTransactions:
    """测试会员交易记录"""

    @pytest.mark.asyncio
    async def test_get_transactions(self):
        """测试获取交易记录"""
        # Mock data
        mock_data = {
            "list": [
                {
                    "id": 1,
                    "transactionNo": "TX20231117001",
                    "transactionType": "deposit",
                    "amount": 1000.0,
                    "balanceBefore": 500.0,
                    "balanceAfter": 1500.0,
                    "transactionTime": "2023-11-17 10:00:00",
                    "remarks": "充值"
                }
            ],
            "total": 1,
            "summary": {
                "totalAmount": 1000.0
            }
        }

        # Mock repository
        mock_repo = AsyncMock(spec=MemberRepository)
        mock_repo.get_transactions = AsyncMock(return_value=mock_data)

        # Create service
        service = MemberService(member_repo=mock_repo)

        # Call service
        result = await service.get_transactions(
            account="test_user",
            page=1,
            page_size=20,
            transaction_type="deposit"
        )

        # Verify
        assert result["total"] == 1
        assert len(result["list"]) == 1
        assert result["summary"]["totalAmount"] == 1000.0


class TestMemberAccountChanges:
    """测试会员账变记录"""

    @pytest.mark.asyncio
    async def test_get_account_changes(self):
        """测试获取账变记录"""
        # Mock data
        mock_data = {
            "list": [
                {
                    "id": 1,
                    "changeType": "bet",
                    "amount": -100.0,
                    "balanceBefore": 1000.0,
                    "balanceAfter": 900.0,
                    "changeTime": "2023-11-17 10:00:00",
                    "remarks": "下注扣款"
                }
            ],
            "total": 1
        }

        # Mock repository
        mock_repo = AsyncMock(spec=MemberRepository)
        mock_repo.get_account_changes = AsyncMock(return_value=mock_data)

        # Create service
        service = MemberService(member_repo=mock_repo)

        # Call service
        result = await service.get_account_changes(
            account="test_user",
            page=1,
            page_size=20,
            change_type="bet"
        )

        # Verify
        assert result["total"] == 1
        assert len(result["list"]) == 1
        assert result["list"][0]["amount"] == -100.0


class TestPasswordValidation:
    """测试密码验证"""

    def test_password_length_validation(self):
        """测试密码长度验证"""
        from biz.users.api.members_api import CreateMemberRequest
        from pydantic import ValidationError

        # 测试太短的密码
        with pytest.raises(ValidationError):
            CreateMemberRequest(
                account="test",
                password="12345",  # 少于6位
                plate="A"
            )

        # 测试太长的密码
        with pytest.raises(ValidationError):
            CreateMemberRequest(
                account="test",
                password="1" * 21,  # 超过20位
                plate="A"
            )

        # 测试有效密码
        valid_request = CreateMemberRequest(
            account="test",
            password="password123",  # 6-20位
            plate="A"
        )
        assert valid_request.password == "password123"


class TestPlateValidation:
    """测试盘口验证"""

    def test_plate_validation(self):
        """测试盘口只能是 A/B/C"""
        from biz.users.api.members_api import CreateMemberRequest
        from pydantic import ValidationError

        # 测试无效盘口
        with pytest.raises(ValidationError):
            CreateMemberRequest(
                account="test",
                password="password123",
                plate="D"  # 无效盘口
            )

        # 测试有效盘口
        for plate in ["A", "B", "C"]:
            valid_request = CreateMemberRequest(
                account="test",
                password="password123",
                plate=plate
            )
            assert valid_request.plate == plate
