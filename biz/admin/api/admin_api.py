"""
Admin API路由
对应admin-server.js中的管理员相关接口
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from pydantic import BaseModel, Field
import os
import jwt
from datetime import datetime, timedelta

from biz.admin.service.admin_service import AdminService
from biz.admin.models.model import AdminLogin, AdminCreate
from dependency_injector.wiring import inject, Provide
from biz.containers import Container

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ===== 请求/响应模型 =====

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    oldPassword: str = Field(..., description="原密码")
    newPassword: str = Field(..., description="新密码")


class UpdateStatusRequest(BaseModel):
    """更新状态请求"""
    status: str = Field(..., description="状态：active/inactive")


# ===== 依赖注入 =====

@inject
def get_admin_service(service: AdminService = Depends(Provide[Container.admin_service])) -> AdminService:
    return service


def get_current_admin_id(request: Request) -> str:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未认证")
    token = auth.split(" ", 1)[1]
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="认证配置缺失")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        admin_id = payload.get("sub") or payload.get("admin_id")
        if not admin_id:
            raise HTTPException(status_code=401, detail="令牌无效")
        return admin_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌过期")
    except Exception:
        raise HTTPException(status_code=401, detail="令牌无效")


# ===== API端点 =====

@router.post("/login")
async def login(
    request: AdminLogin,
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    管理员登录
    对应admin-server.js中的 POST /api/admin/login
    """
    result = await admin_service.login(request.username, request.password)
    if not result.get("success") or not result.get("admin"):
        return result
    admin = result["admin"]
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="认证配置缺失")
    now = datetime.utcnow()
    payload = {
        "sub": admin.get("id"),
        "role": admin.get("role"),
        "exp": now + timedelta(hours=8),
        "iat": now,
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return {"success": True, "admin": admin, "token": token}


@router.get("/info")
async def get_admin_info(
    admin_id: str = Depends(get_current_admin_id),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    获取当前登录管理员信息
    """
    try:
        admin = await admin_service.get_admin(admin_id)
        if not admin:
            return {"success": False, "error": "管理员不存在"}

        return {"success": True, "admin": admin}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/add")
async def create_admin(
    request: AdminCreate,
    admin_service: AdminService = Depends(get_admin_service),
    current_admin_id: str = Depends(get_current_admin_id)
):
    """
    创建管理员（需要超级管理员权限）
    """
    try:
        # TODO: 检查当前管理员是否有权限创建管理员

        result = await admin_service.create_admin(
            username=request.username,
            password=request.password,
            role=request.role,
            managed_chat_id=request.managed_chat_id,
            description=request.description
        )

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/{adminId}")
async def get_admin(
    adminId: str,
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    获取管理员信息
    """
    try:
        admin = await admin_service.get_admin(adminId)
        if not admin:
            return {"success": False, "error": "管理员不存在"}

        return {"success": True, "admin": admin}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{adminId}/password")
async def change_password(
    adminId: str,
    request: ChangePasswordRequest,
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    修改密码
    """
    result = await admin_service.update_password(
        admin_id=adminId,
        old_password=request.oldPassword,
        new_password=request.newPassword
    )
    return result


@router.post("/{adminId}/status")
async def update_status(
    adminId: str,
    request: UpdateStatusRequest,
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    更新管理员状态
    """
    try:
        admin = await admin_service.update_status(adminId, request.status)
        if not admin:
            return {"success": False, "error": "管理员不存在"}

        return {"success": True, "admin": admin}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.delete("/{adminId}")
async def delete_admin(
    adminId: str,
    admin_service: AdminService = Depends(get_admin_service),
    current_admin_id: str = Depends(get_current_admin_id)
):
    """
    删除管理员（需要超级管理员权限）
    """
    try:
        # TODO: 检查权限，不能删除自己

        if adminId == current_admin_id:
            return {"success": False, "error": "不能删除自己"}

        result = await admin_service.delete_admin(adminId)
        if not result:
            return {"success": False, "error": "管理员不存在或删除失败"}

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ===== 管理员列表API =====

@router.get("/admins")
async def get_all_admins(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    获取管理员列表
    支持按角色筛选
    """
    try:
        admins = await admin_service.get_all_admins(skip, limit, role)
        return {"success": True, "admins": admins, "total": len(admins)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/distributors/list")
async def get_distributors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    获取分销商列表
    """
    try:
        distributors = await admin_service.get_distributors(skip, limit)
        return {"success": True, "distributors": distributors, "total": len(distributors)}
    except Exception as e:
        return {"success": False, "error": str(e)}
