import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    记录每个 HTTP 请求的详细信息和响应时间
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # 获取请求信息
        request_id = getattr(request.state, "request_id", "unknown")
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"

        # 记录请求开始
        logger.info(
            f"Request started | ID: {request_id} | Method: {method} | "
            f"URL: {url} | Client: {client_host}"
        )

        # 处理请求
        try:
            response: Response = await call_next(request)

            # 计算响应时间
            process_time = time.time() - start_time

            # 记录请求完成
            logger.info(
                f"Request completed | ID: {request_id} | Method: {method} | "
                f"URL: {url} | Status: {response.status_code} | "
                f"Duration: {process_time:.3f}s"
            )

            # 添加响应时间头
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # 计算错误发生时的响应时间
            process_time = time.time() - start_time

            # 记录请求错误
            logger.error(
                f"Request failed | ID: {request_id} | Method: {method} | "
                f"URL: {url} | Error: {str(e)} | Duration: {process_time:.3f}s",
                exc_info=True
            )

            raise
