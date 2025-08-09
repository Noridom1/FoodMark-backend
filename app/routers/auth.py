from fastapi import APIRouter, HTTPException
from ..models.user_models import UserRegister, UserLogin
from ..services import user_service

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post("/register")
def register(user: UserRegister):
    data, error = user_service.create_user(user)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {
        "status": "success",
        "data": data
    }