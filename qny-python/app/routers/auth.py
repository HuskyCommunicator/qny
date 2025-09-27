from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import create_access_token, verify_password, get_password_hash
from ..models.user import User
from ..schemas.auth import Token
from ..schemas.user import UserCreate, UserOut
from ..core.config import settings
import time
from datetime import datetime, timedelta

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


router = APIRouter(prefix="/auth", tags=["auth"])


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
    user = db.query(User).filter(User.username == form_data.username).first()
    # 模拟延迟防止暴力枚举
    if settings.login_delay_ms > 0:
        time.sleep(settings.login_delay_ms / 1000.0)

    # 账户锁定检查（即使用户不存在，也走相同流程，避免信息泄露）
    if _is_locked(form_data.username):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="账号暂时锁定，请稍后再试")

    if not user or not verify_password(form_data.password, user.hashed_password):
<<<<<<< HEAD:qny-python/ai-roleplay-demo/ai-roleplay-demo/backend/app/routers/auth.py
        _register_failure(form_data.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")
    _reset_failure(form_data.username)
=======
        return {"code": 401, "msg": "用户名或密码错误", "data": None}
>>>>>>> e004c1be9588390d46fc64a0b5f820743c41e2de:qny-python/app/routers/auth.py
    access_token = create_access_token({"sub": user.username})
    token_data = {
        "token": access_token,
    }
    return {"code": 200, "msg": "登录成功", "data": token_data}


