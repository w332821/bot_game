"""
Draw API路由
对应admin-server.js和bot-server.js中的开奖相关接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from biz.draw.service.draw_service import DrawService
from biz.draw.models.model import DrawCreate

router = APIRouter(prefix="/api/draw", tags=["draw"])


# ===== 请求/响应模型 =====

class CreateDrawRequest(BaseModel):
    """创建开奖记录请求"""
    drawNumber: int = Field(..., description="开奖号码")
    issue: str = Field(..., description="期号")
    drawCode: str = Field(..., description="开奖号码串")
    gameType: str = Field(default="lucky8", description="游戏类型")
    isRandom: bool = Field(default=False, description="是否为随机开奖")
    chatId: str = Field(default="system", description="群聊ID")
    betCount: int = Field(default=0, description="投注数量")


# ===== 依赖注入 =====

def get_draw_service() -> DrawService:
    """获取DrawService实例（占位，实际使用依赖注入容器）"""
    # TODO: 从依赖注入容器获取
    raise NotImplementedError("需要配置依赖注入容器")


# ===== API端点 =====

@router.get("/latest")
async def get_latest_draw(
    gameType: str = Query(default="lucky8"),
    chatId: str = Query(default="system"),
    draw_service: DrawService = Depends(get_draw_service)
):
    """
    获取最新开奖记录
    对应bot-server.js和admin-server.js中的获取最新开奖接口
    """
    try:
        draw = await draw_service.get_latest_draw(gameType, chatId)
        if not draw:
            return {"success": False, "error": "暂无开奖记录"}

        return {"success": True, "draw": draw}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/issue/{issue}")
async def get_draw_by_issue(
    issue: str,
    gameType: str = Query(default="lucky8"),
    chatId: str = Query(default="system"),
    draw_service: DrawService = Depends(get_draw_service)
):
    """
    根据期号获取开奖记录
    """
    try:
        draw = await draw_service.get_draw_by_issue(issue, gameType, chatId)
        if not draw:
            return {"success": False, "error": "开奖记录不存在"}

        return {"success": True, "draw": draw}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/add")
async def create_draw(
    request: CreateDrawRequest,
    draw_service: DrawService = Depends(get_draw_service)
):
    """
    创建开奖记录（需要管理员权限）
    """
    result = await draw_service.create_draw(
        draw_number=request.drawNumber,
        issue=request.issue,
        draw_code=request.drawCode,
        game_type=request.gameType,
        is_random=request.isRandom,
        chat_id=request.chatId,
        bet_count=request.betCount
    )
    return result


@router.get("/history")
async def get_draw_history(
    gameType: str = Query(default="lucky8"),
    chatId: str = Query(default="system"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    draw_service: DrawService = Depends(get_draw_service)
):
    """
    获取开奖历史
    """
    try:
        draws = await draw_service.get_draw_history(gameType, chatId, skip, limit)
        return {"success": True, "draws": draws, "total": len(draws)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/recent")
async def get_recent_draws(
    gameType: str = Query(default="lucky8"),
    chatId: str = Query(default="system"),
    count: int = Query(10, ge=1, le=100),
    draw_service: DrawService = Depends(get_draw_service)
):
    """
    获取最近N期开奖记录
    """
    try:
        draws = await draw_service.get_recent_draws(gameType, chatId, count)
        return {"success": True, "draws": draws, "total": len(draws)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/stats")
async def get_draw_stats(
    gameType: str = Query(default="lucky8"),
    chatId: str = Query(default="system"),
    draw_service: DrawService = Depends(get_draw_service)
):
    """
    获取开奖统计信息
    """
    try:
        stats = await draw_service.get_draw_stats(gameType, chatId)
        return {"success": True, "stats": stats}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.delete("/{drawId}")
async def delete_draw(
    drawId: int,
    draw_service: DrawService = Depends(get_draw_service)
):
    """
    删除开奖记录（需要超级管理员权限）
    """
    try:
        result = await draw_service.delete_draw(drawId)
        if not result:
            return {"success": False, "error": "开奖记录不存在或删除失败"}

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ===== 开奖列表API =====

@router.get("s")  # 对应 /api/draws
async def get_all_draws(
    gameType: str = Query(default="lucky8"),
    chatId: str = Query(default="system"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    draw_service: DrawService = Depends(get_draw_service)
):
    """
    获取开奖列表
    """
    try:
        draws = await draw_service.get_draw_history(gameType, chatId, skip, limit)
        return {"success": True, "draws": draws, "total": len(draws)}
    except Exception as e:
        return {"success": False, "error": str(e)}
