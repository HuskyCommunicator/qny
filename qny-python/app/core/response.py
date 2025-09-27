"""
统一响应格式模块
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from app.core.constants import ResponseCode


class APIResponse(BaseModel):
    """统一API响应格式"""
    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: float = Field(..., description="响应时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")

    @classmethod
    def success(
        cls,
        data: Any = None,
        message: str = "操作成功",
        code: int = ResponseCode.SUCCESS.value,
        request_id: Optional[str] = None
    ) -> "APIResponse":
        """成功响应"""
        import time
        return cls(
            code=code,
            message=message,
            data=data,
            timestamp=time.time(),
            request_id=request_id
        )

    @classmethod
    def error(
        cls,
        message: str = "操作失败",
        code: int = ResponseCode.INTERNAL_ERROR.value,
        data: Any = None,
        request_id: Optional[str] = None
    ) -> "APIResponse":
        """错误响应"""
        import time
        return cls(
            code=code,
            message=message,
            data=data,
            timestamp=time.time(),
            request_id=request_id
        )


class PaginationResponse(BaseModel):
    """分页响应格式"""
    items: List[Any] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")

    @classmethod
    def create(
        cls,
        items: List[Any],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginationResponse":
        """创建分页响应"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


class PaginatedAPIResponse(APIResponse):
    """分页API响应格式"""
    data: Optional[PaginationResponse] = Field(None, description="分页数据")

    @classmethod
    def success(
        cls,
        items: List[Any],
        total: int,
        page: int,
        page_size: int,
        message: str = "查询成功",
        code: int = ResponseCode.SUCCESS.value,
        request_id: Optional[str] = None
    ) -> "PaginatedAPIResponse":
        """成功分页响应"""
        import time
        pagination_data = PaginationResponse.create(items, total, page, page_size)
        return cls(
            code=code,
            message=message,
            data=pagination_data,
            timestamp=time.time(),
            request_id=request_id
        )


class ValidationErrorResponse(BaseModel):
    """验证错误响应格式"""
    field: str = Field(..., description="错误字段")
    message: str = Field(..., description="错误消息")
    code: str = Field(..., description="错误代码")


class BatchOperationResponse(BaseModel):
    """批量操作响应格式"""
    success_count: int = Field(..., description="成功数量")
    failure_count: int = Field(..., description="失败数量")
    total_count: int = Field(..., description="总数量")
    success_items: List[Any] = Field(default_factory=list, description="成功项目")
    failure_items: List[Dict[str, Any]] = Field(default_factory=list, description="失败项目")


class FileUploadResponse(BaseModel):
    """文件上传响应格式"""
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    file_type: str = Field(..., description="文件类型")
    file_url: str = Field(..., description="文件访问URL")
    upload_time: float = Field(..., description="上传时间")