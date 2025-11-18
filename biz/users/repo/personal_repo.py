"""
个人中心 Repository
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import json
import bcrypt


class PersonalRepository:
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def get_basic_info(self, account: str) -> Optional[Dict[str, Any]]:
        """
        获取个人基本信息
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 首先判断是代理还是会员
            query = text("""
                SELECT
                    u.id,
                    COALESCE(ap.account, mp.account) as account,
                    u.balance,
                    COALESCE(ap.plate, mp.plate) as plate,
                    COALESCE(ap.superior_account, mp.superior_account) as superior,
                    COALESCE(ap.open_time, mp.open_time) as openTime,
                    CASE WHEN ap.id IS NOT NULL THEN 'agent' ELSE 'member' END as userType,
                    ap.open_plate,
                    ap.earn_rebate,
                    ap.subordinate_transfer,
                    ap.default_rebate_plate
                FROM users u
                LEFT JOIN agent_profiles ap ON u.id = ap.user_id
                LEFT JOIN member_profiles mp ON u.id = mp.user_id
                WHERE ap.account = :account OR mp.account = :account
                LIMIT 1
            """)

            result = await session.execute(query, {"account": account})
            row = result.fetchone()

            if not row:
                return None

            basic_info = {
                "account": row.account,
                "balance": float(row.balance),
                "plate": row.plate,
                "superior": row.superior,
                "openTime": row.openTime.strftime("%Y-%m-%d %H:%M:%S") if row.openTime else None
            }

            # 如果是代理，添加额外字段
            if row.userType == "agent":
                open_plate = []
                if row.open_plate:
                    try:
                        open_plate = json.loads(row.open_plate)
                    except:
                        open_plate = []

                basic_info.update({
                    "openPlate": open_plate,
                    "earnRebate": row.earn_rebate,
                    "subordinateTransfer": row.subordinate_transfer,
                    "defaultRebatePlate": row.default_rebate_plate
                })

            return basic_info

    async def update_basic_info(
        self,
        account: str,
        plate: Optional[str] = None,
        open_plate: Optional[List[str]] = None,
        earn_rebate: Optional[str] = None,
        subordinate_transfer: Optional[str] = None,
        default_rebate_plate: Optional[str] = None
    ) -> bool:
        """
        更新个人基本信息
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 首先判断是代理还是会员
            check_query = text("""
                SELECT
                    u.id,
                    CASE WHEN ap.id IS NOT NULL THEN 'agent' ELSE 'member' END as userType
                FROM users u
                LEFT JOIN agent_profiles ap ON u.id = ap.user_id
                LEFT JOIN member_profiles mp ON u.id = mp.user_id
                WHERE ap.account = :account OR mp.account = :account
                LIMIT 1
            """)

            result = await session.execute(check_query, {"account": account})
            row = result.fetchone()

            if not row:
                raise ValueError("用户不存在")

            user_id = row.id
            user_type = row.userType

            # 根据用户类型更新不同的表
            if user_type == "agent":
                # 代理可以更新所有字段
                update_parts = []
                params = {"account": account}

                if plate is not None:
                    update_parts.append("plate = :plate")
                    params["plate"] = plate

                if open_plate is not None:
                    update_parts.append("open_plate = :open_plate")
                    params["open_plate"] = json.dumps(open_plate, ensure_ascii=False)

                if earn_rebate is not None:
                    update_parts.append("earn_rebate = :earn_rebate")
                    params["earn_rebate"] = earn_rebate

                if subordinate_transfer is not None:
                    update_parts.append("subordinate_transfer = :subordinate_transfer")
                    params["subordinate_transfer"] = subordinate_transfer

                if default_rebate_plate is not None:
                    update_parts.append("default_rebate_plate = :default_rebate_plate")
                    params["default_rebate_plate"] = default_rebate_plate

                if update_parts:
                    update_parts.append("updated_at = NOW()")
                    update_query = text(f"""
                        UPDATE agent_profiles
                        SET {', '.join(update_parts)}
                        WHERE account = :account
                    """)
                    await session.execute(update_query, params)
            else:
                # 会员只能更新盘口
                if plate is not None:
                    update_query = text("""
                        UPDATE member_profiles
                        SET plate = :plate
                        WHERE account = :account
                    """)
                    await session.execute(update_query, {"account": account, "plate": plate})

            await session.commit()
            return True

    async def add_promotion_domain(self, account: str, domain: str) -> bool:
        """
        添加推广域名（仅代理）
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 获取代理的推广域名列表
            query = text("""
                SELECT promotion_domains
                FROM agent_profiles
                WHERE account = :account
            """)

            result = await session.execute(query, {"account": account})
            row = result.fetchone()

            if not row:
                raise ValueError("代理不存在")

            # 解析现有域名
            domains = []
            if row.promotion_domains:
                try:
                    domains = json.loads(row.promotion_domains)
                except:
                    domains = []

            # 检查域名是否已存在
            if domain in domains:
                raise ValueError("域名已存在")

            # 添加新域名
            domains.append(domain)

            # 更新
            update_query = text("""
                UPDATE agent_profiles
                SET promotion_domains = :domains, updated_at = NOW()
                WHERE account = :account
            """)

            await session.execute(update_query, {
                "account": account,
                "domains": json.dumps(domains, ensure_ascii=False)
            })

            await session.commit()
            return True

    async def get_promotion_links(self, account: str) -> List[str]:
        """
        获取推广链接列表（仅代理）
        """
        async with self.session_factory() as session:
            session: AsyncSession

            query = text("""
                SELECT promotion_domains, invite_code
                FROM agent_profiles
                WHERE account = :account
            """)

            result = await session.execute(query, {"account": account})
            row = result.fetchone()

            if not row:
                raise ValueError("代理不存在")

            domains = []
            if row.promotion_domains:
                try:
                    domains = json.loads(row.promotion_domains)
                except:
                    domains = []

            invite_code = row.invite_code

            # 生成推广链接
            links = [f"https://{domain}/?a={invite_code}#/register" for domain in domains]
            return links

    async def get_lottery_rebate_config(self, account: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取彩票退水配置
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 获取 user_id
            user_query = text("""
                SELECT u.id
                FROM users u
                LEFT JOIN agent_profiles ap ON u.id = ap.user_id
                LEFT JOIN member_profiles mp ON u.id = mp.user_id
                WHERE ap.account = :account OR mp.account = :account
                LIMIT 1
            """)

            result = await session.execute(user_query, {"account": account})
            row = result.fetchone()

            if not row:
                return None

            user_id = row.id

            # 查询配置
            config_query = text("""
                SELECT config_data
                FROM lottery_rebate_config
                WHERE user_id = :user_id
            """)

            config_result = await session.execute(config_query, {"user_id": user_id})
            config_row = config_result.fetchone()

            if not config_row or not config_row.config_data:
                return []

            try:
                return json.loads(config_row.config_data)
            except:
                return []

    async def save_lottery_rebate_config(
        self,
        account: str,
        config_data: List[Dict[str, Any]]
    ) -> bool:
        """
        保存彩票退水配置
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 获取 user_id
            user_query = text("""
                SELECT u.id
                FROM users u
                LEFT JOIN agent_profiles ap ON u.id = ap.user_id
                LEFT JOIN member_profiles mp ON u.id = mp.user_id
                WHERE ap.account = :account OR mp.account = :account
                LIMIT 1
            """)

            result = await session.execute(user_query, {"account": account})
            row = result.fetchone()

            if not row:
                raise ValueError("用户不存在")

            user_id = row.id

            # 序列化配置
            config_json = json.dumps(config_data, ensure_ascii=False)

            # 检查是否已存在
            check_query = text("""
                SELECT id FROM lottery_rebate_config WHERE user_id = :user_id
            """)

            check_result = await session.execute(check_query, {"user_id": user_id})
            exists = check_result.fetchone()

            if exists:
                # 更新
                update_query = text("""
                    UPDATE lottery_rebate_config
                    SET config_data = :config_data, updated_at = NOW()
                    WHERE user_id = :user_id
                """)
                await session.execute(update_query, {
                    "user_id": user_id,
                    "config_data": config_json
                })
            else:
                # 插入
                insert_query = text("""
                    INSERT INTO lottery_rebate_config (user_id, config_data, created_at, updated_at)
                    VALUES (:user_id, :config_data, NOW(), NOW())
                """)
                await session.execute(insert_query, {
                    "user_id": user_id,
                    "config_data": config_json
                })

            await session.commit()
            return True

    async def get_login_logs(
        self,
        account: str,
        page: int,
        page_size: int
    ) -> Dict[str, Any]:
        """
        获取登录日志
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 计算偏移量
            offset = (page - 1) * page_size

            # 查询总数
            count_query = text("""
                SELECT COUNT(*) as total
                FROM login_logs
                WHERE account = :account
            """)

            count_result = await session.execute(count_query, {"account": account})
            total = count_result.fetchone().total

            # 查询列表
            list_query = text("""
                SELECT
                    login_time as loginTime,
                    ip_address as ipAddress,
                    ip_location as ipLocation,
                    operator
                FROM login_logs
                WHERE account = :account
                ORDER BY login_time DESC
                LIMIT :limit OFFSET :offset
            """)

            list_result = await session.execute(list_query, {
                "account": account,
                "limit": page_size,
                "offset": offset
            })

            logs = []
            for row in list_result:
                logs.append({
                    "loginTime": row.loginTime.strftime("%Y-%m-%d %H:%M:%S") if row.loginTime else None,
                    "ipAddress": row.ipAddress,
                    "ipLocation": row.ipLocation,
                    "operator": row.operator
                })

            return {
                "list": logs,
                "total": total
            }

    async def update_password(self, account: str, old_password: str, new_password: str) -> bool:
        """
        修改密码
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 获取当前密码
            query = text("""
                SELECT u.id, u.password
                FROM users u
                LEFT JOIN agent_profiles ap ON u.id = ap.user_id
                LEFT JOIN member_profiles mp ON u.id = mp.user_id
                WHERE ap.account = :account OR mp.account = :account
                LIMIT 1
            """)

            result = await session.execute(query, {"account": account})
            row = result.fetchone()

            if not row:
                raise ValueError("用户不存在")

            user_id = row.id
            current_password = row.password

            # 验证旧密码
            if not bcrypt.checkpw(old_password.encode('utf-8'), current_password.encode('utf-8')):
                raise ValueError("旧密码错误")

            # 加密新密码
            new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # 更新密码
            update_query = text("""
                UPDATE users
                SET password = :password, updated_at = NOW()
                WHERE id = :user_id
            """)

            await session.execute(update_query, {
                "user_id": user_id,
                "password": new_password_hash
            })

            await session.commit()
            return True
