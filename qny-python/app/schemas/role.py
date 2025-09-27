from pydantic import BaseModel
from typing import List, Optional


class RoleInfo(BaseModel):
    """角色信息响应模型"""
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: Optional[List[str]] = None
    background: Optional[str] = None
    personality: Optional[str] = None
    is_builtin: bool = True  # 是否为内置角色


class RoleTemplateCreate(BaseModel):
    """创建角色模板请求模型"""
    name: str
    prompt: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: Optional[List[str]] = None
    background: Optional[str] = None
    personality: Optional[str] = None


class RoleTemplateUpdate(BaseModel):
    """更新角色模板请求模型"""
    prompt: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: Optional[List[str]] = None
    background: Optional[str] = None
    personality: Optional[str] = None


class RoleTemplateOut(BaseModel):
    """角色模板响应模型"""
    id: int
    name: str
    prompt: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: Optional[List[str]] = None
    background: Optional[str] = None
    personality: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True
