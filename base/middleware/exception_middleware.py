import logging
import json
from decimal import Decimal
from datetime import datetime, date
from fastapi import Request, status
from fastapi.responses import JSONResponse
from base.exception import UnifyException

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Decimal, datetime, and date types"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            # Convert Decimal to float for JSON serialization
            return float(obj)
        elif isinstance(obj, (datetime, date)):
            # Convert datetime/date to ISO format string
            return obj.isoformat()
        return super().default(obj)


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
        content = {
            "code": exc.exception_biz_code,
            "message": exc.exception_detail,
            "data": exc.exception_kwargs or {}
        }
        return JSONResponse(
            status_code=exc.exception_http_code,
            content=json.loads(json.dumps(content, cls=DecimalEncoder))
        )

    # 处理其他未预期的异常
    logger.error(
        f"Unhandled exception | ID: {request_id} | "
        f"Type: {type(exc).__name__} | Detail: {str(exc)}",
        exc_info=True
    )

    content = {
        "code": 500,
        "message": "Internal server error",
        "data": {
            "request_id": request_id,
            "error_type": type(exc).__name__
        }
    }
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=json.loads(json.dumps(content, cls=DecimalEncoder))
    )
