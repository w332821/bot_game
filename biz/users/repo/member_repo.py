from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import text
from decimal import Decimal
import bcrypt


class MemberRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

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

    async def get_member_detail(self, account: str) -> Optional[Dict[str, Any]]:
        async with self._session_factory() as session:
            query = text(
                """
                SELECT mp.account, mp.superior_account, u.balance, mp.plate, mp.company_remarks, mp.open_time
                FROM member_profiles mp JOIN users u ON CAST(u.id AS CHAR) = CAST(mp.user_id AS CHAR)
                WHERE mp.account COLLATE utf8mb4_unicode_ci = :account
                LIMIT 1
                """
            )
            res = await session.execute(query, {"account": account})
            row = res.fetchone()
            if not row:
                return None
            m = row._mapping
            return {
                "account": m["account"],
                "superior": m["superior_account"] or "",
                "balance": float(m["balance"]),
                "plate": m["plate"],
                "companyRemarks": m["company_remarks"] or "",
                "openTime": str(m["open_time"])
            }

    async def get_login_logs(self, account: str, page: int, page_size: int) -> Dict[str, Any]:
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
            cnt_res = await session.execute(text("SELECT COUNT(*) AS cnt FROM login_logs WHERE account = :account"), {"account": account})
            total_row = cnt_res.fetchone()
            total = int(total_row[0]) if total_row else 0
            return {"list": items, "total": total}

    async def create_member(
        self,
        account: str,
        password: str,
        plate: str,
        superior_account: Optional[str] = None,
        company_remarks: Optional[str] = None
    ) -> int:
        """
        创建会员
        返回: member_profile_id
        """
        # Hash password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        async with self._session_factory() as session:
            # Check if account already exists
            check_query = text("SELECT COUNT(*) FROM member_profiles WHERE account = :account")
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

            # 创建 member profile（扩展信息，包含密码）
            member_query = text(
                """
                INSERT INTO member_profiles (user_id, account, password, plate, superior_account, company_remarks, level, open_time, created_at)
                VALUES (:user_id, :account, :password, :plate, :superior_account, :company_remarks, 1, NOW(), NOW())
                """
            )
            await session.execute(member_query, {
                "user_id": user_id,
                "account": account,
                "password": hashed_password,
                "plate": plate,
                "superior_account": superior_account,
                "company_remarks": company_remarks
            })
            await session.flush()

            # Get member_profile_id
            member_id_result = await session.execute(text("SELECT LAST_INSERT_ID() AS id"))
            member_id = member_id_result.scalar()

            await session.commit()
            return int(member_id)

    async def update_member(self, member_id: int, plate: Optional[str] = None, company_remarks: Optional[str] = None) -> bool:
        """
        修改会员 - 只能修改 plate 和 companyRemarks
        返回: 是否成功
        """
        async with self._session_factory() as session:
            # Check if member exists
            check_query = text("SELECT COUNT(*) FROM member_profiles WHERE id = :id")
            result = await session.execute(check_query, {"id": member_id})
            count = result.scalar()
            if count == 0:
                raise ValueError("会员不存在")

            # Build update query dynamically
            updates = []
            params: Dict[str, Any] = {"id": member_id}

            if plate is not None:
                updates.append("plate = :plate")
                params["plate"] = plate

            if company_remarks is not None:
                updates.append("company_remarks = :company_remarks")
                params["company_remarks"] = company_remarks

            if not updates:
                return True  # Nothing to update

            update_query = text(f"UPDATE member_profiles SET {', '.join(updates)} WHERE id = :id")
            await session.execute(update_query, params)
            await session.commit()
            return True

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
        """
        获取会员注单列表
        返回: {list: [...], total: int, summary: {...}}
        """
        offset = (page - 1) * page_size
        where = ["mp.account = :account"]
        params: Dict[str, Any] = {"account": account, "offset": offset, "limit": page_size}

        if status:
            where.append("bo.status = :status")
            params["status"] = status

        if bet_type:
            where.append("bo.bet_type = :bet_type")
            params["bet_type"] = bet_type

        if start_date:
            where.append("bo.bet_time >= :start_date")
            params["start_date"] = start_date + " 00:00:00"

        if end_date:
            where.append("bo.bet_time <= :end_date")
            params["end_date"] = end_date + " 23:59:59"

        async with self._session_factory() as session:
            # Get list
            list_query = text(
                f"""
                SELECT bo.id, bo.order_no, bo.bet_type, bo.bet_amount, bo.bet_result,
                       bo.status, bo.bet_time, bo.settle_time
                FROM bet_orders bo
                JOIN member_profiles mp ON CAST(mp.user_id AS CHAR) = CAST(bo.user_id AS CHAR)
                WHERE {' AND '.join(where)}
                ORDER BY bo.bet_time DESC
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
                    "orderNo": m["order_no"],
                    "betType": m["bet_type"],
                    "betAmount": float(m["bet_amount"]),
                    "winAmount": float(m["bet_result"]) if m["bet_result"] else 0.0,
                    "status": m["status"],
                    "betTime": str(m["bet_time"]),
                    "settleTime": str(m["settle_time"]) if m["settle_time"] else None
                })

            # Get total count
            count_query = text(
                f"""
                SELECT COUNT(*) AS cnt
                FROM bet_orders bo
                JOIN member_profiles mp ON CAST(mp.user_id AS CHAR) = CAST(bo.user_id AS CHAR)
                WHERE {' AND '.join(where)}
                """
            )
            count_result = await session.execute(count_query, params)
            total = count_result.scalar() or 0

            # Get summary for current page
            summary_query = text(
                f"""
                SELECT
                    COALESCE(SUM(bo.bet_amount), 0) AS total_bet,
                    COALESCE(SUM(bo.bet_result), 0) AS total_win
                FROM bet_orders bo
                JOIN member_profiles mp ON CAST(mp.user_id AS CHAR) = CAST(bo.user_id AS CHAR)
                WHERE {' AND '.join(where)}
                LIMIT :limit OFFSET :offset
                """
            )
            summary_result = await session.execute(summary_query, params)
            summary_row = summary_result.fetchone()
            summary = {
                "totalBet": float(summary_row[0]) if summary_row else 0.0,
                "totalWin": float(summary_row[1]) if summary_row else 0.0
            }

            return {"list": items, "total": int(total), "summary": summary}

    async def get_transactions(
        self,
        account: str,
        page: int,
        page_size: int,
        transaction_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取会员交易记录
        返回: {list: [...], total: int, summary: {...}}
        """
        offset = (page - 1) * page_size
        where = ["mp.account = :account"]
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
                SELECT t.id, t.transaction_type, t.amount, t.fee,
                       t.transaction_time, t.status, t.transaction_info, t.review_comments
                FROM transactions t
                JOIN member_profiles mp ON CAST(mp.user_id AS CHAR) = CAST(t.user_id AS CHAR)
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
                    "transactionNo": str(m["id"]),  # 使用id作为交易号
                    "transactionType": m["transaction_type"],
                    "amount": float(m["amount"]),
                    "fee": float(m["fee"]) if m["fee"] else 0.0,
                    "status": m["status"],
                    "transactionTime": str(m["transaction_time"]),
                    "transactionInfo": m["transaction_info"] or "",
                    "remarks": m["review_comments"] or ""
                })

            # Get total count
            count_query = text(
                f"""
                SELECT COUNT(*) AS cnt
                FROM transactions t
                JOIN member_profiles mp ON CAST(mp.user_id AS CHAR) = CAST(t.user_id AS CHAR)
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
                JOIN member_profiles mp ON CAST(mp.user_id AS CHAR) = CAST(t.user_id AS CHAR)
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

    async def get_account_changes(
        self,
        account: str,
        page: int,
        page_size: int,
        change_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取会员账变记录
        返回: {list: [...], total: int}
        """
        offset = (page - 1) * page_size
        where = ["mp.account = :account"]
        params: Dict[str, Any] = {"account": account, "offset": offset, "limit": page_size}

        if change_type:
            where.append("ac.type = :change_type")
            params["change_type"] = change_type

        if start_date:
            where.append("ac.created_at >= :start_date")
            params["start_date"] = start_date + " 00:00:00"

        if end_date:
            where.append("ac.created_at <= :end_date")
            params["end_date"] = end_date + " 23:59:59"

        async with self._session_factory() as session:
            # Get list
            list_query = text(
                f"""
                SELECT ac.id, ac.type, ac.amount, ac.balance_before,
                       ac.balance_after, ac.created_at, ac.note
                FROM account_changes ac
                JOIN member_profiles mp ON CAST(mp.user_id AS CHAR) = CAST(ac.user_id AS CHAR)
                WHERE {' AND '.join(where)}
                ORDER BY ac.created_at DESC
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
                    "changeType": m["type"],
                    "amount": float(m["amount"]),
                    "balanceBefore": float(m["balance_before"]),
                    "balanceAfter": float(m["balance_after"]),
                    "changeTime": str(m["created_at"]),
                    "note": m["note"] or ""
                })

            # Get total count
            count_query = text(
                f"""
                SELECT COUNT(*) AS cnt
                FROM account_changes ac
                JOIN member_profiles mp ON CAST(mp.user_id AS CHAR) = CAST(ac.user_id AS CHAR)
                WHERE {' AND '.join(where)}
                """
            )
            count_result = await session.execute(count_query, params)
            total = count_result.scalar() or 0

            return {"list": items, "total": int(total)}