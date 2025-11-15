from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from app.user.dependencies import get_blog_info, get_optional_current_user
from app.api.schemas import BlogFullDataDTO
from app.user.schemas import UserDataDTO
from typing import Annotated

templates = Jinja2Templates(directory='app/templates')

router = APIRouter(tags=['Фронтенд'])

@router.get("/blogs/{blog_id}")
async def blog_page(blog_id: int, request: Request, blog_data: Annotated[BlogFullDataDTO, Depends(get_blog_info)], current_user: Annotated[UserDataDTO, Depends(get_optional_current_user)]):
    blog = BlogFullDataDTO.model_validate(blog_data).model_dump()
    blog["author"] = current_user.id
    return templates.TemplateResponse(name="post.html", context={"request": request, "blog": blog, "current_user_id": current_user.id if current_user else None})

@router.get("/blogs/")
async def all_blogs(request: Request):
    pass