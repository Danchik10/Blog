from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.user.dependencies import get_blog_info, get_optional_current_user
from app.api.schemas import BlogFullDataDTO
from app.user.schemas import UserDataDTO
from app.api.dao import BlogDAO
from app.daos.session_maker import SessionDep
from typing import Annotated

templates = Jinja2Templates(directory='app/templates')

router = APIRouter(tags=['Фронтенд'])

@router.get("/blogs/{blog_id}")
async def blog_page(blog_id: int, request: Request, blog_data: Annotated[BlogFullDataDTO, Depends(get_blog_info)],
                    current_user: Annotated[UserDataDTO, Depends(get_optional_current_user)]):
    blog = blog_data.model_dump()
    current_user_id = current_user.id if current_user else None
    return templates.TemplateResponse(name="post.html", context={"request": request, "blog": blog,
                                                                 "current_user_id": current_user_id})


@router.get("/blogs/")
async def blogs_page(request: Request,  session: AsyncSession=SessionDep, author_id: int | None = None, tag: str | None = None, page: int = 1, page_size: int = 3):
    blogs_list = await BlogDAO.get_blog_list(author_id=author_id, tag=tag, session=session, page=page, page_size=page_size)
    return templates.TemplateResponse(name="posts.html", context={"request": request, "blogs_list": blogs_list,
                                                                    "filters": {
                                                                                "author_id": author_id,
                                                                                "tag": tag
                                                                                }})