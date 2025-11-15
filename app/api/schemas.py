from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime
from typing import List, Optional
from app.user.schemas import UserDataDTO

class BaseModelConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class BlogDTO(BaseModelConfig):
    title: str = Field(..., description="название блога")
    content: str = Field(..., description="информация блога")
    short_description: str = Field(..., description="краткое описание блога")
    tags: List[str] = []

class TagsDTO(BaseModelConfig):
    id: int = Field(..., description="ID тэга")
    name: str = Field(..., description="название тэга")

class UserDTO(BaseModelConfig):
    id: int = Field(..., description="ID пользователя")
    email: EmailStr = Field(..., description="Электронная почта")
    name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")

class BlogFullDataDTO(BaseModelConfig):
    id: int = Field(..., description="ID блога")
    created_at: datetime = Field(..., description="дата создания")
    updated_at: Optional[datetime] = Field(None, description="дата обновления")
    title: str = Field(..., description="название блога")
    content: str = Field(..., description="информация блога")
    short_description: str = Field(..., description="краткое описание блога")
    status: str = Field(..., description="статус блога")
    user: UserDTO = Field()
    tags: List["TagsDTO"]