from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class RoleCreate(BaseModel):
    """创建角色的请求数据"""
    name: str = Field(..., min_length=1, max_length=100, description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
    system_prompt: str = Field(..., min_length=1, description="角色系统提示词")
    avatar_url: Optional[str] = Field(None, description="角色头像URL")
    is_public: bool = Field(True, description="是否为公开角色")
    config: Optional[Dict[str, Any]] = Field(None, description="角色配置参数")
    tags: Optional[List[str]] = Field(None, description="角色标签")
    category: Optional[str] = Field(None, max_length=50, description="角色分类")


class RoleUpdate(BaseModel):
    """更新角色的请求数据"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
    system_prompt: Optional[str] = Field(None, min_length=1, description="角色系统提示词")
    avatar_url: Optional[str] = Field(None, description="角色头像URL")
    is_public: Optional[bool] = Field(None, description="是否为公开角色")
    config: Optional[Dict[str, Any]] = Field(None, description="角色配置参数")
    tags: Optional[List[str]] = Field(None, description="角色标签")
    category: Optional[str] = Field(None, max_length=50, description="角色分类")


class RoleOut(BaseModel):
    """角色响应数据"""
    id: int
    name: str
    description: Optional[str]
    system_prompt: str
    avatar_url: Optional[str]
    is_public: bool
    is_active: bool
    created_by: Optional[int]
    config: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    category: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RoleList(BaseModel):
    """角色列表响应数据"""
    roles: List[RoleOut]
    total: int
    page: int
    size: int


class UserRoleCreate(BaseModel):
    """用户添加角色的请求数据"""
    role_id: int
    custom_name: Optional[str] = Field(None, max_length=100, description="用户自定义角色名称")
    custom_config: Optional[Dict[str, Any]] = Field(None, description="用户自定义配置")


class UserRoleUpdate(BaseModel):
    """更新用户角色关系的请求数据"""
    custom_name: Optional[str] = Field(None, max_length=100, description="用户自定义角色名称")
    custom_config: Optional[Dict[str, Any]] = Field(None, description="用户自定义配置")
    is_favorite: Optional[bool] = Field(None, description="是否收藏")


class UserRoleOut(BaseModel):
    """用户角色关系响应数据"""
    id: int
    user_id: int
    role_id: int
    role: RoleOut
    is_favorite: bool
    custom_name: Optional[str]
    custom_config: Optional[Dict[str, Any]]
    usage_count: int
    last_used_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class RoleSearchParams(BaseModel):
    """角色搜索参数"""
    q: Optional[str] = Field(None, description="搜索关键词")
    category: Optional[str] = Field(None, description="角色分类")
    tags: Optional[List[str]] = Field(None, description="角色标签")
    is_public: Optional[bool] = Field(True, description="是否公开")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")


class RoleTemplate(BaseModel):
    """角色模板"""
    name: str
    description: str
    system_prompt: str
    avatar_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None