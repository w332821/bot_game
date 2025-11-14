"""
UserService - 用户业务逻辑层
处理充值、扣款、余额查询、回水比例设置等业务逻辑
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
import logging

from biz.user.repo.user_repo import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """用户服务"""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_in_chat(
        self,
        user_id: str,
        chat_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取用户在特定群的数据"""
        return await self.user_repo.get_user_in_chat(user_id, chat_id)

    async def get_or_create_user(
        self,
        user_id: str,
        username: str,
        chat_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """获取或创建用户"""
        user = await self.user_repo.get_user_in_chat(user_id, chat_id)

        if not user:
            # 创建新用户
            user_data = {
                "id": user_id,
                "username": username,
                "chat_id": chat_id,
                **kwargs
            }
            user = await self.user_repo.create_user(user_data)
            logger.info(f"✅ 创建新用户: {username} ({user_id}) 在群 {chat_id}")

        return user

    async def get_all_user_chats(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户在所有群的数据（超管用）"""
        return await self.user_repo.get_all_user_chats(user_id)

    async def get_chat_users(
        self,
        chat_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取特定群的所有用户（分销商用）"""
        return await self.user_repo.get_chat_users(chat_id, skip, limit)

    async def add_credit(
        self,
        user_id: str,
        chat_id: str,
        amount: Decimal,
        admin_id: str,
        note: str = ""
    ) -> Dict[str, Any]:
        """
        充值（上分）
        返回: {
            "success": bool,
            "old_balance": Decimal,
            "new_balance": Decimal,
            "record": Dict
        }
        """
        if amount <= 0:
            raise ValueError("充值金额必须大于0")

        user = await self.user_repo.get_user_in_chat(user_id, chat_id)
        if not user:
            raise ValueError("用户不存在")

        old_balance = Decimal(str(user["balance"]))

        # 增加余额
        updated_user = await self.user_repo.add_balance(user_id, chat_id, amount)
        new_balance = Decimal(str(updated_user["balance"]))

        # 创建充值记录（这里应该调用DepositRecord的Repository，暂时返回数据）
        record = {
            "id": f"credit_{int(datetime.now().timestamp() * 1000)}",
            "type": "add",
            "user_id": user_id,
            "username": user["username"],
            "amount": float(amount),
            "admin_id": admin_id,
            "note": note,
            "chat_id": chat_id,
            "created_at": datetime.now().isoformat()
        }

        logger.info(
            f"💰 充值成功: 用户 {user['username']} ({user_id}) "
            f"余额: {old_balance} -> {new_balance}"
        )

        return {
            "success": True,
            "old_balance": old_balance,
            "new_balance": new_balance,
            "record": record
        }

    async def remove_credit(
        self,
        user_id: str,
        chat_id: str,
        amount: Decimal,
        admin_id: str,
        note: str = ""
    ) -> Dict[str, Any]:
        """
        扣款（下分）
        返回: {
            "success": bool,
            "old_balance": Decimal,
            "new_balance": Decimal,
            "record": Dict
        }
        """
        if amount <= 0:
            raise ValueError("扣款金额必须大于0")

        user = await self.user_repo.get_user_in_chat(user_id, chat_id)
        if not user:
            raise ValueError("用户不存在")

        old_balance = Decimal(str(user["balance"]))

        if old_balance < amount:
            raise ValueError("余额不足")

        # 减少余额
        updated_user = await self.user_repo.subtract_balance(user_id, chat_id, amount)
        if not updated_user:
            raise ValueError("扣款失败，余额不足")

        new_balance = Decimal(str(updated_user["balance"]))

        # 创建扣款记录
        record = {
            "id": f"credit_{int(datetime.now().timestamp() * 1000)}",
            "type": "remove",
            "user_id": user_id,
            "username": user["username"],
            "amount": float(amount),
            "admin_id": admin_id,
            "note": note,
            "chat_id": chat_id,
            "created_at": datetime.now().isoformat()
        }

        logger.info(
            f"💸 扣款成功: 用户 {user['username']} ({user_id}) "
            f"余额: {old_balance} -> {new_balance}"
        )

        return {
            "success": True,
            "old_balance": old_balance,
            "new_balance": new_balance,
            "record": record
        }

    async def update_balance(
        self,
        user_id: str,
        chat_id: str,
        new_balance: Decimal
    ) -> Optional[Dict[str, Any]]:
        """直接更新余额"""
        new_balance = round(new_balance, 2)
        return await self.user_repo.update_balance(user_id, chat_id, new_balance)

    async def add_score(
        self,
        user_id: str,
        chat_id: str,
        score_change: int
    ) -> Optional[Dict[str, Any]]:
        """增加积分"""
        return await self.user_repo.add_score(user_id, chat_id, score_change)

    async def update_rebate_ratio(
        self,
        user_id: str,
        chat_id: str,
        rebate_ratio: Decimal
    ) -> Optional[Dict[str, Any]]:
        """更新回水比例"""
        if not (0 <= rebate_ratio <= 1):
            raise ValueError("回水比例必须在0-1之间")

        return await self.user_repo.update_rebate_ratio(user_id, chat_id, rebate_ratio)

    async def update_status(
        self,
        user_id: str,
        chat_id: str,
        status: str
    ) -> Optional[Dict[str, Any]]:
        """更新用户状态（活跃/禁用）"""
        if status not in ["活跃", "禁用"]:
            raise ValueError("状态必须是'活跃'或'禁用'")

        return await self.user_repo.update_status(user_id, chat_id, status)

    async def update_bot_config(
        self,
        user_id: str,
        chat_id: str,
        is_bot: bool,
        bot_config: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """更新机器人配置"""
        updates = {"is_bot": is_bot}
        if bot_config is not None:
            updates["bot_config"] = bot_config

        return await self.user_repo.update_user(user_id, chat_id, updates)

    async def update_red_packet_settings(
        self,
        user_id: str,
        chat_id: str,
        settings: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新红包设置"""
        return await self.user_repo.update_user(user_id, chat_id, {
            "red_packet_settings": settings
        })

    async def mark_user_as_read(
        self,
        user_id: str,
        chat_id: str
    ) -> Optional[Dict[str, Any]]:
        """标记用户为已读"""
        return await self.user_repo.mark_as_read(user_id, chat_id)

    async def delete_user(
        self,
        user_id: str,
        chat_id: str
    ) -> bool:
        """删除用户"""
        logger.warning(f"⚠️ 删除用户: {user_id} 在群 {chat_id}")
        return await self.user_repo.delete_user(user_id, chat_id)

    async def get_leaderboard(
        self,
        chat_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取排行榜"""
        return await self.user_repo.get_leaderboard(chat_id, limit)

    async def get_new_users(
        self,
        chat_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取新用户列表"""
        return await self.user_repo.get_new_users(chat_id)

    async def get_user_stats(
        self,
        user_id: str,
        chat_id: str
    ) -> Dict[str, Any]:
        """
        获取用户统计信息
        包含：余额、投注总额、总赢利、胜率等
        """
        user = await self.user_repo.get_user_in_chat(user_id, chat_id)
        if not user:
            raise ValueError("用户不存在")

        # TODO: 从bet表获取投注统计数据
        # 这里暂时返回基础信息
        return {
            "user_id": user["id"],
            "username": user["username"],
            "chat_id": user["chat_id"],
            "balance": float(user["balance"]),
            "score": user["score"],
            "rebate_ratio": float(user["rebate_ratio"]),
            "status": user["status"],
            "join_date": user["join_date"],
            # 以下字段需要从bet表统计
            "total_bets": 0,
            "total_winnings": 0,
            "win_rate": 0,
            "bet_count": 0
        }
