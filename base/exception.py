from typing import Any, Optional, Dict
import json
from decimal import Decimal
from datetime import datetime, date

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


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


class UnifyException(HTTPException):
    exception_detail: Any
    exception_http_code: int
    exception_http_headers: Optional[Dict[str, Any]]
    exception_biz_code: int
    exception_kwargs: Optional[Dict[str, Any]]

    def __init__(self, detail: Any, biz_code, http_code: int,
                 http_header: Optional[Dict[str, Any]] = None):
        self.exception_detail = detail
        self.exception_biz_code = biz_code
        self.exception_http_code = http_code
        self.exception_kwargs = {}
        HTTPException.__init__(self, http_code, detail, http_header)

    def with_args(self, **kwargs) -> "UnifyException":
        for k, v in kwargs.items():
            # 对于 fields 字段，保持原始的 list/dict 格式，不转换为字符串
            if k == 'fields':
                self.exception_kwargs[k] = v
            else:
                self.exception_kwargs[k] = str(v)
        return self


async def unify_exception_handler(_: Request, exc: UnifyException):
    content = {
        'code': exc.exception_biz_code,
        'message': exc.exception_detail,
        'data': exc.exception_kwargs
    }
    # Use custom encoder for Decimal and datetime types
    return JSONResponse(
        status_code=exc.exception_http_code,
        content=json.loads(json.dumps(content, cls=DecimalEncoder))
    )


async def http_exception_handler(_: Request, exc: HTTPException):
    content = {
        'code': exc.status_code,
        'message': exc.detail,
        'data': {}
    }
    # Use custom encoder for consistency
    return JSONResponse(
        status_code=exc.status_code,
        content=json.loads(json.dumps(content, cls=DecimalEncoder))
    )
