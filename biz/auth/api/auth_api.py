"""
认证API路由
提供登录和登出接口
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from base.api import success_response, error_response
from base.error_codes import ErrorCode, get_error_message

from biz.admin.service.admin_service import AdminService
from dependency_injector.wiring import inject, Provide
from biz.containers import Container

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ===== 请求模型 =====

class LoginRequest(BaseModel):
    """登录请求"""
    account: str = Field(..., description="管理员账号")
    password: str = Field(..., description="密码")


# ===== 依赖注入 =====

@inject
def get_admin_service(service: AdminService = Depends(Provide[Container.admin_service])) -> AdminService:
    return service


# ===== API端点 =====

@router.post("/login")
async def login(
    request: LoginRequest,
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    管理员登录

    请求:
        - account: 管理员账号
        - password: 密码

    响应:
        - code: 200 成功, 其他失败
        - message: 提示消息
        - data: 用户信息 { user: { id, account, userType } }
    """
    try:
        result = await admin_service.login(request.account, request.password)

        if result.get('success'):
            # 登录成功,返回用户信息
            admin_data = result.get('admin', {})
            return success_response(
                data={
                    "user": {
                        "id": admin_data.get('id'),
                        "account": admin_data.get('username'),
                        "userType": admin_data.get('role', 'admin')
                    }
                },
                message="登录成功"
            )
        else:
            # 登录失败
            error = result.get('error', '登录失败')
            return error_response(
                code=ErrorCode.ACCOUNT_OR_PASSWORD_ERROR,
                message=error,
                data=None
            )
    except Exception as e:
        return error_response(
            code=ErrorCode.INTERNAL_ERROR,
            message=f"登录失败: {str(e)}",
            data=None
        )


@router.post("/logout")
async def logout():
    """
    管理员登出

    对于无状态JWT系统,登出在前端清除token即可
    后端返回成功响应

    响应:
        - code: 200
        - message: "退出成功"
        - data: null
    """
    return success_response(
        data=None,
        message="退出成功"
    )
