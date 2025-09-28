from pydantic import BaseModel, EmailStr, validator, Field
import re


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名长度必须在3-50个字符之间")
    email: EmailStr = Field(..., description="有效的邮箱地址")
    password: str = Field(..., min_length=6, max_length=128, description="密码长度必须在6-128个字符之间")
    full_name: str | None = None

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
        # 密码强度检查
        if len(v) < 6:
            raise ValueError('密码长度至少6位')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'[0-9]', v):
            raise ValueError('密码必须包含数字')
        return v


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    full_name: str | None = None

    class Config:
        from_attributes = True


