"""
统一错误码定义
根据 API_DOCS(3).md 和 DEV_PLAN.md 规范
"""


class ErrorCode:
    """错误码常量类"""

    # 基础错误码
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

    # 认证相关错误码 (1001-1099)
    ACCOUNT_OR_PASSWORD_ERROR = 1001
    ACCOUNT_DISABLED = 1003
    ACCOUNT_NOT_EXIST = 1004

    # 数据验证错误码 (2001-2099)
    ACCOUNT_ALREADY_EXISTS = 2001
    PASSWORD_FORMAT_ERROR = 2002
    INSUFFICIENT_BALANCE = 2003

    # 数据操作错误码 (3001-3099)
    DATA_NOT_FOUND = 3001
    DATA_DELETED = 3002


# 错误码消息映射
ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "操作成功",
    ErrorCode.BAD_REQUEST: "请求参数错误",
    ErrorCode.UNAUTHORIZED: "未授权，请重新登录",
    ErrorCode.FORBIDDEN: "无权限访问",
    ErrorCode.NOT_FOUND: "资源不存在",
    ErrorCode.INTERNAL_ERROR: "服务器内部错误",

    ErrorCode.ACCOUNT_OR_PASSWORD_ERROR: "账号或密码错误",
    ErrorCode.ACCOUNT_DISABLED: "账号已被禁用，请联系管理员",
    ErrorCode.ACCOUNT_NOT_EXIST: "账号不存在",

    ErrorCode.ACCOUNT_ALREADY_EXISTS: "账号已存在",
    ErrorCode.PASSWORD_FORMAT_ERROR: "密码格式不正确，需6-20位字符",
    ErrorCode.INSUFFICIENT_BALANCE: "余额不足",

    ErrorCode.DATA_NOT_FOUND: "数据不存在",
    ErrorCode.DATA_DELETED: "数据已被删除",
}


def get_error_message(code: int, default: str = "未知错误") -> str:
    """
    获取错误码对应的消息

    Args:
        code: 错误码
        default: 默认消息

    Returns:
        str: 错误消息
    """
    return ERROR_MESSAGES.get(code, default)


def get_http_status_code(error_code: int) -> int:
    """
    将自定义错误码映射到HTTP状态码

    Args:
        error_code: 自定义错误码

    Returns:
        int: 对应的HTTP状态码
    """
    # 基础HTTP状态码直接返回
    if error_code in [200, 400, 401, 403, 404, 500]:
        return error_code

    # 认证相关错误 (1001-1099) -> 401
    if 1001 <= error_code < 1100:
        if error_code == 1003:  # ACCOUNT_DISABLED -> 403
            return 403
        return 401

    # 数据验证错误 (2001-2099) -> 400
    if 2001 <= error_code < 2100:
        return 400

    # 数据操作错误 (3001-3099) -> 404
    if 3001 <= error_code < 3100:
        return 404

    # 默认返回500
    return 500
