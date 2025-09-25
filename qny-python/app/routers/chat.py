from typing import List

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..schemas.chat import ChatRequest, ChatResponse
from ..services.llm_service import generate_reply
from ..services.stt_service import transcribe_audio
from ..services.tts_service import synthesize_speech


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/text", response_model=ChatResponse)
def chat_text(payload: ChatRequest, db: Session = Depends(get_db)):
    messages: List[dict] = [{"role": payload.role, "content": payload.content}]
    reply = generate_reply(messages)
    return ChatResponse(role="assistant", content=reply)


@router.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    data = await file.read()
    text = transcribe_audio(data)
    return {"text": text}


@router.post("/tts")
def text_to_speech(payload: ChatRequest):
    audio_bytes = synthesize_speech(payload.content)
    return {"audio_base64": audio_bytes.decode("utf-8")}


