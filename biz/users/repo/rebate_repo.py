"""
退水配置 Repository
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import json


class RebateRepository:
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def get_rebate_settings(self, account: str) -> Optional[Dict[str, Any]]:
        """
        获取退水配置
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 查询退水配置
            query = text("""
                SELECT
                    u.id as user_id,
                    rs.independent_rebate,
                    rs.earn_rebate,
                    rs.game_settings
                FROM users u
                LEFT JOIN member_profiles mp ON BINARY u.id = BINARY mp.user_id
                LEFT JOIN rebate_settings rs ON BINARY u.id = BINARY rs.user_id
                WHERE mp.account COLLATE utf8mb4_unicode_ci = :account OR (
                    EXISTS (SELECT 1 FROM agent_profiles ap WHERE BINARY ap.user_id = BINARY u.id AND ap.account COLLATE utf8mb4_unicode_ci = :account)
                )
                LIMIT 1
            """)

            result = await session.execute(query, {"account": account})
            row = result.fetchone()

            if not row:
                return None

            # 解析 game_settings JSON
            game_settings = []
            if row.game_settings:
                try:
                    game_settings = json.loads(row.game_settings)
                except:
                    game_settings = []

            return {
                "independentRebate": bool(row.independent_rebate) if row.independent_rebate is not None else False,
                "earnRebate": float(row.earn_rebate) if row.earn_rebate is not None else 0.0,
                "gameSettings": game_settings
            }

    async def update_rebate_settings(
        self,
        account: str,
        independent_rebate: bool,
        earn_rebate: float,
        game_settings: list
    ) -> bool:
        """
        更新退水配置
        """
        async with self.session_factory() as session:
            session: AsyncSession

            # 首先获取 user_id
            get_user_query = text("""
                SELECT u.id
                FROM users u
                LEFT JOIN member_profiles mp ON BINARY u.id = BINARY mp.user_id
                LEFT JOIN agent_profiles ap ON BINARY u.id = BINARY ap.user_id
                WHERE mp.account COLLATE utf8mb4_unicode_ci = :account OR ap.account COLLATE utf8mb4_unicode_ci = :account
                LIMIT 1
            """)

            result = await session.execute(get_user_query, {"account": account})
            row = result.fetchone()

            if not row:
                raise ValueError("用户不存在")

            user_id = row.id

            # 序列化 game_settings
            game_settings_json = json.dumps(game_settings, ensure_ascii=False)

            # 检查是否已存在退水配置
            check_query = text("""
                SELECT id FROM rebate_settings WHERE user_id = :user_id
            """)

            check_result = await session.execute(check_query, {"user_id": user_id})
            exists = check_result.fetchone()

            if exists:
                # 更新
                update_query = text("""
                    UPDATE rebate_settings
                    SET
                        independent_rebate = :independent_rebate,
                        earn_rebate = :earn_rebate,
                        game_settings = :game_settings,
                        updated_at = NOW()
                    WHERE user_id = :user_id
                """)

                await session.execute(update_query, {
                    "user_id": user_id,
                    "independent_rebate": independent_rebate,
                    "earn_rebate": earn_rebate,
                    "game_settings": game_settings_json
                })
            else:
                # 插入
                insert_query = text("""
                    INSERT INTO rebate_settings (
                        user_id, independent_rebate, earn_rebate, game_settings, created_at, updated_at
                    )
                    VALUES (
                        :user_id, :independent_rebate, :earn_rebate, :game_settings, NOW(), NOW()
                    )
                """)

                await session.execute(insert_query, {
                    "user_id": user_id,
                    "independent_rebate": independent_rebate,
                    "earn_rebate": earn_rebate,
                    "game_settings": game_settings_json
                })

            await session.commit()
            return True
