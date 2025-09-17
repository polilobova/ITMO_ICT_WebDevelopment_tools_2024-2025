from fastapi import APIRouter, Depends
from models import User
from schemas import UserRead
from routes.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user