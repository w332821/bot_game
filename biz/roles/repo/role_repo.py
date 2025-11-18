"""
角色管理 Repository
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text


class RoleRepository:
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def get_roles(
        self,
        page: int,
        page_size: int,
        role_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取角色列表（分页）
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 构建查询条件
            where_clause = "WHERE 1=1"
            params = {
                "limit": page_size,
                "offset": (page - 1) * page_size
            }

            if role_name:
                where_clause += " AND r.role_name LIKE :role_name"
                params["role_name"] = f"%{role_name}%"

            # 查询总数
            count_query = text(f"""
                SELECT COUNT(*) as total
                FROM roles r
                {where_clause}
            """)

            count_result = await session.execute(count_query, params)
            total = count_result.fetchone().total

            # 查询列表（包含用户数量）
            list_query = text(f"""
                SELECT
                    r.id,
                    r.role_name as roleName,
                    r.role_code as roleCode,
                    r.remarks,
                    r.status,
                    r.created_at as createTime,
                    COUNT(DISTINCT sa.id) as userCount
                FROM roles r
                LEFT JOIN sub_accounts sa ON sa.role_id = r.id
                {where_clause}
                GROUP BY r.id, r.role_name, r.role_code, r.remarks, r.status, r.created_at
                ORDER BY r.created_at DESC
                LIMIT :limit OFFSET :offset
            """)

            list_result = await session.execute(list_query, params)

            roles = []
            for row in list_result:
                roles.append({
                    "id": row.id,
                    "roleName": row.roleName,
                    "roleCode": row.roleCode,
                    "description": row.remarks or "",
                    "userCount": row.userCount,
                    "status": row.status,
                    "createTime": row.createTime.strftime("%Y-%m-%d %H:%M:%S") if row.createTime else None
                })

            return {
                "list": roles,
                "total": total
            }

    async def get_role_by_id(self, role_id: int) -> Optional[Dict[str, Any]]:
        """
        获取角色详情（包含权限列表）
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 查询角色基本信息
            role_query = text("""
                SELECT
                    id,
                    role_name as roleName,
                    role_code as roleCode,
                    remarks
                FROM roles
                WHERE id = :role_id
            """)

            role_result = await session.execute(role_query, {"role_id": role_id})
            role_row = role_result.fetchone()

            if not role_row:
                return None

            # 查询角色关联的权限
            perm_query = text("""
                SELECT permission_code
                FROM role_permissions
                WHERE role_id = :role_id
            """)

            perm_result = await session.execute(perm_query, {"role_id": role_id})
            permissions = [row.permission_code for row in perm_result]

            return {
                "id": role_row.id,
                "roleName": role_row.roleName,
                "roleCode": role_row.roleCode,
                "remarks": role_row.remarks or "",
                "permissions": permissions
            }

    async def create_role(
        self,
        role_name: str,
        role_code: str,
        remarks: str,
        permissions: List[str]
    ) -> int:
        """
        创建角色
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 插入角色
            insert_role_query = text("""
                INSERT INTO roles (role_name, role_code, remarks, status, created_at, updated_at)
                VALUES (:role_name, :role_code, :remarks, '启用', NOW(), NOW())
            """)

            await session.execute(insert_role_query, {
                "role_name": role_name,
                "role_code": role_code,
                "remarks": remarks
            })

            # 获取插入的角色ID
            result = await session.execute(text("SELECT LAST_INSERT_ID() as id"))
            role_id = result.fetchone().id

            # 插入权限关联
            if permissions:
                for perm_code in permissions:
                    insert_perm_query = text("""
                        INSERT INTO role_permissions (role_id, permission_code, created_at)
                        VALUES (:role_id, :permission_code, NOW())
                    """)
                    await session.execute(insert_perm_query, {
                        "role_id": role_id,
                        "permission_code": perm_code
                    })

            await session.commit()
            return role_id

    async def update_role(
        self,
        role_id: int,
        role_name: str,
        remarks: str,
        permissions: List[str]
    ) -> bool:
        """
        更新角色
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 更新角色基本信息
            update_query = text("""
                UPDATE roles
                SET role_name = :role_name, remarks = :remarks, updated_at = NOW()
                WHERE id = :role_id
            """)

            await session.execute(update_query, {
                "role_id": role_id,
                "role_name": role_name,
                "remarks": remarks
            })

            # 删除旧的权限关联
            delete_perms_query = text("""
                DELETE FROM role_permissions WHERE role_id = :role_id
            """)
            await session.execute(delete_perms_query, {"role_id": role_id})

            # 插入新的权限关联
            if permissions:
                for perm_code in permissions:
                    insert_perm_query = text("""
                        INSERT INTO role_permissions (role_id, permission_code, created_at)
                        VALUES (:role_id, :permission_code, NOW())
                    """)
                    await session.execute(insert_perm_query, {
                        "role_id": role_id,
                        "permission_code": perm_code
                    })

            await session.commit()
            return True

    async def delete_role(self, role_id: int) -> bool:
        """
        删除角色
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 删除权限关联
            delete_perms_query = text("""
                DELETE FROM role_permissions WHERE role_id = :role_id
            """)
            await session.execute(delete_perms_query, {"role_id": role_id})

            # 删除角色
            delete_role_query = text("""
                DELETE FROM roles WHERE id = :role_id
            """)
            await session.execute(delete_role_query, {"role_id": role_id})

            await session.commit()
            return True

    async def get_role_user_count(self, role_id: int) -> int:
        """
        获取角色关联的用户数量
        """
        async with self.session_factory() as session:
            session: AsyncSession

            query = text("""
                SELECT COUNT(*) as count
                FROM sub_accounts
                WHERE role_id = :role_id
            """)

            result = await session.execute(query, {"role_id": role_id})
            return result.fetchone().count

    async def check_role_code_exists(self, role_code: str, exclude_id: Optional[int] = None) -> bool:
        """
        检查角色编码是否已存在
        """
        async with self.session_factory() as session:
            session: AsyncSession

            query_str = """
                SELECT COUNT(*) as count
                FROM roles
                WHERE role_code = :role_code
            """

            params = {"role_code": role_code}

            if exclude_id is not None:
                query_str += " AND id != :exclude_id"
                params["exclude_id"] = exclude_id

            query = text(query_str)
            result = await session.execute(query, params)
            return result.fetchone().count > 0

    def get_permissions_tree(self) -> List[Dict[str, Any]]:
        """
        获取权限树（三级结构）
        """
        return [
            {
                "id": "personal",
                "label": "个人管理",
                "children": [
                    {
                        "id": "personal-basic",
                        "label": "基本资料",
                        "children": [
                            {"id": "personal-basic-1", "label": "修改代理会员注册默认盘口"},
                            {"id": "personal-basic-2", "label": "获取代理个人信息"},
                            {"id": "personal-basic-3", "label": "修改代理个人信息"}
                        ]
                    },
                    {
                        "id": "personal-promote",
                        "label": "推广管理",
                        "children": [
                            {"id": "personal-promote-1", "label": "添加推广域名"},
                            {"id": "personal-promote-2", "label": "查看推广链接"}
                        ]
                    },
                    {
                        "id": "personal-rebate",
                        "label": "退水配置",
                        "children": [
                            {"id": "personal-rebate-1", "label": "查看退水配置"},
                            {"id": "personal-rebate-2", "label": "修改退水配置"}
                        ]
                    }
                ]
            },
            {
                "id": "users",
                "label": "用户管理",
                "children": [
                    {
                        "id": "users-members",
                        "label": "会员管理",
                        "children": [
                            {"id": "users-members-1", "label": "查看会员列表"},
                            {"id": "users-members-2", "label": "创建会员"},
                            {"id": "users-members-3", "label": "修改会员信息"},
                            {"id": "users-members-4", "label": "查看会员详情"}
                        ]
                    },
                    {
                        "id": "users-agents",
                        "label": "代理管理",
                        "children": [
                            {"id": "users-agents-1", "label": "查看代理列表"},
                            {"id": "users-agents-2", "label": "创建代理"},
                            {"id": "users-agents-3", "label": "修改代理信息"},
                            {"id": "users-agents-4", "label": "查看代理详情"}
                        ]
                    }
                ]
            },
            {
                "id": "reports",
                "label": "报表管理",
                "children": [
                    {
                        "id": "reports-financial",
                        "label": "财务报表",
                        "children": [
                            {"id": "reports-financial-1", "label": "查看财务总报表"},
                            {"id": "reports-financial-2", "label": "查看财务明细"},
                            {"id": "reports-financial-3", "label": "导出财务报表"}
                        ]
                    },
                    {
                        "id": "reports-winloss",
                        "label": "输赢报表",
                        "children": [
                            {"id": "reports-winloss-1", "label": "查看输赢报表"},
                            {"id": "reports-winloss-2", "label": "导出输赢报表"}
                        ]
                    }
                ]
            },
            {
                "id": "settings",
                "label": "系统设置",
                "children": [
                    {
                        "id": "settings-system",
                        "label": "系统配置",
                        "children": [
                            {"id": "settings-system-1", "label": "查看系统设置"},
                            {"id": "settings-system-2", "label": "修改系统设置"}
                        ]
                    },
                    {
                        "id": "settings-odds",
                        "label": "赔率配置",
                        "children": [
                            {"id": "settings-odds-1", "label": "查看赔率配置"},
                            {"id": "settings-odds-2", "label": "修改赔率配置"}
                        ]
                    }
                ]
            }
        ]
