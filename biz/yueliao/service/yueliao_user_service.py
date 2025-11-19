from typing import List, Dict, Optional
from biz.yueliao.repo.yueliao_user_repo import YueliaoUserRepo


class YueliaoUserService:
    def __init__(self, repo: YueliaoUserRepo):
        self._repo = repo

    async def get_users(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None
    ) -> Dict:
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        skip = (page - 1) * page_size

        users = await self._repo.get_all_users(
            skip=skip,
            limit=page_size,
            search=search
        )
        total = await self._repo.get_user_count(search=search)

        return {
            "users": users,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def get_user_detail(self, user_id: str) -> Optional[Dict]:
        return await self._repo.get_user_by_id(user_id)

    async def search_user_by_phone(self, phone: str) -> Optional[Dict]:
        return await self._repo.get_user_by_phone(phone)

    async def search_user_by_yueliao_id(self, yueliao_id: str) -> Optional[Dict]:
        return await self._repo.get_user_by_yueliao_id(yueliao_id)

    async def get_user_statistics(self) -> Dict:
        total_users = await self._repo.get_user_count()

        return {
            "total_users": total_users
        }
