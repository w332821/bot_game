from typing import Optional, Dict, Any
from biz.users.repo.member_repo import MemberRepository


class MemberService:
    def __init__(self, member_repo: MemberRepository):
        self.member_repo = member_repo

    async def list_members(
        self,
        page: int,
        page_size: int,
        account: Optional[str],
        show_online: Optional[bool],
        reg_start: Optional[str],
        reg_end: Optional[str],
        plate: Optional[str],
        balance_min: Optional[float],
        balance_max: Optional[float],
    ) -> Dict[str, Any]:
        return await self.member_repo.list_members(
            page, page_size, account, show_online, reg_start, reg_end, plate, balance_min, balance_max
        )

    async def get_member_detail(self, account: str) -> Optional[Dict[str, Any]]:
        return await self.member_repo.get_member_detail(account)

    async def get_login_logs(self, account: str, page: int, page_size: int) -> Dict[str, Any]:
        return await self.member_repo.get_login_logs(account, page, page_size)

    async def create_member(
        self,
        phone: str,
        password: str,
        account: str,
        plate: str,
        nickname: Optional[str] = None,
        superior_account: Optional[str] = None,
        company_remarks: Optional[str] = None
    ) -> int:
        """创建会员"""
        return await self.member_repo.create_member(
            phone, password, account, plate, nickname, superior_account, company_remarks
        )

    async def link_bot_user(
        self,
        bot_user_id: str,
        chat_id: str,
        account: str,
        password: str,
        plate: str,
        superior_account: Optional[str] = None,
        company_remarks: Optional[str] = None
    ) -> int:
        """为现有Bot用户创建member_profiles配置"""
        return await self.member_repo.link_bot_user(
            bot_user_id, chat_id, account, password, plate, superior_account, company_remarks
        )

    async def update_member(self, member_id: int, plate: Optional[str] = None, company_remarks: Optional[str] = None) -> bool:
        """修改会员"""
        return await self.member_repo.update_member(member_id, plate, company_remarks)

    async def get_bet_orders(
        self,
        account: str,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        bet_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取会员注单列表"""
        return await self.member_repo.get_bet_orders(account, page, page_size, status, bet_type, start_date, end_date)

    async def get_transactions(
        self,
        account: str,
        page: int,
        page_size: int,
        transaction_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取会员交易记录"""
        return await self.member_repo.get_transactions(account, page, page_size, transaction_type, start_date, end_date)

    async def get_account_changes(
        self,
        account: str,
        page: int,
        page_size: int,
        change_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取会员账变记录"""
        return await self.member_repo.get_account_changes(account, page, page_size, change_type, start_date, end_date)