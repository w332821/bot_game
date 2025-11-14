"""
User API路由
对应admin-server.js中的 /api/user/* 接口
"""
from decimal import Decimal
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from biz.user.service.user_service import UserService
from biz.user.models.model import User, UserCreate, UserUpdate

router = APIRouter(prefix="/api/user", tags=["user"])


# ===== 请求/响应模型 =====

class AddCreditRequest(BaseModel):
    """充值请求"""
    amount: float = Field(..., gt=0, description="充值金额")
    note: str = Field(default="", description="备注")
    chatId: Optional[str] = Field(default=None, description="群聊ID")


class RemoveCreditRequest(BaseModel):
    """扣款请求"""
    amount: float = Field(..., gt=0, description="扣款金额")
    note: str = Field(default="", description="备注")
    chatId: Optional[str] = Field(default=None, description="群聊ID")


class UpdateStatusRequest(BaseModel):
    """更新状态请求"""
    status: str = Field(..., description="状态：活跃/禁用")
    chatId: Optional[str] = None


class UpdateScoreRequest(BaseModel):
    """更新积分请求"""
    scoreChange: int = Field(..., description="积分变化")
    operation: str = Field(default="add", description="操作：add/set")


class UpdateRebateRequest(BaseModel):
    """更新回水比例请求"""
    rebateRatio: float = Field(..., ge=0, le=1, description="回水比例")
    chatId: Optional[str] = None


class UpdateRedPacketRequest(BaseModel):
    """更新红包设置请求"""
    redPacketSettings: Dict[str, Any]
    chatId: Optional[str] = None


class UpdateBotConfigRequest(BaseModel):
    """更新机器人配置请求"""
    isBot: bool
    botConfig: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    """用户响应"""
    success: bool
    user: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ===== 依赖注入 =====

def get_user_service() -> UserService:
    """获取UserService实例（占位，实际使用依赖注入容器）"""
    # TODO: 从依赖注入容器获取
    raise NotImplementedError("需要配置依赖注入容器")


def get_current_admin_id() -> str:
    """获取当前管理员ID（占位，实际从session/JWT获取）"""
    # TODO: 从JWT token或session获取
    return "admin"


# ===== API端点 =====

@router.get("/{userKey}")
async def get_user(
    userKey: str,
    user_service: UserService = Depends(get_user_service),
    admin_id: str = Depends(get_current_admin_id)
):
    """
    获取用户信息
    userKey可以是:
    - userId (返回该用户在任意群的第一条记录)
    - userId_chatId (返回该用户在指定群的记录)
    """
    try:
        # 解析userKey
        if "_" in userKey:
            # 格式: userId_chatId
            user_id, chat_id = userKey.split("_", 1)
            user = await user_service.get_user_in_chat(user_id, chat_id)
        else:
            # 格式: userId - 返回第一条记录
            users = await user_service.get_all_user_chats(userKey)
            user = users[0] if users else None

        if not user:
            return {"success": False, "error": "用户不存在"}

        return {"success": True, "user": user}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/add")
async def add_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
    admin_id: str = Depends(get_current_admin_id)
):
    """添加用户（需要超级管理员权限）"""
    try:
        # TODO: 检查admin权限

        user = await user_service.get_or_create_user(
            user_id=user_data.id,
            username=user_data.username,
            chat_id=user_data.chat_id,
            balance=user_data.balance,
            score=user_data.score,
            rebate_ratio=user_data.rebate_ratio,
            status=user_data.status,
            role=user_data.role,
            created_by=admin_id
        )

        return {"success": True, "user": user}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{userKey}/add-credit")
async def add_credit(
    userKey: str,
    request: AddCreditRequest,
    user_service: UserService = Depends(get_user_service),
    admin_id: str = Depends(get_current_admin_id)
):
    """
    充值（上分）
    支持群聊隔离
    """
    try:
        # 解析userKey
        if "_" in userKey:
            user_id, chat_id = userKey.split("_", 1)
        else:
            user_id = userKey
            chat_id = request.chatId

        if not chat_id:
            return {"success": False, "error": "缺少chatId参数"}

        amount = Decimal(str(request.amount))

        result = await user_service.add_credit(
            user_id=user_id,
            chat_id=chat_id,
            amount=amount,
            admin_id=admin_id,
            note=request.note
        )

        return {
            "success": True,
            "oldBalance": float(result["old_balance"]),
            "newBalance": float(result["new_balance"]),
            "record": result["record"]
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{userKey}/remove-credit")
async def remove_credit(
    userKey: str,
    request: RemoveCreditRequest,
    user_service: UserService = Depends(get_user_service),
    admin_id: str = Depends(get_current_admin_id)
):
    """
    扣款（下分）
    支持群聊隔离
    """
    try:
        # 解析userKey
        if "_" in userKey:
            user_id, chat_id = userKey.split("_", 1)
        else:
            user_id = userKey
            chat_id = request.chatId

        if not chat_id:
            return {"success": False, "error": "缺少chatId参数"}

        amount = Decimal(str(request.amount))

        result = await user_service.remove_credit(
            user_id=user_id,
            chat_id=chat_id,
            amount=amount,
            admin_id=admin_id,
            note=request.note
        )

        return {
            "success": True,
            "oldBalance": float(result["old_balance"]),
            "newBalance": float(result["new_balance"]),
            "record": result["record"]
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{userId}/status")
async def update_status(
    userId: str,
    request: UpdateStatusRequest,
    user_service: UserService = Depends(get_user_service)
):
    """更新用户状态（活跃/禁用）"""
    try:
        if not request.chatId:
            return {"success": False, "error": "缺少chatId参数"}

        user = await user_service.update_status(
            user_id=userId,
            chat_id=request.chatId,
            status=request.status
        )

        if not user:
            return {"success": False, "error": "用户不存在"}

        return {"success": True, "user": user}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{userId}/score")
async def update_score(
    userId: str,
    request: UpdateScoreRequest,
    user_service: UserService = Depends(get_user_service)
):
    """更新用户积分"""
    try:
        # TODO: 支持 operation="set" 直接设置积分
        # 目前只支持add（增加）

        # 需要chatId，但原版API没有要求，这里先用第一个chat
        users = await user_service.get_all_user_chats(userId)
        if not users:
            return {"success": False, "error": "用户不存在"}

        user = users[0]
        chat_id = user["chat_id"]

        updated_user = await user_service.add_score(
            user_id=userId,
            chat_id=chat_id,
            score_change=request.scoreChange
        )

        return {"success": True, "user": updated_user}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{userId}/rebate")
async def update_rebate(
    userId: str,
    request: UpdateRebateRequest,
    user_service: UserService = Depends(get_user_service)
):
    """更新用户回水比例"""
    try:
        if not request.chatId:
            return {"success": False, "error": "缺少chatId参数"}

        rebate_ratio = Decimal(str(request.rebateRatio))

        user = await user_service.update_rebate_ratio(
            user_id=userId,
            chat_id=request.chatId,
            rebate_ratio=rebate_ratio
        )

        if not user:
            return {"success": False, "error": "用户不存在"}

        return {"success": True, "user": user}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{userId}/red_packet")
async def update_red_packet(
    userId: str,
    request: UpdateRedPacketRequest,
    user_service: UserService = Depends(get_user_service)
):
    """更新用户红包设置"""
    try:
        if not request.chatId:
            return {"success": False, "error": "缺少chatId参数"}

        user = await user_service.update_red_packet_settings(
            user_id=userId,
            chat_id=request.chatId,
            settings=request.redPacketSettings
        )

        if not user:
            return {"success": False, "error": "用户不存在"}

        return {"success": True, "user": user}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{userId}/bot")
async def update_bot_config(
    userId: str,
    request: UpdateBotConfigRequest,
    user_service: UserService = Depends(get_user_service)
):
    """更新用户机器人配置"""
    try:
        # 需要chatId，但原版API没有要求，这里先用第一个chat
        users = await user_service.get_all_user_chats(userId)
        if not users:
            return {"success": False, "error": "用户不存在"}

        user = users[0]
        chat_id = user["chat_id"]

        updated_user = await user_service.update_bot_config(
            user_id=userId,
            chat_id=chat_id,
            is_bot=request.isBot,
            bot_config=request.botConfig
        )

        return {"success": True, "user": updated_user}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{userKey}/mark-read")
async def mark_user_as_read(
    userKey: str,
    user_service: UserService = Depends(get_user_service)
):
    """标记用户为已读"""
    try:
        # 解析userKey
        if "_" in userKey:
            user_id, chat_id = userKey.split("_", 1)
        else:
            return {"success": False, "error": "需要提供完整的userKey (userId_chatId)"}

        user = await user_service.mark_user_as_read(user_id, chat_id)

        if not user:
            return {"success": False, "error": "用户不存在"}

        return {"success": True, "user": user}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/{userId}/deposits")
async def get_user_deposits(
    userId: str,
    user_service: UserService = Depends(get_user_service)
):
    """获取用户的充值记录"""
    try:
        # TODO: 从deposit_records表获取
        # 暂时返回空列表
        return {"success": True, "deposits": []}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/{userId}/account-changes")
async def get_account_changes(
    userId: str,
    chatId: Optional[str] = Query(None),
    user_service: UserService = Depends(get_user_service)
):
    """获取用户账变记录（上下分记录）"""
    try:
        # TODO: 从account_changes表获取
        # 暂时返回空列表
        return {"success": True, "records": []}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ===== 用户列表API =====

@router.get("s")  # 对应 /api/users
async def get_all_users(
    chatId: Optional[str] = Query(None),
    user_service: UserService = Depends(get_user_service),
    admin_id: str = Depends(get_current_admin_id)
):
    """
    获取用户列表
    如果提供chatId，则返回该群的用户；否则返回所有用户
    """
    try:
        if chatId:
            users = await user_service.get_chat_users(chatId)
        else:
            # TODO: 需要实现get_all_users方法
            users = []

        return {"success": True, "users": users}
    except Exception as e:
        return {"success": False, "error": str(e)}
