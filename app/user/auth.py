from jose import jwt
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from app.user.dao import UserDAO
from config import get_auth_data
from pydantic import EmailStr

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashed_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    # кодируем токен по переменным окружения
    encode_jwt = jwt.encode(to_encode, auth_data["secret_key"], algorithm=auth_data['algorithm'])
    return encode_jwt

async def authenticated_user(email: EmailStr, password: str):
    user = await UserDAO.get_by_smth(email=email)
    if not user or not verify_password(password=password, hashed_password=user.hashed_password):
        return None
    return user