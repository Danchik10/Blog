from fastapi import APIRouter, HTTPException, status, Response, Depends
from app.user.auth import authenticated_user, create_access_token, hashed_password
from app.user.schemas import UserAuthDTO, UserRegDTO, UserDataDTO
from app.user.dao import UserDAO
from app.user.dependencies import get_current_user
from app.user.models import User
from typing import Annotated, List

router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post("/login/")
async def login(response: Response, user_in: UserAuthDTO):
    auth_user = await authenticated_user(email=user_in.email, password=user_in.password)
    if not auth_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")
    access_token = create_access_token({"sub": str(auth_user.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {"token": access_token}

@router.post("/register/")
async def register(user_in: UserRegDTO):
    auth_user = await authenticated_user(email=user_in.email, password=user_in.password)
    if auth_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь уже существует")
    if user_in.password!=user_in.password_check:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пароли не совпадают")
    hashed_pass = hashed_password(user_in.password)
    await UserDAO.create_add(email=user_in.email, hashed_password=hashed_pass, name=user_in.name)
    return {"message": "пользователь зареган"}

@router.post("/logout/")
async def logout(response: Response):
    response.delete_cookie(key="users_access_token")
    return {"message": "Пользователь вышел"}

@router.get("/profile/")
async def profile(user_data: Annotated[User, Depends(get_current_user)]):
    return UserDataDTO.model_validate(user_data, from_attributes=True)

@router.get("/all_users/")
async def get_all_users() -> List[UserDataDTO]:
    users = await UserDAO.get_all()
    return [UserDataDTO.model_validate({"id": user.id, "name": user.name}) for user in users]