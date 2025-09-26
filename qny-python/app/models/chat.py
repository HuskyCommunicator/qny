from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, func
from sqlalchemy.orm import relationship

from ..core.db import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)  # 聊天会话唯一ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True, index=True)
    title = Column(String(200), nullable=True)  # 聊天会话标题
    is_active = Column(Boolean, default=True)  # 会话是否活跃
    session_metadata = Column(JSON, nullable=True)  # 会话元数据
    message_count = Column(Integer, default=0)  # 消息数量
    last_message_at = Column(DateTime(timezone=True), nullable=True)  # 最后消息时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联关系
    user = relationship("User", back_populates="chat_sessions")
    role = relationship("Role", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(session_id='{self.session_id}', title='{self.title}')>"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("chat_sessions.session_id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True, index=True)
    message_type = Column(String(32), nullable=False, default="text")  # text/audio/image
    content = Column(Text, nullable=False)
    is_user_message = Column(Boolean, nullable=False)  # 是否为用户消息
    message_metadata = Column(JSON, nullable=True)  # 消息元数据
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联关系
    user = relationship("User", back_populates="chat_messages")
    role = relationship("Role", back_populates="chat_messages")
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id='{self.session_id}')>"


