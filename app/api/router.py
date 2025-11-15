from fastapi import APIRouter, Depends, Query
from app.api.dao import BlogDAO, TagDAO, BlogTagDAO
from app.api.schemas import BlogDTO, BlogFullDataDTO
from app.user.schemas import UserDataDTO
from app.user.dependencies import get_current_user, get_blog_info
from app.daos.session_maker import TransactionSessionDep, SessionDep
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/api', tags=['API'])

@router.post("/add_post/")
async def add_blog(blog_in: BlogDTO, current_user: Annotated[UserDataDTO, Depends(get_current_user)], session: AsyncSession=TransactionSessionDep):
    """ 1. Добавили блог.
        2. Добавили недостающие теги и получили список ID тегов.
        3. Связали теги и блог в таблице временных связей."""
    blog_data = blog_in.model_dump(exclude={'tags'}) # в модели Blog нет поля tag, а в pydantic модели есть. Поэтому исключаем его
    blog_data["author"] = current_user.id  # обращаемся по ключу author, тем самым создавая новое поле в pydantic, оно устанавливаетя значением текущего польователя
    blog = await BlogDAO.create_add(**blog_data)

    tag_ids = await TagDAO.add_tag(session=session, tag_names=blog_in.tags)

    await BlogTagDAO.add_blog_tags(session=session, blog_tag_pairs=[{"blog_id": blog.id, "tag_id": tag_id} for tag_id in tag_ids])
    return {"message" : f"Блог с ID {blog.id} успешно добавлен с тегами {tag_ids}"}

@router.get("/get_blog/{blog_id}")
async def get_blog(blog_id: int, blog_data: Annotated[BlogFullDataDTO, Depends(get_blog_info)]):
    return blog_data

@router.get("/get_blogs/")
async def get_blogs(author_id: int | None = None,
        tag: str | None = None,
        page: int = Query(1, ge=1, description="Номер страницы"),
        page_size: int = Query(10, ge=10, le=100, description="Записей на странице"), session: AsyncSession = SessionDep):
    blogs = await BlogDAO.get_blog_list(author_id=author_id, tag=tag, session=session, page=page, page_size=page_size)
    if not blogs:
        return {"message": "Блоги не найдены"}
    return blogs

@router.delete("/delete_blog/{blog_id}")
async def delete_blog(blog_id: int, current_user: Annotated[UserDataDTO, Depends(get_current_user)], session: AsyncSession=TransactionSessionDep):
    deleted_blog = await BlogDAO.delete_blog_info(blog_id=blog_id, author_id=current_user.id, session=session)
    return deleted_blog

@router.patch("/update_status/{blog_id}")
async def update_blog_status(blog_id: int, new_status: str, current_user: Annotated[UserDataDTO, Depends(get_current_user)], session: AsyncSession=TransactionSessionDep):
    update_status = await BlogDAO.change_blog_status(new_status=new_status, blog_id=blog_id, author_id=current_user.id, session=session)
    return update_status

