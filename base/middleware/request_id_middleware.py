import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    为每个请求生成唯一的 Request ID，用于请求追踪和日志关联
    """

    async def dispatch(self, request: Request, call_next):
        # 从请求头获取或生成新的 request_id
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # 将 request_id 存储在请求状态中，方便后续使用
        request.state.request_id = request_id

        # 调用下一个中间件或路由处理器
        response: Response = await call_next(request)

        # 在响应头中返回 request_id
        response.headers["X-Request-ID"] = request_id

        return response
