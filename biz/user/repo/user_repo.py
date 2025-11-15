"""
UserRepository - 用户数据访问层
复合主键：(id, chat_id)
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import text, and_, desc
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class UserRepository:
    """用户Repository - 使用复合主键(id, chat_id)"""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def get_user_in_chat(self, user_id: str, chat_id: str) -> Optional[Dict[str, Any]]:
        """获取用户在特定群的数据"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM users
                WHERE id = :user_id AND chat_id = :chat_id
            """)
            result = await session.execute(query, {"user_id": user_id, "chat_id": chat_id})
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            return None

    async def get_user_first(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户在任意群的第一条数据（兼容旧API）"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM users
                WHERE id = :user_id
                LIMIT 1
            """)
            result = await session.execute(query, {"user_id": user_id})
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            return None

    async def get_all_user_chats(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户在所有群的数据"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM users
                WHERE id = :user_id
                ORDER BY created_at DESC
            """)
            result = await session.execute(query, {"user_id": user_id})
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def get_chat_users(self, chat_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """获取特定群的所有用户"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM users
                WHERE chat_id = :chat_id
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :skip
            """)
            result = await session.execute(query, {"chat_id": chat_id, "skip": skip, "limit": limit})
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def count_chat_users(self, chat_id: str) -> int:
        """统计群聊用户数"""
        async with self._session_factory() as session:
            query = text("""
                SELECT COUNT(*) as count FROM users
                WHERE chat_id = :chat_id
            """)
            result = await session.execute(query, {"chat_id": chat_id})
            row = result.fetchone()
            return row[0] if row else 0

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建用户"""
        async with self._session_factory() as session:
            query = text("""
                INSERT INTO users (
                    id, username, chat_id, balance, score, rebate_ratio,
                    join_date, status, role, created_by, is_bot, bot_config,
                    is_new, red_packet_settings, created_at, updated_at
                ) VALUES (
                    :id, :username, :chat_id, :balance, :score, :rebate_ratio,
                    :join_date, :status, :role, :created_by, :is_bot, :bot_config,
                    :is_new, :red_packet_settings, NOW(), NOW()
                )
            """)

            from base.json_encoder import safe_json_dumps

            params = {
                "id": user_data["id"],
                "username": user_data["username"],
                "chat_id": user_data["chat_id"],
                "balance": user_data.get("balance", Decimal("0.00")),
                "score": user_data.get("score", 0),
                "rebate_ratio": user_data.get("rebate_ratio", Decimal("0.02")),
                "join_date": user_data.get("join_date", datetime.now().date()),
                "status": user_data.get("status", "活跃"),
                "role": user_data.get("role", "normal"),
                "created_by": user_data.get("created_by", "admin"),
                "is_bot": user_data.get("is_bot", False),
                "bot_config": safe_json_dumps(user_data.get("bot_config", {})),
                "is_new": user_data.get("is_new", True),
                "red_packet_settings": safe_json_dumps(user_data.get("red_packet_settings", {
                    "enabled": True,
                    "max_amount": 1000.00,
                    "min_amount": 10.00,
                    "daily_limit": 5
                }))
            }

            await session.execute(query, params)
            await session.commit()

            return await self.get_user_in_chat(user_data["id"], user_data["chat_id"])

    async def update_user(
        self,
        user_id: str,
        chat_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新用户信息"""
        if not updates:
            return await self.get_user_in_chat(user_id, chat_id)

        async with self._session_factory() as session:
            from base.json_encoder import safe_json_dumps

            # 构建SET子句
            set_parts = []
            params = {"user_id": user_id, "chat_id": chat_id}

            for key, value in updates.items():
                if key in ["bot_config", "red_packet_settings"] and isinstance(value, dict):
                    value = safe_json_dumps(value)
                set_parts.append(f"{key} = :{key}")
                params[key] = value

            set_parts.append("updated_at = NOW()")
            set_clause = ", ".join(set_parts)

            query = text(f"""
                UPDATE users
                SET {set_clause}
                WHERE id = :user_id AND chat_id = :chat_id
            """)

            await session.execute(query, params)
            await session.commit()

            return await self.get_user_in_chat(user_id, chat_id)

    async def update_balance(
        self,
        user_id: str,
        chat_id: str,
        new_balance: Decimal
    ) -> Optional[Dict[str, Any]]:
        """更新用户余额"""
        return await self.update_user(user_id, chat_id, {"balance": new_balance})

    async def add_balance(
        self,
        user_id: str,
        chat_id: str,
        amount: Decimal
    ) -> Optional[Dict[str, Any]]:
        """增加余额（充值）"""
        async with self._session_factory() as session:
            query = text("""
                UPDATE users
                SET balance = balance + :amount, updated_at = NOW()
                WHERE id = :user_id AND chat_id = :chat_id
            """)
            await session.execute(query, {
                "user_id": user_id,
                "chat_id": chat_id,
                "amount": amount
            })
            await session.commit()

            return await self.get_user_in_chat(user_id, chat_id)

    async def subtract_balance(
        self,
        user_id: str,
        chat_id: str,
        amount: Decimal
    ) -> Optional[Dict[str, Any]]:
        """减少余额（下分）"""
        async with self._session_factory() as session:
            query = text("""
                UPDATE users
                SET balance = balance - :amount, updated_at = NOW()
                WHERE id = :user_id AND chat_id = :chat_id AND balance >= :amount
            """)
            result = await session.execute(query, {
                "user_id": user_id,
                "chat_id": chat_id,
                "amount": amount
            })
            await session.commit()

            if result.rowcount == 0:
                return None  # 余额不足或用户不存在

            return await self.get_user_in_chat(user_id, chat_id)

    async def add_score(
        self,
        user_id: str,
        chat_id: str,
        score_change: int
    ) -> Optional[Dict[str, Any]]:
        """增加积分"""
        async with self._session_factory() as session:
            query = text("""
                UPDATE users
                SET score = score + :score_change, updated_at = NOW()
                WHERE id = :user_id AND chat_id = :chat_id
            """)
            await session.execute(query, {
                "user_id": user_id,
                "chat_id": chat_id,
                "score_change": score_change
            })
            await session.commit()

            return await self.get_user_in_chat(user_id, chat_id)

    async def update_rebate_ratio(
        self,
        user_id: str,
        chat_id: str,
        rebate_ratio: Decimal
    ) -> Optional[Dict[str, Any]]:
        """更新回水比例"""
        return await self.update_user(user_id, chat_id, {"rebate_ratio": rebate_ratio})

    async def update_status(
        self,
        user_id: str,
        chat_id: str,
        status: str
    ) -> Optional[Dict[str, Any]]:
        """更新用户状态（活跃/禁用）"""
        return await self.update_user(user_id, chat_id, {"status": status})

    async def mark_as_read(
        self,
        user_id: str,
        chat_id: str
    ) -> Optional[Dict[str, Any]]:
        """标记用户为已读"""
        return await self.update_user(user_id, chat_id, {
            "is_new": False,
            "marked_read_at": datetime.now()
        })

    async def exists(self, user_id: str, chat_id: str) -> bool:
        """检查用户是否存在"""
        async with self._session_factory() as session:
            query = text("""
                SELECT 1 FROM users
                WHERE id = :user_id AND chat_id = :chat_id
                LIMIT 1
            """)
            result = await session.execute(query, {"user_id": user_id, "chat_id": chat_id})
            return result.fetchone() is not None

    async def delete_user(self, user_id: str, chat_id: str) -> bool:
        """删除用户"""
        async with self._session_factory() as session:
            query = text("""
                DELETE FROM users
                WHERE id = :user_id AND chat_id = :chat_id
            """)
            result = await session.execute(query, {"user_id": user_id, "chat_id": chat_id})
            await session.commit()
            return result.rowcount > 0

    async def get_leaderboard(
        self,
        chat_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取排行榜（按余额排序）"""
        async with self._session_factory() as session:
            query = text("""
                SELECT id, username, balance, score
                FROM users
                WHERE chat_id = :chat_id AND status = '活跃'
                ORDER BY balance DESC
                LIMIT :limit
            """)
            result = await session.execute(query, {"chat_id": chat_id, "limit": limit})
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def get_new_users(
        self,
        chat_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取新用户列表"""
        async with self._session_factory() as session:
            if chat_id:
                query = text("""
                    SELECT * FROM users
                    WHERE chat_id = :chat_id AND is_new = 1
                    ORDER BY created_at DESC
                """)
                result = await session.execute(query, {"chat_id": chat_id})
            else:
                query = text("""
                    SELECT * FROM users
                    WHERE is_new = 1
                    ORDER BY created_at DESC
                """)
                result = await session.execute(query)

            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
