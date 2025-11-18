"""
角色管理 Service
"""
from typing import Optional, Dict, Any, List
import re
from datetime import datetime
from biz.roles.repo.role_repo import RoleRepository


class RoleService:
    def __init__(self, role_repo: RoleRepository):
        self.role_repo = role_repo

    def validate_role_name(self, role_name: str) -> str:
        """
        验证角色名称
        """
        if not role_name or not role_name.strip():
            raise ValueError("角色名称不能为空")

        role_name = role_name.strip()

        if len(role_name) < 1 or len(role_name) > 50:
            raise ValueError("角色名称长度必须在 1-50 之间")

        return role_name

    def generate_role_code(self, role_name: str) -> str:
        """
        生成角色编码（拼音 + 时间戳）
        """
        try:
            from pypinyin import lazy_pinyin
            pinyin = ''.join(lazy_pinyin(role_name))
        except ImportError:
            # 如果没有安装 pypinyin，使用简单方案
            pinyin = re.sub(r'[^a-zA-Z0-9]', '', role_name.lower())

        timestamp = int(datetime.now().timestamp())
        return f"{pinyin}_{timestamp}"

    def validate_permissions(self, permissions: List[str]) -> List[str]:
        """
        验证权限列表
        """
        if not permissions or len(permissions) == 0:
            raise ValueError("权限列表不能为空")

        # 验证权限编码格式：{module}-{submodule}-{id}
        pattern = r'^[a-z]+-[a-z]+-\d+$'

        for perm in permissions:
            if not re.match(pattern, perm):
                raise ValueError(f"无效的权限编码: {perm}")

        return permissions

    async def get_roles(
        self,
        page: int,
        page_size: int,
        role_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取角色列表
        """
        return await self.role_repo.get_roles(page, page_size, role_name)

    async def get_role_detail(self, role_id: int) -> Optional[Dict[str, Any]]:
        """
        获取角色详情
        """
        return await self.role_repo.get_role_by_id(role_id)

    async def create_role(
        self,
        role_name: str,
        remarks: str,
        permissions: List[str]
    ) -> int:
        """
        创建角色
        """
        # 验证角色名称
        role_name = self.validate_role_name(role_name)

        # 生成角色编码
        role_code = self.generate_role_code(role_name)

        # 检查编码是否已存在（理论上不会冲突，但保险起见）
        exists = await self.role_repo.check_role_code_exists(role_code)
        if exists:
            # 添加额外的随机后缀
            import random
            role_code = f"{role_code}_{random.randint(1000, 9999)}"

        # 验证权限列表
        validated_permissions = self.validate_permissions(permissions)

        # 创建角色
        return await self.role_repo.create_role(
            role_name, role_code, remarks, validated_permissions
        )

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
        # 检查角色是否存在
        role = await self.role_repo.get_role_by_id(role_id)
        if not role:
            raise ValueError("角色不存在")

        # 验证角色名称
        role_name = self.validate_role_name(role_name)

        # 验证权限列表
        validated_permissions = self.validate_permissions(permissions)

        # 更新角色
        return await self.role_repo.update_role(
            role_id, role_name, remarks, validated_permissions
        )

    async def delete_role(self, role_id: int) -> bool:
        """
        删除角色
        """
        # 检查角色是否存在
        role = await self.role_repo.get_role_by_id(role_id)
        if not role:
            raise ValueError("角色不存在")

        # 检查角色下是否有用户
        user_count = await self.role_repo.get_role_user_count(role_id)
        if user_count > 0:
            raise ValueError(f"该角色下有 {user_count} 个用户，无法删除")

        # 删除角色
        return await self.role_repo.delete_role(role_id)

    def get_permissions_tree(self) -> List[Dict[str, Any]]:
        """
        获取权限树
        """
        return self.role_repo.get_permissions_tree()
