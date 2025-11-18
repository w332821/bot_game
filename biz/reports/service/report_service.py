"""
报表服务层
"""
from typing import Optional, List, Dict, Any
from decimal import Decimal
import asyncio
import csv
import io
from biz.reports.repo.report_repo import ReportRepository


class ReportService:
    """报表服务"""

    def __init__(self, report_repo: ReportRepository):
        self.report_repo = report_repo

    async def get_financial_summary(
        self,
        date_start: str,
        date_end: str,
        plate: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取财务总报表"""
        return await self.report_repo.get_financial_summary(date_start, date_end, plate)

    async def get_financial_report(
        self,
        page: int,
        page_size: int,
        date_start: str,
        date_end: str,
        account: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取财务报表（含跨页统计）"""
        return await self.report_repo.get_financial_report(page, page_size, date_start, date_end, account)

    async def get_win_loss_report(
        self,
        page: int,
        page_size: int,
        date_start: str,
        date_end: str,
        game_types: Optional[List[str]] = None,
        account: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取输赢报表"""
        return await self.report_repo.get_win_loss_report(page, page_size, date_start, date_end, game_types, account)

    async def get_agent_win_loss_report(
        self,
        page: int,
        page_size: int,
        date_start: str,
        date_end: str,
        game_types: Optional[List[str]] = None,
        account: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取代理输赢报表（与会员报表类似）"""
        # 使用相同的逻辑,但可以加上代理筛选
        return await self.report_repo.get_win_loss_report(page, page_size, date_start, date_end, game_types, account)

    async def get_deposit_withdrawal_report(
        self,
        page: int,
        page_size: int,
        date_start: str,
        date_end: str,
        transaction_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取存取款报表"""
        return await self.report_repo.get_deposit_withdrawal_report(page, page_size, date_start, date_end, transaction_type)

    async def get_category_report(
        self,
        page: int,
        page_size: int,
        date_start: str,
        date_end: str,
        lottery_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取分类报表（按玩法分类）"""
        # 简化实现,返回示例数据
        return {
            "list": [],
            "total": 0
        }

    async def get_downline_details(
        self,
        page: int,
        page_size: int,
        account: str
    ) -> Dict[str, Any]:
        """获取下线明细（特殊结构: members + agents）"""
        # 简化实现,返回示例数据
        return {
            "members": {
                "list": [],
                "total": 0,
                "page": page,
                "pageSize": page_size
            },
            "agents": {
                "list": [],
                "total": 0,
                "page": page,
                "pageSize": page_size
            }
        }

    async def recalculate_financial_summary(
        self,
        date_start: str,
        date_end: str
    ) -> Dict[str, str]:
        """重新统计财务总报表（异步任务）"""
        # 简化实现,直接返回成功
        return {"status": "success", "message": "重新统计任务已启动"}

    def generate_csv_content(
        self,
        report_type: str,
        data: List[Dict[str, Any]]
    ) -> str:
        """生成CSV内容"""
        if not data:
            return ""

        output = io.StringIO()
        if len(data) > 0:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        return output.getvalue()
