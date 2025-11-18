"""
报表仓储层
负责从数据库查询报表数据
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from typing import Optional, List, Dict, Any
from datetime import datetime
from base.game_name_mapper import game_code_to_name, GAME_CODE_TO_NAME


class ReportRepository:
    """报表仓储"""

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def get_financial_summary(
        self,
        date_start: str,
        date_end: str,
        plate: Optional[str] = None
    ) -> Dict[str, Decimal]:
        """
        查询财务总报表

        Args:
            date_start: 开始日期 YYYY-MM-DD
            date_end: 结束日期 YYYY-MM-DD
            plate: 盘口 A/B/C/D (可选)

        Returns:
            dict: 财务汇总数据
        """
        async with self.session_factory() as session:
            # 构建日期时间范围
            start_dt = f"{date_start} 00:00:00"
            end_dt = f"{date_end} 23:59:59"

            # 查询存取款数据
            deposit_query = text("""
                SELECT
                    COALESCE(SUM(CASE WHEN transaction_type = 'deposit' THEN amount ELSE 0 END), 0) as total_deposit,
                    COALESCE(SUM(CASE WHEN transaction_type = 'withdrawal' THEN amount ELSE 0 END), 0) as total_withdrawal,
                    COALESCE(SUM(fee), 0) as total_fee
                FROM transactions
                WHERE transaction_time BETWEEN :start_dt AND :end_dt
                    AND status = 'success'
            """)

            result = await session.execute(deposit_query, {"start_dt": start_dt, "end_dt": end_dt})
            row = result.fetchone()

            deposit_amount = Decimal(str(row[0])) if row and row[0] else Decimal("0.00")
            withdrawal_amount = Decimal(str(row[1])) if row and row[1] else Decimal("0.00")
            total_fee = Decimal(str(row[2])) if row and row[2] else Decimal("0.00")

            # 查询注单数据
            bet_query = text("""
                SELECT
                    COALESCE(SUM(bet_amount), 0) as total_bet,
                    COALESCE(SUM(valid_amount), 0) as total_valid,
                    COALESCE(SUM(rebate), 0) as total_rebate,
                    COALESCE(SUM(bet_result), 0) as total_win_loss
                FROM bet_orders
                WHERE bet_time BETWEEN :start_dt AND :end_dt
                    AND status = 'settled'
            """)

            result = await session.execute(bet_query, {"start_dt": start_dt, "end_dt": end_dt})
            row = result.fetchone()

            total_bet = Decimal(str(row[0])) if row and row[0] else Decimal("0.00")
            total_valid = Decimal(str(row[1])) if row and row[1] else Decimal("0.00")
            total_rebate = Decimal(str(row[2])) if row and row[2] else Decimal("0.00")
            total_win_loss = Decimal(str(row[3])) if row and row[3] else Decimal("0.00")

            # 计算利润 = 存款 - 取款 - 输赢
            profit = deposit_amount - withdrawal_amount - total_win_loss

            return {
                "depositAmount": deposit_amount,
                "withdrawalAmount": withdrawal_amount,
                "bonus": Decimal("0.00"),  # 暂无优惠数据
                "irregularBet": Decimal("0.00"),  # 暂无异常注单
                "returnAmount": Decimal("0.00"),  # 暂无返还数据
                "handlingFee": total_fee,
                "depositWithdrawalFee": total_fee,
                "winLoss": total_win_loss,
                "profit": profit,
                "totalBetAmount": total_bet,
                "totalRebate": total_rebate
            }

    async def get_financial_report(
        self,
        page: int,
        page_size: int,
        date_start: str,
        date_end: str,
        account: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询财务报表（分页）

        Args:
            page: 页码
            page_size: 每页数量
            date_start: 开始日期
            date_end: 结束日期
            account: 账号（可选）

        Returns:
            dict: {list, total, cross_page_stats}
        """
        async with self.session_factory() as session:
            start_dt = f"{date_start} 00:00:00"
            end_dt = f"{date_end} 23:59:59"

            # 构建WHERE条件
            where_clause = "WHERE b.bet_time BETWEEN :start_dt AND :end_dt AND b.status = 'settled'"
            params = {"start_dt": start_dt, "end_dt": end_dt}

            if account:
                where_clause += " AND m.account = :account"
                params["account"] = account

            # 查询分页数据
            offset = (page - 1) * page_size
            list_query = text(f"""
                SELECT
                    m.account,
                    COALESCE(m.name, m.account) as account_name,
                    b.bet_type as game_type,
                    COALESCE(SUM(b.bet_amount), 0) as bet_amount,
                    COALESCE(SUM(b.valid_amount), 0) as valid_amount,
                    COALESCE(SUM(b.rebate), 0) as rebate,
                    COALESCE(SUM(b.bet_result), 0) as win_loss
                FROM bet_orders b
                LEFT JOIN member_profiles m ON BINARY b.user_id = BINARY m.user_id
                {where_clause}
                GROUP BY m.account, m.name, b.bet_type
                LIMIT :page_size OFFSET :offset
            """)

            params["page_size"] = page_size
            params["offset"] = offset

            result = await session.execute(list_query, params)
            rows = result.fetchall()

            list_data = []
            for row in rows:
                # 将游戏类型从数据库代码转换为中文名
                game_type_cn = row[2]  # 已经是中文了(bet_type字段)
                list_data.append({
                    "account": row[0] or "",
                    "accountName": row[1] or "",
                    "gameType": game_type_cn or "",
                    "betAmount": Decimal(str(row[3])) if row[3] else Decimal("0.00"),
                    "validAmount": Decimal(str(row[4])) if row[4] else Decimal("0.00"),
                    "rebate": Decimal(str(row[5])) if row[5] else Decimal("0.00"),
                    "winLoss": Decimal(str(row[6])) if row[6] else Decimal("0.00"),
                    "depositAmount": Decimal("0.00"),
                    "withdrawalAmount": Decimal("0.00")
                })

            # 查询总数
            count_query = text(f"""
                SELECT COUNT(DISTINCT CONCAT(m.account, '-', b.bet_type))
                FROM bet_orders b
                LEFT JOIN member_profiles m ON BINARY b.user_id = BINARY m.user_id
                {where_clause}
            """)

            count_params = {"start_dt": start_dt, "end_dt": end_dt}
            if account:
                count_params["account"] = account

            result = await session.execute(count_query, count_params)
            total = result.scalar() or 0

            # 查询跨页统计（所有页）
            cross_stats_query = text(f"""
                SELECT
                    COALESCE(SUM(b.bet_amount), 0) as total_bet,
                    COALESCE(SUM(b.valid_amount), 0) as total_valid,
                    COALESCE(SUM(b.rebate), 0) as total_rebate,
                    COALESCE(SUM(b.bet_result), 0) as total_win_loss
                FROM bet_orders b
                LEFT JOIN member_profiles m ON BINARY b.user_id = BINARY m.user_id
                {where_clause}
            """)

            result = await session.execute(cross_stats_query, count_params)
            stats_row = result.fetchone()

            cross_page_stats = {
                "totalBetAmount": Decimal(str(stats_row[0])) if stats_row and stats_row[0] else Decimal("0.00"),
                "totalValidAmount": Decimal(str(stats_row[1])) if stats_row and stats_row[1] else Decimal("0.00"),
                "totalRebate": Decimal(str(stats_row[2])) if stats_row and stats_row[2] else Decimal("0.00"),
                "totalWinLoss": Decimal(str(stats_row[3])) if stats_row and stats_row[3] else Decimal("0.00"),
                "totalDeposit": Decimal("0.00"),
                "totalWithdrawal": Decimal("0.00")
            }

            return {
                "list": list_data,
                "total": total,
                "cross_page_stats": cross_page_stats
            }

    async def get_win_loss_report(
        self,
        page: int,
        page_size: int,
        date_start: str,
        date_end: str,
        game_types: Optional[List[str]] = None,
        account: Optional[str] = None
    ) -> Dict[str, Any]:
        """查询输赢报表"""
        async with self.session_factory() as session:
            start_dt = f"{date_start} 00:00:00"
            end_dt = f"{date_end} 23:59:59"

            where_clause = "WHERE b.bet_time BETWEEN :start_dt AND :end_dt AND b.status = 'settled'"
            params = {"start_dt": start_dt, "end_dt": end_dt}

            if account:
                where_clause += " AND m.account = :account"
                params["account"] = account

            if game_types:
                # game_types是中文名称列表,bet_type字段存储的也是中文
                placeholders = ",".join([f":game_type_{i}" for i in range(len(game_types))])
                where_clause += f" AND b.bet_type IN ({placeholders})"
                for i, gt in enumerate(game_types):
                    params[f"game_type_{i}"] = gt

            offset = (page - 1) * page_size
            query = text(f"""
                SELECT
                    m.account,
                    COALESCE(m.name, m.account) as account_name,
                    b.bet_type as game_type,
                    COALESCE(SUM(b.bet_amount), 0) as bet_amount,
                    COALESCE(SUM(b.valid_amount), 0) as valid_amount,
                    COALESCE(SUM(b.rebate), 0) as rebate,
                    COALESCE(SUM(b.bet_result), 0) as win_loss
                FROM bet_orders b
                LEFT JOIN member_profiles m ON b.user_id = m.user_id
                {where_clause}
                GROUP BY m.account, m.name, b.bet_type
                LIMIT :page_size OFFSET :offset
            """)

            params["page_size"] = page_size
            params["offset"] = offset

            result = await session.execute(query, params)
            rows = result.fetchall()

            list_data = []
            for row in rows:
                list_data.append({
                    "account": row[0] or "",
                    "accountName": row[1] or "",
                    "gameType": row[2] or "",  # 已经是中文
                    "betAmount": Decimal(str(row[3])) if row[3] else Decimal("0.00"),
                    "validAmount": Decimal(str(row[4])) if row[4] else Decimal("0.00"),
                    "rebate": Decimal(str(row[5])) if row[5] else Decimal("0.00"),
                    "winLoss": Decimal(str(row[6])) if row[6] else Decimal("0.00")
                })

            # 查询总数
            count_params = {"start_dt": start_dt, "end_dt": end_dt}
            if account:
                count_params["account"] = account
            if game_types:
                for i, gt in enumerate(game_types):
                    count_params[f"game_type_{i}"] = gt

            count_query = text(f"""
                SELECT COUNT(DISTINCT CONCAT(m.account, '-', b.bet_type))
                FROM bet_orders b
                LEFT JOIN member_profiles m ON b.user_id = m.user_id
                {where_clause}
            """)

            result = await session.execute(count_query, count_params)
            total = result.scalar() or 0

            return {
                "list": list_data,
                "total": total
            }

    async def get_deposit_withdrawal_report(
        self,
        page: int,
        page_size: int,
        date_start: str,
        date_end: str,
        transaction_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """查询存取款报表"""
        async with self.session_factory() as session:
            start_dt = f"{date_start} 00:00:00"
            end_dt = f"{date_end} 23:59:59"

            where_clause = "WHERE t.transaction_time BETWEEN :start_dt AND :end_dt"
            params = {"start_dt": start_dt, "end_dt": end_dt}

            if transaction_type:
                where_clause += " AND t.transaction_type = :transaction_type"
                params["transaction_type"] = transaction_type

            offset = (page - 1) * page_size
            query = text(f"""
                SELECT
                    m.account,
                    COALESCE(m.name, m.account) as account_name,
                    t.transaction_time,
                    t.transaction_type,
                    t.amount,
                    t.fee,
                    t.status,
                    t.processor
                FROM transactions t
                LEFT JOIN member_profiles m ON BINARY t.user_id = BINARY m.user_id
                {where_clause}
                ORDER BY t.transaction_time DESC
                LIMIT :page_size OFFSET :offset
            """)

            params["page_size"] = page_size
            params["offset"] = offset

            result = await session.execute(query, params)
            rows = result.fetchall()

            list_data = []
            for row in rows:
                list_data.append({
                    "account": row[0] or "",
                    "accountName": row[1] or "",
                    "transactionTime": row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else "",
                    "transactionType": row[3] or "",
                    "amount": Decimal(str(row[4])) if row[4] else Decimal("0.00"),
                    "fee": Decimal(str(row[5])) if row[5] else Decimal("0.00"),
                    "status": row[6] or "",
                    "processor": row[7]
                })

            # 查询总数
            count_query = text(f"""
                SELECT COUNT(*)
                FROM transactions t
                LEFT JOIN member_profiles m ON BINARY t.user_id = BINARY m.user_id
                {where_clause}
            """)

            count_params = {"start_dt": start_dt, "end_dt": end_dt}
            if transaction_type:
                count_params["transaction_type"] = transaction_type

            result = await session.execute(count_query, count_params)
            total = result.scalar() or 0

            return {
                "list": list_data,
                "total": total
            }
