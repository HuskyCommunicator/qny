from typing import List, Generator
import json

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
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
    # 修复：正确解析历史对话，按 role 分组
    current_user_msg = ""
    current_assistant_msg = ""
    
    for msg in recent:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            current_user_msg = content
        elif role == "assistant":
            current_assistant_msg = content
            # 当有完整的 user-assistant 对时，添加到历史
            if current_user_msg and current_assistant_msg:
                history_pairs.append({
                    "user": current_user_msg, 
                    "assistant": current_assistant_msg
                })
                current_user_msg = ""
                current_assistant_msg = ""
    
    retrieved_docs = [text for _, text, _ in rag_hits]
    full_prompt = build_prompt(payload.role, payload.content, history_pairs, retrieved_docs)
    
    # 调试日志
    print(f"[DEBUG] Recent context: {len(recent)} messages")
    print(f"[DEBUG] History pairs: {len(history_pairs)} pairs")
    print(f"[DEBUG] First history pair: {history_pairs[0] if history_pairs else 'None'}")
    
    # 生成回复
    reply = generate_reply(
        messages=messages, 
        full_prompt=full_prompt,
        role=payload.role,
        user_message=payload.content,
        history=history_pairs,
        retrieved_docs=retrieved_docs
    )

    # 持久化到 MySQL
    db.add(ChatMessage(conversation_id=conversation.id, user_id=user_id, role="user", content=payload.content))
    db.add(ChatMessage(conversation_id=conversation.id, user_id=user_id, role="assistant", content=reply))
    db.commit()

    # 更新短期记忆
    append_turn(user_id, conversation.id, "user", payload.content)
    append_turn(user_id, conversation.id, "assistant", reply)

    return ChatResponse(role="assistant", content=reply, conversation_id=conversation.id)


@router.post("/text/stream")
def chat_text_stream(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """流式聊天接口 - 实时输出 LLM 回复"""
    # 获取或创建对话
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
    
    # RAG 检索
    rag_hits = rag.search(payload.content, top_k=3)
    rag_context = "\n\n".join([f"[DOC:{doc_id}] {text}" for doc_id, text, score in rag_hits])

    # 构建历史对话对
    history_pairs = []
    current_user_msg = ""
    current_assistant_msg = ""
    
    for msg in recent:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            current_user_msg = content
        elif role == "assistant":
            current_assistant_msg = content
            if current_user_msg and current_assistant_msg:
                history_pairs.append({
                    "user": current_user_msg, 
                    "assistant": current_assistant_msg
                })
                current_user_msg = ""
                current_assistant_msg = ""
    
    retrieved_docs = [text for _, text, _ in rag_hits]
    full_prompt = build_prompt(payload.role, payload.content, history_pairs, retrieved_docs)
    
    def generate_stream() -> Generator[str, None, None]:
        """生成流式响应"""
        full_reply = ""
        
        try:
            # 调用流式 LLM 生成
            for chunk in generate_reply_stream(
                messages=[{"role": "user", "content": payload.content}],
                full_prompt=full_prompt,
                role=payload.role,
                user_message=payload.content,
                history=history_pairs,
                retrieved_docs=retrieved_docs
            ):
                if chunk:
                    full_reply += chunk
                    # 发送 SSE 格式的数据
                    yield f"data: {json.dumps({'content': chunk, 'conversation_id': conversation.id}, ensure_ascii=False)}\n\n"
            
            # 发送结束标记
            yield f"data: {json.dumps({'done': True, 'conversation_id': conversation.id}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            # 发送错误信息
            yield f"data: {json.dumps({'error': str(e), 'conversation_id': conversation.id}, ensure_ascii=False)}\n\n"
            return
        
        # 保存完整对话到数据库
        try:
            db.add(ChatMessage(conversation_id=conversation.id, user_id=user_id, role="user", content=payload.content))
            db.add(ChatMessage(conversation_id=conversation.id, user_id=user_id, role="assistant", content=full_reply))
            db.commit()
            
            # 更新短期记忆
            append_turn(user_id, conversation.id, "user", payload.content)
            append_turn(user_id, conversation.id, "assistant", full_reply)
        except Exception as e:
            print(f"[ERROR] Failed to save conversation: {e}")

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


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


