"""
子账号管理 API
"""
from fastapi import APIRouter, Query, Depends, Body
from pydantic import BaseModel, Field, validator
from base.api import UnifyResponse, paginate_response
from base.exception import UnifyException
from base.error_codes import ErrorCode, get_error_message
from dependency_injector.wiring import inject, Provide
from biz.containers import Container
from biz.roles.service.subaccount_service import SubAccountService
from biz.auth.dependencies import get_current_admin


class CreateSubAccountRequest(BaseModel):
    """创建子账号请求"""
    agentAccount: str = Field(..., description="代理账号")
    loginPassword: str = Field(..., min_length=6, max_length=20, description="登录密码")
    paymentPassword: str = Field(..., min_length=6, max_length=20, description="支付密码")
    accountName: str = Field(..., min_length=1, max_length=50, description="账户名称")
    role: str = Field(..., description="角色名称")

    @validator('agentAccount')
    def validate_agent_account(cls, v):
        if not v or not v.strip():
            raise ValueError("代理账号不能为空")
        return v.strip()

    @validator('accountName')
    def validate_account_name(cls, v):
        if not v or not v.strip():
            raise ValueError("账户名称不能为空")
        return v.strip()

    @validator('role')
    def validate_role(cls, v):
        if not v or not v.strip():
            raise ValueError("角色不能为空")
        return v.strip()


class UpdateSubAccountRequest(BaseModel):
    """更新子账号请求"""
    accountName: str = Field(..., min_length=1, max_length=50, description="账户名称")
    role: str = Field(..., description="角色名称")
    status: str = Field(..., pattern="^(启用|禁用)$", description="状态")

    @validator('accountName')
    def validate_account_name(cls, v):
        if not v or not v.strip():
            raise ValueError("账户名称不能为空")
        return v.strip()

    @validator('role')
    def validate_role(cls, v):
        if not v or not v.strip():
            raise ValueError("角色不能为空")
        return v.strip()


router = APIRouter(prefix="/api/roles/sub-accounts", tags=["sub-accounts"])


@inject
def get_subaccount_service(service: SubAccountService = Depends(Provide[Container.subaccount_service])) -> SubAccountService:
    return service


@router.get("", response_class=UnifyResponse)
async def get_sub_accounts(
    agentAccount: str = Query(..., description="代理账号"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_admin: dict = Depends(get_current_admin),
    service: SubAccountService = Depends(get_subaccount_service)
):
    """
    获取子账号列表
    """
    try:
        result = await service.get_sub_accounts(agentAccount, page, pageSize)
        return paginate_response(
            list_data=result["list"],
            total=result["total"],
            page=page,
            page_size=pageSize
        )
    except ValueError as e:
        error_msg = str(e)
        if "代理账号不存在" in error_msg:
            raise UnifyException(
                get_error_message(ErrorCode.DATA_NOT_FOUND),
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)


@router.post("", response_class=UnifyResponse)
async def create_sub_account(
    request: CreateSubAccountRequest = Body(...),
    service: SubAccountService = Depends(get_subaccount_service)
):
    """
    新增子账号
    """
    try:
        sub_id = await service.create_sub_account(
            agent_account=request.agentAccount,
            login_password=request.loginPassword,
            payment_password=request.paymentPassword,
            account_name=request.accountName,
            role_name=request.role
        )
        return {"id": sub_id, "message": "新增子账号成功"}
    except ValueError as e:
        error_msg = str(e)
        if "代理账号不存在" in error_msg:
            raise UnifyException(
                "代理账号不存在",
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        if "角色不存在" in error_msg:
            raise UnifyException(
                error_msg,
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)


@router.put("/{sub_id}", response_class=UnifyResponse)
async def update_sub_account(
    sub_id: int,
    request: UpdateSubAccountRequest = Body(...),
    service: SubAccountService = Depends(get_subaccount_service)
):
    """
    更新子账号
    """
    try:
        await service.update_sub_account(
            sub_id=sub_id,
            account_name=request.accountName,
            role_name=request.role,
            status=request.status
        )
        return {"message": "更新子账号成功"}
    except ValueError as e:
        error_msg = str(e)
        if "子账号不存在" in error_msg or "角色不存在" in error_msg:
            raise UnifyException(
                get_error_message(ErrorCode.DATA_NOT_FOUND),
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)


@router.delete("/{sub_id}", response_class=UnifyResponse)
async def delete_sub_account(
    sub_id: int,
    service: SubAccountService = Depends(get_subaccount_service)
):
    """
    删除子账号
    """
    try:
        await service.delete_sub_account(sub_id)
        return {"message": "删除子账号成功"}
    except ValueError as e:
        error_msg = str(e)
        if "子账号不存在" in error_msg:
            raise UnifyException(
                get_error_message(ErrorCode.DATA_NOT_FOUND),
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)
