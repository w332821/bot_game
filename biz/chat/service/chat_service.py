"""
ChatService - 群聊业务逻辑层
处理群聊创建、配置更新、统计等业务逻辑
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
import logging

from biz.chat.repo.chat_repo import ChatRepository

logger = logging.getLogger(__name__)


class ChatService:
    """群聊服务"""

    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo

    async def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """获取群聊信息"""
        return await self.chat_repo.get_chat(chat_id)

    async def get_or_create_chat(
        self,
        chat_id: str,
        name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """获取或创建群聊"""
        chat = await self.chat_repo.get_chat(chat_id)

        if not chat:
            # 创建新群聊
            chat_data = {
                "id": chat_id,
                "name": name,
                **kwargs
            }
            chat = await self.chat_repo.create_chat(chat_data)
            logger.info(f"✅ 创建新群聊: {name} ({chat_id})")

        return chat

    async def create_chat(
        self,
        chat_id: str,
        name: str,
        game_type: str = "lucky8",
        owner_id: Optional[str] = None,
        auto_draw: bool = True,
        bet_lock_time: int = 60
    ) -> Dict[str, Any]:
        """创建群聊"""
        chat_data = {
            "id": chat_id,
            "name": name,
            "game_type": game_type,
            "owner_id": owner_id,
            "auto_draw": auto_draw,
            "bet_lock_time": bet_lock_time
        }

        chat = await self.chat_repo.create_chat(chat_data)
        logger.info(f"✅ 创建群聊: {name} ({chat_id}) 游戏类型: {game_type}")

        return chat

    async def update_chat(
        self,
        chat_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新群聊信息"""
        chat = await self.chat_repo.update_chat(chat_id, updates)

        if chat:
            logger.info(f"✅ 更新群聊: {chat_id} 更新内容: {updates}")

        return chat

    async def update_game_type(
        self,
        chat_id: str,
        game_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        更新游戏类型
        支持: lucky8, liuhecai
        """
        if game_type not in ["lucky8", "liuhecai"]:
            raise ValueError("游戏类型必须是lucky8或liuhecai")

        chat = await self.chat_repo.update_game_type(chat_id, game_type)

        if chat:
            logger.info(f"✅ 更新群聊 {chat_id} 游戏类型: {game_type}")

        return chat

    async def update_owner(
        self,
        chat_id: str,
        owner_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """更新所属分销商"""
        chat = await self.chat_repo.update_owner(chat_id, owner_id)

        if chat:
            logger.info(f"✅ 更新群聊 {chat_id} 所属分销商: {owner_id}")

        return chat

    async def update_status(
        self,
        chat_id: str,
        status: str
    ) -> Optional[Dict[str, Any]]:
        """更新群聊状态"""
        if status not in ["active", "inactive"]:
            raise ValueError("状态必须是active或inactive")

        return await self.chat_repo.update_status(chat_id, status)

    async def on_member_join(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """成员加入时的处理"""
        return await self.chat_repo.increment_member_count(chat_id)

    async def on_member_leave(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """成员离开时的处理"""
        return await self.chat_repo.decrement_member_count(chat_id)

    async def on_bet_placed(
        self,
        chat_id: str,
        bet_amount: Decimal
    ) -> Optional[Dict[str, Any]]:
        """投注时更新统计"""
        return await self.chat_repo.increment_bet_stats(chat_id, bet_amount)

    async def delete_chat(self, chat_id: str) -> bool:
        """删除群聊"""
        logger.warning(f"⚠️ 删除群聊: {chat_id}")
        return await self.chat_repo.delete_chat(chat_id)

    async def get_all_chats(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取所有群聊（管理后台用）"""
        return await self.chat_repo.get_all_chats(skip, limit, status)

    async def get_chats_by_owner(
        self,
        owner_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取指定分销商的所有群聊"""
        return await self.chat_repo.get_chats_by_owner(owner_id, skip, limit)

    async def get_chat_stats(self, chat_id: str) -> Dict[str, Any]:
        """
        获取群聊统计信息
        """
        chat = await self.chat_repo.get_chat(chat_id)
        if not chat:
            raise ValueError("群聊不存在")

        # TODO: 从其他表获取更详细的统计数据
        return {
            "chat_id": chat["id"],
            "name": chat["name"],
            "game_type": chat["game_type"],
            "member_count": chat["member_count"],
            "total_bets": chat["total_bets"],
            "total_volume": float(chat["total_volume"]),
            "status": chat["status"]
        }

    async def exists(self, chat_id: str) -> bool:
        """检查群聊是否存在"""
        return await self.chat_repo.exists(chat_id)
