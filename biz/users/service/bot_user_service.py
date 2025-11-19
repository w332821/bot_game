from typing import Optional, Dict, Any, List
from biz.user.repo.user_repo import UserRepository
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import text


class BotUserService:

    def __init__(self, user_repo: UserRepository, session_factory: async_sessionmaker[AsyncSession]):
        self.user_repo = user_repo
        self.session_factory = session_factory

    async def list_bot_users(
        self,
        page: int,
        page_size: int,
        chat_id: Optional[str] = None,
        has_member_profile: Optional[bool] = None,
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        async with self.session_factory() as session:
            where_clauses = []
            params = {}

            if chat_id:
                where_clauses.append("u.chat_id = :chat_id")
                params["chat_id"] = chat_id

            if username:
                where_clauses.append("u.username LIKE :username")
                params["username"] = f"%{username}%"

            if has_member_profile is not None:
                if has_member_profile:
                    where_clauses.append("mp.id IS NOT NULL")
                else:
                    where_clauses.append("mp.id IS NULL")

            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

            offset = (page - 1) * page_size
            params["page_size"] = page_size
            params["offset"] = offset

            list_query = text(f"""
                SELECT
                    u.id as userId,
                    u.chat_id as chatId,
                    u.username,
                    u.balance,
                    u.join_date as joinDate,
                    u.status,
                    mp.id IS NOT NULL as hasMemberProfile,
                    mp.account as memberAccount,
                    mp.plate as memberPlate
                FROM users u
                LEFT JOIN member_profiles mp ON mp.user_id = u.id
                WHERE {where_clause}
                ORDER BY u.created_at DESC
                LIMIT :page_size OFFSET :offset
            """)

            result = await session.execute(list_query, params)
            rows = result.fetchall()

            list_data = []
            for row in rows:
                list_data.append({
                    "userId": row[0],
                    "chatId": row[1],
                    "username": row[2],
                    "balance": float(row[3]) if row[3] else 0.0,
                    "joinDate": row[4].strftime("%Y-%m-%d") if row[4] else "",
                    "status": row[5],
                    "hasMemberProfile": bool(row[6]),
                    "memberAccount": row[7] if row[7] else None,
                    "memberPlate": row[8] if row[8] else None
                })

            count_query = text(f"""
                SELECT COUNT(*)
                FROM users u
                LEFT JOIN member_profiles mp ON mp.user_id = u.id
                WHERE {where_clause}
            """)

            count_params = {k: v for k, v in params.items() if k not in ["page_size", "offset"]}
            result = await session.execute(count_query, count_params)
            total = result.scalar() or 0

            return {
                "list": list_data,
                "total": total
            }

    async def list_bot_chats(self) -> List[Dict[str, Any]]:
        async with self.session_factory() as session:
            query = text("""
                SELECT DISTINCT
                    u.chat_id as chatId,
                    COUNT(DISTINCT u.id) as userCount
                FROM users u
                WHERE u.chat_id != 'admin_backend'
                GROUP BY u.chat_id
                ORDER BY userCount DESC
            """)

            result = await session.execute(query)
            rows = result.fetchall()

            chats = []
            for row in rows:
                chats.append({
                    "chatId": row[0],
                    "userCount": row[1]
                })

            return chats
