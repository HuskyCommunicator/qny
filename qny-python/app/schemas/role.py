from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, constr
from datetime import datetime
import re


class RoleCreate(BaseModel):
    """创建角色的请求数据"""
    name: constr(min_length=1, max_length=100) = Field(..., description="角色名称，长度1-100个字符")
    description: Optional[constr(max_length=500)] = Field(None, description="角色描述，最多500个字符")
    system_prompt: constr(min_length=5, max_length=2000) = Field(..., description="角色系统提示词，长度5-2000个字符")
    avatar_url: Optional[str] = Field(None, description="角色头像URL")
    is_public: bool = Field(True, description="是否为公开角色")
    config: Optional[Dict[str, Any]] = Field(None, description="角色配置参数")
    tags: Optional[List[constr(max_length=20)]] = Field(None, description="角色标签，每个标签最多20个字符")
    category: Optional[constr(max_length=50)] = Field(None, description="角色分类，最多50个字符")

    @validator('avatar_url')
    def validate_avatar_url(cls, v):
        if v is not None:
            # 简单的URL格式验证
            if not re.match(r'^https?://.+', v):
                raise ValueError('头像URL必须是有效的HTTP或HTTPS链接')
            if len(v) > 500:
                raise ValueError('头像URL长度不能超过500个字符')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('标签数量不能超过10个')
            for tag in v:
                if len(tag.strip()) == 0:
                    raise ValueError('标签不能为空')
        return v


class RoleUpdate(BaseModel):
    """更新角色的请求数据"""
    name: Optional[constr(min_length=1, max_length=100)] = Field(None, description="角色名称，长度1-100个字符")
    description: Optional[constr(max_length=500)] = Field(None, description="角色描述，最多500个字符")
    system_prompt: Optional[constr(min_length=5, max_length=2000)] = Field(None, description="角色系统提示词，长度5-2000个字符")
    avatar_url: Optional[str] = Field(None, description="角色头像URL")
    is_public: Optional[bool] = Field(None, description="是否为公开角色")
    config: Optional[Dict[str, Any]] = Field(None, description="角色配置参数")
    tags: Optional[List[constr(max_length=20)]] = Field(None, description="角色标签，每个标签最多20个字符")
    category: Optional[constr(max_length=50)] = Field(None, description="角色分类，最多50个字符")

    @validator('avatar_url')
    def validate_avatar_url(cls, v):
        if v is not None:
            if not re.match(r'^https?://.+', v):
                raise ValueError('头像URL必须是有效的HTTP或HTTPS链接')
            if len(v) > 500:
                raise ValueError('头像URL长度不能超过500个字符')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('标签数量不能超过10个')
            for tag in v:
                if len(tag.strip()) == 0:
                    raise ValueError('标签不能为空')
        return v


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
    role_id: int = Field(..., gt=0, description="角色ID必须大于0")
    custom_name: Optional[constr(max_length=100)] = Field(None, description="用户自定义角色名称，最多100个字符")
    custom_config: Optional[Dict[str, Any]] = Field(None, description="用户自定义配置")


class UserRoleUpdate(BaseModel):
    """更新用户角色关系的请求数据"""
    custom_name: Optional[constr(max_length=100)] = Field(None, description="用户自定义角色名称，最多100个字符")
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
    q: Optional[constr(max_length=100)] = Field(None, description="搜索关键词，最多100个字符")
    category: Optional[constr(max_length=50)] = Field(None, description="角色分类，最多50个字符")
    tags: Optional[List[constr(max_length=20)]] = Field(None, description="角色标签，每个标签最多20个字符")
    is_public: Optional[bool] = Field(True, description="是否公开")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")


class RoleInfo(BaseModel):
    """角色信息（用于搜索和展示）"""
    id: Optional[int] = Field(None, description="角色ID")
    name: str = Field(..., description="角色名称")
    display_name: Optional[str] = Field(None, description="显示名称")
    description: Optional[str] = Field(None, description="角色描述")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    skills: Optional[List[str]] = Field(None, description="技能列表")
    background: Optional[str] = Field(None, description="背景故事")
    personality: Optional[str] = Field(None, description="性格特点")
    is_builtin: bool = Field(False, description="是否为内置角色")
    category: Optional[str] = Field(None, description="角色分类")
    tags: Optional[List[str]] = Field(None, description="角色标签")
    is_public: Optional[bool] = Field(True, description="是否为公开角色")
    created_at: Optional[datetime] = Field(None, description="创建时间")


class RoleTemplateCreate(BaseModel):
    """创建角色模板的请求数据"""
    name: constr(min_length=1, max_length=100) = Field(..., description="角色名称")
    display_name: Optional[constr(max_length=128)] = Field(None, description="显示名称")
    description: Optional[constr(max_length=500)] = Field(None, description="角色描述")
    system_prompt: constr(min_length=5, max_length=2000) = Field(..., description="系统提示词")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    skills: Optional[str] = Field(None, description="技能列表（JSON字符串）")
    background: Optional[str] = Field(None, description="背景故事")
    personality: Optional[str] = Field(None, description="性格特点")
    category: Optional[constr(max_length=50)] = Field(None, description="角色分类")
    tags: Optional[List[constr(max_length=20)]] = Field(None, description="角色标签")


class RoleTemplateUpdate(BaseModel):
    """更新角色模板的请求数据"""
    display_name: Optional[constr(max_length=128)] = Field(None, description="显示名称")
    description: Optional[constr(max_length=500)] = Field(None, description="角色描述")
    system_prompt: Optional[constr(min_length=5, max_length=2000)] = Field(None, description="系统提示词")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    skills: Optional[str] = Field(None, description="技能列表（JSON字符串）")
    background: Optional[str] = Field(None, description="背景故事")
    personality: Optional[str] = Field(None, description="性格特点")
    category: Optional[constr(max_length=50)] = Field(None, description="角色分类")
    tags: Optional[List[constr(max_length=20)]] = Field(None, description="角色标签")


class RoleTemplateOut(BaseModel):
    """角色模板响应数据"""
    id: Optional[int] = None
    name: str
    display_name: Optional[str]
    description: Optional[str]
    system_prompt: str
    avatar_url: Optional[str]
    skills: Optional[str]
    background: Optional[str]
    personality: Optional[str]
    category: Optional[str]
    tags: Optional[List[str]]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoleTemplate(BaseModel):
    """角色模板"""
    id: Optional[int] = None
    name: constr(min_length=1, max_length=100) = Field(..., description="角色名称，长度1-100个字符")
    display_name: Optional[str] = Field(None, description="显示名称")
    description: constr(max_length=500) = Field(..., description="角色描述，最多500个字符")
    system_prompt: constr(min_length=5, max_length=2000) = Field(..., description="角色系统提示词，长度5-2000个字符")
    avatar_url: Optional[str] = None
    skills: Optional[str] = Field(None, description="技能列表")
    background: Optional[str] = Field(None, description="背景故事")
    personality: Optional[str] = Field(None, description="性格特点")
    config: Optional[Dict[str, Any]] = None
    tags: Optional[List[constr(max_length=20)]] = None
    category: Optional[constr(max_length=50)] = None
    created_at: Optional[datetime] = None

    @validator('avatar_url')
    def validate_avatar_url(cls, v):
        if v is not None:
            if not re.match(r'^https?://.+', v):
                raise ValueError('头像URL必须是有效的HTTP或HTTPS链接')
            if len(v) > 500:
                raise ValueError('头像URL长度不能超过500个字符')
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('标签数量不能超过10个')
            for tag in v:
                if len(tag.strip()) == 0:
                    raise ValueError('标签不能为空')
        return v