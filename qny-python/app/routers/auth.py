from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import create_access_token, verify_password, get_password_hash
from ..models.user import User
from ..schemas.auth import Token
from ..schemas.user import UserCreate, UserOut


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
    if not user or not verify_password(form_data.password, user.hashed_password):
        return {"code": 401, "msg": "用户名或密码错误", "data": None}
    access_token = create_access_token({"sub": user.username})
    token_data = {
        "token": access_token,
    }
    return {"code": 200, "msg": "登录成功", "data": token_data}


