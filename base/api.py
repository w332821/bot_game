import typing
import json
from fastapi.responses import JSONResponse
from base.json_encoder import DecimalEncoder


class UnifyResponse(JSONResponse):
    """
    统一的 API 响应类
    自动处理 Decimal、datetime 等类型的序列化
    """

    def render(self, content: typing.Any) -> bytes:
        new_content = {
            "code": 200,
            "message": 'success',
            "data": content
        }
        # Use custom encoder to handle Decimal and datetime types
        return json.dumps(
            new_content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=DecimalEncoder
        ).encode("utf-8")
