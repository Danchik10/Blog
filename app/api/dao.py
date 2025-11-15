from app.daos.base import BaseDao
from app.api.models import Blog, Tag, BlogTag
from app.api.schemas import BlogFullDataDTO
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from typing import Optional

class BlogDAO(BaseDao):
    model = Blog

    @classmethod
    async def get_blog_info_by_id(cls, blog_id: int, author_id: int, session: AsyncSession):
        query = select(cls.model).options(joinedload(cls.model.user), selectinload(cls.model.tags)).filter_by(id=blog_id)
        res = await session.execute(query)                  # many-to-one(blogs->user) + many-to-many(blogs->tags)
        blog = res.scalar_one_or_none()
        if not blog:
            return {"message": f"Блог с ID={blog_id} не найден или нет прав для его просмотра"}
        if blog.status == "draft" and (author_id!=blog.author):
            return {'message': "Этот блог находится в статусе черновика, и доступ к нему имеют только авторы.",}
        return BlogFullDataDTO.model_validate(blog)

    @classmethod
    async def change_blog_status(cls, new_status: str, blog_id: int, author_id: int, session: AsyncSession):
        if new_status not in ["draft", "published"]:
            return {"message": "Недопустимый статус. Используйте 'draft' или 'published'."}
        try:
            query = select(cls.model).filter_by(id=blog_id)
            res = await session.execute(query)
            blog = res.scalar_one_or_none()
            if not blog:
                return {"message": f"Блог с ID={blog_id} не найден"}
            if blog.author != author_id:
                return {"message": "У вас нет прав на изменение статуса этого блога"}
            if blog.status == new_status:
                return {"message": f"Блог уже имеет статус {new_status}"}
            blog.status = new_status
            await session.flush()

            return {
            'message': f"Статус блога успешно изменен на '{new_status}'.",
            'status': 'success',
            'blog_id': blog_id,
            'new_status': new_status
            }
        except SQLAlchemyError as e:
            await session.rollback()
            return {
                'message': f"Произошла ошибка при изменении статуса блога: {str(e)}",
                'status': 'error'
            }


    @classmethod
    async def delete_blog_info(cls, blog_id: int, author_id: int, session: AsyncSession):
        try:
            query = select(cls.model).filter_by(id=blog_id)
            res = await session.execute(query)
            blog = res.scalar_one_or_none()
            if not blog:
                return {"message": f"Блог с ID={blog_id} не найден"}
            if blog.author != author_id:
                return {'message': "У вас нет прав на удаление этого блога."}
            await session.delete(blog)
            await session.flush()
            return {"message" : f"Блог с ID={blog_id} удалён"}
        except SQLAlchemyError as e:
            await session.rollback()
            return {
                'message': f"Произошла ошибка при удалении блога: {str(e)}",
                'status': 'error'
            }

    # получать все блоги с пагинацией(также можно фильтровать по автору, тэгам)
    @classmethod
    async def get_blog_list(cls, author_id: Optional[int], tag: Optional[str], session: AsyncSession, page: int=1, page_size: int=10):
        # количество записей на странице (от 3 до 100)
        page_size = max(3, min(page_size, 100))
        # номер страницы не будет меньше 1.
        page = max(1, page)
        # выбираем только опубликованные блоги
        query = select(cls.model).options(joinedload(cls.model.user), selectinload(cls.model.tags)).filter_by(status="published")
        if author_id is not None:
            # отфильтровать блоги по автору
            query = query.filter_by(author=author_id)
        if tag:
            # найти блоги по тегу (нечувствительный к регистру поиск)
            query = query.join(cls.model.tags).filter(cls.model.tags.any(Tag.name.ilike(f"%{tag.lower()}%")))
        # подзапрос для подсчета общего числа блогов
        count_query = select(func.count()).select_from(query.subquery())
        res = await session.execute(count_query)
        total_result = res.scalar()
        # общее количество страниц
        total_page = (total_result + page_size - 1) // page_size
        # Пагинация
        # 1. вычисление смещения для текущей страницы
        offset = (page-1)*page_size
        # 2. сколько записей мы видим на странице
        paginated_query = query.offset(offset).limit(page_size)

        res = await session.execute(paginated_query)
        blogs = res.scalars().all()
        # удаление дубликатов блогов по их ID
        unique_blogs = []
        seen_id = set()
        for blog in blogs:
            if blog.id not in seen_id:
                # преобразуем блоги в модель ответа
                unique_blogs.append(BlogFullDataDTO.model_validate(blog))
                seen_id.add(blog.id)
        return {
        "page": page,
        "total_page": total_page,
        "total_result": total_result,
        "blogs": unique_blogs   # выводим блоги
        }

class TagDAO(BaseDao):
    model = Tag

    # добавления тегов в базу данных.
    @classmethod
    async def add_tag(cls, session: AsyncSession, tag_names: list[str]) -> list[int]:
        tag_ids = []
        for tag_name in tag_names:
            tag_low = tag_name.lower()
            # проверяем(по имени) есть ли тэг в бд
            query = select(cls.model).filter_by(name=tag_low)
            query_res = await session.execute(query)
            tag = query_res.scalars().first()
            # если тэг найден, добавляем id в список
            if tag:
                tag_ids.append(tag.id)
            # если тэг не найден, то создаём его и добавляем id в список
            else:
                new_tag = cls.model(name=tag_low)
                session.add(new_tag)
                try:
                    await session.flush() # получаем ID тэга без коммита
                    tag_ids.append(new_tag.id)
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
        return tag_ids


class BlogTagDAO(BaseDao):
    model = BlogTag

    #связываем id блогов и тэгов
    @classmethod
    async def add_blog_tags(cls, session: AsyncSession, blog_tag_pairs: list[dict]) -> None:
        blog_tag_instances = []
        # так выглядит каждый словарь tag_blog = {"blog_id": 1, "tag_id": 2}
        for pair in blog_tag_pairs:
            blog_id = pair.get('blog_id')
            tag_id = pair.get('tag_id')
            if blog_id and tag_id:
                blog_tag = cls.model(blog_id=blog_id, tag_id=tag_id)
                blog_tag_instances.append(blog_tag)
        if blog_tag_instances:
            session.add_all(blog_tag_instances)  # добавляем все объекты за один раз
            try:
                await session.flush()  # сохраняем записи в базе данных без коммита
            except SQLAlchemyError as e:
                await session.rollback()
                raise e