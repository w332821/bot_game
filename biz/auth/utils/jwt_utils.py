"""
JWT工具函数
用于生成和验证JWT token
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import os
import logging

logger = logging.getLogger(__name__)

# 从环境变量读取配置
SECRET_KEY = os.getenv("JWT_SECRET", "default-secret-key-please-change-in-production")
ALGORITHM = "HS256"
EXPIRE_DAYS = int(os.getenv("JWT_EXPIRE_DAYS", "7"))  # 默认7天

# 如果使用默认密钥，输出警告
if SECRET_KEY == "default-secret-key-please-change-in-production":
    logger.warning("⚠️ 使用默认JWT_SECRET，生产环境请修改！")


def create_access_token(data: Dict) -> str:
    """
    生成JWT access token

    Args:
        data: 要编码到token中的数据，通常包含：
              - admin_id: 管理员ID
              - username: 用户名
              - role: 角色

    Returns:
        str: JWT token字符串

    Example:
        >>> token = create_access_token({
        ...     "admin_id": "admin_123",
        ...     "username": "admin",
        ...     "role": "super_admin"
        ... })
    """
    to_encode = data.copy()

    # 设置过期时间（7天后）
    expire = datetime.utcnow() + timedelta(days=EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()  # 签发时间
    })

    # 生成token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    logger.info(f"✅ 生成JWT token: {data.get('username')} (有效期{EXPIRE_DAYS}天)")

    return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
    """
    验证JWT token并返回payload

    Args:
        token: JWT token字符串

    Returns:
        Dict: token中的数据（如果有效）
        None: token无效或过期

    Example:
        >>> payload = verify_token(token)
        >>> if payload:
        ...     print(payload["admin_id"])
    """
    try:
        # 解码并验证token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("⚠️ JWT token已过期")
        return None

    except jwt.InvalidTokenError as e:
        logger.warning(f"⚠️ 无效的JWT token: {str(e)}")
        return None

    except Exception as e:
        logger.error(f"❌ JWT验证错误: {str(e)}")
        return None


def decode_token_unsafe(token: str) -> Optional[Dict]:
    """
    不验证直接解码token（仅用于调试）
    ⚠️ 不要在生产环境使用此函数进行认证！

    Args:
        token: JWT token字符串

    Returns:
        Dict: token中的数据（未验证）
        None: 解码失败
    """
    try:
        # 不验证签名和过期时间
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        logger.error(f"❌ 解码token失败: {str(e)}")
        return None
