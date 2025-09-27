from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, func
from sqlalchemy.orm import relationship

from ..core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    full_name = Column(String(128), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(String(500), nullable=True)
    preferences = Column(JSON, nullable=True)  # 用户偏好设置
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联关系
    created_roles = relationship("Role", back_populates="creator")
    user_roles = relationship("UserRole", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")


