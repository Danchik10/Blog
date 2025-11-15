from fastapi import HTTPException, Request, status, Depends
from jose import jwt, JWTError
from datetime import datetime, timezone
from config import get_auth_data
from typing import Annotated
from app.user.dao import UserDAO
from app.user.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dao import BlogDAO
from app.daos.session_maker import SessionDep

def get_token(request: Request) -> str:
    token = request.cookies.get("user_access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="токен не найден")
    return token


async def get_current_user(token: Annotated[str, Depends(get_token)]) -> User:
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], auth_data['algorithm'])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен невалидный")
    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истёк")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не найден id пользователя')
    user = await UserDAO.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    return user

async def get_current_admin_user(user: Annotated[User, Depends(get_current_user)]):
    if user.is_admin or user.is_super_admin:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав')


def get_token_optional(request: Request) -> str | None:
    token = request.cookies.get("user_access_token")
    return token

async def get_optional_current_user(token: Annotated[str, Depends(get_token_optional)]) -> User | None:
    if not token:
        return None
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], auth_data['algorithm'])
    except JWTError:
        return None
    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = await UserDAO.get_by_id(user_id)
    return user

# принимает как авторизованных, так и неавторизованных пользователей
async def get_blog_info(blog_id: int, current_user: Annotated[User | None, Depends(get_optional_current_user)], session: AsyncSession = SessionDep):
    author_id = current_user.id if current_user else None
    blog_info = await BlogDAO.get_blog_info_by_id(blog_id=blog_id, author_id=author_id, session=session)
    return blog_info

