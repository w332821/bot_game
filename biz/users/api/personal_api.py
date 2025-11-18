"""
个人中心 API
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, Depends, Body
from pydantic import BaseModel, Field, validator
from base.api import UnifyResponse, paginate_response
from base.exception import UnifyException
from base.error_codes import ErrorCode, get_error_message
from dependency_injector.wiring import inject, Provide
from biz.containers import Container
from biz.users.service.personal_service import PersonalService
from biz.auth.dependencies import get_current_admin
from base.game_name_mapper import validate_game_name


class UpdateBasicInfoRequest(BaseModel):
    """更新基本信息请求"""
    plate: Optional[str] = Field(None, pattern="^[ABCD]$")
    openPlate: Optional[List[str]] = None
    earnRebate: Optional[str] = Field(None, pattern="^(full|partial|none)$")
    subordinateTransfer: Optional[str] = Field(None, pattern="^(enable|disable)$")
    defaultRebatePlate: Optional[str] = Field(None, pattern="^[ABCD]$")

    @validator('openPlate')
    def validate_open_plate_items(cls, v):
        if v is None:
            return v
        valid_plates = {'A', 'B', 'C', 'D'}
        for plate in v:
            if plate not in valid_plates:
                raise ValueError(f'开放盘口只能是 A/B/C/D，收到: {plate}')
        return v


class AddPromotionDomainRequest(BaseModel):
    """添加推广域名请求"""
    domain: str = Field(..., min_length=1, max_length=255)


class LotteryRebateItem(BaseModel):
    """彩票退水配置项"""
    gameName: str = Field(..., description="游戏名称（中文）")
    betTypeName: Optional[str] = Field(None, description="投注类型名称")
    rebate: Optional[float] = Field(None, ge=0, le=100, description="退水比例 0-100")
    isGroup: Optional[bool] = Field(None, description="是否为分组")
    children: Optional[List[Dict[str, Any]]] = Field(None, description="子项（投注类型）")

    @validator('gameName')
    def validate_game_name_field(cls, v):
        try:
            validate_game_name(v)
        except ValueError as e:
            raise ValueError(str(e))
        return v


class SaveLotteryRebateConfigRequest(BaseModel):
    """保存彩票退水配置请求"""
    config: List[LotteryRebateItem] = Field(..., min_items=1)


class UpdatePasswordRequest(BaseModel):
    """修改密码请求"""
    oldPassword: str = Field(..., min_length=6, max_length=20)
    newPassword: str = Field(..., min_length=6, max_length=20)


router = APIRouter(prefix="/api/personal", tags=["personal"])


@inject
def get_personal_service(service: PersonalService = Depends(Provide[Container.personal_service])) -> PersonalService:
    return service


@router.get("/basic", response_class=UnifyResponse)
async def get_basic_info(
    account: str = Query(..., description="账号"),
    current_admin: dict = Depends(get_current_admin),
    service: PersonalService = Depends(get_personal_service)
):
    """
    获取个人基本信息
    """
    try:
        info = await service.get_basic_info(account)
        if not info:
            raise UnifyException(
                "用户不存在",
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        return info
    except UnifyException:
        raise
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.put("/basic", response_class=UnifyResponse)
async def update_basic_info(
    account: str = Query(..., description="账号"),
    request: UpdateBasicInfoRequest = Body(...),
    service: PersonalService = Depends(get_personal_service)
):
    """
    更新个人基本信息
    """
    try:
        await service.update_basic_info(
            account=account,
            plate=request.plate,
            open_plate=request.openPlate,
            earn_rebate=request.earnRebate,
            subordinate_transfer=request.subordinateTransfer,
            default_rebate_plate=request.defaultRebatePlate
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
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.post("/promote/domain", response_class=UnifyResponse)
async def add_promotion_domain(
    account: str = Query(..., description="代理账号"),
    request: AddPromotionDomainRequest = Body(...),
    service: PersonalService = Depends(get_personal_service)
):
    """
    添加推广域名（仅代理）
    """
    try:
        result = await service.add_promotion_domain(account, request.domain)
        return result
    except ValueError as e:
        error_msg = str(e)
        if "代理不存在" in error_msg:
            raise UnifyException(
                get_error_message(ErrorCode.DATA_NOT_FOUND),
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        if "域名已存在" in error_msg:
            raise UnifyException(
                "域名已存在",
                biz_code=ErrorCode.DUPLICATE_DATA,
                http_code=200
            )
        raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.get("/lottery-rebate-config", response_class=UnifyResponse)
async def get_lottery_rebate_config(
    account: str = Query(..., description="账号"),
    service: PersonalService = Depends(get_personal_service)
):
    """
    获取彩票退水配置
    """
    try:
        config = await service.get_lottery_rebate_config(account)
        return {"config": config}
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.put("/lottery-rebate-config", response_class=UnifyResponse)
async def save_lottery_rebate_config(
    account: str = Query(..., description="账号"),
    request: SaveLotteryRebateConfigRequest = Body(...),
    service: PersonalService = Depends(get_personal_service)
):
    """
    保存彩票退水配置
    """
    try:
        # 将 Pydantic 模型转为字典列表
        config_data = [item.dict(exclude_none=True) for item in request.config]

        await service.save_lottery_rebate_config(account, config_data)
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
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.get("/login-log", response_class=UnifyResponse)
async def get_login_logs(
    account: str = Query(..., description="账号"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    service: PersonalService = Depends(get_personal_service)
):
    """
    获取登录日志
    """
    try:
        result = await service.get_login_logs(account, page, pageSize)
        return paginate_response(
            list_data=result["list"],
            total=result["total"],
            page=page,
            page_size=pageSize
        )
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.put("/password", response_class=UnifyResponse)
async def update_password(
    account: str = Query(..., description="账号"),
    request: UpdatePasswordRequest = Body(...),
    service: PersonalService = Depends(get_personal_service)
):
    """
    修改密码
    """
    try:
        await service.update_password(
            account=account,
            old_password=request.oldPassword,
            new_password=request.newPassword
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
        if "旧密码错误" in error_msg:
            raise UnifyException(
                "旧密码错误",
                biz_code=ErrorCode.INVALID_CREDENTIALS,
                http_code=200
            )
        raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)
