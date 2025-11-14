"""
Odds API路由
对应admin-server.js中的赔率相关接口
"""
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from biz.odds.service.odds_service import OddsService
from biz.odds.models.model import OddsCreate, OddsUpdate

router = APIRouter(prefix="/api/odds", tags=["odds"])


# ===== 请求/响应模型 =====

class UpdateOddsRequest(BaseModel):
    """更新赔率请求"""
    odds: Optional[float] = Field(None, description="赔率")
    minBet: Optional[float] = Field(None, description="最小投注额")
    maxBet: Optional[float] = Field(None, description="最大投注额")
    periodMax: Optional[float] = Field(None, description="单期最大投注额")
    description: Optional[str] = None
    status: Optional[str] = None


class CreateOddsRequest(BaseModel):
    """创建赔率请求"""
    betType: str = Field(..., description="投注类型")
    odds: float = Field(..., description="赔率")
    gameType: str = Field(default="lucky8", description="游戏类型")
    minBet: float = Field(default=10.0)
    maxBet: float = Field(default=10000.0)
    periodMax: float = Field(default=50000.0)
    description: Optional[str] = None


# ===== 依赖注入 =====

def get_odds_service() -> OddsService:
    """获取OddsService实例（占位，实际使用依赖注入容器）"""
    # TODO: 从依赖注入容器获取
    raise NotImplementedError("需要配置依赖注入容器")


# ===== API端点 =====

@router.get("")
async def get_all_odds(
    gameType: str = Query(default="lucky8"),
    status: Optional[str] = Query(None),
    odds_service: OddsService = Depends(get_odds_service)
):
    """
    获取所有赔率配置
    对应admin-server.js中的 GET /api/odds
    """
    try:
        odds_list = await odds_service.get_all_odds(gameType, status)
        return {"success": True, "odds": odds_list, "total": len(odds_list)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/{betType}")
async def get_odds(
    betType: str,
    gameType: str = Query(default="lucky8"),
    odds_service: OddsService = Depends(get_odds_service)
):
    """
    获取指定类型的赔率配置
    """
    try:
        odds = await odds_service.get_odds(betType, gameType)
        if not odds:
            return {"success": False, "error": "赔率配置不存在"}

        return {"success": True, "odds": odds}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/add")
async def create_odds(
    request: CreateOddsRequest,
    odds_service: OddsService = Depends(get_odds_service)
):
    """
    创建赔率配置（需要管理员权限）
    """
    result = await odds_service.create_odds(
        bet_type=request.betType,
        odds=Decimal(str(request.odds)),
        game_type=request.gameType,
        min_bet=Decimal(str(request.minBet)),
        max_bet=Decimal(str(request.maxBet)),
        period_max=Decimal(str(request.periodMax)),
        description=request.description
    )
    return result


@router.put("/{betType}")
async def update_odds(
    betType: str,
    request: UpdateOddsRequest,
    gameType: str = Query(default="lucky8"),
    odds_service: OddsService = Depends(get_odds_service)
):
    """
    更新赔率配置
    对应admin-server.js中的 PUT /api/odds/:betType
    """
    try:
        # 构建更新数据
        updates = {}
        if request.odds is not None:
            updates["odds"] = Decimal(str(request.odds))
        if request.minBet is not None:
            updates["min_bet"] = Decimal(str(request.minBet))
        if request.maxBet is not None:
            updates["max_bet"] = Decimal(str(request.maxBet))
        if request.periodMax is not None:
            updates["period_max"] = Decimal(str(request.periodMax))
        if request.description is not None:
            updates["description"] = request.description
        if request.status is not None:
            updates["status"] = request.status

        result = await odds_service.update_odds(betType, gameType, updates)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{betType}/status")
async def update_odds_status(
    betType: str,
    status: str = Query(...),
    gameType: str = Query(default="lucky8"),
    odds_service: OddsService = Depends(get_odds_service)
):
    """
    更新赔率状态（启用/禁用）
    """
    try:
        odds = await odds_service.update_status(betType, gameType, status)
        if not odds:
            return {"success": False, "error": "赔率配置不存在"}

        return {"success": True, "odds": odds}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.delete("/{betType}")
async def delete_odds(
    betType: str,
    gameType: str = Query(default="lucky8"),
    odds_service: OddsService = Depends(get_odds_service)
):
    """
    删除赔率配置（需要超级管理员权限）
    """
    try:
        result = await odds_service.delete_odds(betType, gameType)
        if not result:
            return {"success": False, "error": "赔率配置不存在或删除失败"}

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/validate")
async def validate_bet_amount(
    betType: str = Query(...),
    betAmount: float = Query(...),
    gameType: str = Query(default="lucky8"),
    odds_service: OddsService = Depends(get_odds_service)
):
    """
    验证投注金额是否在限额范围内
    """
    try:
        result = await odds_service.validate_bet_amount(
            betType,
            Decimal(str(betAmount)),
            gameType
        )
        return result
    except Exception as e:
        return {"valid": False, "error": str(e)}
