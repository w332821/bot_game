from typing import Optional
from fastapi import APIRouter, Query, Depends, Body
from pydantic import BaseModel, Field
from base.api import UnifyResponse, success_response, paginate_response
from base.exception import UnifyException
from base.error_codes import ErrorCode, get_error_message
from dependency_injector.wiring import inject, Provide
from biz.containers import Container
from biz.users.service.member_service import MemberService
from biz.auth.dependencies import get_current_admin


class CreateMemberRequest(BaseModel):
    account: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6, max_length=20)
    plate: str = Field(..., pattern="^[ABC]$")
    superiorAccount: Optional[str] = Field(None, max_length=50)
    companyRemarks: Optional[str] = Field(None, max_length=500)


class UpdateMemberRequest(BaseModel):
    plate: Optional[str] = Field(None, pattern="^[ABC]$")
    companyRemarks: Optional[str] = Field(None, max_length=500)

router = APIRouter(prefix="/api/users/members", tags=["users", "members"]) 


@inject
def get_member_service(service: MemberService = Depends(Provide[Container.member_service])) -> MemberService:
    return service


@router.get("", response_class=UnifyResponse)
async def list_members(
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
    service: MemberService = Depends(get_member_service)
):
    try:
        result = await service.list_members(
            page, pageSize, account, showOnline, registrationDateStart, registrationDateEnd, plate, balanceMin, balanceMax
        )
        return {
            "list": result["list"],
            "total": result["total"],
            "page": page,
            "pageSize": pageSize
        }
    except Exception as e:
        raise UnifyException(str(e), biz_code=500, http_code=200)


@router.get("/{account}", response_class=UnifyResponse)
async def get_member_detail(account: str, current_admin: dict = Depends(get_current_admin), service: MemberService = Depends(get_member_service)):
    try:
        detail = await service.get_member_detail(account)
        if not detail:
            raise UnifyException("会员不存在", biz_code=404, http_code=200)
        return detail
    except UnifyException:
        raise
    except Exception as e:
        raise UnifyException(str(e), biz_code=500, http_code=200)


@router.get("/{account}/login-log", response_class=UnifyResponse)
async def get_member_login_log(
    account: str,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_admin: dict = Depends(get_current_admin),
    service: MemberService = Depends(get_member_service)
):
    try:
        result = await service.get_login_logs(account, page, pageSize)
        return {
            "list": result["list"],
            "total": result["total"],
            "page": page,
            "pageSize": pageSize
        }
    except Exception as e:
        raise UnifyException(str(e), biz_code=500, http_code=200)


@router.post("", response_class=UnifyResponse)
async def create_member(
    request: CreateMemberRequest = Body(...),
    current_admin: dict = Depends(get_current_admin),
    service: MemberService = Depends(get_member_service)
):
    """创建会员"""
    try:
        member_id = await service.create_member(
            account=request.account,
            password=request.password,
            plate=request.plate,
            superior_account=request.superiorAccount,
            company_remarks=request.companyRemarks
        )
        return {"id": member_id}
    except ValueError as e:
        error_msg = str(e)
        if "账号已存在" in error_msg:
            raise UnifyException(
                get_error_message(ErrorCode.ACCOUNT_ALREADY_EXISTS),
                biz_code=ErrorCode.ACCOUNT_ALREADY_EXISTS,
                http_code=200
            )
        raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.put("/{member_id}", response_class=UnifyResponse)
async def update_member(
    member_id: int,
    request: UpdateMemberRequest = Body(...),
    service: MemberService = Depends(get_member_service)
):
    """修改会员 - 只能修改 plate 和 companyRemarks"""
    try:
        await service.update_member(
            member_id=member_id,
            plate=request.plate,
            company_remarks=request.companyRemarks
        )
        return {"success": True}
    except ValueError as e:
        error_msg = str(e)
        if "会员不存在" in error_msg:
            raise UnifyException(
                get_error_message(ErrorCode.DATA_NOT_FOUND),
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=200)


@router.get("/{account}/bet-orders", response_class=UnifyResponse)
async def get_member_bet_orders(
    account: str,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    betType: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    service: MemberService = Depends(get_member_service)
):
    """获取会员注单列表（带当前页汇总）"""
    try:
        result = await service.get_bet_orders(
            account=account,
            page=page,
            page_size=pageSize,
            status=status,
            bet_type=betType,
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


@router.get("/{account}/transactions", response_class=UnifyResponse)
async def get_member_transactions(
    account: str,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    transactionType: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    service: MemberService = Depends(get_member_service)
):
    """获取会员交易记录（带当前页汇总）"""
    try:
        result = await service.get_transactions(
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
async def get_member_account_changes(
    account: str,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    changeType: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    service: MemberService = Depends(get_member_service)
):
    """获取会员账变记录"""
    try:
        result = await service.get_account_changes(
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