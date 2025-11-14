"""
Bet API路由
对应admin-server.js和bot-server.js中的投注相关接口
"""
from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from biz.bet.service.bet_service import BetService
from biz.bet.models.model import Bet, BetCreate

router = APIRouter(prefix="/api/bet", tags=["bet"])


# ===== 请求/响应模型 =====

class PlaceBetRequest(BaseModel):
    """下注请求"""
    userId: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    chatId: str = Field(..., description="群聊ID")
    gameType: str = Field(default="lucky8", description="游戏类型")
    lotteryType: str = Field(..., description="投注类型")
    betNumber: Optional[int] = Field(None, description="投注号码")
    betAmount: float = Field(..., gt=0, description="投注金额")
    odds: float = Field(..., gt=0, description="赔率")
    issue: Optional[str] = Field(None, description="期号")


class CancelBetRequest(BaseModel):
    """取消投注请求"""
    userId: str = Field(..., description="用户ID")


# ===== 依赖注入 =====

def get_bet_service() -> BetService:
    """获取BetService实例（占位，实际使用依赖注入容器）"""
    # TODO: 从依赖注入容器获取
    raise NotImplementedError("需要配置依赖注入容器")


# ===== API端点 =====

@router.post("/place")
async def place_bet(
    request: PlaceBetRequest,
    bet_service: BetService = Depends(get_bet_service)
):
    """
    下注接口
    """
    try:
        result = await bet_service.place_bet(
            user_id=request.userId,
            username=request.username,
            chat_id=request.chatId,
            game_type=request.gameType,
            lottery_type=request.lotteryType,
            bet_amount=Decimal(str(request.betAmount)),
            odds=Decimal(str(request.odds)),
            bet_number=request.betNumber,
            issue=request.issue
        )

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/{betId}")
async def get_bet(
    betId: str,
    bet_service: BetService = Depends(get_bet_service)
):
    """
    获取投注详情
    """
    try:
        bet = await bet_service.get_bet(betId)
        if not bet:
            return {"success": False, "error": "投注不存在"}

        return {"success": True, "bet": bet}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("s")  # 对应 /api/bets
async def get_bets(
    userId: Optional[str] = Query(None),
    chatId: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    bet_service: BetService = Depends(get_bet_service)
):
    """
    获取投注列表
    支持按用户、群聊筛选
    """
    try:
        if userId and chatId:
            bets = await bet_service.get_bet_history(userId, chatId, skip, limit)
        elif chatId:
            bets = await bet_service.get_chat_bets(chatId, skip, limit)
        else:
            return {"success": False, "error": "需要提供userId+chatId或chatId参数"}

        return {"success": True, "bets": bets, "total": len(bets)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{betId}/cancel")
async def cancel_bet(
    betId: str,
    request: CancelBetRequest,
    bet_service: BetService = Depends(get_bet_service)
):
    """
    取消投注
    """
    try:
        result = await bet_service.cancel_bet(betId, request.userId)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/user/{userId}/stats")
async def get_user_stats(
    userId: str,
    chatId: str = Query(...),
    bet_service: BetService = Depends(get_bet_service)
):
    """
    获取用户投注统计
    """
    try:
        stats = await bet_service.get_user_stats(userId, chatId)
        return {"success": True, "stats": stats}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/history")
async def get_bet_history(
    userId: str = Query(...),
    chatId: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    bet_service: BetService = Depends(get_bet_service)
):
    """
    获取投注历史
    """
    try:
        bets = await bet_service.get_bet_history(userId, chatId, skip, limit)
        return {"success": True, "bets": bets, "total": len(bets)}
    except Exception as e:
        return {"success": False, "error": str(e)}
