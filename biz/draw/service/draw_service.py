"""
DrawService - 开奖业务逻辑层
处理开奖记录创建、查询、历史管理等业务逻辑
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from biz.draw.repo.draw_repo import DrawRepository

logger = logging.getLogger(__name__)


class DrawService:
    """开奖服务"""

    def __init__(self, draw_repo: DrawRepository):
        self.draw_repo = draw_repo

    async def create_draw(
        self,
        draw_number: int,
        issue: str,
        draw_code: str,
        game_type: str = "lucky8",
        is_random: bool = False,
        chat_id: str = "system",
        bet_count: int = 0,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        创建开奖记录
        返回: {
            "success": bool,
            "draw": Dict,
            "error": str
        }
        """
        try:
            # 检查期号是否已存在
            if await self.draw_repo.exists_issue(issue, game_type, chat_id):
                return {
                    "success": False,
                    "draw": None,
                    "error": f"期号 {issue} 已存在"
                }

            # 创建开奖数据
            draw_data = {
                "draw_number": draw_number,
                "issue": issue,
                "draw_code": draw_code,
                "game_type": game_type,
                "is_random": is_random,
                "chat_id": chat_id,
                "bet_count": bet_count,
                "timestamp": timestamp or datetime.now()
            }

            draw = await self.draw_repo.create_draw(draw_data)

            logger.info(
                f"✅ 创建开奖记录: {game_type} 期号 {issue} "
                f"号码 {draw_number} ({draw_code})"
            )

            return {
                "success": True,
                "draw": draw,
                "error": None
            }
        except Exception as e:
            logger.error(f"❌ 创建开奖记录失败: {str(e)}")
            return {
                "success": False,
                "draw": None,
                "error": str(e)
            }

    async def get_latest_draw(
        self,
        game_type: str = "lucky8",
        chat_id: str = "system"
    ) -> Optional[Dict[str, Any]]:
        """获取最新开奖记录"""
        return await self.draw_repo.get_latest_draw(game_type, chat_id)

    async def get_draw_by_issue(
        self,
        issue: str,
        game_type: str = "lucky8",
        chat_id: str = "system"
    ) -> Optional[Dict[str, Any]]:
        """根据期号获取开奖记录"""
        return await self.draw_repo.get_draw_by_issue(issue, game_type, chat_id)

    async def get_draw_history(
        self,
        game_type: str = "lucky8",
        chat_id: str = "system",
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取开奖历史"""
        return await self.draw_repo.get_draw_history(game_type, chat_id, skip, limit)

    async def get_draw_history_by_date(
        self,
        game_type: str,
        chat_id: str,
        date: str,
        skip: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """按日期过滤获取开奖历史"""
        return await self.draw_repo.get_draw_history_by_date(game_type, chat_id, date, skip, limit)

    async def get_recent_draws(
        self,
        game_type: str = "lucky8",
        chat_id: str = "system",
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """获取最近N期开奖记录"""
        return await self.draw_repo.get_recent_draws(game_type, chat_id, count)

    async def update_bet_count(
        self,
        draw_id: int,
        bet_count: int
    ) -> Optional[Dict[str, Any]]:
        """更新投注数量"""
        return await self.draw_repo.update_bet_count(draw_id, bet_count)

    async def get_draw_stats(
        self,
        game_type: str = "lucky8",
        chat_id: str = "system"
    ) -> Dict[str, Any]:
        """
        获取开奖统计信息
        """
        try:
            total_count = await self.draw_repo.count_draws(game_type, chat_id)
            latest_draw = await self.draw_repo.get_latest_draw(game_type, chat_id)

            return {
                "total_count": total_count,
                "latest_issue": latest_draw["issue"] if latest_draw else None,
                "latest_draw_number": latest_draw["draw_number"] if latest_draw else None,
                "latest_timestamp": latest_draw["timestamp"] if latest_draw else None,
                "game_type": game_type,
                "chat_id": chat_id
            }
        except Exception as e:
            logger.error(f"❌ 获取开奖统计失败: {str(e)}")
            return {
                "total_count": 0,
                "latest_issue": None,
                "latest_draw_number": None,
                "latest_timestamp": None,
                "game_type": game_type,
                "chat_id": chat_id
            }

    async def count_draws_by_date(
        self,
        game_type: str,
        chat_id: str,
        date: str
    ) -> int:
        """按日期统计开奖记录数量"""
        return await self.draw_repo.count_draws_by_date(game_type, chat_id, date)

    async def delete_draw(self, draw_id: int) -> bool:
        """删除开奖记录（需要超级管理员权限）"""
        logger.warning(f"⚠️ 删除开奖记录: {draw_id}")
        return await self.draw_repo.delete_draw(draw_id)

    async def generate_next_issue(
        self,
        game_type: str = "lucky8",
        chat_id: str = "system"
    ) -> str:
        """
        生成下一期期号
        TODO: 实际需要根据游戏类型和当前时间生成正确的期号
        """
        latest_draw = await self.draw_repo.get_latest_draw(game_type, chat_id)

        if not latest_draw:
            # 首期
            if game_type == "lucky8":
                # Lucky8格式: YYYYMMDD-001
                today = datetime.now().strftime("%Y%m%d")
                return f"{today}-001"
            elif game_type == "liuhecai":
                # 六合彩格式: YYYY001
                year = datetime.now().year
                return f"{year}001"

        # 解析上一期期号并递增
        last_issue = latest_draw["issue"]

        if game_type == "lucky8":
            # YYYYMMDD-NNN
            date_part, num_part = last_issue.rsplit("-", 1)
            today = datetime.now().strftime("%Y%m%d")

            if date_part == today:
                # 同一天，期号递增
                next_num = int(num_part) + 1
                return f"{today}-{next_num:03d}"
            else:
                # 新的一天，从001开始
                return f"{today}-001"

        elif game_type == "liuhecai":
            # YYYYNNN
            year_part = last_issue[:4]
            num_part = last_issue[4:]
            current_year = str(datetime.now().year)

            if year_part == current_year:
                # 同一年，期号递增
                next_num = int(num_part) + 1
                return f"{current_year}{next_num:03d}"
            else:
                # 新的一年，从001开始
                return f"{current_year}001"

        return last_issue
