from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import text
from decimal import Decimal
import bcrypt
import random
import string
import json


class AgentRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    def _generate_invite_code(self, length=8) -> str:
        """生成邀请码（大写字母+数字）"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=length))

    async def generate_unique_invite_code(self) -> str:
        """生成唯一邀请码"""
        async with self._session_factory() as session:
            max_attempts = 100
            for _ in range(max_attempts):
                code = self._generate_invite_code()
                # 检查唯一性
                check_query = text("SELECT COUNT(*) FROM agent_profiles WHERE invite_code = :code")
                result = await session.execute(check_query, {"code": code})
                count = result.scalar()
                if count == 0:
                    return code
            raise RuntimeError("无法生成唯一邀请码")

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
        online_window_minutes: int = 5,
    ) -> Dict[str, Any]:
        offset = (page - 1) * page_size
        where = ["1=1"]
        params: Dict[str, Any] = {
            "offset": offset,
            "limit": page_size,
            "win": online_window_minutes,
        }
        if account:
            where.append("ap.account LIKE :account")
            params["account"] = f"%{account}%"
        if plate:
            where.append("ap.plate = :plate")
            params["plate"] = plate
        if reg_start:
            where.append("ap.open_time >= :reg_start")
            params["reg_start"] = reg_start + " 00:00:00"
        if reg_end:
            where.append("ap.open_time <= :reg_end")
            params["reg_end"] = reg_end + " 23:59:59"
        if balance_min is not None:
            where.append("u.balance >= :bmin")
            params["bmin"] = balance_min
        if balance_max is not None:
            where.append("u.balance <= :bmax")
            params["bmax"] = balance_max

        online_filter = ""
        if show_online:
            online_filter = (
                "AND EXISTS ("
                "SELECT 1 FROM online_status os "
                "WHERE CAST(os.user_id AS CHAR) = CAST(u.id AS CHAR) "
                "AND os.last_seen >= DATE_SUB(NOW(), INTERVAL :win MINUTE)"
                ")"
            )

        async with self._session_factory() as session:
            query = text(
                f"""
                SELECT ap.id, ap.account, u.balance, ap.plate, ap.open_plate,
                       ap.open_time, ap.superior_account,
                       CASE WHEN EXISTS (
                           SELECT 1 FROM online_status os
                           WHERE CAST(os.user_id AS CHAR) = CAST(u.id AS CHAR) AND os.last_seen >= DATE_SUB(NOW(), INTERVAL :win MINUTE)
                       ) THEN 1 ELSE 0 END AS online
                FROM agent_profiles ap
                JOIN users u ON CAST(u.id AS CHAR) = CAST(ap.user_id AS CHAR)
                WHERE {' AND '.join(where)} {online_filter}
                ORDER BY ap.open_time DESC
                LIMIT :limit OFFSET :offset
                """
            )
            result = await session.execute(query, params)
            rows = result.fetchall()

            count_query = text(
                f"""
                SELECT COUNT(*) AS cnt
                FROM agent_profiles ap
                JOIN users u ON CAST(u.id AS CHAR) = CAST(ap.user_id AS CHAR)
                WHERE {' AND '.join(where)} {online_filter}
                """
            )
            total_res = await session.execute(count_query, params)
            total_row = total_res.fetchone()
            total = int(total_row[0]) if total_row else 0

            items: List[Dict[str, Any]] = []
            for r in rows:
                m = r._mapping
                # 解析 open_plate JSON
                try:
                    open_plate_list = json.loads(m["open_plate"])
                    plate_display = ",".join([f"{p}盘" for p in open_plate_list])
                except:
                    plate_display = f"{m['plate']}盘"

                items.append({
                    "id": int(m["id"]),
                    "account": m["account"],
                    "online": bool(m["online"]),
                    "balance": float(m["balance"]),
                    "plate": plate_display,  # 显示为 "A盘,B盘,C盘"
                    "openTime": str(m["open_time"]),
                    "superior": m["superior_account"] or ""
                })

            return {"list": items, "total": total}

    async def get_agent_detail(self, account: str) -> Optional[Dict[str, Any]]:
        async with self._session_factory() as session:
            query = text(
                """
                SELECT ap.account, ap.superior_account, u.balance, ap.plate,
                       ap.open_plate, ap.earn_rebate, ap.subordinate_transfer,
                       ap.default_rebate_plate, ap.invite_code, ap.promotion_domains,
                       ap.company_remarks, ap.open_time
                FROM agent_profiles ap
                JOIN users u ON CAST(u.id AS CHAR) = CAST(ap.user_id AS CHAR)
                WHERE ap.account COLLATE utf8mb4_unicode_ci = :account
                LIMIT 1
                """
            )
            res = await session.execute(query, {"account": account})
            row = res.fetchone()
            if not row:
                return None
            m = row._mapping

            # 解析 JSON 字段
            try:
                open_plate = json.loads(m["open_plate"])
            except:
                open_plate = ["A", "B", "C"]

            try:
                promotion_domains = json.loads(m["promotion_domains"])
            except:
                promotion_domains = []

            return {
                "account": m["account"],
                "superior": m["superior_account"] or "",
                "balance": float(m["balance"]),
                "plate": m["plate"],
                "openPlate": open_plate,  # 返回数组
                "earnRebate": m["earn_rebate"],
                "subordinateTransfer": m["subordinate_transfer"],
                "defaultRebatePlate": m["default_rebate_plate"],
                "inviteCode": m["invite_code"],
                "promotionDomains": promotion_domains,  # 返回数组
                "companyRemarks": m["company_remarks"] or "",
                "openTime": str(m["open_time"])
            }

    async def get_agent_login_logs(self, account: str, page: int, page_size: int) -> Dict[str, Any]:
        """复用登录日志查询逻辑"""
        offset = (page - 1) * page_size
        async with self._session_factory() as session:
            q = text(
                """
                SELECT id, login_time, ip_address, ip_location, operator
                FROM login_logs
                WHERE account = :account
                ORDER BY login_time DESC
                LIMIT :limit OFFSET :offset
                """
            )
            res = await session.execute(q, {"account": account, "limit": page_size, "offset": offset})
            rows = res.fetchall()
            items = []
            for r in rows:
                m = r._mapping
                items.append({
                    "id": int(m["id"]),
                    "loginTime": str(m["login_time"]),
                    "ipAddress": m["ip_address"] or "",
                    "ipLocation": m["ip_location"] or "",
                    "operator": m["operator"] or ""
                })
            cnt_res = await session.execute(
                text("SELECT COUNT(*) AS cnt FROM login_logs WHERE account = :account"),
                {"account": account}
            )
            total_row = cnt_res.fetchone()
            total = int(total_row[0]) if total_row else 0
            return {"list": items, "total": total}

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
        online_window_minutes: int = 5,
    ) -> Dict[str, Any]:
        """获取代理的下线会员列表"""
        offset = (page - 1) * page_size
        where = ["mp.superior_account = :agent_account"]
        params: Dict[str, Any] = {
            "agent_account": agent_account,
            "offset": offset,
            "limit": page_size,
            "win": online_window_minutes,
        }
        if account:
            where.append("mp.account LIKE :account")
            params["account"] = f"%{account}%"
        if plate:
            where.append("mp.plate = :plate")
            params["plate"] = plate
        if reg_start:
            where.append("mp.open_time >= :reg_start")
            params["reg_start"] = reg_start + " 00:00:00"
        if reg_end:
            where.append("mp.open_time <= :reg_end")
            params["reg_end"] = reg_end + " 23:59:59"
        if balance_min is not None:
            where.append("u.balance >= :bmin")
            params["bmin"] = balance_min
        if balance_max is not None:
            where.append("u.balance <= :bmax")
            params["bmax"] = balance_max

        online_filter = ""
        if show_online:
            online_filter = "AND EXISTS (SELECT 1 FROM online_status os WHERE CAST(os.user_id AS CHAR) = CAST(u.id AS CHAR) AND os.last_seen >= DATE_SUB(NOW(), INTERVAL :win MINUTE))"

        async with self._session_factory() as session:
            query = text(
                f"""
                SELECT mp.id, mp.account, u.balance, mp.plate, mp.open_time, mp.superior_account,
                       CASE WHEN EXISTS (
                           SELECT 1 FROM online_status os
                           WHERE CAST(os.user_id AS CHAR) = CAST(u.id AS CHAR) AND os.last_seen >= DATE_SUB(NOW(), INTERVAL :win MINUTE)
                       ) THEN 1 ELSE 0 END AS online
                FROM member_profiles mp
                JOIN users u ON CAST(u.id AS CHAR) = CAST(mp.user_id AS CHAR)
                WHERE {' AND '.join(where)} {online_filter}
                ORDER BY mp.open_time DESC
                LIMIT :limit OFFSET :offset
                """
            )
            result = await session.execute(query, params)
            rows = result.fetchall()

            count_query = text(
                f"""
                SELECT COUNT(*) AS cnt
                FROM member_profiles mp
                JOIN users u ON CAST(u.id AS CHAR) = CAST(mp.user_id AS CHAR)
                WHERE {' AND '.join(where)} {online_filter}
                """
            )
            total_res = await session.execute(count_query, params)
            total_row = total_res.fetchone()
            total = int(total_row[0]) if total_row else 0

            items: List[Dict[str, Any]] = []
            for r in rows:
                m = r._mapping
                items.append({
                    "id": int(m["id"]),
                    "account": m["account"],
                    "online": bool(m["online"]),
                    "balance": float(m["balance"]),
                    "plate": f"{m['plate']}盘",
                    "openTime": str(m["open_time"]),
                    "superior": m["superior_account"] or ""
                })

            return {"list": items, "total": total}

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
        """
        创建代理
        返回: agent_profile_id
        """
        # Hash password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # 生成唯一邀请码
        invite_code = await self.generate_unique_invite_code()

        async with self._session_factory() as session:
            # Check if account already exists
            check_query = text("SELECT COUNT(*) FROM agent_profiles WHERE account = :account")
            result = await session.execute(check_query, {"account": account})
            count = result.scalar()
            if count > 0:
                raise ValueError("账号已存在")

            # 先创建 users 记录（通用账户数据，不含密码）
            # 生成唯一的 user_id
            import uuid
            user_id = str(uuid.uuid4())

            user_query = text(
                """
                INSERT INTO users (id, username, chat_id, balance, join_date, created_at, updated_at)
                VALUES (:id, :username, :chat_id, :balance, CURDATE(), NOW(), NOW())
                """
            )
            await session.execute(user_query, {
                "id": user_id,
                "username": account,  # 使用账号作为用户名
                "chat_id": "admin_backend",  # 后台管理账号，标记为特殊 chat_id
                "balance": Decimal("0.00")
            })
            await session.flush()

            # 创建 agent profile（扩展信息，包含密码）
            agent_query = text(
                """
                INSERT INTO agent_profiles
                (user_id, account, password, plate, open_plate, earn_rebate, subordinate_transfer,
                 default_rebate_plate, invite_code, promotion_domains, superior_account, company_remarks, open_time, created_at)
                VALUES
                (:user_id, :account, :password, :plate, :open_plate, :earn_rebate, :subordinate_transfer,
                 :default_rebate_plate, :invite_code, :promotion_domains, :superior_account, :company_remarks, NOW(), NOW())
                """
            )
            await session.execute(agent_query, {
                "user_id": user_id,
                "account": account,
                "password": hashed_password,
                "plate": plate,
                "open_plate": json.dumps(open_plate),
                "earn_rebate": earn_rebate,
                "subordinate_transfer": subordinate_transfer,
                "default_rebate_plate": default_rebate_plate,
                "invite_code": invite_code,
                "promotion_domains": json.dumps([]),  # 初始化为空数组
                "superior_account": superior_account,
                "company_remarks": company_remarks
            })
            await session.flush()

            # Get agent_profile_id
            agent_id_result = await session.execute(text("SELECT LAST_INSERT_ID() AS id"))
            agent_id = agent_id_result.scalar()

            await session.commit()
            return int(agent_id)

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
        """
        修改代理
        返回: 是否成功
        """
        async with self._session_factory() as session:
            # Check if agent exists
            check_query = text("SELECT COUNT(*) FROM agent_profiles WHERE id = :id")
            result = await session.execute(check_query, {"id": agent_id})
            count = result.scalar()
            if count == 0:
                raise ValueError("代理不存在")

            # Build update query dynamically
            updates = []
            params: Dict[str, Any] = {"id": agent_id}

            if plate is not None:
                updates.append("plate = :plate")
                params["plate"] = plate

            if open_plate is not None:
                updates.append("open_plate = :open_plate")
                params["open_plate"] = json.dumps(open_plate)

            if earn_rebate is not None:
                updates.append("earn_rebate = :earn_rebate")
                params["earn_rebate"] = earn_rebate

            if subordinate_transfer is not None:
                updates.append("subordinate_transfer = :subordinate_transfer")
                params["subordinate_transfer"] = subordinate_transfer

            if default_rebate_plate is not None:
                updates.append("default_rebate_plate = :default_rebate_plate")
                params["default_rebate_plate"] = default_rebate_plate

            if company_remarks is not None:
                updates.append("company_remarks = :company_remarks")
                params["company_remarks"] = company_remarks

            if not updates:
                return True  # Nothing to update

            update_query = text(f"UPDATE agent_profiles SET {', '.join(updates)} WHERE id = :id")
            await session.execute(update_query, params)
            await session.commit()
            return True

    async def get_agent_transactions(
        self,
        account: str,
        page: int,
        page_size: int,
        transaction_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取代理交易记录
        返回: {list: [...], total: int, summary: {...}}
        """
        offset = (page - 1) * page_size
        where = ["ap.account = :account"]
        params: Dict[str, Any] = {"account": account, "offset": offset, "limit": page_size}

        if transaction_type:
            where.append("t.transaction_type = :transaction_type")
            params["transaction_type"] = transaction_type

        if start_date:
            where.append("t.transaction_time >= :start_date")
            params["start_date"] = start_date + " 00:00:00"

        if end_date:
            where.append("t.transaction_time <= :end_date")
            params["end_date"] = end_date + " 23:59:59"

        async with self._session_factory() as session:
            # Get list
            list_query = text(
                f"""
                SELECT t.id, t.transaction_no, t.transaction_type, t.amount,
                       t.balance_before, t.balance_after, t.transaction_time, t.remarks
                FROM transactions t
                JOIN agent_profiles ap ON CAST(ap.user_id AS CHAR) = CAST(t.user_id AS CHAR)
                WHERE {' AND '.join(where)}
                ORDER BY t.transaction_time DESC
                LIMIT :limit OFFSET :offset
                """
            )
            result = await session.execute(list_query, params)
            rows = result.fetchall()

            items = []
            for r in rows:
                m = r._mapping
                items.append({
                    "id": int(m["id"]),
                    "transactionNo": m["transaction_no"],
                    "transactionType": m["transaction_type"],
                    "amount": float(m["amount"]),
                    "balanceBefore": float(m["balance_before"]),
                    "balanceAfter": float(m["balance_after"]),
                    "transactionTime": str(m["transaction_time"]),
                    "remarks": m["remarks"] or ""
                })

            # Get total count
            count_query = text(
                f"""
                SELECT COUNT(*) AS cnt
                FROM transactions t
                JOIN agent_profiles ap ON CAST(ap.user_id AS CHAR) = CAST(t.user_id AS CHAR)
                WHERE {' AND '.join(where)}
                """
            )
            count_result = await session.execute(count_query, params)
            total = count_result.scalar() or 0

            # Get summary for current page
            summary_query = text(
                f"""
                SELECT COALESCE(SUM(t.amount), 0) AS total_amount
                FROM transactions t
                JOIN agent_profiles ap ON CAST(ap.user_id AS CHAR) = CAST(t.user_id AS CHAR)
                WHERE {' AND '.join(where)}
                LIMIT :limit OFFSET :offset
                """
            )
            summary_result = await session.execute(summary_query, params)
            summary_row = summary_result.fetchone()
            summary = {
                "totalAmount": float(summary_row[0]) if summary_row else 0.0
            }

            return {"list": items, "total": int(total), "summary": summary}

    async def get_agent_account_changes(
        self,
        account: str,
        page: int,
        page_size: int,
        change_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取代理账变记录
        返回: {list: [...], total: int}
        """
        offset = (page - 1) * page_size
        where = ["ap.account = :account"]
        params: Dict[str, Any] = {"account": account, "offset": offset, "limit": page_size}

        if change_type:
            where.append("ac.change_type = :change_type")
            params["change_type"] = change_type

        if start_date:
            where.append("ac.change_time >= :start_date")
            params["start_date"] = start_date + " 00:00:00"

        if end_date:
            where.append("ac.change_time <= :end_date")
            params["end_date"] = end_date + " 23:59:59"

        async with self._session_factory() as session:
            # Get list
            list_query = text(
                f"""
                SELECT ac.id, ac.change_type, ac.amount, ac.balance_before,
                       ac.balance_after, ac.change_time, ac.remarks
                FROM account_changes ac
                JOIN agent_profiles ap ON CAST(ap.user_id AS CHAR) = CAST(ac.user_id AS CHAR)
                WHERE {' AND '.join(where)}
                ORDER BY ac.change_time DESC
                LIMIT :limit OFFSET :offset
                """
            )
            result = await session.execute(list_query, params)
            rows = result.fetchall()

            items = []
            for r in rows:
                m = r._mapping
                items.append({
                    "id": int(m["id"]),
                    "changeType": m["change_type"],
                    "amount": float(m["amount"]),
                    "balanceBefore": float(m["balance_before"]),
                    "balanceAfter": float(m["balance_after"]),
                    "changeTime": str(m["change_time"]),
                    "remarks": m["remarks"] or ""
                })

            # Get total count
            count_query = text(
                f"""
                SELECT COUNT(*) AS cnt
                FROM account_changes ac
                JOIN agent_profiles ap ON CAST(ap.user_id AS CHAR) = CAST(ac.user_id AS CHAR)
                WHERE {' AND '.join(where)}
                """
            )
            count_result = await session.execute(count_query, params)
            total = count_result.scalar() or 0

            return {"list": items, "total": int(total)}
