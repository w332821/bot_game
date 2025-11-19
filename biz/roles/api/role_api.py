"""
角色管理 API
"""
from typing import List, Optional
from fastapi import APIRouter, Query, Depends, Body
from pydantic import BaseModel, Field, validator
from base.api import UnifyResponse, paginate_response
from base.exception import UnifyException
from base.error_codes import ErrorCode, get_error_message
from dependency_injector.wiring import inject, Provide
from biz.containers import Container
from biz.roles.service.role_service import RoleService
from biz.auth.dependencies import get_current_admin
import re


class CreateRoleRequest(BaseModel):
    """创建角色请求"""
    roleName: str = Field(..., min_length=1, max_length=50, description="角色名称")
    remarks: Optional[str] = Field("", max_length=500, description="备注")
    permissions: List[str] = Field(..., min_items=1, description="权限列表")

    @validator('roleName')
    def validate_role_name(cls, v):
        if not v or not v.strip():
            raise ValueError("角色名称不能为空")
        return v.strip()

    @validator('permissions')
    def validate_permissions(cls, v):
        if not v:
            raise ValueError("权限列表不能为空")
        # 验证权限编码格式
        pattern = r'^[a-z]+-[a-z]+-\d+$'
        for perm in v:
            if not re.match(pattern, perm):
                raise ValueError(f"无效的权限编码: {perm}")
        return v


class UpdateRoleRequest(BaseModel):
    """更新角色请求"""
    roleName: str = Field(..., min_length=1, max_length=50, description="角色名称")
    remarks: Optional[str] = Field("", max_length=500, description="备注")
    permissions: List[str] = Field(..., min_items=1, description="权限列表")

    @validator('roleName')
    def validate_role_name(cls, v):
        if not v or not v.strip():
            raise ValueError("角色名称不能为空")
        return v.strip()

    @validator('permissions')
    def validate_permissions(cls, v):
        if not v:
            raise ValueError("权限列表不能为空")
        # 验证权限编码格式
        pattern = r'^[a-z]+-[a-z]+-\d+$'
        for perm in v:
            if not re.match(pattern, perm):
                raise ValueError(f"无效的权限编码: {perm}")
        return v


router = APIRouter(prefix="/api/roles", tags=["roles"])


@inject
def get_role_service(service: RoleService = Depends(Provide[Container.role_service])) -> RoleService:
    return service


@router.get("", response_class=UnifyResponse)
async def get_roles(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    roleName: Optional[str] = Query(None, description="角色名称搜索"),
    current_admin: dict = Depends(get_current_admin),
    service: RoleService = Depends(get_role_service)
):
    """
    获取角色列表
    """
    try:
        result = await service.get_roles(page, pageSize, roleName)
        return paginate_response(
            list_data=result["list"],
            total=result["total"],
            page=page,
            page_size=pageSize
        )
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)


@router.get("/permissions", response_class=UnifyResponse)
async def get_permissions_tree(
    current_admin: dict = Depends(get_current_admin)
):
    """
    获取权限树(所有可用权限的树形结构)
    """
    tree = [
        {
            "id": "personal",
            "label": "个人管理",
            "children": [
                {
                    "id": "personal-basic",
                    "label": "基本资料",
                    "children": [
                        {"id": "personal-basic-1", "label": "修改代理会员注册默认盘口"},
                        {"id": "personal-basic-2", "label": "获取代理个人信息"},
                        {"id": "personal-basic-3", "label": "获取代理盘口信息"},
                        {"id": "personal-basic-4", "label": "获取代理盘口退水信息"}
                    ]
                },
                {"id": "personal-log", "label": "登录日志"},
                {
                    "id": "personal-password",
                    "label": "修改密码",
                    "children": [
                        {"id": "personal-password-1", "label": "保存"}
                    ]
                }
            ]
        },
        {
            "id": "reports",
            "label": "报表查询",
            "children": [
                {"id": "reports-1", "label": "报表查询"},
                {"id": "reports-summary", "label": "财务总报表"},
                {"id": "reports-financial", "label": "财务报表"},
                {"id": "reports-win-loss", "label": "输赢报表"},
                {"id": "reports-agent-win-loss", "label": "代理输赢报表"},
                {"id": "reports-deposit-withdrawal", "label": "存取款报表"},
                {"id": "reports-category", "label": "分类报表"},
                {"id": "reports-downline-details", "label": "下线明细报表"},
                {"id": "reports-lottery-types", "label": "彩种列表"}
            ]
        },
        {
            "id": "lottery",
            "label": "开奖结果",
            "children": [
                {"id": "lottery-1", "label": "开奖结果"}
            ]
        },
        {
            "id": "users",
            "label": "用户管理",
            "children": [
                {"id": "users-1", "label": "用户管理"},
                {
                    "id": "users-members",
                    "label": "下线会员",
                    "children": [
                        {"id": "users-members-add", "label": "新增会员"},
                        {"id": "users-members-rebate", "label": "会员默认退水"},
                        {"id": "users-members-view", "label": "查看资料"},
                        {"id": "users-members-log", "label": "登录日志"},
                        {"id": "users-members-bets", "label": "查看注单"},
                        {"id": "users-members-transaction", "label": "交易记录"},
                        {"id": "users-members-account", "label": "查看帐变"},
                        {"id": "users-members-plate", "label": "查看盘口"}
                    ]
                },
                {
                    "id": "users-agents",
                    "label": "下线代理",
                    "children": [
                        {"id": "users-agents-add", "label": "新增代理"},
                        {"id": "users-agents-rebate", "label": "退水"},
                        {"id": "users-agents-view", "label": "查看资料"},
                        {"id": "users-agents-log", "label": "登录日志"},
                        {"id": "users-agents-transaction", "label": "交易记录"},
                        {"id": "users-agents-account", "label": "查看帐变"},
                        {"id": "users-agents-plate", "label": "查看盘口"}
                    ]
                }
            ]
        }
    ]
    return {"tree": tree}


@router.get("/{role_id}", response_class=UnifyResponse)
async def get_role_detail(
    role_id: int,
    current_admin: dict = Depends(get_current_admin),
    service: RoleService = Depends(get_role_service)
):
    """
    获取角色详情
    """
    try:
        role = await service.get_role_detail(role_id)
        if not role:
            raise UnifyException(
                "角色不存在",
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        return role
    except UnifyException:
        raise
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)


@router.post("", response_class=UnifyResponse)
async def create_role(
    request: CreateRoleRequest = Body(...),
    current_admin: dict = Depends(get_current_admin),
    service: RoleService = Depends(get_role_service)
):
    """
    新增角色
    """
    try:
        role_id = await service.create_role(
            role_name=request.roleName,
            remarks=request.remarks or "",
            permissions=request.permissions
        )
        return {"id": role_id, "message": "新增角色成功"}
    except ValueError as e:
        raise UnifyException(str(e), biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)


@router.put("/{role_id}", response_class=UnifyResponse)
async def update_role(
    role_id: int,
    request: UpdateRoleRequest = Body(...),
    current_admin: dict = Depends(get_current_admin),
    service: RoleService = Depends(get_role_service)
):
    """
    更新角色
    """
    try:
        await service.update_role(
            role_id=role_id,
            role_name=request.roleName,
            remarks=request.remarks or "",
            permissions=request.permissions
        )
        return {"message": "更新角色成功"}
    except ValueError as e:
        error_msg = str(e)
        if "角色不存在" in error_msg:
            raise UnifyException(
                get_error_message(ErrorCode.DATA_NOT_FOUND),
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)


@router.delete("/{role_id}", response_class=UnifyResponse)
async def delete_role(
    role_id: int,
    current_admin: dict = Depends(get_current_admin),
    service: RoleService = Depends(get_role_service)
):
    """
    删除角色
    """
    try:
        await service.delete_role(role_id)
        return {"message": "删除角色成功"}
    except ValueError as e:
        error_msg = str(e)
        if "角色不存在" in error_msg:
            raise UnifyException(
                get_error_message(ErrorCode.DATA_NOT_FOUND),
                biz_code=ErrorCode.DATA_NOT_FOUND,
                http_code=200
            )
        if "无法删除" in error_msg:
            raise UnifyException(
                error_msg,
                biz_code=ErrorCode.OPERATION_NOT_ALLOWED,
                http_code=200
            )
        raise UnifyException(error_msg, biz_code=ErrorCode.BAD_REQUEST, http_code=200)
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)


