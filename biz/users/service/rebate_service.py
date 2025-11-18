"""
退水配置 Service
"""
from typing import Optional, Dict, Any, List
from biz.users.repo.rebate_repo import RebateRepository
from base.game_name_mapper import validate_game_name


class RebateService:
    def __init__(self, rebate_repo: RebateRepository):
        self.rebate_repo = rebate_repo

    def validate_game_settings(self, game_settings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        验证游戏退水配置
        """
        if not game_settings:
            raise ValueError("游戏退水配置不能为空")

        for game in game_settings:
            # 验证必需字段
            if "gameName" not in game or "rebate" not in game:
                raise ValueError("游戏退水配置缺少必需字段: gameName, rebate")

            # 验证游戏名称（必须是中文）
            try:
                validate_game_name(game["gameName"])
            except ValueError as e:
                raise ValueError(f"无效的游戏名称: {str(e)}")

            # 验证 rebate 范围
            rebate = game["rebate"]
            if not isinstance(rebate, (int, float)) or rebate < 0 or rebate > 100:
                raise ValueError(f"退水比例必须在 0-100 之间，收到: {rebate}")

        return game_settings

    async def get_rebate_settings(self, account: str) -> Optional[Dict[str, Any]]:
        """
        获取退水配置
        """
        return await self.rebate_repo.get_rebate_settings(account)

    async def update_rebate_settings(
        self,
        account: str,
        independent_rebate: bool,
        earn_rebate: float,
        game_settings: List[Dict[str, Any]]
    ) -> bool:
        """
        更新退水配置
        """
        # 验证 earnRebate 范围
        if not isinstance(earn_rebate, (int, float)) or earn_rebate < 0 or earn_rebate > 100:
            raise ValueError(f"赚取退水比例必须在 0-100 之间，收到: {earn_rebate}")

        # 验证游戏退水配置
        validated_game_settings = self.validate_game_settings(game_settings)

        return await self.rebate_repo.update_rebate_settings(
            account, independent_rebate, earn_rebate, validated_game_settings
        )
