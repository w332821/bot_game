"""
BetRepository - 投注数据访问层
主键：id
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class BetRepository:
    """投注Repository"""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    def _parse_json_fields(self, bet_data: Dict[str, Any]) -> None:
        """解析投注数据中的 JSON 字段"""
        import json

        # 解析 bet_details
        if bet_data.get("bet_details") and isinstance(bet_data["bet_details"], str):
            try:
                bet_data["bet_details"] = json.loads(bet_data["bet_details"])
            except:
                bet_data["bet_details"] = None

    async def create_bet(self, bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建投注记录"""
        async with self._session_factory() as session:
            query = text("""
                INSERT INTO bets (
                    id, user_id, username, chat_id, game_type, lottery_type,
                    bet_number, bet_amount, valid_amount, odds, status, result, pnl, rebate,
                    issue, created_at
                ) VALUES (
                    :id, :user_id, :username, :chat_id, :game_type, :lottery_type,
                    :bet_number, :bet_amount, :valid_amount, :odds, :status, :result, :pnl, :rebate,
                    :issue, NOW()
                )
            """)

            params = {
                "id": bet_data["id"],
                "user_id": bet_data["user_id"],
                "username": bet_data["username"],
                "chat_id": bet_data["chat_id"],
                "game_type": bet_data.get("game_type", "lucky8"),
                "lottery_type": bet_data["lottery_type"],
                "bet_number": bet_data.get("bet_number"),
                "bet_amount": bet_data["bet_amount"],
                "valid_amount": bet_data.get("valid_amount", bet_data["bet_amount"]),
                "odds": bet_data["odds"],
                "status": bet_data.get("status", "active"),
                "result": bet_data.get("result", "pending"),
                "pnl": bet_data.get("pnl", Decimal("0.00")),
                "rebate": bet_data.get("rebate", Decimal("0.00")),
                "issue": bet_data.get("issue")
            }

            await session.execute(query, params)
            await session.commit()

            return await self.get_bet(bet_data["id"])

    async def get_bet(self, bet_id: str) -> Optional[Dict[str, Any]]:
        """获取投注记录"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM bets
                WHERE id = :bet_id
            """)
            result = await session.execute(query, {"bet_id": bet_id})
            row = result.fetchone()
            if row:
                data = dict(row._mapping)
                self._parse_json_fields(data)
                return data
            return None

    async def get_user_bets(
        self,
        user_id: str,
        chat_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取用户投注记录"""
        async with self._session_factory() as session:
            if status:
                query = text("""
                    SELECT * FROM bets
                    WHERE user_id = :user_id AND chat_id = :chat_id AND status = :status
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :skip
                """)
                params = {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "status": status,
                    "skip": skip,
                    "limit": limit
                }
            else:
                query = text("""
                    SELECT * FROM bets
                    WHERE user_id = :user_id AND chat_id = :chat_id
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :skip
                """)
                params = {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "skip": skip,
                    "limit": limit
                }

            result = await session.execute(query, params)
            rows = result.fetchall()
            bets = []
            for row in rows:
                data = dict(row._mapping)
                self._parse_json_fields(data)
                bets.append(data)
            return bets

    async def get_chat_bets(
        self,
        chat_id: str,
        skip: int = 0,
        limit: int = 100,
        result_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取群聊所有投注记录"""
        async with self._session_factory() as session:
            if result_filter:
                query = text("""
                    SELECT * FROM bets
                    WHERE chat_id = :chat_id AND result = :result_filter
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :skip
                """)
                params = {
                    "chat_id": chat_id,
                    "result_filter": result_filter,
                    "skip": skip,
                    "limit": limit
                }
            else:
                query = text("""
                    SELECT * FROM bets
                    WHERE chat_id = :chat_id
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :skip
                """)
                params = {"chat_id": chat_id, "skip": skip, "limit": limit}

            result = await session.execute(query, params)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def get_pending_bets(
        self,
        chat_id: Optional[str] = None,
        issue: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取待结算的投注记录"""
        async with self._session_factory() as session:
            if chat_id and issue:
                query = text("""
                    SELECT * FROM bets
                    WHERE chat_id = :chat_id AND issue = :issue
                          AND status = 'active' AND result = 'pending'
                    ORDER BY created_at ASC
                """)
                params = {"chat_id": chat_id, "issue": issue}
            elif chat_id:
                query = text("""
                    SELECT * FROM bets
                    WHERE chat_id = :chat_id
                          AND status = 'active' AND result = 'pending'
                    ORDER BY created_at ASC
                """)
                params = {"chat_id": chat_id}
            else:
                query = text("""
                    SELECT * FROM bets
                    WHERE status = 'active' AND result = 'pending'
                    ORDER BY created_at ASC
                """)
                params = {}

            result = await session.execute(query, params)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def settle_bet(
        self,
        bet_id: str,
        result: str,
        pnl: Decimal,
        draw_number: Optional[int],
        draw_code: Optional[str],
        issue: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """结算投注"""
        async with self._session_factory() as session:
            # 如果提供了期号，则同时更新期号
            if issue:
                query = text("""
                    UPDATE bets
                    SET result = :result, pnl = :pnl,
                        draw_number = :draw_number, draw_code = :draw_code,
                        issue = :issue, settled_at = NOW()
                    WHERE id = :bet_id
                """)
                params = {
                    "bet_id": bet_id,
                    "result": result,
                    "pnl": pnl,
                    "draw_number": draw_number,
                    "draw_code": draw_code,
                    "issue": issue
                }
            else:
                query = text("""
                    UPDATE bets
                    SET result = :result, pnl = :pnl,
                        draw_number = :draw_number, draw_code = :draw_code,
                        settled_at = NOW()
                    WHERE id = :bet_id
                """)
                params = {
                    "bet_id": bet_id,
                    "result": result,
                    "pnl": pnl,
                    "draw_number": draw_number,
                    "draw_code": draw_code
                }
            await session.execute(query, params)
            await session.commit()

            return await self.get_bet(bet_id)

    async def cancel_bet(self, bet_id: str) -> Optional[Dict[str, Any]]:
        """取消投注"""
        async with self._session_factory() as session:
            query = text("""
                UPDATE bets
                SET status = 'cancelled', result = 'cancelled'
                WHERE id = :bet_id AND result = 'pending'
            """)
            result = await session.execute(query, {"bet_id": bet_id})
            await session.commit()

            if result.rowcount == 0:
                return None

            return await self.get_bet(bet_id)

    async def count_user_bets(
        self,
        user_id: str,
        chat_id: str,
        status: Optional[str] = None
    ) -> int:
        """统计用户投注数量"""
        async with self._session_factory() as session:
            if status:
                query = text("""
                    SELECT COUNT(*) as count FROM bets
                    WHERE user_id = :user_id AND chat_id = :chat_id AND status = :status
                """)
                params = {"user_id": user_id, "chat_id": chat_id, "status": status}
            else:
                query = text("""
                    SELECT COUNT(*) as count FROM bets
                    WHERE user_id = :user_id AND chat_id = :chat_id
                """)
                params = {"user_id": user_id, "chat_id": chat_id}

            result = await session.execute(query, params)
            row = result.fetchone()
            return row[0] if row else 0

    async def get_user_bet_stats(
        self,
        user_id: str,
        chat_id: str
    ) -> Dict[str, Any]:
        """获取用户投注统计"""
        async with self._session_factory() as session:
            query = text("""
                SELECT
                    COUNT(*) as total_count,
                    SUM(bet_amount) as total_amount,
                    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as win_count,
                    SUM(CASE WHEN result = 'win' THEN pnl ELSE 0 END) as total_win,
                    SUM(CASE WHEN result = 'lose' THEN pnl ELSE 0 END) as total_lose,
                    SUM(pnl) as total_pnl
                FROM bets
                WHERE user_id = :user_id AND chat_id = :chat_id AND status = 'active'
            """)
            result = await session.execute(query, {"user_id": user_id, "chat_id": chat_id})
            row = result.fetchone()

            if row:
                return {
                    "total_count": row[0] or 0,
                    "total_amount": float(row[1] or 0),
                    "win_count": row[2] or 0,
                    "total_win": float(row[3] or 0),
                    "total_lose": float(row[4] or 0),
                    "total_pnl": float(row[5] or 0),
                    "win_rate": (row[2] / row[0] * 100) if row[0] > 0 else 0
                }
            return {
                "total_count": 0,
                "total_amount": 0,
                "win_count": 0,
                "total_win": 0,
                "total_lose": 0,
                "total_pnl": 0,
                "win_rate": 0
            }

    async def create(self, bet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建投注记录（通用方法，兼容GameService）

        Args:
            bet_data: 投注数据，包含以下字段：
                - user_id: 用户ID
                - chat_id: 群聊ID
                - game_type: 游戏类型（lucky8/liuhecai）
                - bet_type: 下注类型（fan/zheng/nian等）
                - amount: 下注金额
                - odds: 赔率
                - status: 状态（pending）
                - draw_issue: 期号
                - bet_details: 投注详情（dict/JSON）

        Returns:
            Dict: 创建的投注记录
        """
        from uuid import uuid4
        from base.json_encoder import safe_json_dumps

        async with self._session_factory() as session:
            bet_id = str(uuid4())

            # 从bet_details或直接字段获取username
            username = bet_data.get('username', 'unknown')

            query = text("""
                INSERT INTO bets (
                    id, user_id, username, chat_id, game_type, lottery_type,
                    bet_number, bet_amount, valid_amount, odds, status, result, rebate,
                    issue, bet_details, created_at
                ) VALUES (
                    :id, :user_id, :username, :chat_id, :game_type, :lottery_type,
                    :bet_number, :bet_amount, :valid_amount, :odds, :status, :result, :rebate,
                    :issue, :bet_details, NOW()
                )
            """)

            bet_amount = bet_data["amount"]
            params = {
                "id": bet_id,
                "user_id": bet_data["user_id"],
                "username": username,
                "chat_id": bet_data["chat_id"],
                "game_type": bet_data.get("game_type", "lucky8"),
                "lottery_type": bet_data.get("bet_type", "unknown"),
                "bet_number": bet_data.get("bet_number"),
                "bet_amount": bet_amount,
                "valid_amount": bet_data.get("valid_amount", bet_amount),
                "odds": bet_data["odds"],
                "status": "active",
                "result": bet_data.get("status", "pending"),
                "rebate": bet_data.get("rebate", Decimal("0.00")),
                "issue": bet_data.get("draw_issue"),
                "bet_details": safe_json_dumps(bet_data.get("bet_details")) if bet_data.get("bet_details") else None
            }

            await session.execute(query, params)
            await session.commit()

            return await self.get_bet(bet_id)

    async def get_user_bets_since(
        self,
        user_id: str,
        chat_id: str,
        since_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        获取用户从某个时间开始的投注记录

        Args:
            user_id: 用户ID
            chat_id: 群聊ID
            since_time: 起始时间

        Returns:
            List[Dict]: 投注记录列表
        """
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM bets
                WHERE user_id = :user_id AND chat_id = :chat_id
                      AND created_at >= :since_time
                ORDER BY created_at DESC
            """)

            params = {
                "user_id": user_id,
                "chat_id": chat_id,
                "since_time": since_time
            }

            result = await session.execute(query, params)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def get_user_pending_bets(
        self,
        user_id: str,
        chat_id: str,
        issue: str
    ) -> List[Dict[str, Any]]:
        """
        获取用户某期的待结算投注

        Args:
            user_id: 用户ID
            chat_id: 群聊ID
            issue: 期号

        Returns:
            List[Dict]: 投注记录列表
        """
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM bets
                WHERE user_id = :user_id AND chat_id = :chat_id
                      AND issue = :issue
                      AND status = 'active' AND result = 'pending'
                ORDER BY created_at ASC
            """)

            params = {
                "user_id": user_id,
                "chat_id": chat_id,
                "issue": issue
            }

            result = await session.execute(query, params)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def get_all_pending_bets(
        self,
        chat_id: str
    ) -> List[Dict[str, Any]]:
        """
        获取群聊的所有待结算投注（不限期号）
        对应 Node.js: session.pendingBets

        Args:
            chat_id: 群聊ID

        Returns:
            List[Dict]: 投注记录列表
        """
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM bets
                WHERE chat_id = :chat_id
                      AND status = 'active' AND result = 'pending'
                ORDER BY created_at ASC
            """)

            params = {
                "chat_id": chat_id
            }

            result = await session.execute(query, params)
            rows = result.fetchall()

            return [dict(row._mapping) for row in rows]

    async def get_user_all_pending_bets(
        self,
        user_id: str,
        chat_id: str
    ) -> List[Dict[str, Any]]:
        """
        获取用户在群聊的所有待结算投注（不限期号）
        对应 Node.js: session.pendingBets.filter(b => b.playerId === senderId)

        Args:
            user_id: 用户ID
            chat_id: 群聊ID

        Returns:
            List[Dict]: 投注记录列表
        """
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM bets
                WHERE user_id = :user_id AND chat_id = :chat_id
                      AND status = 'active' AND result = 'pending'
                ORDER BY created_at ASC
            """)

            params = {
                "user_id": user_id,
                "chat_id": chat_id
            }

            result = await session.execute(query, params)
            rows = result.fetchall()

            return [dict(row._mapping) for row in rows]

    async def get_pending_bets_by_issue(
        self,
        chat_id: str,
        issue: str
    ) -> List[Dict[str, Any]]:
        """
        获取某期的所有待结算投注

        Args:
            chat_id: 群聊ID
            issue: 期号

        Returns:
            List[Dict]: 投注记录列表
        """
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM bets
                WHERE chat_id = :chat_id AND issue = :issue
                      AND status = 'active' AND result = 'pending'
                ORDER BY created_at ASC
            """)

            params = {
                "chat_id": chat_id,
                "issue": issue
            }

            result = await session.execute(query, params)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
