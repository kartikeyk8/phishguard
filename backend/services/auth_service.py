from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from backend.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from backend.database import users_col
from bson import ObjectId

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=10)

def hash_password(plain): return pwd_ctx.hash(plain)
def verify_password(plain, hashed): return pwd_ctx.verify(plain, hashed)

def create_token(user_id: str) -> str:
    expire  = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> str:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM]).get("sub")

def register_user(name, email, password, phone="") -> dict:
    if users_col.find_one({"email": email}):
        raise ValueError("Email already registered")
    user = {
        "name": name, "email": email, "phone": phone,
        "password": hash_password(password),
        "score": 0, "level": "beginner",
        "created_at": datetime.utcnow()
    }
    result = users_col.insert_one(user)
    user["_id"] = result.inserted_id
    return user

def login_user(email, password) -> dict:
    user = users_col.find_one({"email": email})
    if not user or not verify_password(password, user["password"]):
        raise ValueError("Invalid credentials")
    return user

def get_user_by_id(user_id: str) -> dict:
    return users_col.find_one({"_id": ObjectId(user_id)})
