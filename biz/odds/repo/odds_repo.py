"""
OddsRepository - 赔率配置数据访问层
主键：bet_type
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class OddsRepository:
    """赔率Repository"""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def get_odds(
        self,
        bet_type: str,
        game_type: str = "lucky8"
    ) -> Optional[Dict[str, Any]]:
        """获取赔率配置"""
        async with self._session_factory() as session:
            query = text("""
                SELECT * FROM odds_config
                WHERE bet_type = :bet_type AND game_type = :game_type
            """)
            result = await session.execute(query, {
                "bet_type": bet_type,
                "game_type": game_type
            })
            row = result.fetchone()
            if row:
                data = dict(row._mapping)
                # 解析JSON字段
                if data.get("tema_odds"):
                    import json
                    try:
                        data["tema_odds"] = json.loads(data["tema_odds"])
                    except:
                        data["tema_odds"] = None
                return data
            return None

    async def create_odds(self, odds_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建赔率配置"""
        async with self._session_factory() as session:
            import json

            query = text("""
                INSERT INTO odds_config (
                    bet_type, odds, min_bet, max_bet, period_max, game_type,
                    description, tema_odds, status, created_at, updated_at
                ) VALUES (
                    :bet_type, :odds, :min_bet, :max_bet, :period_max, :game_type,
                    :description, :tema_odds, :status, NOW(), NOW()
                )
            """)

            params = {
                "bet_type": odds_data["bet_type"],
                "odds": odds_data["odds"],
                "min_bet": odds_data.get("min_bet", Decimal("10.00")),
                "max_bet": odds_data.get("max_bet", Decimal("10000.00")),
                "period_max": odds_data.get("period_max", Decimal("50000.00")),
                "game_type": odds_data.get("game_type", "lucky8"),
                "description": odds_data.get("description"),
                "tema_odds": json.dumps(odds_data.get("tema_odds")) if odds_data.get("tema_odds") else None,
                "status": odds_data.get("status", "active")
            }

            await session.execute(query, params)
            await session.commit()

            return await self.get_odds(odds_data["bet_type"], odds_data.get("game_type", "lucky8"))

    async def update_odds(
        self,
        bet_type: str,
        game_type: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新赔率配置"""
        if not updates:
            return await self.get_odds(bet_type, game_type)

        async with self._session_factory() as session:
            import json

            # 构建SET子句
            set_parts = []
            params = {"bet_type": bet_type, "game_type": game_type}

            for key, value in updates.items():
                if key == "tema_odds" and isinstance(value, dict):
                    value = json.dumps(value)
                set_parts.append(f"{key} = :{key}")
                params[key] = value

            set_parts.append("updated_at = NOW()")
            set_clause = ", ".join(set_parts)

            query = text(f"""
                UPDATE odds_config
                SET {set_clause}
                WHERE bet_type = :bet_type AND game_type = :game_type
            """)

            await session.execute(query, params)
            await session.commit()

            return await self.get_odds(bet_type, game_type)

    async def get_all_odds(
        self,
        game_type: str = "lucky8",
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取所有赔率配置"""
        async with self._session_factory() as session:
            if status:
                query = text("""
                    SELECT * FROM odds_config
                    WHERE game_type = :game_type AND status = :status
                    ORDER BY bet_type
                """)
                params = {"game_type": game_type, "status": status}
            else:
                query = text("""
                    SELECT * FROM odds_config
                    WHERE game_type = :game_type
                    ORDER BY bet_type
                """)
                params = {"game_type": game_type}

            result = await session.execute(query, params)
            rows = result.fetchall()

            # 解析JSON字段
            import json
            odds_list = []
            for row in rows:
                data = dict(row._mapping)
                if data.get("tema_odds"):
                    try:
                        data["tema_odds"] = json.loads(data["tema_odds"])
                    except:
                        data["tema_odds"] = None
                odds_list.append(data)

            return odds_list

    async def get_odds_by_types(
        self,
        bet_types: List[str],
        game_type: str = "lucky8"
    ) -> List[Dict[str, Any]]:
        """批量获取赔率配置"""
        async with self._session_factory() as session:
            placeholders = ",".join([f":bet_type_{i}" for i in range(len(bet_types))])
            query_str = f"""
                SELECT * FROM odds_config
                WHERE bet_type IN ({placeholders}) AND game_type = :game_type
                ORDER BY bet_type
            """
            query = text(query_str)

            params = {"game_type": game_type}
            for i, bet_type in enumerate(bet_types):
                params[f"bet_type_{i}"] = bet_type

            result = await session.execute(query, params)
            rows = result.fetchall()

            # 解析JSON字段
            import json
            odds_list = []
            for row in rows:
                data = dict(row._mapping)
                if data.get("tema_odds"):
                    try:
                        data["tema_odds"] = json.loads(data["tema_odds"])
                    except:
                        data["tema_odds"] = None
                odds_list.append(data)

            return odds_list

    async def exists(
        self,
        bet_type: str,
        game_type: str = "lucky8"
    ) -> bool:
        """检查赔率配置是否存在"""
        async with self._session_factory() as session:
            query = text("""
                SELECT 1 FROM odds_config
                WHERE bet_type = :bet_type AND game_type = :game_type
                LIMIT 1
            """)
            result = await session.execute(query, {
                "bet_type": bet_type,
                "game_type": game_type
            })
            return result.fetchone() is not None

    async def delete_odds(
        self,
        bet_type: str,
        game_type: str = "lucky8"
    ) -> bool:
        """删除赔率配置"""
        async with self._session_factory() as session:
            query = text("""
                DELETE FROM odds_config
                WHERE bet_type = :bet_type AND game_type = :game_type
            """)
            result = await session.execute(query, {
                "bet_type": bet_type,
                "game_type": game_type
            })
            await session.commit()
            return result.rowcount > 0

    async def update_status(
        self,
        bet_type: str,
        game_type: str,
        status: str
    ) -> Optional[Dict[str, Any]]:
        """更新赔率状态"""
        return await self.update_odds(bet_type, game_type, {"status": status})
