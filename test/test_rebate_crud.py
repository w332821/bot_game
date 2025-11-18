"""
测试退水配置 CRUD 接口
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from biz.users.service.rebate_service import RebateService
from biz.users.repo.rebate_repo import RebateRepository
from base.error_codes import ErrorCode


class TestRebateGet:
    """测试获取退水配置"""

    @pytest.mark.asyncio
    async def test_get_rebate_settings_success(self):
        """测试成功获取退水配置"""
        # Mock repository
        mock_repo = AsyncMock(spec=RebateRepository)
        mock_repo.get_rebate_settings = AsyncMock(return_value={
            "independentRebate": True,
            "earnRebate": 5.5,
            "gameSettings": [
                {"gameName": "新奥六合彩", "rebate": 2.5},
                {"gameName": "168澳洲幸运8", "rebate": 3.0}
            ]
        })

        # Create service
        service = RebateService(rebate_repo=mock_repo)

        # Call service
        result = await service.get_rebate_settings("test_account")

        # Verify
        assert result["independentRebate"] is True
        assert result["earnRebate"] == 5.5
        assert len(result["gameSettings"]) == 2
        mock_repo.get_rebate_settings.assert_called_once_with("test_account")

    @pytest.mark.asyncio
    async def test_get_rebate_settings_not_found(self):
        """测试获取不存在的退水配置"""
        # Mock repository
        mock_repo = AsyncMock(spec=RebateRepository)
        mock_repo.get_rebate_settings = AsyncMock(return_value=None)

        # Create service
        service = RebateService(rebate_repo=mock_repo)

        # Call service
        result = await service.get_rebate_settings("nonexistent")

        # Verify
        assert result is None


class TestRebateUpdate:
    """测试更新退水配置"""

    @pytest.mark.asyncio
    async def test_update_rebate_settings_success(self):
        """测试成功更新退水配置"""
        # Mock repository
        mock_repo = AsyncMock(spec=RebateRepository)
        mock_repo.update_rebate_settings = AsyncMock(return_value=True)

        # Create service
        service = RebateService(rebate_repo=mock_repo)

        # Call service
        game_settings = [
            {"gameName": "新奥六合彩", "rebate": 2.5},
            {"gameName": "168澳洲幸运8", "rebate": 3.0}
        ]

        result = await service.update_rebate_settings(
            account="test_account",
            independent_rebate=True,
            earn_rebate=5.5,
            game_settings=game_settings
        )

        # Verify
        assert result is True
        mock_repo.update_rebate_settings.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_rebate_invalid_earn_rebate(self):
        """测试更新退水配置时 earnRebate 超出范围"""
        # Mock repository
        mock_repo = AsyncMock(spec=RebateRepository)

        # Create service
        service = RebateService(rebate_repo=mock_repo)

        # Test invalid earnRebate
        game_settings = [{"gameName": "新奥六合彩", "rebate": 2.5}]

        with pytest.raises(ValueError, match="赚取退水比例必须在 0-100 之间"):
            await service.update_rebate_settings(
                account="test_account",
                independent_rebate=False,
                earn_rebate=150.0,  # 超出范围
                game_settings=game_settings
            )

    @pytest.mark.asyncio
    async def test_update_rebate_empty_game_settings(self):
        """测试更新退水配置时游戏配置为空"""
        # Mock repository
        mock_repo = AsyncMock(spec=RebateRepository)

        # Create service
        service = RebateService(rebate_repo=mock_repo)

        # Test empty gameSettings
        with pytest.raises(ValueError, match="游戏退水配置不能为空"):
            await service.update_rebate_settings(
                account="test_account",
                independent_rebate=False,
                earn_rebate=5.0,
                game_settings=[]
            )

    @pytest.mark.asyncio
    async def test_update_rebate_invalid_game_name(self):
        """测试更新退水配置时游戏名称无效"""
        # Mock repository
        mock_repo = AsyncMock(spec=RebateRepository)

        # Create service
        service = RebateService(rebate_repo=mock_repo)

        # Test invalid game name
        game_settings = [{"gameName": "Invalid Game", "rebate": 2.5}]

        with pytest.raises(ValueError, match="无效的游戏名称"):
            await service.update_rebate_settings(
                account="test_account",
                independent_rebate=False,
                earn_rebate=5.0,
                game_settings=game_settings
            )

    @pytest.mark.asyncio
    async def test_update_rebate_invalid_rebate_range(self):
        """测试更新退水配置时游戏退水比例超出范围"""
        # Mock repository
        mock_repo = AsyncMock(spec=RebateRepository)

        # Create service
        service = RebateService(rebate_repo=mock_repo)

        # Test invalid rebate range
        game_settings = [{"gameName": "新奥六合彩", "rebate": 150.0}]

        with pytest.raises(ValueError, match="退水比例必须在 0-100 之间"):
            await service.update_rebate_settings(
                account="test_account",
                independent_rebate=False,
                earn_rebate=5.0,
                game_settings=game_settings
            )


class TestGameSettingsValidation:
    """测试游戏退水配置验证"""

    def test_validate_game_settings_success(self):
        """测试有效的游戏退水配置"""
        mock_repo = MagicMock(spec=RebateRepository)
        service = RebateService(rebate_repo=mock_repo)

        game_settings = [
            {"gameName": "新奥六合彩", "rebate": 2.5},
            {"gameName": "168澳洲幸运8", "rebate": 3.0}
        ]

        result = service.validate_game_settings(game_settings)
        assert len(result) == 2
        assert result[0]["gameName"] == "新奥六合彩"

    def test_validate_game_settings_missing_fields(self):
        """测试缺少必需字段"""
        mock_repo = MagicMock(spec=RebateRepository)
        service = RebateService(rebate_repo=mock_repo)

        # Missing rebate
        game_settings = [{"gameName": "新奥六合彩"}]

        with pytest.raises(ValueError, match="缺少必需字段"):
            service.validate_game_settings(game_settings)

    def test_validate_game_settings_invalid_game_name(self):
        """测试无效的游戏名称"""
        mock_repo = MagicMock(spec=RebateRepository)
        service = RebateService(rebate_repo=mock_repo)

        game_settings = [{"gameName": "Some Invalid Game", "rebate": 2.5}]

        with pytest.raises(ValueError, match="无效的游戏名称"):
            service.validate_game_settings(game_settings)

    def test_validate_game_settings_invalid_rebate(self):
        """测试无效的退水比例"""
        mock_repo = MagicMock(spec=RebateRepository)
        service = RebateService(rebate_repo=mock_repo)

        # Negative rebate
        game_settings = [{"gameName": "新奥六合彩", "rebate": -1.0}]

        with pytest.raises(ValueError, match="退水比例必须在 0-100 之间"):
            service.validate_game_settings(game_settings)

        # Rebate > 100
        game_settings = [{"gameName": "新奥六合彩", "rebate": 101.0}]

        with pytest.raises(ValueError, match="退水比例必须在 0-100 之间"):
            service.validate_game_settings(game_settings)


class TestPydanticValidation:
    """测试 Pydantic 模型验证"""

    def test_update_rebate_request_validation(self):
        """测试更新退水配置请求验证"""
        from biz.users.api.rebate_api import UpdateRebateRequest, GameSettingItem
        from pydantic import ValidationError

        # 测试 earnRebate 超出范围
        with pytest.raises(ValidationError):
            UpdateRebateRequest(
                independentRebate=True,
                earnRebate=150.0,  # 超出范围
                gameSettings=[
                    GameSettingItem(gameName="新奥六合彩", rebate=2.5)
                ]
            )

        # 测试 gameSettings 为空
        with pytest.raises(ValidationError):
            UpdateRebateRequest(
                independentRebate=True,
                earnRebate=5.0,
                gameSettings=[]  # 空数组
            )

        # 测试无效的游戏名称
        with pytest.raises(ValidationError):
            UpdateRebateRequest(
                independentRebate=True,
                earnRebate=5.0,
                gameSettings=[
                    GameSettingItem(gameName="Invalid Game", rebate=2.5)
                ]
            )

        # 测试有效请求
        valid_request = UpdateRebateRequest(
            independentRebate=True,
            earnRebate=5.5,
            gameSettings=[
                GameSettingItem(gameName="新奥六合彩", rebate=2.5),
                GameSettingItem(gameName="168澳洲幸运8", rebate=3.0)
            ]
        )
        assert valid_request.independentRebate is True
        assert valid_request.earnRebate == 5.5
        assert len(valid_request.gameSettings) == 2
