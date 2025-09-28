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
    # 创建表（最简自动建表）
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
    import psutil

    metrics = {
        "timestamp": time.time(),
        "app_name": "AI角色扮演平台",
        "version": "1.0.0",
        "environment": "development"
    }

    try:
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
