import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from base.exception import UnifyException

logger = logging.getLogger(__name__)


async def exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器
    捕获所有未处理的异常并返回统一的错误响应
    """
    request_id = getattr(request.state, "request_id", "unknown")

    # 处理自定义的统一异常
    if isinstance(exc, UnifyException):
        logger.warning(
            f"Business exception | ID: {request_id} | "
            f"Code: {exc.exception_biz_code} | Detail: {exc.exception_detail}"
        )
        return JSONResponse(
            status_code=exc.exception_http_code,
            content={
                "code": exc.exception_biz_code,
                "message": exc.exception_detail,
                "data": exc.exception_data or {}
            }
        )

    # 处理其他未预期的异常
    logger.error(
        f"Unhandled exception | ID: {request_id} | "
        f"Type: {type(exc).__name__} | Detail: {str(exc)}",
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "Internal server error",
            "data": {
                "request_id": request_id,
                "error_type": type(exc).__name__
            }
        }
    )
