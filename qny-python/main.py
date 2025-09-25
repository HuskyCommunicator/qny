from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from database import get_db, engine
from models import Base, User, Agent, ChatMessage, ChatSession
from schemas import *
from auth import verify_password, create_access_token, get_current_user, SECRET_KEY, ALGORITHM
import crud
from utils import call_ai_service

load_dotenv()

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Roleplay Chat API",
    description="AI角色扮演聊天应用后端API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT认证
security = HTTPBearer()

# 配置
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

@app.get("/")
def read_root():
    return {"message": "AI Roleplay Backend Running"}

# 用户认证API
@app.post("/compare/v1/user/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )
    # 检查邮箱是否已存在
    if user.email and crud.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=400,
            detail="邮箱已存在"
        )
    return crud.create_user(db=db, user=user)

@app.post("/compare/v1/user/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    # 认证用户
    db_user = crud.authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email
        }
    }

@app.get("/compare/v1/user/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/compare/v1/user/profile", response_model=UserResponse)
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.update_user(db, current_user.id, user_update)

# AI角色管理API
@app.get("/compare/v1/agents/public", response_model=List[AgentResponse])
def get_public_agents(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_public_agents(db, skip=skip, limit=limit, category=category)

@app.get("/compare/v1/agents/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = crud.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="AI角色不存在")
    return agent

@app.get("/compare/v1/agents/my", response_model=List[AgentResponse])
def get_my_agents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_agents(db, current_user.id)

@app.post("/compare/v1/agents", response_model=AgentResponse)
def create_agent(
    agent: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_agent(db, agent, current_user.id)

@app.put("/compare/v1/agents/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: int,
    agent: AgentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_agent = crud.get_agent(db, agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="AI角色不存在")
    if db_agent.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改此AI角色")

    return crud.update_agent(db, agent_id, agent)

@app.delete("/compare/v1/agents/{agent_id}")
def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_agent = crud.get_agent(db, agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="AI角色不存在")
    if db_agent.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此AI角色")

    crud.delete_agent(db, agent_id)
    return {"message": "删除成功"}

# 聊天功能API
@app.get("/compare/v1/chat/sessions", response_model=List[ChatSessionResponse])
def get_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_sessions(db, current_user.id)

@app.post("/compare/v1/chat/sessions", response_model=ChatSessionResponse)
def create_chat_session(
    session: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_chat_session(db, session, current_user.id)

@app.get("/compare/v1/chat/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = crud.get_chat_session(db, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="会话不存在")

    return crud.get_session_messages(db, session_id)

@app.post("/compare/v1/chat/messages", response_model=ChatMessageResponse)
def send_message(
    message: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 验证会话权限
    session = crud.get_chat_session(db, message.session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 保存用户消息
    user_message = crud.create_chat_message(db, message, current_user.id)

    # 调用AI服务
    agent = crud.get_agent(db, session.agent_id)
    ai_response = call_ai_service(
        user_message=user_message.user_message,
        system_prompt=agent.system_prompt,
        agent_name=agent.name
    )

    # 保存AI回复
    ai_message_data = {
        "session_id": message.session_id,
        "user_message": "",
        "assistant_message": ai_response
    }
    ai_message = ChatMessageCreate(**ai_message_data)
    ai_message_saved = crud.create_chat_message(db, ai_message, current_user.id)

    return ai_message_saved

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
