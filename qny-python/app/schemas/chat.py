from pydantic import BaseModel


class ChatRequest(BaseModel):
    role: str = "user"
    content: str


class ChatResponse(BaseModel):
    role: str = "assistant"
    content: str


