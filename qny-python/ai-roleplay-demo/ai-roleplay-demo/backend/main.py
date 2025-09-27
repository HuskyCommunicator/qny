from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import Base, engine
from app.routers import auth as auth_router
from app.routers import chat as chat_router
from app.routers import role as role_router
from app.routers import me as me_router
from app.routers import rag as rag_router
from app.services.rag_service import rebuild_from_db
from app.models.chat import Document
from app.utils.logger import trace_id_middleware_factory
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware


app = FastAPI(title=settings.app_name)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trace-Id 中间件
app.add_middleware(BaseHTTPMiddleware, dispatch=trace_id_middleware_factory)


@app.on_event("startup")
def on_startup():
    # 创建表（最简自动建表）
    Base.metadata.create_all(bind=engine)
    # 从 DB 重建 RAG 索引
    try:
        with engine.connect() as conn:
            rows = conn.execute(Document.__table__.select().with_only_columns([Document.doc_id, Document.text])).fetchall()
            rebuild_from_db(rows)
    except Exception:
        # 索引重建失败不影响启动
        pass


@app.get("/")
def root():
    return {"message": "AI Roleplay Backend Running"}


app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(role_router.router)
app.include_router(me_router.router)
app.include_router(rag_router.router)


@app.exception_handler(Exception)
async def unified_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", None)
    # 默认 500；FastAPI/HTTPException 会由框架处理，我们这里主要兜底
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": "服务器内部错误",
            "trace_id": trace_id,
        },
    )
