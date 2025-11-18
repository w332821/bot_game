"""
子账号管理 Repository
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import bcrypt


class SubAccountRepository:
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def get_sub_accounts(
        self,
        parent_user_id: str,
        page: int,
        page_size: int
    ) -> Dict[str, Any]:
        """
        获取子账号列表（分页）
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 查询总数
            count_query = text("""
                SELECT COUNT(*) as total
                FROM sub_accounts
                WHERE parent_user_id = :parent_user_id
            """)

            count_result = await session.execute(count_query, {"parent_user_id": parent_user_id})
            total = count_result.fetchone().total

            # 查询列表
            list_query = text("""
                SELECT
                    sa.id,
                    sa.account,
                    sa.account_name as name,
                    r.role_name as role,
                    sa.created_at as createDate,
                    sa.status
                FROM sub_accounts sa
                LEFT JOIN roles r ON sa.role_id = r.id
                WHERE sa.parent_user_id = :parent_user_id
                ORDER BY sa.created_at DESC
                LIMIT :limit OFFSET :offset
            """)

            list_result = await session.execute(list_query, {
                "parent_user_id": parent_user_id,
                "limit": page_size,
                "offset": (page - 1) * page_size
            })

            sub_accounts = []
            for row in list_result:
                sub_accounts.append({
                    "id": row.id,
                    "account": row.account,
                    "name": row.name,
                    "role": row.role or "",
                    "createDate": row.createDate.strftime("%Y-%m-%d %H:%M:%S") if row.createDate else None,
                    "status": row.status
                })

            return {
                "list": sub_accounts,
                "total": total
            }

    async def get_sub_account_by_id(self, sub_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取子账号详情
        """
        async with self.session_factory() as session:
            session: AsyncSession

            query = text("""
                SELECT
                    sa.id,
                    sa.account,
                    sa.account_name,
                    sa.role_id,
                    r.role_name,
                    sa.status,
                    sa.parent_user_id
                FROM sub_accounts sa
                LEFT JOIN roles r ON sa.role_id = r.id
                WHERE sa.id = :sub_id
            """)

            result = await session.execute(query, {"sub_id": sub_id})
            row = result.fetchone()

            if not row:
                return None

            return {
                "id": row.id,
                "account": row.account,
                "accountName": row.account_name,
                "roleId": row.role_id,
                "roleName": row.role_name or "",
                "status": row.status,
                "parentUserId": row.parent_user_id
            }

    async def create_sub_account(
        self,
        parent_user_id: str,
        account: str,
        password: str,
        payment_password: Optional[str],
        account_name: str,
        role_id: int
    ) -> int:
        """
        创建子账号
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 加密密码
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            hashed_payment_pwd = None
            if payment_password:
                hashed_payment_pwd = bcrypt.hashpw(payment_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # 插入子账号
            insert_query = text("""
                INSERT INTO sub_accounts (
                    parent_user_id, account, password, payment_password,
                    account_name, role_id, status, created_at, updated_at
                )
                VALUES (
                    :parent_user_id, :account, :password, :payment_password,
                    :account_name, :role_id, '启用', NOW(), NOW()
                )
            """)

            await session.execute(insert_query, {
                "parent_user_id": parent_user_id,
                "account": account,
                "password": hashed_password,
                "payment_password": hashed_payment_pwd,
                "account_name": account_name,
                "role_id": role_id
            })

            # 获取插入的ID
            result = await session.execute(text("SELECT LAST_INSERT_ID() as id"))
            sub_id = result.fetchone().id

            await session.commit()
            return sub_id

    async def update_sub_account(
        self,
        sub_id: int,
        account_name: str,
        role_id: int,
        status: str
    ) -> bool:
        """
        更新子账号
        """
        async with self.session_factory() as session:
            session: AsyncSession

            update_query = text("""
                UPDATE sub_accounts
                SET
                    account_name = :account_name,
                    role_id = :role_id,
                    status = :status,
                    updated_at = NOW()
                WHERE id = :sub_id
            """)

            await session.execute(update_query, {
                "sub_id": sub_id,
                "account_name": account_name,
                "role_id": role_id,
                "status": status
            })

            await session.commit()
            return True

    async def delete_sub_account(self, sub_id: int) -> bool:
        """
        删除子账号
        """
        async with self.session_factory() as session:
            session: AsyncSession

            delete_query = text("""
                DELETE FROM sub_accounts WHERE id = :sub_id
            """)

            await session.execute(delete_query, {"sub_id": sub_id})
            await session.commit()
            return True

    async def check_account_exists(self, account: str) -> bool:
        """
        检查账号是否已存在
        """
        async with self.session_factory() as session:
            session: AsyncSession

            query = text("""
                SELECT COUNT(*) as count
                FROM sub_accounts
                WHERE account = :account
            """)

            result = await session.execute(query, {"account": account})
            return result.fetchone().count > 0

    async def generate_account(self, agent_account: str) -> str:
        """
        生成子账号：{agentAccount}_sub_{序号}
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 查询该代理下已有的子账号数量
            query = text("""
                SELECT COUNT(*) as count
                FROM sub_accounts sa
                INNER JOIN agent_profiles ap ON sa.parent_user_id = ap.user_id
                WHERE ap.account COLLATE utf8mb4_unicode_ci = :agent_account
            """)

            result = await session.execute(query, {"agent_account": agent_account})
            count = result.fetchone().count

            return f"{agent_account}_sub_{count+1:03d}"

    async def get_parent_user_id_by_agent_account(self, agent_account: str) -> Optional[str]:
        """
        根据代理账号获取 user_id
        """
        async with self.session_factory() as session:
            session: AsyncSession

            query = text("""
                SELECT user_id
                FROM agent_profiles
                WHERE account COLLATE utf8mb4_unicode_ci = :agent_account
            """)

            result = await session.execute(query, {"agent_account": agent_account})
            row = result.fetchone()

            return row.user_id if row else None

    async def get_role_id_by_name(self, role_name: str) -> Optional[int]:
        """
        根据角色名称获取角色ID
        """
        async with self.session_factory() as session:
            session: AsyncSession

            query = text("""
                SELECT id
                FROM roles
                WHERE role_name = :role_name
            """)

            result = await session.execute(query, {"role_name": role_name})
            row = result.fetchone()

            return row.id if row else None
