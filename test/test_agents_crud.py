"""
测试代理管理 CRUD 接口
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from biz.users.service.agent_service import AgentService
from biz.users.repo.agent_repo import AgentRepository
from base.error_codes import ErrorCode


class TestAgentCreate:
    """测试创建代理"""

    @pytest.mark.asyncio
    async def test_create_agent_success(self):
        """测试成功创建代理"""
        # Mock repository
        mock_repo = AsyncMock(spec=AgentRepository)
        mock_repo.create_agent = AsyncMock(return_value=123)

        # Create service
        service = AgentService(agent_repo=mock_repo)

        # Call service
        agent_id = await service.create_agent(
            account="agent001",
            password="password123",
            plate="A",
            open_plate=["A", "B", "C"],
            earn_rebate="partial",
            subordinate_transfer="enable",
            default_rebate_plate="B",
            superior_account="admin",
            company_remarks="测试代理"
        )

        # Verify
        assert agent_id == 123
        mock_repo.create_agent.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_agent_duplicate_account(self):
        """测试创建重复账号"""
        # Mock repository to raise error
        mock_repo = AsyncMock(spec=AgentRepository)
        mock_repo.create_agent = AsyncMock(side_effect=ValueError("账号已存在"))

        # Create service
        service = AgentService(agent_repo=mock_repo)

        # Call and verify error
        with pytest.raises(ValueError, match="账号已存在"):
            await service.create_agent(
                account="existing_agent",
                password="password123",
                plate="B",
                open_plate=["A"],
                earn_rebate="full",
                subordinate_transfer="enable",
                default_rebate_plate="A"
            )

    def test_validate_open_plate_success(self):
        """测试有效的 openPlate 验证"""
        mock_repo = MagicMock(spec=AgentRepository)
        service = AgentService(agent_repo=mock_repo)

        # 测试有效的盘口数组
        result = service.validate_open_plate(["A", "B", "C"])
        assert result == ["A", "B", "C"]

        # 测试去重
        result = service.validate_open_plate(["A", "B", "A", "C", "B"])
        assert result == ["A", "B", "C"]

    def test_validate_open_plate_invalid_element(self):
        """测试无效的 openPlate 元素"""
        mock_repo = MagicMock(spec=AgentRepository)
        service = AgentService(agent_repo=mock_repo)

        # 测试无效盘口
        with pytest.raises(ValueError, match="无效的盘口"):
            service.validate_open_plate(["A", "E"])

        with pytest.raises(ValueError, match="无效的盘口"):
            service.validate_open_plate(["X"])

    def test_validate_open_plate_empty(self):
        """测试空 openPlate 数组"""
        mock_repo = MagicMock(spec=AgentRepository)
        service = AgentService(agent_repo=mock_repo)

        # 测试空数组
        with pytest.raises(ValueError, match="开放盘口不能为空"):
            service.validate_open_plate([])


class TestAgentUpdate:
    """测试修改代理"""

    @pytest.mark.asyncio
    async def test_update_agent_success(self):
        """测试成功修改代理"""
        # Mock repository
        mock_repo = AsyncMock(spec=AgentRepository)
        mock_repo.update_agent = AsyncMock(return_value=True)

        # Create service
        service = AgentService(agent_repo=mock_repo)

        # Call service
        result = await service.update_agent(
            agent_id=123,
            plate="C",
            open_plate=["A", "B"],
            earn_rebate="none",
            company_remarks="更新备注"
        )

        # Verify
        assert result is True
        mock_repo.update_agent.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_agent_not_found(self):
        """测试修改不存在的代理"""
        # Mock repository to raise error
        mock_repo = AsyncMock(spec=AgentRepository)
        mock_repo.update_agent = AsyncMock(side_effect=ValueError("代理不存在"))

        # Create service
        service = AgentService(agent_repo=mock_repo)

        # Call and verify error
        with pytest.raises(ValueError, match="代理不存在"):
            await service.update_agent(agent_id=999, plate="A")


class TestAgentList:
    """测试代理列表"""

    @pytest.mark.asyncio
    async def test_list_agents(self):
        """测试获取代理列表"""
        # Mock data
        mock_data = {
            "list": [
                {
                    "id": 1,
                    "account": "agent001",
                    "online": False,
                    "balance": 5000.0,
                    "plate": "A盘,B盘",
                    "openTime": "2023-11-17 10:00:00",
                    "superior": "admin"
                }
            ],
            "total": 1
        }

        # Mock repository
        mock_repo = AsyncMock(spec=AgentRepository)
        mock_repo.list_agents = AsyncMock(return_value=mock_data)

        # Create service
        service = AgentService(agent_repo=mock_repo)

        # Call service
        result = await service.list_agents(
            page=1,
            page_size=20,
            account="agent",
            show_online=None,
            reg_start=None,
            reg_end=None,
            plate=None,
            balance_min=None,
            balance_max=None
        )

        # Verify
        assert result["total"] == 1
        assert len(result["list"]) == 1
        assert result["list"][0]["plate"] == "A盘,B盘"


class TestAgentDetail:
    """测试代理详情"""

    @pytest.mark.asyncio
    async def test_get_agent_detail(self):
        """测试获取代理详情"""
        # Mock data
        mock_data = {
            "account": "agent001",
            "superior": "admin",
            "balance": 5000.0,
            "plate": "A",
            "openPlate": ["A", "B", "C"],
            "earnRebate": "partial",
            "subordinateTransfer": "enable",
            "defaultRebatePlate": "B",
            "inviteCode": "ABC12345",
            "promotionDomains": ["https://example.com"],
            "companyRemarks": "测试代理",
            "openTime": "2023-11-17 10:00:00"
        }

        # Mock repository
        mock_repo = AsyncMock(spec=AgentRepository)
        mock_repo.get_agent_detail = AsyncMock(return_value=mock_data)

        # Create service
        service = AgentService(agent_repo=mock_repo)

        # Call service
        result = await service.get_agent_detail("agent001")

        # Verify
        assert result["account"] == "agent001"
        assert result["openPlate"] == ["A", "B", "C"]
        assert result["earnRebate"] == "partial"
        assert result["inviteCode"] == "ABC12345"


class TestAgentMembers:
    """测试代理的下线会员"""

    @pytest.mark.asyncio
    async def test_get_agent_members(self):
        """测试获取代理的下线会员列表"""
        # Mock data
        mock_data = {
            "list": [
                {
                    "id": 1,
                    "account": "member001",
                    "online": True,
                    "balance": 1000.0,
                    "plate": "A盘",
                    "openTime": "2023-11-17 11:00:00",
                    "superior": "agent001"
                }
            ],
            "total": 1
        }

        # Mock repository
        mock_repo = AsyncMock(spec=AgentRepository)
        mock_repo.get_agent_members = AsyncMock(return_value=mock_data)

        # Create service
        service = AgentService(agent_repo=mock_repo)

        # Call service
        result = await service.get_agent_members(
            agent_account="agent001",
            page=1,
            page_size=20
        )

        # Verify
        assert result["total"] == 1
        assert result["list"][0]["superior"] == "agent001"


class TestAgentTransactions:
    """测试代理交易记录"""

    @pytest.mark.asyncio
    async def test_get_agent_transactions(self):
        """测试获取代理交易记录"""
        # Mock data
        mock_data = {
            "list": [
                {
                    "id": 1,
                    "transactionNo": "TX20231117001",
                    "transactionType": "deposit",
                    "amount": 10000.0,
                    "balanceBefore": 5000.0,
                    "balanceAfter": 15000.0,
                    "transactionTime": "2023-11-17 10:00:00",
                    "remarks": "代理充值"
                }
            ],
            "total": 1,
            "summary": {
                "totalAmount": 10000.0
            }
        }

        # Mock repository
        mock_repo = AsyncMock(spec=AgentRepository)
        mock_repo.get_agent_transactions = AsyncMock(return_value=mock_data)

        # Create service
        service = AgentService(agent_repo=mock_repo)

        # Call service
        result = await service.get_agent_transactions(
            account="agent001",
            page=1,
            page_size=20,
            transaction_type="deposit"
        )

        # Verify
        assert result["total"] == 1
        assert result["summary"]["totalAmount"] == 10000.0


class TestAgentAccountChanges:
    """测试代理账变记录"""

    @pytest.mark.asyncio
    async def test_get_agent_account_changes(self):
        """测试获取代理账变记录"""
        # Mock data
        mock_data = {
            "list": [
                {
                    "id": 1,
                    "changeType": "transfer",
                    "amount": 1000.0,
                    "balanceBefore": 10000.0,
                    "balanceAfter": 9000.0,
                    "changeTime": "2023-11-17 10:00:00",
                    "remarks": "转账给下线"
                }
            ],
            "total": 1
        }

        # Mock repository
        mock_repo = AsyncMock(spec=AgentRepository)
        mock_repo.get_agent_account_changes = AsyncMock(return_value=mock_data)

        # Create service
        service = AgentService(agent_repo=mock_repo)

        # Call service
        result = await service.get_agent_account_changes(
            account="agent001",
            page=1,
            page_size=20,
            change_type="transfer"
        )

        # Verify
        assert result["total"] == 1
        assert result["list"][0]["amount"] == 1000.0


class TestPydanticValidation:
    """测试 Pydantic 模型验证"""

    def test_create_agent_request_validation(self):
        """测试创建代理请求验证"""
        from biz.users.api.agents_api import CreateAgentRequest
        from pydantic import ValidationError

        # 测试密码长度
        with pytest.raises(ValidationError):
            CreateAgentRequest(
                account="test",
                password="12345",  # 少于6位
                plate="A",
                openPlate=["A"],
                earnRebate="full",
                subordinateTransfer="enable",
                defaultRebatePlate="A"
            )

        # 测试无效的 earnRebate
        with pytest.raises(ValidationError):
            CreateAgentRequest(
                account="test",
                password="password123",
                plate="A",
                openPlate=["A"],
                earnRebate="invalid",  # 无效值
                subordinateTransfer="enable",
                defaultRebatePlate="A"
            )

        # 测试无效的 subordinateTransfer
        with pytest.raises(ValidationError):
            CreateAgentRequest(
                account="test",
                password="password123",
                plate="A",
                openPlate=["A"],
                earnRebate="full",
                subordinateTransfer="invalid",  # 无效值
                defaultRebatePlate="A"
            )

        # 测试有效请求
        valid_request = CreateAgentRequest(
            account="agent001",
            password="password123",
            plate="A",
            openPlate=["A", "B"],
            earnRebate="partial",
            subordinateTransfer="enable",
            defaultRebatePlate="B"
        )
        assert valid_request.account == "agent001"
        assert valid_request.openPlate == ["A", "B"]
