from pydantic import BaseModel, EmailStr, Field

class UserAuthDTO(BaseModel):
    email: EmailStr = Field(..., description="почта", min_length=7, max_length=100)
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 1000 знаков")


class UserRegDTO(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 1000 знаков")
    password_check: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 1000 знаков")
    name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")


class UserDataDTO(BaseModel):
    id: int = Field(..., description="ID пользователя")
    email: EmailStr = Field(..., description="Электронная почта")
    name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    is_user: bool = Field(..., description="Является ли пользователем")
    is_admin: bool = Field(..., description="Является ли админом")
    is_super_admin: bool = Field(..., description="Является ли суперпользователем")

