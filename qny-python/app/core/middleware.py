"""
中间件模块
"""
import time
import uuid
import json
from typing import Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.exceptions import RateLimitError
from app.utils.logger import get_logger
logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """请求ID中间件"""

    async def dispatch(self, request: Request, call_next):
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 添加到响应头
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # 记录请求信息
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        logger.info(
            f"请求开始: {request.method} {request.url} | "
            f"客户端IP: {client_ip} | "
            f"User-Agent: {user_agent}"
        )

        try:
            response = await call_next(request)

            # 记录响应信息
            process_time = time.time() - start_time
            logger.info(
                f"请求完成: {request.method} {request.url} | "
                f"状态码: {response.status_code} | "
                f"耗时: {process_time:.3f}s"
            )

            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as e:
            # 记录异常信息
            process_time = time.time() - start_time
            logger.error(
                f"请求异常: {request.method} {request.url} | "
                f"耗时: {process_time:.3f}s | "
                f"异常: {str(e)}"
            )
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件（简化版）"""

    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.request_records: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # 清理过期记录（1分钟前）
        if client_ip in self.request_records:
            self.request_records[client_ip] = [
                timestamp for timestamp in self.request_records[client_ip]
                if current_time - timestamp < 60
            ]

        # 检查限流
        if client_ip not in self.request_records:
            self.request_records[client_ip] = []

        if len(self.request_records[client_ip]) >= self.calls_per_minute:
            raise RateLimitError("请求过于频繁，请稍后再试")

        # 记录请求时间
        self.request_records[client_ip].append(current_time)

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 添加安全相关的HTTP头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 为API文档页面放宽CSP策略
        if request.url.path.startswith("/docs"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://cdn.jsdelivr.net; "
                "font-src 'self' data: https://cdn.jsdelivr.net;"
            )
        else:
            response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """性能指标中间件"""

    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.total_response_time = 0
        self.status_codes: Dict[int, int] = {}

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        try:
            response = await call_next(request)

            # 更新指标
            self.request_count += 1
            process_time = time.time() - start_time
            self.total_response_time += process_time

            # 统计状态码
            status_code = response.status_code
            self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1

            return response

        except Exception as e:
            self.request_count += 1
            process_time = time.time() - start_time
            self.total_response_time += process_time
            self.status_codes[500] = self.status_codes.get(500, 0) + 1
            raise

    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        avg_response_time = self.total_response_time / self.request_count if self.request_count > 0 else 0
        return {
            "total_requests": self.request_count,
            "avg_response_time": avg_response_time,
            "status_codes": self.status_codes
        }