from database import async_session_maker
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

class BaseDao:
    model = None

    @classmethod
    async def create_add(cls, **values):
        async with async_session_maker() as session:
            query = cls.model(**values)
            session.add(query)
            try:
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
            return query

    @classmethod
    async def get_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            res = await session.execute(query)
            res_orm = res.scalars().all()
            return res_orm

    @classmethod
    async def get_by_id(cls, id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=id)
            res = await session.execute(query)
            res_orm = res.scalar_one_or_none()
            return res_orm

    @classmethod
    async def get_by_smth(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            res = await session.execute(query)
            res_orm = res.scalar_one_or_none()
            return res_orm

    @classmethod
    async def update_by_id(cls, id: int, **values):
        async with async_session_maker() as session:
            query = update(cls.model).values(**values).filter_by(id=id)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def delete_by_id(cls, id: int):
        async with async_session_maker() as session:
            query = await session.get(cls.model, id)
            if query:
                await session.delete(query)
                await session.commit()
                return True
            return False