from fastapi import APIRouter, Depends

from ..core.security import get_current_user
from ..models.user import User
from ..schemas.user import UserOut


router = APIRouter(prefix="", tags=["me"])


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


