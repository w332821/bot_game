from typing import Optional, List
from fastapi import APIRouter, Query, Depends, Body
from pydantic import BaseModel, Field, validator
from base.api import UnifyResponse, paginate_response
from base.exception import UnifyException
from base.error_codes import ErrorCode, get_error_message
from dependency_injector.wiring import inject, Provide
from biz.containers import Container
from biz.users.service.agent_service import AgentService
from biz.auth.dependencies import get_current_admin


class CreateAgentRequest(BaseModel):
    account: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6, max_length=20)
    plate: str = Field(..., pattern="^[ABC]$")
    openPlate: List[str] = Field(..., min_items=1)
    earnRebate: str = Field(..., pattern="^(full|partial|none)$")
    subordinateTransfer: str = Field(..., pattern="^(enable|disable)$")
    defaultRebatePlate: str = Field(..., pattern="^[ABCD]$")
    superiorAccount: Optional[str] = Field(None, max_length=50)
    companyRemarks: Optional[str] = Field(None, max_length=500)

    @validator('openPlate')
    def validate_open_plate_items(cls, v):
        """验证 openPlate 数组的每个元素"""
        valid_plates = {'A', 'B', 'C', 'D'}
        for plate in v:
            if plate not in valid_plates:
                raise ValueError(f'开放盘口只能是 A/B/C/D，收到: {plate}')
        return v


class UpdateAgentRequest(BaseModel):
    plate: Optional[str] = Field(None, pattern="^[ABC]$")
    openPlate: Optional[List[str]] = None
    earnRebate: Optional[str] = Field(None, pattern="^(full|partial|none)$")
    subordinateTransfer: Optional[str] = Field(None, pattern="^(enable|disable)$")
    defaultRebatePlate: Optional[str] = Field(None, pattern="^[ABCD]$")
    companyRemarks: Optional[str] = Field(None, max_length=500)

    @validator('openPlate')
    def validate_open_plate_items(cls, v):
        """验证 openPlate 数组的每个元素"""
        if v is None:
            return v
        valid_plates = {'A', 'B', 'C', 'D'}
        for plate in v:
            if plate not in valid_plates:
                raise ValueError(f'开放盘口只能是 A/B/C/D，收到: {plate}')
        return v


router = APIRouter(prefix="/api/users/agents", tags=["users", "agents"])


@inject
def get_agent_service(service: AgentService = Depends(Provide[Container.agent_service])) -> AgentService:
    return service


@router.get("", response_class=UnifyResponse)
async def list_agents(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    account: Optional[str] = Query(None),
    showOnline: Optional[bool] = Query(None),
    registrationDateStart: Optional[str] = Query(None),
    registrationDateEnd: Optional[str] = Query(None),
    plate: Optional[str] = Query(None),
    balanceMin: Optional[float] = Query(None),
    balanceMax: Optional[float] = Query(None),
    current_admin: dict = Depends(get_current_admin),
    service: AgentService = Depends(get_agent_service)
):
    """代理列表"""
    try:
        result = await service.list_agents(
            page, pageSize, account, showOnline, registrationDateStart, registrationDateEnd,
            plate, balanceMin, balanceMax
        )
        return {
            "list": result["list"],
            "total": result["total"],
            "page": page,
            "pageSize": pageSize
        }
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.get("/{account}", response_class=UnifyResponse)
async def get_agent_detail(account: str, current_admin: dict = Depends(get_current_admin), service: AgentService = Depends(get_agent_service)):
    """代理详情"""
    try:
        detail = await service.get_agent_detail(account)
        if not detail:
            raise UnifyException("代理不存在", biz_code=ErrorCode.DATA_NOT_FOUND, http_code=200)
        return detail
    except UnifyException:
        raise
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.get("/{account}/login-log", response_class=UnifyResponse)
async def get_agent_login_log(
    account: str,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    service: AgentService = Depends(get_agent_service)
):
    """代理登录日志"""
    try:
        result = await service.get_agent_login_logs(account, page, pageSize)
        return {
            "list": result["list"],
            "total": result["total"],
            "page": page,
            "pageSize": pageSize
        }
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.get("/{account}/members", response_class=UnifyResponse)
async def get_agent_members(
    account: str,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    memberAccount: Optional[str] = Query(None),
    showOnline: Optional[bool] = Query(None),
    registrationDateStart: Optional[str] = Query(None),
    registrationDateEnd: Optional[str] = Query(None),
    plate: Optional[str] = Query(None),
    balanceMin: Optional[float] = Query(None),
    balanceMax: Optional[float] = Query(None),
    service: AgentService = Depends(get_agent_service)
):
    """代理的下线会员列表"""
    try:
        result = await service.get_agent_members(
            agent_account=account,
            page=page,
            page_size=pageSize,
            account=memberAccount,
            show_online=showOnline,
            reg_start=registrationDateStart,
            reg_end=registrationDateEnd,
            plate=plate,
            balance_min=balanceMin,
            balance_max=balanceMax
        )
        return {
            "list": result["list"],
            "total": result["total"],
            "page": page,
            "pageSize": pageSize
        }
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.post("", response_class=UnifyResponse)
async def create_agent(
    request: CreateAgentRequest = Body(...),
    service: AgentService = Depends(get_agent_service)
):
    """创建代理"""
    try:
        agent_id = await service.create_agent(
            account=request.account,
            password=request.password,
            plate=request.plate,
            open_plate=request.openPlate,
            earn_rebate=request.earnRebate,
            subordinate_transfer=request.subordinateTransfer,
            default_rebate_plate=request.defaultRebatePlate,
            superior_account=request.superiorAccount,
            company_remarks=request.companyRemarks
        )
        return {"id": agent_id}
    except ValueError as e:
        error_msg = str(e)
        if "账号已存在" in error_msg:
            raise UnifyException(
                get_error_message(ErrorCode.ACCOUNT_ALREADY_EXISTS),
                biz_code=ErrorCode.ACCOUNT_ALREADY_EXISTS,
                http_code=200
            )
        if "开放盘口" in error_msg or "无效的盘口" in error_msg:
            raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
        raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.put("/{agent_id}", response_class=UnifyResponse)
async def update_agent(
    agent_id: int,
    request: UpdateAgentRequest = Body(...),
    service: AgentService = Depends(get_agent_service)
):
    """修改代理"""
    try:
        await service.update_agent(
            agent_id=agent_id,
            plate=request.plate,
            open_plate=request.openPlate,
            earn_rebate=request.earnRebate,
            subordinate_transfer=request.subordinateTransfer,
            default_rebate_plate=request.defaultRebatePlate,
            company_remarks=request.companyRemarks
        )
        return {"success": True}
    except ValueError as e:
        error_msg = str(e)
        if "代理不存在" in error_msg:
            raise UnifyException(
                get_error_message(ErrorCode.DATA_NOT_FOUND),
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        if "开放盘口" in error_msg or "无效的盘口" in error_msg:
            raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
        raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.get("/{account}/transactions", response_class=UnifyResponse)
async def get_agent_transactions(
    account: str,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    transactionType: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    service: AgentService = Depends(get_agent_service)
):
    """获取代理交易记录（带当前页汇总）"""
    try:
        result = await service.get_agent_transactions(
            account=account,
            page=page,
            page_size=pageSize,
            transaction_type=transactionType,
            start_date=startDate,
            end_date=endDate
        )
        return paginate_response(
            list_data=result["list"],
            total=result["total"],
            page=page,
            page_size=pageSize,
            summary=result["summary"]
        )
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.get("/{account}/account-changes", response_class=UnifyResponse)
async def get_agent_account_changes(
    account: str,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    changeType: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    service: AgentService = Depends(get_agent_service)
):
    """获取代理账变记录"""
    try:
        result = await service.get_agent_account_changes(
            account=account,
            page=page,
            page_size=pageSize,
            change_type=changeType,
            start_date=startDate,
            end_date=endDate
        )
        return paginate_response(
            list_data=result["list"],
            total=result["total"],
            page=page,
            page_size=pageSize
        )
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)
