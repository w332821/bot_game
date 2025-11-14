"""
AdminService - 管理员业务逻辑层
处理登录、权限验证、管理员管理等业务逻辑
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
import logging
import uuid
import bcrypt

from biz.admin.repo.admin_repo import AdminRepository

logger = logging.getLogger(__name__)


class AdminService:
    """管理员服务"""

    def __init__(self, admin_repo: AdminRepository):
        self.admin_repo = admin_repo

    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"密码验证失败: {str(e)}")
            return False

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        管理员登录
        返回: {
            "success": bool,
            "admin": Dict,
            "error": str
        }
        """
        try:
            # 获取管理员信息
            admin = await self.admin_repo.get_admin_by_username(username)

            if not admin:
                return {
                    "success": False,
                    "admin": None,
                    "error": "用户名或密码错误"
                }

            # 验证密码
            if not self._verify_password(password, admin["password"]):
                return {
                    "success": False,
                    "admin": None,
                    "error": "用户名或密码错误"
                }

            # 检查账户状态
            if admin["status"] != "active":
                return {
                    "success": False,
                    "admin": None,
                    "error": "账户已被禁用"
                }

            # 移除密码字段
            admin_info = {k: v for k, v in admin.items() if k != "password"}

            logger.info(f"✅ 管理员登录成功: {username} ({admin['role']})")

            return {
                "success": True,
                "admin": admin_info,
                "error": None
            }
        except Exception as e:
            logger.error(f"❌ 登录失败: {str(e)}")
            return {
                "success": False,
                "admin": None,
                "error": "登录失败"
            }

    async def verify_password(self, admin_id: str, password: str) -> bool:
        """验证管理员密码"""
        admin = await self.admin_repo.get_admin(admin_id)
        if not admin:
            return False

        return self._verify_password(password, admin["password"])

    async def create_admin(
        self,
        username: str,
        password: str,
        role: str = "distributor",
        managed_chat_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建管理员
        返回: {
            "success": bool,
            "admin": Dict,
            "error": str
        }
        """
        try:
            # 检查用户名是否已存在
            if await self.admin_repo.exists_username(username):
                return {
                    "success": False,
                    "admin": None,
                    "error": "用户名已存在"
                }

            # 生成管理员ID
            admin_id = f"admin_{int(datetime.now().timestamp() * 1000)}_{uuid.uuid4().hex[:8]}"

            # 密码哈希
            password_hash = self._hash_password(password)

            # 创建管理员数据
            admin_data = {
                "id": admin_id,
                "username": username,
                "password": password_hash,
                "role": role,
                "managed_chat_id": managed_chat_id,
                "description": description,
                "created_date": date.today()
            }

            admin = await self.admin_repo.create_admin(admin_data)

            # 移除密码字段
            admin_info = {k: v for k, v in admin.items() if k != "password"}

            logger.info(f"✅ 创建管理员: {username} ({role})")

            return {
                "success": True,
                "admin": admin_info,
                "error": None
            }
        except Exception as e:
            logger.error(f"❌ 创建管理员失败: {str(e)}")
            return {
                "success": False,
                "admin": None,
                "error": str(e)
            }

    async def update_password(
        self,
        admin_id: str,
        old_password: str,
        new_password: str
    ) -> Dict[str, Any]:
        """修改密码"""
        try:
            # 验证旧密码
            if not await self.verify_password(admin_id, old_password):
                return {
                    "success": False,
                    "error": "原密码错误"
                }

            # 哈希新密码
            new_password_hash = self._hash_password(new_password)

            # 更新密码
            await self.admin_repo.update_password(admin_id, new_password_hash)

            logger.info(f"✅ 管理员 {admin_id} 修改密码成功")

            return {
                "success": True,
                "error": None
            }
        except Exception as e:
            logger.error(f"❌ 修改密码失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_admin(self, admin_id: str) -> Optional[Dict[str, Any]]:
        """获取管理员信息（不含密码）"""
        admin = await self.admin_repo.get_admin(admin_id)
        if admin:
            return {k: v for k, v in admin.items() if k != "password"}
        return None

    async def get_all_admins(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取所有管理员（不含密码）"""
        admins = await self.admin_repo.get_all_admins(skip, limit, role)
        return [{k: v for k, v in admin.items() if k != "password"} for admin in admins]

    async def get_distributors(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取所有分销商"""
        return await self.get_all_admins(skip, limit, "distributor")

    async def update_status(
        self,
        admin_id: str,
        status: str
    ) -> Optional[Dict[str, Any]]:
        """更新管理员状态"""
        if status not in ["active", "inactive"]:
            raise ValueError("状态必须是active或inactive")

        admin = await self.admin_repo.update_status(admin_id, status)
        if admin:
            return {k: v for k, v in admin.items() if k != "password"}
        return None

    async def add_rebate(
        self,
        admin_id: str,
        amount: Decimal
    ) -> Optional[Dict[str, Any]]:
        """增加回水收入"""
        admin = await self.admin_repo.add_balance(admin_id, amount)
        if admin:
            logger.info(f"💰 管理员 {admin_id} 回水收入: {amount}")
            return {k: v for k, v in admin.items() if k != "password"}
        return None

    async def delete_admin(self, admin_id: str) -> bool:
        """删除管理员"""
        logger.warning(f"⚠️ 删除管理员: {admin_id}")
        return await self.admin_repo.delete_admin(admin_id)
