from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models.models import User, Agent, ChatMessage, ChatSession
from ..schemas.auth import UserCreate
from ..schemas.user import UserUpdate
from ..schemas.role import AgentCreate, AgentUpdate
from ..schemas.chat import ChatSessionCreate, ChatMessageCreate
from ..core.security import get_password_hash
from datetime import datetime
import uuid

# 用户相关操作
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.dict(exclude_unset=True)
    if 'password' in update_data:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user

# AI角色相关操作
def get_agent(db: Session, agent_id: int):
    return db.query(Agent).filter(Agent.id == agent_id).first()

def get_public_agents(db: Session, skip: int = 0, limit: int = 20, category: str = None):
    query = db.query(Agent).filter(Agent.is_public == True)
    if category:
        query = query.filter(Agent.category == category)
    return query.offset(skip).limit(limit).all()

def get_user_agents(db: Session, user_id: int):
    return db.query(Agent).filter(Agent.creator_id == user_id).all()

def create_agent(db: Session, agent: AgentCreate, creator_id: int):
    db_agent = Agent(
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        avatar_url=agent.avatar_url,
        is_public=agent.is_public,
        category=agent.category,
        creator_id=creator_id
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def update_agent(db: Session, agent_id: int, agent_update: AgentUpdate):
    db_agent = get_agent(db, agent_id)
    if not db_agent:
        return None

    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_agent, field, value)

    db_agent.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_agent)
    return db_agent

def delete_agent(db: Session, agent_id: int):
    db_agent = get_agent(db, agent_id)
    if db_agent:
        db.delete(db_agent)
        db.commit()
    return True

# 聊天会话相关操作
def get_chat_session(db: Session, session_id: int):
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()

def get_user_sessions(db: Session, user_id: int):
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

def create_chat_session(db: Session, session: ChatSessionCreate, user_id: int):
    # 生成唯一会话ID
    session_id = str(uuid.uuid4())

    db_session = ChatSession(
        session_id=session_id,
        user_id=user_id,
        agent_id=session.agent_id,
        title=session.title or f"与{session.agent_id}的对话"
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

# 聊天消息相关操作
def get_session_messages(db: Session, session_id: int):
    return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at).all()

def create_chat_message(db: Session, message: ChatMessageCreate, user_id: int):
    # 获取会话信息以获取agent_id
    session = get_chat_session(db, message.session_id)
    if not session:
        return None

    db_message = ChatMessage(
        session_id=message.session_id,
        user_id=user_id,
        agent_id=session.agent_id,
        user_message=message.user_message,
        assistant_message=message.assistant_message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_last_message(db: Session, session_id: int):
    return db.query(ChatMessage).filter(ChatSession.id == session_id).order_by(ChatMessage.created_at.desc()).first()

# 工具函数（从auth模块导入）
def verify_password(plain_password: str, hashed_password: str) -> bool:
    from auth import pwd_context
    return pwd_context.verify(plain_password, hashed_password)