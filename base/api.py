import typing
import json
from decimal import Decimal
from datetime import datetime, date
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


class UnifyResponse(JSONResponse):
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
