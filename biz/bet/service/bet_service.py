"""
BetService - 投注业务逻辑层
处理下注、结算、历史查询等业务逻辑
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
import logging
import uuid

from biz.bet.repo.bet_repo import BetRepository

logger = logging.getLogger(__name__)


class BetService:
    """投注服务"""

    def __init__(self, bet_repo: BetRepository):
        self.bet_repo = bet_repo

    async def place_bet(
        self,
        user_id: str,
        username: str,
        chat_id: str,
        game_type: str,
        lottery_type: str,
        bet_amount: Decimal,
        odds: Decimal,
        bet_number: Optional[int] = None,
        issue: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        下注
        返回: {
            "success": bool,
            "bet": Dict,
            "error": str
        }
        """
        try:
            # 生成投注ID
            bet_id = f"bet_{int(datetime.now().timestamp() * 1000)}_{uuid.uuid4().hex[:8]}"

            # 创建投注数据
            bet_data = {
                "id": bet_id,
                "user_id": user_id,
                "username": username,
                "chat_id": chat_id,
                "game_type": game_type,
                "lottery_type": lottery_type,
                "bet_number": bet_number,
                "bet_amount": bet_amount,
                "odds": odds,
                "issue": issue,
                "status": "active",
                "result": "pending",
                "pnl": Decimal("0.00")
            }

            # 创建投注记录
            bet = await self.bet_repo.create_bet(bet_data)

            logger.info(
                f"💰 下注成功: {username} ({user_id}) 在群 {chat_id} "
                f"下注 {lottery_type} {bet_number or ''} 金额 {bet_amount}"
            )

            return {
                "success": True,
                "bet": bet,
                "error": None
            }
        except Exception as e:
            logger.error(f"❌ 下注失败: {str(e)}")
            return {
                "success": False,
                "bet": None,
                "error": str(e)
            }

    async def settle_bets(
        self,
        chat_id: str,
        issue: str,
        draw_number: int,
        draw_code: str,
        game_type: str
    ) -> List[Dict[str, Any]]:
        """
        结算投注
        返回: List of {
            "bet_id": str,
            "user_id": str,
            "result": str,
            "pnl": Decimal
        }
        """
        # 获取待结算的投注
        pending_bets = await self.bet_repo.get_pending_bets(chat_id, issue)

        settle_results = []

        for bet in pending_bets:
            # 计算输赢（这里需要调用game_logic进行判断）
            # 暂时简化处理
            result, pnl = await self._calculate_bet_result(
                bet, draw_number, draw_code, game_type
            )

            # 更新投注记录
            settled_bet = await self.bet_repo.settle_bet(
                bet_id=bet["id"],
                result=result,
                pnl=pnl,
                draw_number=draw_number,
                draw_code=draw_code
            )

            settle_results.append({
                "bet_id": bet["id"],
                "user_id": bet["user_id"],
                "username": bet["username"],
                "chat_id": bet["chat_id"],
                "result": result,
                "pnl": pnl,
                "bet_amount": bet["bet_amount"]
            })

            logger.info(
                f"✅ 结算投注: {bet['username']} {bet['lottery_type']} "
                f"结果:{result} 盈亏:{pnl}"
            )

        return settle_results

    async def _calculate_bet_result(
        self,
        bet: Dict[str, Any],
        draw_number: int,
        draw_code: str,
        game_type: str
    ) -> tuple[str, Decimal]:
        """
        计算投注结果
        TODO: 这里需要调用game_logic模块的实际计算逻辑
        """
        # 占位逻辑，实际需要根据lottery_type和draw_number计算
        # 这里简化为随机结果
        import random

        if random.random() > 0.5:
            # 赢
            pnl = bet["bet_amount"] * bet["odds"] - bet["bet_amount"]
            return "win", round(pnl, 2)
        else:
            # 输
            pnl = -bet["bet_amount"]
            return "lose", round(pnl, 2)

    async def get_bet_history(
        self,
        user_id: str,
        chat_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取投注历史"""
        return await self.bet_repo.get_user_bets(user_id, chat_id, skip, limit)

    async def get_bet(self, bet_id: str) -> Optional[Dict[str, Any]]:
        """获取投注详情"""
        return await self.bet_repo.get_bet(bet_id)

    async def cancel_bet(
        self,
        bet_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        取消投注
        返回: {
            "success": bool,
            "bet": Dict,
            "error": str
        }
        """
        try:
            # 获取投注信息
            bet = await self.bet_repo.get_bet(bet_id)
            if not bet:
                return {
                    "success": False,
                    "bet": None,
                    "error": "投注不存在"
                }

            # 检查是否是本人的投注
            if bet["user_id"] != user_id:
                return {
                    "success": False,
                    "bet": None,
                    "error": "无权取消此投注"
                }

            # 取消投注
            cancelled_bet = await self.bet_repo.cancel_bet(bet_id)
            if not cancelled_bet:
                return {
                    "success": False,
                    "bet": None,
                    "error": "投注已结算，无法取消"
                }

            logger.info(f"🚫 取消投注: {bet['username']} 投注ID {bet_id}")

            return {
                "success": True,
                "bet": cancelled_bet,
                "error": None
            }
        except Exception as e:
            logger.error(f"❌ 取消投注失败: {str(e)}")
            return {
                "success": False,
                "bet": None,
                "error": str(e)
            }

    async def get_user_stats(
        self,
        user_id: str,
        chat_id: str
    ) -> Dict[str, Any]:
        """获取用户投注统计"""
        return await self.bet_repo.get_user_bet_stats(user_id, chat_id)

    async def get_chat_bets(
        self,
        chat_id: str,
        skip: int = 0,
        limit: int = 100,
        result_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取群聊投注记录（管理后台用）"""
        return await self.bet_repo.get_chat_bets(chat_id, skip, limit, result_filter)
