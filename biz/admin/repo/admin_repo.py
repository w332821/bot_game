"""
AdminRepository - 管理员数据访问层
主键：id
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class AdminRepository:
    """管理员Repository"""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def get_admin(self, admin_id: str) -> Optional[Dict[str, Any]]:
        """获取管理员信息"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM admin_accounts
                WHERE id = :admin_id
            """)
            result = await session.execute(query, {"admin_id": admin_id})
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            return None

    async def get_admin_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """通过用户名获取管理员"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM admin_accounts
                WHERE username = :username
            """)
            result = await session.execute(query, {"username": username})
            row = result.fetchone()
            if row:
                return dict(row._mapping)
            return None

    async def create_admin(self, admin_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建管理员"""
        async with self._session_factory() as session:
            query = text("""
                INSERT INTO admin_accounts (
                    id, username, password, role, managed_chat_id,
                    balance, total_rebate_collected, status, description,
                    created_date, created_at, updated_at
                ) VALUES (
                    :id, :username, :password, :role, :managed_chat_id,
                    :balance, :total_rebate_collected, :status, :description,
                    :created_date, NOW(), NOW()
                )
            """)

            params = {
                "id": admin_data["id"],
                "username": admin_data["username"],
                "password": admin_data["password"],
                "role": admin_data.get("role", "distributor"),
                "managed_chat_id": admin_data.get("managed_chat_id"),
                "balance": admin_data.get("balance", Decimal("0.00")),
                "total_rebate_collected": admin_data.get("total_rebate_collected", Decimal("0.00")),
                "status": admin_data.get("status", "active"),
                "description": admin_data.get("description"),
                "created_date": admin_data.get("created_date", date.today())
            }

            await session.execute(query, params)
            await session.commit()

            return await self.get_admin(admin_data["id"])

    async def update_admin(
        self,
        admin_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新管理员信息"""
        if not updates:
            return await self.get_admin(admin_id)

        async with self._session_factory() as session:
            # 构建SET子句
            set_parts = []
            params = {"admin_id": admin_id}

            for key, value in updates.items():
                set_parts.append(f"{key} = :{key}")
                params[key] = value

            set_parts.append("updated_at = NOW()")
            set_clause = ", ".join(set_parts)

            query = text(f"""
                UPDATE admin_accounts
                SET {set_clause}
                WHERE id = :admin_id
            """)

            await session.execute(query, params)
            await session.commit()

            return await self.get_admin(admin_id)

    async def update_password(
        self,
        admin_id: str,
        password_hash: str
    ) -> Optional[Dict[str, Any]]:
        """更新密码"""
        return await self.update_admin(admin_id, {"password": password_hash})

    async def update_status(
        self,
        admin_id: str,
        status: str
    ) -> Optional[Dict[str, Any]]:
        """更新状态"""
        return await self.update_admin(admin_id, {"status": status})

    async def add_balance(
        self,
        admin_id: str,
        amount: Decimal
    ) -> Optional[Dict[str, Any]]:
        """增加余额（回水收入）"""
        async with self._session_factory() as session:
            query = text("""
                UPDATE admin_accounts
                SET balance = balance + :amount,
                    total_rebate_collected = total_rebate_collected + :amount,
                    updated_at = NOW()
                WHERE id = :admin_id
            """)
            await session.execute(query, {"admin_id": admin_id, "amount": amount})
            await session.commit()

            return await self.get_admin(admin_id)

    async def subtract_balance(
        self,
        admin_id: str,
        amount: Decimal
    ) -> Optional[Dict[str, Any]]:
        """减少余额"""
        async with self._session_factory() as session:
            query = text("""
                UPDATE admin_accounts
                SET balance = balance - :amount, updated_at = NOW()
                WHERE id = :admin_id AND balance >= :amount
            """)
            result = await session.execute(query, {"admin_id": admin_id, "amount": amount})
            await session.commit()

            if result.rowcount == 0:
                return None  # 余额不足或管理员不存在

            return await self.get_admin(admin_id)

    async def get_all_admins(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取所有管理员"""
        async with self._session_factory() as session:
            if role:
                query = text("""
                    SELECT * FROM admin_accounts
                    WHERE role = :role
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :skip
                """)
                params = {"role": role, "skip": skip, "limit": limit}
            else:
                query = text("""
                    SELECT * FROM admin_accounts
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :skip
                """)
                params = {"skip": skip, "limit": limit}

            result = await session.execute(query, params)
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]

    async def get_distributors(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取所有分销商"""
        return await self.get_all_admins(skip, limit, "distributor")

    async def exists_username(self, username: str) -> bool:
        """检查用户名是否已存在"""
        async with self._session_factory() as session:
            query = text("""
                SELECT 1 FROM admin_accounts
                WHERE username = :username
                LIMIT 1
            """)
            result = await session.execute(query, {"username": username})
            return result.fetchone() is not None

    async def delete_admin(self, admin_id: str) -> bool:
        """删除管理员"""
        async with self._session_factory() as session:
            query = text("""
                DELETE FROM admin_accounts
                WHERE id = :admin_id
            """)
            result = await session.execute(query, {"admin_id": admin_id})
            await session.commit()
            return result.rowcount > 0
