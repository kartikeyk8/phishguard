from fastapi import APIRouter, HTTPException, Depends
from backend.models.user import UserRegister, UserLogin, TokenOut, UserOut
from backend.services.auth_service import register_user, login_user, create_token
from backend.utils.dependencies import get_current_user

router = APIRouter()

def _out(user: dict) -> UserOut:
    return UserOut(
        id    = str(user.get("_id") or user.get("id")),
        name  = user["name"],
        email = user["email"],
        phone = user.get("phone", ""),
        score = user.get("score", 0),
        level = user.get("level", "beginner"),
    )

@router.post("/register", response_model=TokenOut)
def register(body: UserRegister):
    try:
        user = register_user(body.name, body.email, body.password, body.phone)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return TokenOut(access_token=create_token(str(user["_id"])), user=_out(user))

@router.post("/login", response_model=TokenOut)
def login(body: UserLogin):
    try:
        user = login_user(body.email, body.password)
    except ValueError as e:
        raise HTTPException(401, str(e))
    return TokenOut(access_token=create_token(str(user["_id"])), user=_out(user))

@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return _out(current_user)
