"""
Draw API路由
对应admin-server.js和bot-server.js中的开奖相关接口
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from biz.draw.service.draw_service import DrawService
from biz.draw.models.model import DrawCreate
from dependency_injector.wiring import inject, Provide
from biz.containers import Container
from base.api import UnifyResponse
from base.exception import UnifyException

router = APIRouter(prefix="/api", tags=["lottery", "draw"]) 


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

@inject
def get_draw_service(service: DrawService = Depends(Provide[Container.draw_service])) -> DrawService:
    return service


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

@router.get("s")
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


def _to_chinese_game_name(game_type: str) -> str:
    return "168澳洲幸运8" if game_type == "lucky8" else "新奥六合彩"


def _parse_numbers(draw_code: str) -> List[str]:
    return re.findall(r"\d+", str(draw_code))


def _compute_metrics(numbers: List[int]) -> Dict[str, Any]:
    if len(numbers) < 2:
        return {
            "championSum": None,
            "championSize": None,
            "championParity": None,
            "dragonTiger": [None, None, None, None, None]
        }
    s = numbers[0] + numbers[1]
    size = "大" if s >= 12 else "小"
    parity = "单" if s % 2 == 1 else "双"
    dt = []
    if len(numbers) >= 10:
        for i in range(5):
            dt.append("龙" if numbers[i] > numbers[9 - i] else "虎")
    else:
        dt = [None, None, None, None, None]
    return {
        "championSum": s,
        "championSize": size,
        "championParity": parity,
        "dragonTiger": dt
    }


def _format_time(ts: Any) -> str:
    if isinstance(ts, datetime):
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    try:
        return datetime.fromisoformat(str(ts)).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)


@router.get("/lottery/results", response_class=UnifyResponse)
async def get_lottery_results(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    type: Optional[str] = Query(None, alias="type"),
    date: Optional[str] = Query(None, alias="date"),
    lotteryType: Optional[str] = Query(None),
    lotteryDate: Optional[str] = Query(None),
    draw_service: DrawService = Depends(get_draw_service)
):
    try:
        # Support both 'type' and 'lotteryType' parameter names for backwards compatibility
        lottery_type = type or lotteryType
        lottery_date = date or lotteryDate

        gt = "lucky8"
        if lottery_type == "新奥六合彩":
            gt = "liuhecai"
        elif lottery_type == "168澳洲幸运8":
            gt = "lucky8"
        skip = (page - 1) * pageSize
        if lottery_date:
            try:
                datetime.strptime(lottery_date, "%Y-%m-%d")
            except Exception:
                raise UnifyException("日期格式错误，应为 YYYY-MM-DD", biz_code=400, http_code=200)
            rows = await draw_service.get_draw_history_by_date(gt, "system", lottery_date, skip, pageSize)
            total = await draw_service.count_draws_by_date(gt, "system", lottery_date)
        else:
            rows = await draw_service.get_draw_history(gt, "system", skip, pageSize)
            stats = await draw_service.get_draw_stats(gt, "system")
            total = stats.get("total_count", 0)
        items = []
        for r in rows:
            nums_str = _parse_numbers(r.get("draw_code", ""))
            nums_int = []
            for s in nums_str:
                try:
                    nums_int.append(int(s))
                except Exception:
                    nums_int.append(None)
            metrics = _compute_metrics([n for n in nums_int if isinstance(n, int)])
            item = {
                "id": r.get("id"),
                "issueNumber": r.get("issue"),
                "lotteryTime": _format_time(r.get("timestamp")),
                "lotteryType": _to_chinese_game_name(r.get("game_type", gt)),
                "numbers": nums_str,
                "championSum": metrics["championSum"],
                "championSize": metrics["championSize"],
                "championParity": metrics["championParity"],
                "dragonTiger1": metrics["dragonTiger"][0],
                "dragonTiger2": metrics["dragonTiger"][1],
                "dragonTiger3": metrics["dragonTiger"][2],
                "dragonTiger4": metrics["dragonTiger"][3],
                "dragonTiger5": metrics["dragonTiger"][4],
            }
            items.append(item)
        return {
            "list": items,
            "total": total,
            "page": page,
            "pageSize": pageSize
        }
    except Exception as e:
        raise UnifyException(str(e), biz_code=500, http_code=500)


@router.get("/lottery/results/{id}", response_class=UnifyResponse)
async def get_lottery_result_detail(
    id: int,
    draw_service: DrawService = Depends(get_draw_service)
):
    try:
        r = await draw_service.draw_repo.get_draw(id)
        if not r:
            raise UnifyException("资源不存在", biz_code=404, http_code=200)
        nums_str = _parse_numbers(r.get("draw_code", ""))
        nums_int = []
        for s in nums_str:
            try:
                nums_int.append(int(s))
            except Exception:
                nums_int.append(None)
        metrics = _compute_metrics([n for n in nums_int if isinstance(n, int)])
        item = {
            "id": r.get("id"),
            "issueNumber": r.get("issue"),
            "lotteryTime": _format_time(r.get("timestamp")),
            "lotteryType": _to_chinese_game_name(r.get("game_type", "lucky8")),
            "numbers": nums_str,
            "championSum": metrics["championSum"],
            "championSize": metrics["championSize"],
            "championParity": metrics["championParity"],
            "dragonTiger1": metrics["dragonTiger"][0],
            "dragonTiger2": metrics["dragonTiger"][1],
            "dragonTiger3": metrics["dragonTiger"][2],
            "dragonTiger4": metrics["dragonTiger"][3],
            "dragonTiger5": metrics["dragonTiger"][4],
        }
        return item
    except Exception as e:
        raise UnifyException(str(e), biz_code=500, http_code=500)
