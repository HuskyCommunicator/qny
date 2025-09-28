from pydantic import BaseModel, EmailStr, validator, Field
import re


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None
    email: str | None = None


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名长度必须在3-50个字符之间")
    password: str = Field(..., min_length=6, max_length=128, description="密码长度必须在6-128个字符之间")

    @validator('username')
    def validate_username(cls, v):
        # 允许邮箱格式或普通用户名格式
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        username_pattern = r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$'
        
        if not (re.match(email_pattern, v) or re.match(username_pattern, v)):
            raise ValueError('用户名只能是有效的邮箱地址或包含字母、数字、下划线和中文的用户名')
        return v

    @validator('password')
    def validate_password(cls, v):
        # 简化密码验证，只检查长度
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        return v


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名长度必须在3-50个字符之间")
    email: EmailStr = Field(..., description="有效的邮箱地址")
    password: str = Field(..., min_length=6, max_length=128, description="密码长度必须在6-128个字符之间")
    confirm_password: str = Field(..., min_length=6, max_length=128, description="确认密码")

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和中文')
        return v

    @validator('password')
    def validate_password(cls, v):
        # 密码强度检查
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'[0-9]', v):
            raise ValueError('密码必须包含数字')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v


