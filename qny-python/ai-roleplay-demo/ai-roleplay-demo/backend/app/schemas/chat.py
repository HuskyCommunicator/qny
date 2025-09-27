from pydantic import BaseModel


class ChatRequest(BaseModel):
    role: str
    content: str
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    role: str = "assistant"
    content: str
    conversation_id: int


