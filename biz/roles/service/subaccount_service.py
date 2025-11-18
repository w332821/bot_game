"""
子账号管理 Service
"""
from typing import Optional, Dict, Any
from biz.roles.repo.subaccount_repo import SubAccountRepository


class SubAccountService:
    def __init__(self, subaccount_repo: SubAccountRepository):
        self.subaccount_repo = subaccount_repo

    def validate_account_name(self, account_name: str) -> str:
        """
        验证账户名称
        """
        if not account_name or not account_name.strip():
            raise ValueError("账户名称不能为空")

        account_name = account_name.strip()

        if len(account_name) < 1 or len(account_name) > 50:
            raise ValueError("账户名称长度必须在 1-50 之间")

        return account_name

    def validate_passwords(self, login_password: str, payment_password: str) -> tuple:
        """
        验证密码
        """
        # 验证登录密码
        if not login_password or len(login_password) < 6 or len(login_password) > 20:
            raise ValueError("登录密码长度必须在 6-20 之间")

        # 验证支付密码
        if not payment_password or len(payment_password) < 6 or len(payment_password) > 20:
            raise ValueError("支付密码长度必须在 6-20 之间")

        return (login_password, payment_password)

    def validate_status(self, status: str) -> str:
        """
        验证状态
        """
        if status not in ["启用", "禁用"]:
            raise ValueError(f"无效的状态: {status}，只能是 '启用' 或 '禁用'")
        return status

    async def get_sub_accounts(
        self,
        agent_account: str,
        page: int,
        page_size: int
    ) -> Dict[str, Any]:
        """
        获取子账号列表
        """
        # 根据代理账号获取 user_id
        parent_user_id = await self.subaccount_repo.get_parent_user_id_by_agent_account(agent_account)
        if not parent_user_id:
            raise ValueError("代理账号不存在")

        return await self.subaccount_repo.get_sub_accounts(parent_user_id, page, page_size)

    async def create_sub_account(
        self,
        agent_account: str,
        login_password: str,
        payment_password: str,
        account_name: str,
        role_name: str
    ) -> int:
        """
        创建子账号
        """
        # 根据代理账号获取 user_id
        parent_user_id = await self.subaccount_repo.get_parent_user_id_by_agent_account(agent_account)
        if not parent_user_id:
            raise ValueError("代理账号不存在")

        # 验证账户名称
        account_name = self.validate_account_name(account_name)

        # 验证密码
        login_password, payment_password = self.validate_passwords(login_password, payment_password)

        # 根据角色名称获取角色ID
        role_id = await self.subaccount_repo.get_role_id_by_name(role_name)
        if not role_id:
            raise ValueError(f"角色不存在: {role_name}")

        # 生成账号
        account = await self.subaccount_repo.generate_account(agent_account)

        # 检查账号是否已存在（理论上不会，但保险起见）
        exists = await self.subaccount_repo.check_account_exists(account)
        if exists:
            import random
            account = f"{account}_{random.randint(100, 999)}"

        # 创建子账号
        return await self.subaccount_repo.create_sub_account(
            parent_user_id, account, login_password, payment_password, account_name, role_id
        )

    async def update_sub_account(
        self,
        sub_id: int,
        account_name: str,
        role_name: str,
        status: str
    ) -> bool:
        """
        更新子账号
        """
        # 检查子账号是否存在
        sub_account = await self.subaccount_repo.get_sub_account_by_id(sub_id)
        if not sub_account:
            raise ValueError("子账号不存在")

        # 验证账户名称
        account_name = self.validate_account_name(account_name)

        # 验证状态
        status = self.validate_status(status)

        # 根据角色名称获取角色ID
        role_id = await self.subaccount_repo.get_role_id_by_name(role_name)
        if not role_id:
            raise ValueError(f"角色不存在: {role_name}")

        # 更新子账号
        return await self.subaccount_repo.update_sub_account(
            sub_id, account_name, role_id, status
        )

    async def delete_sub_account(self, sub_id: int) -> bool:
        """
        删除子账号
        """
        # 检查子账号是否存在
        sub_account = await self.subaccount_repo.get_sub_account_by_id(sub_id)
        if not sub_account:
            raise ValueError("子账号不存在")

        # 删除子账号
        return await self.subaccount_repo.delete_sub_account(sub_id)
