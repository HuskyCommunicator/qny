from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    role: str = "user"
    content: str


class ChatResponse(BaseModel):
    role: str = "assistant"
    content: str


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


