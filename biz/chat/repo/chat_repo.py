"""
ChatRepository - 群聊数据访问层
主键：id
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class ChatRepository:
    """群聊Repository"""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """获取群聊信息"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM chats
                WHERE id = :chat_id
            """)
            result = await session.execute(query, {"chat_id": chat_id})
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            return None

    async def get_by_id(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """获取群聊信息（别名方法，兼容BaseRepository接口）"""
        return await self.get_chat(chat_id)

    async def create_chat(self, chat_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建群聊"""
        async with self._session_factory() as session:
            query = text("""
                INSERT INTO chats (
                    id, name, game_type, owner_id, auto_draw, bet_lock_time,
                    member_count, total_bets, total_volume, status, created_at, updated_at
                ) VALUES (
                    :id, :name, :game_type, :owner_id, :auto_draw, :bet_lock_time,
                    :member_count, :total_bets, :total_volume, :status, NOW(), NOW()
                )
            """)

            params = {
                "id": chat_data["id"],
                "name": chat_data["name"],
                "game_type": chat_data.get("game_type", "lucky8"),
                "owner_id": chat_data.get("owner_id"),
                "auto_draw": chat_data.get("auto_draw", True),
                "bet_lock_time": chat_data.get("bet_lock_time", 60),
                "member_count": chat_data.get("member_count", 0),
                "total_bets": chat_data.get("total_bets", 0),
                "total_volume": chat_data.get("total_volume", Decimal("0.00")),
                "status": chat_data.get("status", "active")
            }

            await session.execute(query, params)
            await session.commit()

            return await self.get_chat(chat_data["id"])

    async def update_chat(
        self,
        chat_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新群聊信息"""
        if not updates:
            return await self.get_chat(chat_id)

        async with self._session_factory() as session:
            # 构建SET子句
            set_parts = []
            params = {"chat_id": chat_id}

            for key, value in updates.items():
                set_parts.append(f"{key} = :{key}")
                params[key] = value

            set_parts.append("updated_at = NOW()")
            set_clause = ", ".join(set_parts)

            query = text(f"""
                UPDATE chats
                SET {set_clause}
                WHERE id = :chat_id
            """)

            await session.execute(query, params)
            await session.commit()

            return await self.get_chat(chat_id)

    async def update_game_type(
        self,
        chat_id: str,
        game_type: str
    ) -> Optional[Dict[str, Any]]:
        """更新游戏类型"""
        return await self.update_chat(chat_id, {"game_type": game_type})

    async def update_owner(
        self,
        chat_id: str,
        owner_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """更新所属分销商"""
        return await self.update_chat(chat_id, {"owner_id": owner_id})

    async def update_status(
        self,
        chat_id: str,
        status: str
    ) -> Optional[Dict[str, Any]]:
        """更新群聊状态"""
        return await self.update_chat(chat_id, {"status": status})

    async def increment_member_count(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """增加成员数"""
        async with self._session_factory() as session:
            query = text("""
                UPDATE chats
                SET member_count = member_count + 1, updated_at = NOW()
                WHERE id = :chat_id
            """)
            await session.execute(query, {"chat_id": chat_id})
            await session.commit()

            return await self.get_chat(chat_id)

    async def decrement_member_count(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """减少成员数"""
        async with self._session_factory() as session:
            query = text("""
                UPDATE chats
                SET member_count = GREATEST(member_count - 1, 0), updated_at = NOW()
                WHERE id = :chat_id
            """)
            await session.execute(query, {"chat_id": chat_id})
            await session.commit()

            return await self.get_chat(chat_id)

    async def increment_bet_stats(
        self,
        chat_id: str,
        bet_amount: Decimal
    ) -> Optional[Dict[str, Any]]:
        """增加投注统计"""
        async with self._session_factory() as session:
            query = text("""
                UPDATE chats
                SET total_bets = total_bets + 1,
                    total_volume = total_volume + :bet_amount,
                    updated_at = NOW()
                WHERE id = :chat_id
            """)
            await session.execute(query, {"chat_id": chat_id, "bet_amount": bet_amount})
            await session.commit()

            return await self.get_chat(chat_id)

    async def get_all_chats(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取所有群聊"""
        async with self._session_factory() as session:
            if status:
                query = text("""
                    SELECT * FROM chats
                    WHERE status = :status
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :skip
                """)
                params = {"status": status, "skip": skip, "limit": limit}
            else:
                query = text("""
                    SELECT * FROM chats
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :skip
                """)
                params = {"skip": skip, "limit": limit}

            result = await session.execute(query, params)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def get_chats_by_owner(
        self,
        owner_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取指定分销商的所有群聊"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM chats
                WHERE owner_id = :owner_id
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :skip
            """)
            result = await session.execute(query, {
                "owner_id": owner_id,
                "skip": skip,
                "limit": limit
            })
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def count_chats(self, status: Optional[str] = None) -> int:
        """统计群聊数量"""
        async with self._session_factory() as session:
            if status:
                query = text("""
                    SELECT COUNT(*) as count FROM chats
                    WHERE status = :status
                """)
                result = await session.execute(query, {"status": status})
            else:
                query = text("""
                    SELECT COUNT(*) as count FROM chats
                """)
                result = await session.execute(query)

            row = result.fetchone()
            return row[0] if row else 0

    async def exists(self, chat_id: str) -> bool:
        """检查群聊是否存在"""
        async with self._session_factory() as session:
            query = text("""
                SELECT 1 FROM chats
                WHERE id = :chat_id
                LIMIT 1
            """)
            result = await session.execute(query, {"chat_id": chat_id})
            return result.fetchone() is not None

    async def delete_chat(self, chat_id: str) -> bool:
        """删除群聊"""
        async with self._session_factory() as session:
            query = text("""
                DELETE FROM chats
                WHERE id = :chat_id
            """)
            result = await session.execute(query, {"chat_id": chat_id})
            await session.commit()
            return result.rowcount > 0
