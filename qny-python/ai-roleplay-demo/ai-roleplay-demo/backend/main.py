from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import Base, engine
from app.routers import auth as auth_router
from app.routers import chat as chat_router
from app.routers import role as role_router
from app.routers import me as me_router


app = FastAPI(title=settings.app_name)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # 创建表（最简自动建表）
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "AI Roleplay Backend Running"}


app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(role_router.router)
app.include_router(me_router.router)
