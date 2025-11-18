from typing import Dict
from biz.home.repo.home_repo import HomeRepository


class HomeService:
    def __init__(self, home_repo: HomeRepository):
        self.home_repo = home_repo

    async def get_online_counts(self, window_minutes: int = 5) -> Dict[str, int]:
        return await self.home_repo.get_online_counts(window_minutes)

    async def get_online_trend(self, metric_date: str) -> Dict[str, list]:
        return await self.home_repo.get_online_trend(metric_date)