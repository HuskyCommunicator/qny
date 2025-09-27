from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.db import Base, engine
from app.models.chat import Document
from app.routers import auth as auth_router
from app.routers import chat as chat_router
from app.routers import role as role_router
from app.routers import me as me_router
from app.routers import rag as rag_router
from app.services.rag_service import rebuild_from_db
from app.utils.logger import trace_id_middleware_factory

# 初始化 FastAPI
app = FastAPI(title=settings.app_name)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trace-ID 中间件
app.add_middleware(BaseHTTPMiddleware, dispatch=trace_id_middleware_factory())


@app.on_event("startup")
def on_startup():
    # 自动创建数据库表
    Base.metadata.create_all(bind=engine)

    # 数据库迁移：为 role_templates 表添加新字段
    try:
        with engine.connect() as conn:
            # 检查表是否存在
            result = conn.execute(text("SHOW TABLES LIKE 'role_templates'"))
            if result.fetchone():
                # 检查字段是否已存在
                result = conn.execute(text("SHOW COLUMNS FROM role_templates LIKE 'display_name'"))
                if not result.fetchone():
                    print("[MIGRATION] 开始添加新字段到 role_templates 表...")
                    migrations = [
                        "ALTER TABLE role_templates ADD COLUMN display_name VARCHAR(128) NULL",
                        "ALTER TABLE role_templates ADD COLUMN description TEXT NULL",
                        "ALTER TABLE role_templates ADD COLUMN avatar_url VARCHAR(512) NULL",
                        "ALTER TABLE role_templates ADD COLUMN skills TEXT NULL",
                        "ALTER TABLE role_templates ADD COLUMN background TEXT NULL",
                        "ALTER TABLE role_templates ADD COLUMN personality TEXT NULL",
                    ]
                    
                    for migration in migrations:
                        try:
                            conn.execute(text(migration))
                            print(f"[MIGRATION] ✓ {migration}")
                        except Exception as e:
                            print(f"[MIGRATION] ✗ {migration} - {e}")
                    
                    conn.commit()
                    print("[MIGRATION] 数据库迁移完成！")
    except Exception as e:
        print(f"[MIGRATION] 迁移失败: {e}")

    # 尝试从数据库重建 RAG 索引
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                Document.__table__.select().with_only_columns([Document.doc_id, Document.text])
            ).fetchall()
            rebuild_from_db(rows)
    except Exception as e:
        # 索引重建失败不影响启动
        from app.utils.logger import get_logger
        logger = get_logger("startup")
        logger.warning(f"RAG 索引重建失败: {e}")


# 根路径测试
@app.get("/")
def root():
    return {"message": "AI Roleplay Backend Running"}


# 注册路由
app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(role_router.router)
app.include_router(me_router.router)
app.include_router(rag_router.router)


# 统一异常处理
@app.exception_handler(Exception)
async def unified_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", None)
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": "服务器内部错误",
            "trace_id": trace_id,
        },
    )
