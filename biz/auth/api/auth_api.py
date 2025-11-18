"""
认证API路由
提供登录和登出接口
支持管理员、代理、会员三种账号类型登录
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from base.api import success_response, error_response
from base.error_codes import ErrorCode, get_error_message
from sqlalchemy import text
import bcrypt

from biz.admin.service.admin_service import AdminService
from biz.auth.utils.jwt_utils import create_access_token
from dependency_injector.wiring import inject, Provide
from biz.containers import Container
from base.session import async_session_factory

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
    统一登录接口（支持管理员/代理/会员）

    请求:
        - account: 账号（管理员username / 代理account / 会员account）
        - password: 密码

    响应:
        - code: 200 成功, 其他失败
        - message: 提示消息
        - data: 用户信息 { user: { id, account, userType }, token }
    """
    try:
        # 先尝试管理员登录
        result = await admin_service.login(request.account, request.password)

        if result.get('success'):
            # 管理员登录成功
            admin_data = result.get('admin', {})
            token = create_access_token({
                "admin_id": admin_data.get('id'),
                "username": admin_data.get('username'),
                "role": admin_data.get('role', 'admin')
            })

            return success_response(
                data={
                    "user": {
                        "id": admin_data.get('id'),
                        "account": admin_data.get('username'),
                        "userType": admin_data.get('role', 'admin')
                    },
                    "token": token
                },
                message="登录成功"
            )

        # 尝试代理/会员登录
        async with async_session_factory() as session:
            # 查询代理账号
            agent_query = text("""
                SELECT id, user_id, account, password
                FROM agent_profiles
                WHERE account = :account
                LIMIT 1
            """)
            result = await session.execute(agent_query, {"account": request.account})
            agent_row = result.fetchone()

            if agent_row and agent_row.password:
                # 验证代理密码
                if bcrypt.checkpw(request.password.encode('utf-8'), agent_row.password.encode('utf-8')):
                    token = create_access_token({
                        "user_id": agent_row.user_id,
                        "profile_id": agent_row.id,
                        "account": agent_row.account,
                        "role": "agent"
                    })

                    return success_response(
                        data={
                            "user": {
                                "id": agent_row.user_id,
                                "account": agent_row.account,
                                "userType": "agent"
                            },
                            "token": token
                        },
                        message="登录成功"
                    )

            # 查询会员账号
            member_query = text("""
                SELECT id, user_id, account, password
                FROM member_profiles
                WHERE account = :account
                LIMIT 1
            """)
            result = await session.execute(member_query, {"account": request.account})
            member_row = result.fetchone()

            if member_row and member_row.password:
                # 验证会员密码
                if bcrypt.checkpw(request.password.encode('utf-8'), member_row.password.encode('utf-8')):
                    token = create_access_token({
                        "user_id": member_row.user_id,
                        "profile_id": member_row.id,
                        "account": member_row.account,
                        "role": "member"
                    })

                    return success_response(
                        data={
                            "user": {
                                "id": member_row.user_id,
                                "account": member_row.account,
                                "userType": "member"
                            },
                            "token": token
                        },
                        message="登录成功"
                    )

        # 所有登录尝试失败
        return error_response(
            code=ErrorCode.ACCOUNT_OR_PASSWORD_ERROR,
            message="账号或密码错误",
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
