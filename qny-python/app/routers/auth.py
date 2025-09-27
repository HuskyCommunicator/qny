from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import time

from ..core.db import get_db
from ..core.security import create_access_token, verify_password, get_password_hash
from ..models.user import User
from ..schemas.user import UserCreate
from ..core.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])

# 简单内存失败计数（生产建议使用 Redis 等）
_FAILED_LOGIN: dict[str, dict] = {}


def _is_locked(username: str) -> bool:
    meta = _FAILED_LOGIN.get(username)
    if not meta:
        return False
    locked_until: datetime | None = meta.get("lock_until")
    return bool(locked_until and locked_until > datetime.utcnow())


def _register_failure(username: str) -> None:
    meta = _FAILED_LOGIN.get(username) or {"count": 0, "lock_until": None}
    meta["count"] = int(meta.get("count", 0)) + 1
    if meta["count"] >= settings.login_max_attempts:
        meta["lock_until"] = datetime.utcnow() + timedelta(minutes=settings.login_lockout_minutes)
        meta["count"] = 0
    _FAILED_LOGIN[username] = meta


def _reset_failure(username: str) -> None:
    if username in _FAILED_LOGIN:
        _FAILED_LOGIN.pop(username, None)


@router.post("/register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existed = db.query(User).filter((User.username == payload.username) | (User.email == payload.email)).first()
    if existed:
        return {"code": 400, "msg": "用户名或邮箱已存在", "data": None}
    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_out = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "full_name": user.full_name,
    }
    return {"code": 200, "msg": "注册成功", "data": user_out}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 防止暴力枚举：固定延迟
    if settings.login_delay_ms > 0:
        time.sleep(settings.login_delay_ms / 1000.0)

    # 检查锁定状态
    if _is_locked(form_data.username):
        return {"code": 429, "msg": "账号暂时锁定，请稍后再试", "data": None}

    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        _register_failure(form_data.username)
        return {"code": 401, "msg": "用户名或密码错误", "data": None}

    if not user.is_active:
        return {"code": 403, "msg": "账号已被禁用", "data": None}

    _reset_failure(form_data.username)

    access_token = create_access_token({"sub": user.username})
    token_data = {
        "token": access_token,
    }
    return {"code": 200, "msg": "登录成功", "data": token_data}
