from typing import List
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.chat import (
    ChatRequest, ChatResponse, ChatSessionCreate,
    ChatMessageCreate, ChatHistoryRequest, ChatHistoryResponse,
    ChatSessionResponse, ChatMessageResponse, TTSRequest
)
from ..services.llm_service import generate_reply
from ..services.stt_service import transcribe_audio
from ..services.tts_service import synthesize_speech
from ..services.chat_service import ChatService
from ..services.growth_service import GrowthService


router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(db)


@router.post("/text", response_model=ChatResponse)
def chat_text(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """文本聊天接口，自动保存聊天历史"""
    try:
        user_id = current_user.id

        # 输入验证
        if not payload.content or not payload.content.strip():
            raise HTTPException(status_code=422, detail="消息内容不能为空")

        # 获取或创建会话
        session_id = payload.session_id
        if not session_id:
            # 创建新会话
            session_data = ChatSessionCreate(role_id=payload.role_id)
            session = chat_service.create_session(user_id, session_data)
            session_id = session.session_id
        else:
            # 验证会话是否存在
            session = chat_service.get_session(session_id, user_id)
            if not session:
                raise HTTPException(status_code=404, detail="会话不存在")

        # 保存用户消息
        user_message = ChatMessageCreate(
            session_id=session_id,
            role_id=payload.role_id,
            content=payload.content.strip(),
            is_user_message=True
        )
        chat_service.save_message(user_message, user_id)

        # 获取会话历史用于AI回复（限制上下文长度以提高性能）
        session_messages = chat_service.get_session_messages(session_id, user_id, limit=10)
        messages = []
        for msg in session_messages:
            role = "user" if msg.is_user_message else "assistant"
            messages.append({"role": role, "content": msg.content})

        # 生成AI回复（传入角色ID和数据库会话）
        reply = generate_reply(messages, payload.role_id, db)

        # 保存AI回复
        assistant_message = ChatMessageCreate(
            session_id=session_id,
            role_id=payload.role_id,
            content=reply,
            is_user_message=False
        )
        chat_service.save_message(assistant_message, user_id)

        # 记录对话并计算成长
        growth_service = GrowthService(db)
        growth_service.record_conversation(payload.role_id, user_id, session_id)

        return ChatResponse(role="assistant", content=reply, session_id=session_id)

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 记录错误日志
        import logging
        logging.error(f"聊天接口错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/session", response_model=ChatSessionResponse)
def create_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """创建新的聊天会话"""
    user_id = current_user.id
    session = chat_service.create_session(user_id, session_data)
    return session


@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_sessions(
    role_id: int = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """获取用户的聊天会话列表"""
    user_id = current_user.id
    sessions = chat_service.get_user_sessions(user_id, role_id, limit, offset)
    return sessions


@router.get("/session/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_session_messages(
    session_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """获取会话的消息列表"""
    try:
        user_id = current_user.id
        messages = chat_service.get_session_messages(session_id, user_id, limit, offset)
        return messages
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/history", response_model=ChatHistoryResponse)
def get_chat_history(
    request: ChatHistoryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """获取聊天历史"""
    user_id = current_user.id
    history = chat_service.get_chat_history(user_id, request)
    return ChatHistoryResponse(
        sessions=history["sessions"],
        messages=history["messages"],
        total=history["total"]
    )


@router.delete("/session/{session_id}")
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """删除聊天会话"""
    user_id = current_user.id
    success = chat_service.delete_session(session_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在或无权限删除")
    return {"message": "会话删除成功"}


@router.put("/session/{session_id}/title")
def update_session_title(
    session_id: str,
    title_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """更新会话标题"""
    title = title_data.get("title")
    if not title:
        raise HTTPException(status_code=422, detail="标题不能为空")

    user_id = current_user.id
    session = chat_service.update_session_title(session_id, user_id, title)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或无权限修改")
    return session


@router.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    """语音转文字"""
    data = await file.read()
    text = transcribe_audio(data)
    return {"text": text}


@router.post("/tts")
def text_to_speech(payload: TTSRequest):
    """文字转语音"""
    try:
        audio_bytes = synthesize_speech(payload.content, payload.voice, payload.format)
        if audio_bytes:
            import base64
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            return {"audio_base64": audio_base64, "format": payload.format}
        else:
            raise HTTPException(status_code=500, detail="语音合成失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音合成错误: {str(e)}")


