"""
Chat API路由
对应admin-server.js中的 /api/chat/* 接口
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from biz.chat.service.chat_service import ChatService
from biz.chat.models.model import Chat, ChatCreate, ChatUpdate

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ===== 请求/响应模型 =====

class UpdateGameTypeRequest(BaseModel):
    """更新游戏类型请求"""
    gameType: str = Field(..., description="游戏类型：lucky8/liuhecai")


class UpdateOwnerRequest(BaseModel):
    """更新所属分销商请求"""
    ownerId: Optional[str] = Field(None, description="分销商ID")


class UpdateStatusRequest(BaseModel):
    """更新状态请求"""
    status: str = Field(..., description="状态：active/inactive")


# ===== 依赖注入 =====

from dependency_injector.wiring import inject, Provide
from biz.containers import Container

@inject
def get_chat_service(
    service: ChatService = Depends(Provide[Container.chat_service])
) -> ChatService:
    """获取ChatService实例"""
    return service


# ===== API端点 =====

@router.get("/{chatId}")
async def get_chat(
    chatId: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    获取群聊信息
    """
    try:
        chat = await chat_service.get_chat(chatId)
        if not chat:
            return {"success": False, "error": "群聊不存在"}

        return {"success": True, "chat": chat}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/add")
async def create_chat(
    chat_data: ChatCreate,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    创建群聊（需要管理员权限）
    """
    try:
        chat = await chat_service.create_chat(
            chat_id=chat_data.id,
            name=chat_data.name,
            game_type=chat_data.game_type,
            owner_id=chat_data.owner_id,
            auto_draw=chat_data.auto_draw,
            bet_lock_time=chat_data.bet_lock_time
        )

        return {"success": True, "chat": chat}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{chatId}/gametype")
async def update_game_type(
    chatId: str,
    request: UpdateGameTypeRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    更新群聊游戏类型
    对应admin-server.js中的 POST /api/chat/:chatId/gametype
    """
    try:
        chat = await chat_service.update_game_type(chatId, request.gameType)

        if not chat:
            return {"success": False, "error": "群聊不存在"}

        return {"success": True, "chat": chat}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{chatId}/owner")
async def update_owner(
    chatId: str,
    request: UpdateOwnerRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    更新群聊所属分销商
    """
    try:
        chat = await chat_service.update_owner(chatId, request.ownerId)

        if not chat:
            return {"success": False, "error": "群聊不存在"}

        return {"success": True, "chat": chat}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{chatId}/status")
async def update_status(
    chatId: str,
    request: UpdateStatusRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    更新群聊状态
    """
    try:
        chat = await chat_service.update_status(chatId, request.status)

        if not chat:
            return {"success": False, "error": "群聊不存在"}

        return {"success": True, "chat": chat}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/{chatId}/stats")
async def get_chat_stats(
    chatId: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    获取群聊统计信息
    """
    try:
        stats = await chat_service.get_chat_stats(chatId)
        return {"success": True, "stats": stats}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.delete("/{chatId}")
async def delete_chat(
    chatId: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    删除群聊（需要超级管理员权限）
    """
    try:
        result = await chat_service.delete_chat(chatId)
        if not result:
            return {"success": False, "error": "群聊不存在或删除失败"}

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ===== 群聊列表API =====

@router.get("s")  # 对应 /api/chats
async def get_all_chats(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    ownerId: Optional[str] = Query(None),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    获取群聊列表
    支持按状态、所属分销商筛选
    """
    try:
        if ownerId:
            chats = await chat_service.get_chats_by_owner(ownerId, skip, limit)
        else:
            chats = await chat_service.get_all_chats(skip, limit, status)

        return {"success": True, "chats": chats, "total": len(chats)}
    except Exception as e:
        return {"success": False, "error": str(e)}
