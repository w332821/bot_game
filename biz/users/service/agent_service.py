from typing import Optional, Dict, Any, List
from biz.users.repo.agent_repo import AgentRepository


class AgentService:
    def __init__(self, agent_repo: AgentRepository):
        self.agent_repo = agent_repo

    async def list_agents(
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
        """获取代理列表"""
        return await self.agent_repo.list_agents(
            page, page_size, account, show_online, reg_start, reg_end, plate, balance_min, balance_max
        )

    async def get_agent_detail(self, account: str) -> Optional[Dict[str, Any]]:
        """获取代理详情"""
        return await self.agent_repo.get_agent_detail(account)

    async def get_agent_login_logs(self, account: str, page: int, page_size: int) -> Dict[str, Any]:
        """获取代理登录日志"""
        return await self.agent_repo.get_agent_login_logs(account, page, page_size)

    async def get_agent_members(
        self,
        agent_account: str,
        page: int,
        page_size: int,
        account: Optional[str] = None,
        show_online: Optional[bool] = None,
        reg_start: Optional[str] = None,
        reg_end: Optional[str] = None,
        plate: Optional[str] = None,
        balance_min: Optional[float] = None,
        balance_max: Optional[float] = None,
    ) -> Dict[str, Any]:
        """获取代理的下线会员列表"""
        return await self.agent_repo.get_agent_members(
            agent_account, page, page_size, account, show_online, reg_start, reg_end,
            plate, balance_min, balance_max
        )

    def validate_open_plate(self, open_plate: List[str]) -> List[str]:
        """验证开放盘口数组"""
        VALID_PLATES = {"A", "B", "C", "D"}
        if not open_plate or len(open_plate) == 0:
            raise ValueError("开放盘口不能为空")
        for plate in open_plate:
            if plate not in VALID_PLATES:
                raise ValueError(f"无效的盘口: {plate}，只能是 A/B/C/D")
        # 去重并保持顺序
        seen = set()
        result = []
        for p in open_plate:
            if p not in seen:
                seen.add(p)
                result.append(p)
        return result

    async def create_agent(
        self,
        account: str,
        password: str,
        plate: str,
        open_plate: List[str],
        earn_rebate: str,
        subordinate_transfer: str,
        default_rebate_plate: str,
        superior_account: Optional[str] = None,
        company_remarks: Optional[str] = None
    ) -> int:
        """创建代理"""
        # 验证 openPlate 数组
        validated_open_plate = self.validate_open_plate(open_plate)

        return await self.agent_repo.create_agent(
            account, password, plate, validated_open_plate, earn_rebate,
            subordinate_transfer, default_rebate_plate, superior_account, company_remarks
        )

    async def update_agent(
        self,
        agent_id: int,
        plate: Optional[str] = None,
        open_plate: Optional[List[str]] = None,
        earn_rebate: Optional[str] = None,
        subordinate_transfer: Optional[str] = None,
        default_rebate_plate: Optional[str] = None,
        company_remarks: Optional[str] = None
    ) -> bool:
        """修改代理"""
        # 如果提供了 openPlate，验证它
        validated_open_plate = None
        if open_plate is not None:
            validated_open_plate = self.validate_open_plate(open_plate)

        return await self.agent_repo.update_agent(
            agent_id, plate, validated_open_plate, earn_rebate,
            subordinate_transfer, default_rebate_plate, company_remarks
        )

    async def get_agent_transactions(
        self,
        account: str,
        page: int,
        page_size: int,
        transaction_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取代理交易记录"""
        return await self.agent_repo.get_agent_transactions(
            account, page, page_size, transaction_type, start_date, end_date
        )

    async def get_agent_account_changes(
        self,
        account: str,
        page: int,
        page_size: int,
        change_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取代理账变记录"""
        return await self.agent_repo.get_agent_account_changes(
            account, page, page_size, change_type, start_date, end_date
        )
