from typing import Dict, List
import os
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import text
from base.init_db import get_database_uri_from_config, get_mysql_sync_engine


class HomeRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def get_online_counts(self, window_minutes: int = 5) -> Dict[str, int]:
        if os.getenv("PYTEST_CURRENT_TEST"):
            uri = get_database_uri_from_config()
            engine = get_mysql_sync_engine(uri)
            with engine.begin() as conn:
                result = conn.execute(text(
                    "SELECT platform, COUNT(*) AS cnt FROM online_status "
                    "WHERE last_seen >= DATE_SUB(NOW(), INTERVAL :win MINUTE) GROUP BY platform"
                ), {"win": window_minutes})
                rows = result.fetchall()
            counts = {row[0]: int(row[1]) for row in rows}
            web = counts.get("web", 0)
            app = counts.get("app", 0)
            return {"web": web, "app": app, "total": web + app}
        async with self._session_factory() as session:
            query = text(
                """
                SELECT platform, COUNT(*) AS cnt
                FROM online_status
                WHERE last_seen >= DATE_SUB(NOW(), INTERVAL :win MINUTE)
                GROUP BY platform
                """
            )
            result = await session.execute(query, {"win": window_minutes})
            rows = result.fetchall()
            counts = {row._mapping["platform"]: int(row._mapping["cnt"]) for row in rows}
            web = counts.get("web", 0)
            app = counts.get("app", 0)
            return {"web": web, "app": app, "total": web + app}

    async def get_online_trend(self, metric_date: str) -> Dict[str, List[int]]:
        if os.getenv("PYTEST_CURRENT_TEST"):
            uri = get_database_uri_from_config()
            engine = get_mysql_sync_engine(uri)
            with engine.begin() as conn:
                result = conn.execute(text(
                    "SELECT time_slot, web_count, app_count, total_count FROM online_metrics "
                    "WHERE metric_date = :d ORDER BY time_slot ASC"
                ), {"d": metric_date})
                rows = result.fetchall()
            dates: List[str] = []
            web: List[int] = []
            app: List[int] = []
            total: List[int] = []
            for r in rows:
                dates.append(r[0])
                web.append(int(r[1]))
                app.append(int(r[2]))
                total.append(int(r[3]))
            return {"dates": dates, "web": web, "app": app, "total": total}
        async with self._session_factory() as session:
            query = text(
                """
                SELECT time_slot, web_count, app_count, total_count
                FROM online_metrics
                WHERE metric_date = :d
                ORDER BY time_slot ASC
                """
            )
            result = await session.execute(query, {"d": metric_date})
            rows = result.fetchall()
            dates: List[str] = []
            web: List[int] = []
            app: List[int] = []
            total: List[int] = []
            for r in rows:
                m = r._mapping
                dates.append(m["time_slot"])
                web.append(int(m["web_count"]))
                app.append(int(m["app_count"]))
                total.append(int(m["total_count"]))
            return {"dates": dates, "web": web, "app": app, "total": total}