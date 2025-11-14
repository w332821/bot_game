import typing
from fastapi.responses import JSONResponse

class UnifyResponse(JSONResponse):
    def render(self, content: typing.Any) -> bytes:
        new_content = {
            "code": 200,
            "message": 'success',
            "data": content
        }
        return super().render(new_content)
