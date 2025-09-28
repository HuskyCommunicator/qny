from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class ChatRequest(BaseModel):
    role: str = "user"
    content: str
    session_id: Optional[str] = None
    role_id: Optional[int] = None


class ChatResponse(BaseModel):
    role: str = "assistant"
    content: str
    session_id: str


class TTSRequest(BaseModel):
    content: str
    voice: str = "longxiaochun"
    format: str = "mp3"


class ChatMessageCreate(BaseModel):
    session_id: str
    role_id: Optional[int] = None
    message_type: str = "text"
    content: str
    is_user_message: bool
    message_metadata: Optional[dict] = None


class ChatMessageResponse(BaseModel):
    id: int
    session_id: str
    role_id: Optional[int]
    message_type: str
    content: str
    is_user_message: bool
    message_metadata: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    role_id: Optional[int] = None
    title: Optional[str] = None
    session_metadata: Optional[dict] = None


class ChatSessionResponse(BaseModel):
    id: int
    session_id: str
    user_id: int
    role_id: Optional[int]
    title: Optional[str]
    is_active: bool
    session_metadata: Optional[dict]
    message_count: int
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ChatHistoryRequest(BaseModel):
    session_id: Optional[str] = None
    role_id: Optional[int] = None
    limit: int = 50
    offset: int = 0


class ChatHistoryResponse(BaseModel):
    sessions: List[ChatSessionResponse]
    messages: List[ChatMessageResponse]
    total: int