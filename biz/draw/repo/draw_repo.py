"""
DrawRepository - 开奖历史数据访问层
主键：id (自增)
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class DrawRepository:
    """开奖Repository"""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def create_draw(self, draw_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建开奖记录"""
        async with self._session_factory() as session:
            query = text("""
                INSERT INTO draw_history (
                    draw_number, issue, draw_code, game_type, is_random,
                    chat_id, bet_count, timestamp, created_at
                ) VALUES (
                    :draw_number, :issue, :draw_code, :game_type, :is_random,
                    :chat_id, :bet_count, :timestamp, NOW()
                )
            """)

            params = {
                "draw_number": draw_data["draw_number"],
                "issue": draw_data["issue"],
                "draw_code": draw_data["draw_code"],
                "game_type": draw_data.get("game_type", "lucky8"),
                "is_random": draw_data.get("is_random", False),
                "chat_id": draw_data.get("chat_id", "system"),
                "bet_count": draw_data.get("bet_count", 0),
                "timestamp": draw_data.get("timestamp", datetime.now())
            }

            await session.execute(query, params)
            await session.commit()

            # 获取最后插入的ID
            result = await session.execute(text("SELECT LAST_INSERT_ID() as id"))
            row = result.fetchone()
            draw_id = row[0] if row else None

            return await self.get_draw(draw_id)

    async def get_draw(self, draw_id: int) -> Optional[Dict[str, Any]]:
        """获取开奖记录"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM draw_history
                WHERE id = :draw_id
            """)
            result = await session.execute(query, {"draw_id": draw_id})
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            return None

    async def get_draw_by_issue(
        self,
        issue: str,
        game_type: str = "lucky8",
        chat_id: str = "system"
    ) -> Optional[Dict[str, Any]]:
        """根据期号获取开奖记录"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM draw_history
                WHERE issue = :issue AND game_type = :game_type AND chat_id = :chat_id
                LIMIT 1
            """)
            result = await session.execute(query, {
                "issue": issue,
                "game_type": game_type,
                "chat_id": chat_id
            })
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            return None

    async def get_latest_draw(
        self,
        game_type: str = "lucky8",
        chat_id: str = "system"
    ) -> Optional[Dict[str, Any]]:
        """获取最新开奖记录"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM draw_history
                WHERE game_type = :game_type AND chat_id = :chat_id
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            result = await session.execute(query, {
                "game_type": game_type,
                "chat_id": chat_id
            })
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            return None

    async def get_draw_history(
        self,
        game_type: str = "lucky8",
        chat_id: str = "system",
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取开奖历史"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM draw_history
                WHERE game_type = :game_type AND chat_id = :chat_id
                ORDER BY timestamp DESC
                LIMIT :limit OFFSET :skip
            """)
            result = await session.execute(query, {
                "game_type": game_type,
                "chat_id": chat_id,
                "skip": skip,
                "limit": limit
            })
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def get_recent_draws(
        self,
        game_type: str = "lucky8",
        chat_id: str = "system",
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """获取最近N期开奖记录"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM draw_history
                WHERE game_type = :game_type AND chat_id = :chat_id
                ORDER BY timestamp DESC
                LIMIT :count
            """)
            result = await session.execute(query, {
                "game_type": game_type,
                "chat_id": chat_id,
                "count": count
            })
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def count_draws(
        self,
        game_type: str = "lucky8",
        chat_id: str = "system"
    ) -> int:
        """统计开奖记录数量"""
        async with self._session_factory() as session:
            query = text("""
                SELECT COUNT(*) as count FROM draw_history
                WHERE game_type = :game_type AND chat_id = :chat_id
            """)
            result = await session.execute(query, {
                "game_type": game_type,
                "chat_id": chat_id
            })
            row = result.fetchone()
            return row[0] if row else 0

    async def exists_issue(
        self,
        issue: str,
        game_type: str = "lucky8",
        chat_id: str = "system"
    ) -> bool:
        """检查期号是否已存在"""
        async with self._session_factory() as session:
            query = text("""
                SELECT 1 FROM draw_history
                WHERE issue = :issue AND game_type = :game_type AND chat_id = :chat_id
                LIMIT 1
            """)
            result = await session.execute(query, {
                "issue": issue,
                "game_type": game_type,
                "chat_id": chat_id
            })
            return result.fetchone() is not None

    async def update_bet_count(
        self,
        draw_id: int,
        bet_count: int
    ) -> Optional[Dict[str, Any]]:
        """更新投注数量"""
        async with self._session_factory() as session:
            query = text("""
                UPDATE draw_history
                SET bet_count = :bet_count
                WHERE id = :draw_id
            """)
            await session.execute(query, {"draw_id": draw_id, "bet_count": bet_count})
            await session.commit()

            return await self.get_draw(draw_id)

    async def delete_draw(self, draw_id: int) -> bool:
        """删除开奖记录"""
        async with self._session_factory() as session:
            query = text("""
                DELETE FROM draw_history
                WHERE id = :draw_id
            """)
            result = await session.execute(query, {"draw_id": draw_id})
            await session.commit()
            return result.rowcount > 0

    async def create(self, draw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建开奖记录（通用方法，兼容GameService）

        Args:
            draw_data: 开奖数据，包含以下字段：
                - chat_id: 群聊ID
                - game_type: 游戏类型（lucky8/liuhecai）
                - issue: 期号
                - draw_number: 开奖番数（1-4）
                - draw_code: 完整开奖号码
                - special_number: 特码（1-49）
                - draw_time: 开奖时间

        Returns:
            Dict: 创建的开奖记录
        """
        async with self._session_factory() as session:
            query = text("""
                INSERT INTO draw_history (
                    draw_number, issue, draw_code, game_type, is_random,
                    chat_id, bet_count, timestamp, special_number, created_at
                ) VALUES (
                    :draw_number, :issue, :draw_code, :game_type, :is_random,
                    :chat_id, :bet_count, :timestamp, :special_number, NOW()
                )
            """)

            params = {
                "draw_number": draw_data.get("draw_number"),
                "issue": draw_data["issue"],
                "draw_code": draw_data["draw_code"],
                "game_type": draw_data.get("game_type", "lucky8"),
                "is_random": draw_data.get("is_random", False),
                "chat_id": draw_data["chat_id"],
                "bet_count": draw_data.get("bet_count", 0),
                "timestamp": draw_data.get("draw_time", datetime.now()),
                "special_number": draw_data.get("special_number")
            }

            await session.execute(query, params)
            await session.commit()

            # 获取最后插入的ID
            result = await session.execute(text("SELECT LAST_INSERT_ID() as id"))
            row = result.fetchone()
            draw_id = row[0] if row else None

            return await self.get_draw(draw_id)

    async def get_recent_draws(
        self,
        chat_id: str,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        获取最近N期开奖记录（兼容GameService）

        Args:
            chat_id: 群聊ID
            limit: 数量限制

        Returns:
            List[Dict]: 开奖记录列表
        """
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM draw_history
                WHERE chat_id = :chat_id
                ORDER BY timestamp DESC
                LIMIT :limit
            """)
            result = await session.execute(query, {
                "chat_id": chat_id,
                "limit": limit
            })
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def get_latest_draw_by_date(
        self,
        date_str: str,
        game_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取某日最新的开奖记录（用于生成期号）

        Args:
            date_str: 日期字符串（YYYYMMDD）
            game_type: 游戏类型

        Returns:
            Dict: 开奖记录
        """
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM draw_history
                WHERE issue LIKE :pattern AND game_type = :game_type
                ORDER BY issue DESC
                LIMIT 1
            """)
            result = await session.execute(query, {
                "pattern": f"{date_str}%",
                "game_type": game_type
            })
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            return None
