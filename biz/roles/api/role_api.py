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


@router.get("/permissions", response_class=UnifyResponse)
async def get_permissions_tree(
    current_admin: dict = Depends(get_current_admin),
    service: RoleService = Depends(get_role_service)
):
    """
    获取权限树(所有可用权限的树形结构)
    """
    try:
        tree = service.get_permissions_tree()
        return {"tree": tree}
    except Exception as e:
        raise UnifyException(str(e), biz_code=ErrorCode.INTERNAL_ERROR, http_code=500)
