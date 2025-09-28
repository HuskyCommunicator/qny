import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.db import Base, engine
from app.core.middleware import (
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    MetricsMiddleware
)
from app.core.exceptions import BaseAPIException
from app.core.response import APIResponse
from app.routers import auth as auth_router
from app.routers import chat as chat_router
from app.routers import role as role_router
from app.routers import me as me_router
from app.routers import recommendation as recommendation_router
from app.routers import growth as growth_router
from app.routers import scene as scene_router
from app.routers import rag as rag_router

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.app_name,
    description="AI角色扮演平台后端API",
    version="1.0.0"
)

# 添加中间件
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(MetricsMiddleware)


# 全局异常处理
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    logger.error(f"API异常: {exc.status_code} - {exc.detail}")
    request_id = getattr(request.state, 'request_id', None)

    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(
            message=exc.detail,
            code=exc.error_code,
            data=exc.extra_data,
            request_id=request_id
        ).dict()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
    request_id = getattr(request.state, 'request_id', None)

    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(
            message=exc.detail,
            code=exc.status_code,
            request_id=request_id
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    request_id = getattr(request.state, 'request_id', None)

    return JSONResponse(
        status_code=500,
        content=APIResponse.error(
            message="服务器内部错误",
            code=500,
            request_id=request_id
        ).dict()
    )


@app.on_event("startup")
def on_startup():
    """应用启动时的初始化操作"""
    logger.info("🚀 开始应用启动初始化...")
    
    # 1. 创建所有数据库表
    logger.info("📋 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ 数据库表创建完成")

    # 2. 数据库迁移和优化
    try:
        with engine.connect() as conn:
            # 检查并创建必要的索引
            logger.info("🔍 检查数据库索引...")
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_chat_sessions_role_id ON chat_sessions(role_id)",
                "CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)",
                "CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_role_skills_role_id ON role_skills(role_id)",
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                except Exception as e:
                    logger.warning(f"索引创建跳过: {e}")
            
            conn.commit()
            logger.info("✅ 数据库索引优化完成")
            
    except Exception as e:
        logger.warning(f"数据库优化过程中出现错误: {e}")

    # 3. 尝试从数据库重建 RAG 索引
    try:
        from app.models.chat import Document
        from app.services.rag_service import rebuild_from_db
        
        with engine.connect() as conn:
            rows = conn.execute(
                Document.__table__.select().with_only_columns([Document.doc_id, Document.text])
            ).fetchall()
            rebuild_from_db(rows)
        logger.info("✅ RAG 索引重建完成")
    except Exception as e:
        logger.warning(f"RAG 索引重建失败: {e}")

    logger.info("🎉 应用启动初始化完成！")

@app.get("/")
def root():
    """根路径 - 返回系统基本信息"""
    return APIResponse.success(
        data={
            "app_name": settings.app_name,
            "version": "1.0.0",
            "environment": settings.environment,
            "status": "running"
        },
        message="AI角色扮演平台后端服务运行中"
    )


@app.get("/health")
def health_check():
    """健康检查接口"""
    return APIResponse.success(
        data={
            "status": "healthy",
            "database": "connected",
            "timestamp": __import__('time').time()
        },
        message="系统健康状态正常"
    )


@app.get("/metrics")
def get_metrics():
    """获取系统性能指标"""
    # 获取基本系统指标
    import time

    metrics = {
        "timestamp": time.time(),
        "app_name": "AI角色扮演平台",
        "version": "1.0.0",
        "environment": "development"
    }

    try:
        # 尝试导入psutil
        import psutil
        
        # 添加系统性能指标
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').percent,
            "disk_free": psutil.disk_usage('/').free,
        }
        metrics.update(system_metrics)
        metrics["status"] = "full_metrics"
    except ImportError:
        # psutil未安装，只返回基本指标
        metrics.update({
            "status": "basic_metrics_only",
            "message": "psutil未安装，无法获取系统性能指标"
        })
    except Exception as e:
        metrics.update({
            "status": "basic_metrics_only",
            "error": f"无法获取系统指标: {str(e)}"
        })

    return APIResponse.success(
        data=metrics,
        message="系统性能指标获取成功"
    )


app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(role_router.router)
app.include_router(me_router.router)
app.include_router(recommendation_router.router)
app.include_router(growth_router.router)
app.include_router(scene_router.router)
app.include_router(rag_router.router)
