"""
退水配置 API
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel, Field, validator
from base.api import UnifyResponse
from base.exception import UnifyException
from base.error_codes import ErrorCode, get_error_message
from dependency_injector.wiring import inject, Provide
from biz.containers import Container
from biz.users.service.rebate_service import RebateService
from biz.auth.dependencies import get_current_admin
from base.game_name_mapper import validate_game_name


class GameSettingItem(BaseModel):
    """游戏退水配置项"""
    gameName: str = Field(..., description="游戏名称（中文）")
    rebate: float = Field(..., ge=0, le=100, description="退水比例 0-100")

    @validator('gameName')
    def validate_game_name_field(cls, v):
        """验证游戏名称必须是中文"""
        try:
            validate_game_name(v)
        except ValueError as e:
            raise ValueError(str(e))
        return v


class UpdateRebateRequest(BaseModel):
    """更新退水配置请求"""
    independentRebate: bool = Field(..., description="是否独立退水")
    earnRebate: float = Field(..., ge=0, le=100, description="赚取退水比例 0-100")
    gameSettings: List[GameSettingItem] = Field(..., min_items=1, description="游戏退水配置")


router = APIRouter(prefix="/api/users/rebate", tags=["users", "rebate"])


@inject
def get_rebate_service(service: RebateService = Depends(Provide[Container.rebate_service])) -> RebateService:
    return service


@router.get("/{account}", response_class=UnifyResponse)
async def get_rebate_settings(
    account: str,
    current_admin: dict = Depends(get_current_admin),
    service: RebateService = Depends(get_rebate_service)
):
    """
    获取退水配置
    """
    try:
        settings = await service.get_rebate_settings(account)
        if not settings:
            raise UnifyException(
                "用户不存在或未配置退水",
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        return settings
    except UnifyException:
        raise
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)


@router.put("/{account}", response_class=UnifyResponse)
async def update_rebate_settings(
    account: str,
    request: UpdateRebateRequest = Body(...),
    current_admin: dict = Depends(get_current_admin),
    service: RebateService = Depends(get_rebate_service)
):
    """
    更新退水配置
    """
    try:
        # 将 Pydantic 模型转为字典列表
        game_settings = [item.dict() for item in request.gameSettings]

        await service.update_rebate_settings(
            account=account,
            independent_rebate=request.independentRebate,
            earn_rebate=request.earnRebate,
            game_settings=game_settings
        )
        return {"success": True}
    except ValueError as e:
        error_msg = str(e)
        if "用户不存在" in error_msg:
            raise UnifyException(
                get_error_message(ErrorCode.DATA_NOT_FOUND),
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)
