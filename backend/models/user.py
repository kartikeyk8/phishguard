from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = ""
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = ""
    score: int
    level: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
