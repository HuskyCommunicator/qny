from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..schemas.chat import ChatRequest, ChatResponse
from ..services.llm_service import generate_reply
from ..services.stt_service import transcribe_audio
from ..services.tts_service import synthesize_speech
from ..services.memory_service import get_recent_context, append_turn, clear_context
from ..services.rag_service import rag
from ..models.chat import Conversation, ChatMessage
from ..models.user import User
from ..core.config import settings
from ..core.security import get_current_user
from prompt_templates import build_prompt


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/text", response_model=ChatResponse)
def chat_text(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 简化：此处从请求体/外层中获取 user_id，生产中建议从 token 解出
    # 若没有 conversation 则创建
    conversation = None
    if payload.conversation_id:
        conversation = db.query(Conversation).filter(Conversation.id == payload.conversation_id).first()
    if conversation is None:
        conversation = Conversation(user_id=current_user.id, role=payload.role, title=None)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    user_id = current_user.id
    recent = get_recent_context(user_id, conversation.id, limit=10)
    # RAG 检索（可配置 Top-K）
    rag_hits = rag.search(payload.content, top_k=3)
    rag_context = "\n\n".join([f"[DOC:{doc_id}] {text}" for doc_id, text, score in rag_hits])

    messages: List[dict] = recent + [{"role": "user", "content": payload.content}]
    # 将 Redis 历史转为 build_prompt 期望的结构
    history_pairs = []
    for i in range(0, len(recent), 2):
        user_turn = recent[i].get("content", "") if i < len(recent) else ""
        assistant_turn = recent[i + 1].get("content", "") if i + 1 < len(recent) else ""
        history_pairs.append({"user": user_turn, "assistant": assistant_turn})
    retrieved_docs = [text for _, text, _ in rag_hits]
    full_prompt = build_prompt(payload.role, payload.content, history_pairs, retrieved_docs)
    # 生成回复
    reply = generate_reply(messages, full_prompt=full_prompt)

    # 持久化到 MySQL
    db.add(ChatMessage(conversation_id=conversation.id, user_id=user_id, role="user", content=payload.content))
    db.add(ChatMessage(conversation_id=conversation.id, user_id=user_id, role="assistant", content=reply))
    db.commit()

    # 更新短期记忆
    append_turn(user_id, conversation.id, "user", payload.content)
    append_turn(user_id, conversation.id, "assistant", reply)

    return ChatResponse(role="assistant", content=reply, conversation_id=conversation.id)


@router.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    data = await file.read()
    text = transcribe_audio(data)
    return {"text": text}


@router.post("/tts")
def text_to_speech(payload: ChatRequest):
    audio_bytes = synthesize_speech(payload.content)
    return {"audio_base64": audio_bytes.decode("utf-8")}


@router.post("/clear")
def clear_conversation(payload: ChatRequest, current_user: User = Depends(get_current_user)):
    if payload.conversation_id is not None:
        clear_context(current_user.id, payload.conversation_id)
    return {"ok": True}


