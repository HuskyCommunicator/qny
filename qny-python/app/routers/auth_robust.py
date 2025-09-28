"""
健壮性增强的用户认证路由
- 完善的错误处理
- 输入验证和清理
- 安全防护措施
- 日志记录
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from ..core.db import get_db
from ..core.security import create_access_token, verify_password, get_password_hash, get_current_user_jwt
from ..core.config import settings
from ..core.exceptions import ValidationError, AuthenticationError, BusinessLogicError
from ..core.response import APIResponse
from ..models.user import User
from ..schemas.auth import Token, LoginRequest
from ..schemas.user import UserCreate, UserOut
from ..utils.helpers import validate_email, validate_password, sanitize_input
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthService:
    """认证服务类"""

    def __init__(self, db: Session):
        self.db = db

    def validate_user_input(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """验证用户输入"""
        errors = []

        # 用户名验证
        if not username or len(username.strip()) < 3:
            errors.append("用户名至少需要3个字符")
        elif len(username) > 50:
            errors.append("用户名不能超过50个字符")
        else:
            # 清理用户名
            clean_username = sanitize_input(username, max_length=50)
            if not clean_username:
                errors.append("用户名包含非法字符")

        # 邮箱验证
        if not email:
            errors.append("邮箱不能为空")
        elif not validate_email(email):
            errors.append("邮箱格式不正确")

        # 密码验证
        password_validation = validate_password(password)
        if not password_validation["is_valid"]:
            errors.extend(password_validation["errors"])

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "clean_username": clean_username if 'clean_username' in locals() else username
        }

    def check_user_exists(self, username: str, email: str) -> Optional[User]:
        """检查用户是否已存在"""
        try:
            return self.db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
        except Exception as e:
            logger.error(f"查询用户失败: {str(e)}")
            raise BusinessLogicError("用户查询失败")

    def create_user(self, user_data: UserCreate, clean_username: str) -> User:
        """创建用户"""
        try:
            # 清理和验证输入
            clean_email = sanitize_input(user_data.email, max_length=100)
            clean_full_name = sanitize_input(user_data.full_name or "", max_length=100)

            # 创建用户对象
            user = User(
                username=clean_username,
                email=clean_email,
                hashed_password=get_password_hash(user_data.password),
                full_name=clean_full_name,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            logger.info(f"用户创建成功: {user.username} (ID: {user.id})")
            return user

        except Exception as e:
            self.db.rollback()
            logger.error(f"用户创建失败: {str(e)}")
            raise BusinessLogicError("用户创建失败")

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        try:
            # 清理输入
            clean_username = sanitize_input(username, max_length=50)

            # 查询用户
            user = self.db.query(User).filter(User.username == clean_username).first()

            if not user:
                logger.warning(f"用户不存在: {clean_username}")
                return None

            if not user.is_active:
                logger.warning(f"用户已被禁用: {clean_username}")
                raise AuthenticationError("用户账户已被禁用")

            # 验证密码
            if not verify_password(password, user.hashed_password):
                logger.warning(f"密码错误: {clean_username}")
                return None

            # 更新最后登录时间
            user.last_login = datetime.now()
            self.db.commit()

            logger.info(f"用户登录成功: {clean_username} (ID: {user.id})")
            return user

        except Exception as e:
            logger.error(f"用户认证失败: {str(e)}")
            raise BusinessLogicError("用户认证失败")

    def record_login_attempt(self, username: str, success: bool, ip_address: str = None, user_agent: str = None):
        """记录登录尝试（安全审计）"""
        try:
            # 这里可以创建LoginAttempt模型来记录登录尝试
            # 目前仅记录日志
            status = "成功" if success else "失败"
            logger.info(f"登录尝试 {status}: 用户={username}, IP={ip_address}, User-Agent={user_agent}")
        except Exception as e:
            logger.error(f"记录登录尝试失败: {str(e)}")


@router.post("/register", response_model=UserOut)
def register(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """用户注册（健壮版）"""
    auth_service = AuthService(db)

    try:
        # 获取客户端信息
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        logger.info(f"用户注册请求: {payload.username}, IP: {client_ip}")

        # 验证输入
        validation_result = auth_service.validate_user_input(
            payload.username, payload.email, payload.password
        )

        if not validation_result["is_valid"]:
            raise ValidationError(f"输入验证失败: {', '.join(validation_result['errors'])}")

        # 检查用户是否已存在
        existing_user = auth_service.check_user_exists(
            validation_result["clean_username"], payload.email
        )

        if existing_user:
            if existing_user.username == validation_result["clean_username"]:
                raise ValidationError("用户名已存在")
            else:
                raise ValidationError("邮箱已被注册")

        # 创建用户
        user = auth_service.create_user(payload, validation_result["clean_username"])

        logger.info(f"用户注册成功: {user.username} (ID: {user.id})")

        return user

    except ValidationError as e:
        logger.warning(f"用户注册验证失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except BusinessLogicError as e:
        logger.error(f"用户注册业务逻辑错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"用户注册未知错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册过程中发生错误，请稍后重试"
        )


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """用户登录（OAuth2表单格式）"""
    return _handle_login(form_data.username, form_data.password, request, db)


@router.post("/login-json", response_model=Token)
def login_json(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """用户登录（JSON格式）"""
    return _handle_login(payload.username, payload.password, request, db)


@router.post("/user/login", response_model=Token)
def user_login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """用户登录 - JSON格式，前端使用"""
    return _handle_login(payload.username, payload.password, request, db)


def _handle_login(
    username: str,
    password: str,
    request: Request,
    db: Session
) -> Token:
    """统一的登录处理逻辑"""
    auth_service = AuthService(db)

    try:
        # 获取客户端信息
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        logger.info(f"用户登录请求: {username}, IP: {client_ip}")

        # 基本输入验证
        if not username or not password:
            raise ValidationError("用户名和密码不能为空")

        # 清理输入
        clean_username = sanitize_input(username, max_length=50)

        # 用户认证
        user = auth_service.authenticate_user(clean_username, password)

        if not user:
            auth_service.record_login_attempt(clean_username, False, client_ip, user_agent)
            raise AuthenticationError("用户名或密码错误")

        # 检查账户状态
        if not user.is_active:
            auth_service.record_login_attempt(clean_username, False, client_ip, user_agent)
            raise AuthenticationError("用户账户已被禁用")

        # 生成访问令牌
        access_token = create_access_token(data={"sub": user.username})

        # 记录成功登录
        auth_service.record_login_attempt(clean_username, True, client_ip, user_agent)

        logger.info(f"用户登录成功: {user.username} (ID: {user.id})")

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except ValidationError as e:
        logger.warning(f"用户登录验证失败: {username} - {str(e)}")
        if request:
            auth_service.record_login_attempt(username, False, client_ip, user_agent)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except AuthenticationError as e:
        logger.warning(f"用户认证失败: {username} - {str(e)}")
        if request:
            auth_service.record_login_attempt(username, False, client_ip, user_agent)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except BusinessLogicError as e:
        logger.error(f"用户登录业务逻辑错误: {username} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"用户登录未知错误: {username} - {str(e)}", exc_info=True)
        if request:
            auth_service.record_login_attempt(username, False, client_ip, user_agent)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录过程中发生错误，请稍后重试"
        )


@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user_jwt)):
    """获取当前用户信息"""
    return current_user


# 注意：这里使用已存在的get_current_user_jwt函数


@router.post("/logout")
def logout(request: Request, current_user: User = Depends(get_current_user_jwt)):
    """用户登出"""
    try:
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"用户登出: {current_user.username}, IP: {client_ip}")

        # 这里可以添加令牌黑名单逻辑
        # 目前仅记录日志

        return APIResponse.success(
            message="登出成功",
            data={"logout_time": datetime.now().isoformat()}
        )

    except Exception as e:
        logger.error(f"用户登出错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出过程中发生错误"
        )


@router.get("/status")
def get_auth_status():
    """获取认证服务状态"""
    return APIResponse.success(
        data={
            "service": "auth",
            "status": "healthy",
            "features": [
                "user_registration",
                "user_login",
                "jwt_authentication",
                "password_validation",
                "input_sanitization"
            ],
            "timestamp": datetime.now().isoformat()
        },
        message="认证服务运行正常"
    )