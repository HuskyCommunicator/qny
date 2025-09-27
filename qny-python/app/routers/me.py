from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..core.config import settings
from ..core.db import get_db
from ..models.user import User
from ..models.role import UserRole
from ..models.chat import ChatSession, ChatMessage
from ..schemas.user import UserOut
from ..schemas.role import UserRoleOut
from ..schemas.chat import (
    ChatHistoryRequest, ChatHistoryResponse,
    ChatSessionResponse, ChatMessageResponse
)
from ..services.chat_service import ChatService


router = APIRouter(prefix="", tags=["me"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效令牌",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.get("/me/agents", response_model=List[UserRoleOut])
def get_my_agents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的智能体列表"""
    user_roles = db.query(UserRole).filter(
        UserRole.user_id == current_user.id
    ).order_by(desc(UserRole.last_used_at)).all()

    return user_roles


@router.get("/me/chat-history", response_model=ChatHistoryResponse)
def get_chat_history(
    session_id: Optional[str] = Query(None),
    role_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取聊天历史记录"""
    request = ChatHistoryRequest(
        session_id=session_id,
        role_id=role_id,
        limit=limit,
        offset=offset
    )
    chat_service = ChatService(db)
    history = chat_service.get_chat_history(current_user.id, request)
    return ChatHistoryResponse(
        sessions=history["sessions"],
        messages=history["messages"],
        total=history["total"]
    )


@router.get("/me/sessions", response_model=List[ChatSessionResponse])
def get_my_sessions(
    role_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取我的聊天会话列表"""
    chat_service = ChatService(db)
    sessions = chat_service.get_user_sessions(current_user.id, role_id, limit, offset)
    return sessions


@router.get("/me/session/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_session_messages(
    session_id: str,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取指定会话的消息列表"""
    chat_service = ChatService(db)
    messages = chat_service.get_session_messages(session_id, current_user.id, limit, offset)
    return messages


@router.delete("/me/session/{session_id}")
def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除聊天会话"""
    chat_service = ChatService(db)
    success = chat_service.delete_session(session_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在或无权限删除")
    return {"message": "会话删除成功"}


@router.delete("/me/chat-history")
def clear_chat_history(
    session_id: Optional[str] = Query(None),
    role_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清除聊天历史记录"""
    if session_id:
        # 删除指定会话
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        if session:
            db.delete(session)
            db.commit()
        return {"message": "会话删除成功"}
    else:
        # 删除用户的所有会话
        if role_id:
            sessions = db.query(ChatSession).filter(
                ChatSession.user_id == current_user.id,
                ChatSession.role_id == role_id
            ).all()
        else:
            sessions = db.query(ChatSession).filter(
                ChatSession.user_id == current_user.id
            ).all()

        for session in sessions:
            db.delete(session)
        db.commit()
        return {"message": f"成功删除 {len(sessions)} 个会话"}


