from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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