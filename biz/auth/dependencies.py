"""
FastAPI JWT认证依赖
用于保护需要登录的API端点
"""
from fastapi import Depends, HTTPException, Header
from typing import Optional, Dict, List
import logging

from .utils.jwt_utils import verify_token

logger = logging.getLogger(__name__)


async def get_current_admin(
    authorization: Optional[str] = Header(None)
) -> Dict:
    """
    获取当前登录的管理员（JWT验证）

    从HTTP Header中提取JWT token并验证
    Header格式: Authorization: Bearer <token>

    Args:
        authorization: HTTP Authorization header

    Returns:
        Dict: 管理员信息 {admin_id, username, role, ...}

    Raises:
        HTTPException(401): 认证失败

    Example:
        @router.get("/protected")
        async def protected_route(
            current_admin: dict = Depends(get_current_admin)
        ):
            admin_id = current_admin["admin_id"]
            username = current_admin["username"]
            ...
    """
    # 1. 检查是否提供了Authorization header
    if not authorization:
        logger.warning("⚠️ 缺少Authorization header")
        raise HTTPException(
            status_code=401,
            detail="请先登录"
        )

    # 2. 检查格式是否正确 (Bearer <token>)
    if not authorization.startswith("Bearer "):
        logger.warning("⚠️ Authorization格式错误")
        raise HTTPException(
            status_code=401,
            detail="认证格式错误，应为: Bearer <token>"
        )

    # 3. 提取token
    token = authorization.replace("Bearer ", "").strip()

    if not token:
        logger.warning("⚠️ Token为空")
        raise HTTPException(
            status_code=401,
            detail="认证信息为空"
        )

    # 4. 验证token
    payload = verify_token(token)

    if not payload:
        logger.warning("⚠️ Token验证失败")
        raise HTTPException(
            status_code=401,
            detail="登录已过期或认证无效，请重新登录"
        )

    # 5. 返回管理员信息
    logger.debug(f"✅ JWT验证成功: {payload.get('username')}")
    return payload


async def get_current_admin_optional(
    authorization: Optional[str] = Header(None)
) -> Optional[Dict]:
    """
    可选的JWT验证

    如果提供了token就验证，没有提供返回None
    不会抛出异常

    Args:
        authorization: HTTP Authorization header

    Returns:
        Dict: 管理员信息（如果token有效）
        None: 没有token或token无效

    Example:
        @router.get("/optional-auth")
        async def optional_auth_route(
            current_admin: Optional[dict] = Depends(get_current_admin_optional)
        ):
            if current_admin:
                # 已登录用户
                username = current_admin["username"]
            else:
                # 未登录用户
                username = "游客"
    """
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "").strip()

    if not token:
        return None

    payload = verify_token(token)

    return payload


def require_role(allowed_roles: List[str]):
    """
    创建角色验证依赖

    用于限制只有特定角色才能访问的端点

    Args:
        allowed_roles: 允许的角色列表

    Returns:
        依赖函数

    Example:
        @router.delete("/admin/{id}")
        async def delete_admin(
            id: str,
            current_admin: dict = Depends(get_current_admin),
            _: None = Depends(require_role(["super_admin"]))
        ):
            # 只有super_admin可以访问
            ...
    """
    async def check_role(
        current_admin: dict = Depends(get_current_admin)
    ):
        user_role = current_admin.get("role")

        if user_role not in allowed_roles:
            logger.warning(
                f"⚠️ 权限不足: {current_admin.get('username')} "
                f"(角色: {user_role}, 需要: {allowed_roles})"
            )
            raise HTTPException(
                status_code=403,
                detail=f"权限不足，需要角色: {', '.join(allowed_roles)}"
            )

        return None

    return check_role
