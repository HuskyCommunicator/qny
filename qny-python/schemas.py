from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# 用户相关模型
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Token模型
class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

# AI角色相关模型
class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: str
    avatar_url: Optional[str] = None
    is_public: bool = True
    category: str = "general"

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    avatar_url: Optional[str] = None
    is_public: Optional[bool] = None
    category: Optional[str] = None

class AgentResponse(AgentBase):
    id: int
    creator_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 聊天会话相关模型
class ChatSessionBase(BaseModel):
    session_id: str
    agent_id: int
    title: Optional[str] = None

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None

class ChatSessionResponse(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

# 聊天消息相关模型
class ChatMessageBase(BaseModel):
    session_id: int
    user_message: str
    assistant_message: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    user_id: int
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 通用响应模型
class MessageResponse(BaseModel):
    message: str
    success: bool = True