from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    full_name: str | None = None

    class Config:
        from_attributes = True


