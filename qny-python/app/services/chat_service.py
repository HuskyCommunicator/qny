from typing import List, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from ..models.chat import ChatSession, ChatMessage
from ..schemas.chat import ChatSessionCreate, ChatMessageCreate, ChatHistoryRequest
from ..core.security import get_current_user


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: int, session_data: ChatSessionCreate) -> ChatSession:
        """创建新的聊天会话"""
        try:
            session_id = str(uuid.uuid4())

            # 如果没有提供标题，使用角色名称或默认标题
            title = session_data.title
            if not title and session_data.role_id:
                from ..models.role import Role
                role = self.db.query(Role).filter(Role.id == session_data.role_id).first()
                if role:
                    title = f"与{role.name}的对话"

            if not title:
                title = f"新对话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

            db_session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                role_id=session_data.role_id,
                title=title,
                session_metadata=session_data.session_metadata or {}
            )

            self.db.add(db_session)
            self.db.commit()
            self.db.refresh(db_session)
            return db_session
        except Exception as e:
            self.db.rollback()
            raise e

    def get_session(self, session_id: str, user_id: int) -> Optional[ChatSession]:
        """获取聊天会话"""
        return self.db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == user_id
        ).first()

    def get_user_sessions(self, user_id: int, role_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[ChatSession]:
        """获取用户的聊天会话列表"""
        query = self.db.query(ChatSession).filter(ChatSession.user_id == user_id)

        if role_id:
            query = query.filter(ChatSession.role_id == role_id)

        return query.order_by(ChatSession.updated_at.desc()).offset(offset).limit(limit).all()

    def save_message(self, message_data: ChatMessageCreate, user_id: int) -> ChatMessage:
        """保存聊天消息"""
        # 验证会话是否存在且属于该用户
        session = self.get_session(message_data.session_id, user_id)
        if not session:
            raise ValueError("会话不存在或无权限访问")

        db_message = ChatMessage(
            session_id=message_data.session_id,
            user_id=user_id,
            role_id=message_data.role_id,
            message_type=message_data.message_type,
            content=message_data.content,
            is_user_message=message_data.is_user_message,
            message_metadata=message_data.message_metadata or {}
        )

        self.db.add(db_message)

        # 更新会话信息
        session.message_count += 1
        session.last_message_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    def get_session_messages(self, session_id: str, user_id: int, limit: int = 100, offset: int = 0) -> List[ChatMessage]:
        """获取会话的消息列表"""
        # 验证会话权限
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("会话不存在或无权限访问")

        return self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.asc()).offset(offset).limit(limit).all()

    def get_chat_history(self, user_id: int, request: ChatHistoryRequest) -> dict:
        """获取聊天历史"""
        sessions = []
        messages = []
        total = 0

        if request.session_id:
            # 获取特定会话的消息
            session = self.get_session(request.session_id, user_id)
            if session:
                sessions = [session]
                messages = self.get_session_messages(request.session_id, user_id, request.limit, request.offset)
                total = self.db.query(ChatMessage).filter(
                    ChatMessage.session_id == request.session_id
                ).count()
        else:
            # 获取用户的会话列表
            sessions = self.get_user_sessions(user_id, request.role_id, request.limit, request.offset)

            # 获取最近的消息用于预览
            if sessions:
                # 获取所有会话的session_id
                session_ids = [s.session_id for s in sessions]

                # 获取最近的消息（按时间排序）
                messages = self.db.query(ChatMessage).filter(
                    ChatMessage.session_id.in_(session_ids),
                    ChatMessage.user_id == user_id
                ).order_by(ChatMessage.created_at.desc()).limit(request.limit).offset(request.offset).all()

                # 反转顺序，让最新的消息在后面
                messages = list(reversed(messages))

            # 计算总数
            if request.role_id:
                total = self.db.query(ChatSession).filter(
                    ChatSession.user_id == user_id,
                    ChatSession.role_id == request.role_id
                ).count()
            else:
                total = self.db.query(ChatSession).filter(ChatSession.user_id == user_id).count()

        return {
            "sessions": sessions,
            "messages": messages,
            "total": total
        }

    def delete_session(self, session_id: str, user_id: int) -> bool:
        """删除聊天会话"""
        session = self.get_session(session_id, user_id)
        if not session:
            return False

        self.db.delete(session)
        self.db.commit()
        return True

    def update_session_title(self, session_id: str, user_id: int, title: str) -> Optional[ChatSession]:
        """更新会话标题"""
        session = self.get_session(session_id, user_id)
        if not session:
            return None

        session.title = title
        session.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(session)
        return session