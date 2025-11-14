"""
OddsService - 赔率业务逻辑层
处理赔率查询、更新、管理等业务逻辑
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
import logging

from biz.odds.repo.odds_repo import OddsRepository

logger = logging.getLogger(__name__)


class OddsService:
    """赔率服务"""

    def __init__(self, odds_repo: OddsRepository):
        self.odds_repo = odds_repo

    async def get_odds(
        self,
        bet_type: str,
        game_type: str = "lucky8"
    ) -> Optional[Dict[str, Any]]:
        """获取赔率配置"""
        return await self.odds_repo.get_odds(bet_type, game_type)

    async def get_all_odds(
        self,
        game_type: str = "lucky8",
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取所有赔率配置"""
        return await self.odds_repo.get_all_odds(game_type, status)

    async def update_odds(
        self,
        bet_type: str,
        game_type: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        更新赔率配置
        返回: {
            "success": bool,
            "odds": Dict,
            "error": str
        }
        """
        try:
            # 检查赔率配置是否存在
            if not await self.odds_repo.exists(bet_type, game_type):
                return {
                    "success": False,
                    "odds": None,
                    "error": f"赔率配置不存在: {bet_type} ({game_type})"
                }

            # 更新赔率
            odds = await self.odds_repo.update_odds(bet_type, game_type, updates)

            logger.info(f"✅ 更新赔率: {bet_type} ({game_type}) 更新内容: {updates}")

            return {
                "success": True,
                "odds": odds,
                "error": None
            }
        except Exception as e:
            logger.error(f"❌ 更新赔率失败: {str(e)}")
            return {
                "success": False,
                "odds": None,
                "error": str(e)
            }

    async def create_odds(
        self,
        bet_type: str,
        odds: Decimal,
        game_type: str = "lucky8",
        min_bet: Decimal = Decimal("10.00"),
        max_bet: Decimal = Decimal("10000.00"),
        period_max: Decimal = Decimal("50000.00"),
        description: Optional[str] = None,
        tema_odds: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建赔率配置
        返回: {
            "success": bool,
            "odds": Dict,
            "error": str
        }
        """
        try:
            # 检查是否已存在
            if await self.odds_repo.exists(bet_type, game_type):
                return {
                    "success": False,
                    "odds": None,
                    "error": f"赔率配置已存在: {bet_type} ({game_type})"
                }

            # 创建赔率数据
            odds_data = {
                "bet_type": bet_type,
                "odds": odds,
                "game_type": game_type,
                "min_bet": min_bet,
                "max_bet": max_bet,
                "period_max": period_max,
                "description": description,
                "tema_odds": tema_odds
            }

            odds_config = await self.odds_repo.create_odds(odds_data)

            logger.info(f"✅ 创建赔率配置: {bet_type} ({game_type}) 赔率: {odds}")

            return {
                "success": True,
                "odds": odds_config,
                "error": None
            }
        except Exception as e:
            logger.error(f"❌ 创建赔率配置失败: {str(e)}")
            return {
                "success": False,
                "odds": None,
                "error": str(e)
            }

    async def update_odds_value(
        self,
        bet_type: str,
        game_type: str,
        odds: Decimal
    ) -> Dict[str, Any]:
        """更新赔率值（快捷方法）"""
        return await self.update_odds(bet_type, game_type, {"odds": odds})

    async def update_bet_limits(
        self,
        bet_type: str,
        game_type: str,
        min_bet: Optional[Decimal] = None,
        max_bet: Optional[Decimal] = None,
        period_max: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """更新投注限额"""
        updates = {}
        if min_bet is not None:
            updates["min_bet"] = min_bet
        if max_bet is not None:
            updates["max_bet"] = max_bet
        if period_max is not None:
            updates["period_max"] = period_max

        return await self.update_odds(bet_type, game_type, updates)

    async def update_status(
        self,
        bet_type: str,
        game_type: str,
        status: str
    ) -> Optional[Dict[str, Any]]:
        """更新赔率状态"""
        if status not in ["active", "inactive"]:
            raise ValueError("状态必须是active或inactive")

        return await self.odds_repo.update_status(bet_type, game_type, status)

    async def get_odds_by_types(
        self,
        bet_types: List[str],
        game_type: str = "lucky8"
    ) -> List[Dict[str, Any]]:
        """批量获取赔率配置"""
        return await self.odds_repo.get_odds_by_types(bet_types, game_type)

    async def delete_odds(
        self,
        bet_type: str,
        game_type: str = "lucky8"
    ) -> bool:
        """删除赔率配置（需要超级管理员权限）"""
        logger.warning(f"⚠️ 删除赔率配置: {bet_type} ({game_type})")
        return await self.odds_repo.delete_odds(bet_type, game_type)

    async def get_odds_for_bet(
        self,
        bet_type: str,
        bet_number: Optional[int],
        game_type: str = "lucky8"
    ) -> Optional[Decimal]:
        """
        获取投注的实际赔率
        对于特码投注，可能根据号码有不同赔率
        """
        odds_config = await self.odds_repo.get_odds(bet_type, game_type)
        if not odds_config:
            return None

        # 如果是特码且有tema_odds配置，根据号码返回对应赔率
        if bet_type == "tema" and bet_number is not None:
            tema_odds = odds_config.get("tema_odds")
            if tema_odds and isinstance(tema_odds, dict):
                # 尝试获取特定号码的赔率
                number_odds = tema_odds.get(str(bet_number))
                if number_odds:
                    return Decimal(str(number_odds))

        # 返回默认赔率
        return odds_config["odds"]

    async def validate_bet_amount(
        self,
        bet_type: str,
        bet_amount: Decimal,
        game_type: str = "lucky8"
    ) -> Dict[str, Any]:
        """
        验证投注金额是否在限额范围内
        返回: {
            "valid": bool,
            "error": str
        }
        """
        odds_config = await self.odds_repo.get_odds(bet_type, game_type)
        if not odds_config:
            return {
                "valid": False,
                "error": f"赔率配置不存在: {bet_type}"
            }

        min_bet = odds_config["min_bet"]
        max_bet = odds_config["max_bet"]

        if bet_amount < min_bet:
            return {
                "valid": False,
                "error": f"投注金额不能低于 {min_bet}"
            }

        if bet_amount > max_bet:
            return {
                "valid": False,
                "error": f"投注金额不能超过 {max_bet}"
            }

        return {
            "valid": True,
            "error": None
        }
