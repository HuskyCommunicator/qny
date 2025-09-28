"""
自定义异常类模块
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException
from app.core.constants import ResponseCode


class BaseAPIException(HTTPException):
    """基础API异常类"""

    def __init__(
        self,
        status_code: int,
        error_code: int,
        detail: str,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra_data = extra_data or {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code,
            "detail": self.detail,
            "extra_data": self.extra_data
        }


class ValidationError(BaseAPIException):
    """验证错误"""

    def __init__(self, detail: str = "数据验证失败", extra_data: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=ResponseCode.VALIDATION_ERROR.value,
            error_code=422001,
            detail=detail,
            extra_data=extra_data
        )


class AuthenticationError(BaseAPIException):
    """认证错误"""

    def __init__(self, detail: str = "认证失败", extra_data: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=ResponseCode.UNAUTHORIZED.value,
            error_code=401001,
            detail=detail,
            extra_data=extra_data
        )


class AuthorizationError(BaseAPIException):
    """授权错误"""

    def __init__(self, detail: str = "权限不足", extra_data: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=ResponseCode.FORBIDDEN.value,
            error_code=403001,
            detail=detail,
            extra_data=extra_data
        )


class NotFoundError(BaseAPIException):
    """资源未找到"""

    def __init__(self, detail: str = "资源未找到", extra_data: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=ResponseCode.NOT_FOUND.value,
            error_code=404001,
            detail=detail,
            extra_data=extra_data
        )


class BusinessLogicError(BaseAPIException):
    """业务逻辑错误"""

    def __init__(self, detail: str = "业务逻辑错误", extra_data: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=ResponseCode.BAD_REQUEST.value,
            error_code=400001,
            detail=detail,
            extra_data=extra_data
        )


class InternalServerError(BaseAPIException):
    """内部服务器错误"""

    def __init__(self, detail: str = "服务器内部错误", extra_data: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=ResponseCode.INTERNAL_ERROR.value,
            error_code=500001,
            detail=detail,
            extra_data=extra_data
        )


class RateLimitError(BaseAPIException):
    """限流错误"""

    def __init__(self, detail: str = "请求过于频繁", extra_data: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=ResponseCode.BAD_REQUEST.value,
            error_code=429001,
            detail=detail,
            extra_data=extra_data
        )